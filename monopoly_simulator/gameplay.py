from monopoly_simulator import initialize_game_elements
from monopoly_simulator.action_choices import roll_die
import numpy as np
from monopoly_simulator.card_utility_actions import move_player_after_die_roll
from monopoly_simulator import background_agent_v1
# import simple_decision_agent_1
import json
from monopoly_simulator import diagnostics
from monopoly_simulator.agent import Agent
import xlsxwriter

def write_history_to_file(game_board, workbook):
    worksheet = workbook.add_worksheet()
    col = 0
    for key in game_board['history']:
        if key=='param':
            col += 1
            row = 0
            worksheet.write(row, col, key)
            worksheet.write(row, col+1, 'current_player')
            for item in game_board['history'][key]:
                worksheet.write(row+1, col, str(item))
                try:
                    worksheet.write(row+1, col+1, item['player'].player_name)
                except:
                    pass
                row += 1
            col+=1

        else:
            col += 1
            row = 0
            worksheet.write(row, col, key)
            for item in game_board['history'][key]:
                worksheet.write(row+1, col, str(item))
                row += 1
    workbook.close()
    print("History logged into history_log.xlsx file.")

def simulate_game_instance(game_elements, np_seed=6, history_log_file=None):
    """
    Simulate a game instance.
    :param game_elements: The dict output by set_up_board
    :param np_seed: The numpy seed to use to control randomness.
    :return: None
    """
    np.random.seed(np_seed)
    np.random.shuffle(game_elements['players'])
    game_elements['seed'] = np_seed
    game_elements['card_seed'] = np_seed
    game_elements['choice_function'] = np.random.choice

    num_die_rolls = 0
    # game_elements['go_increment'] = 100 # we should not be modifying this here. It is only for testing purposes.
    # One reason to modify go_increment is if your decision agent is not aggressively trying to monopolize. Since go_increment
    # by default is 200 it can lead to runaway cash increases for simple agents like ours.

    print('players will play in the following order: ','->'.join([p.player_name for p in game_elements['players']]))
    print('Beginning play. Rolling first die...')
    current_player_index = 0
    num_active_players = 4
    winner = None
    workbook = None
    if history_log_file:
        workbook = xlsxwriter.Workbook(history_log_file)

    while num_active_players > 1:
        current_player = game_elements['players'][current_player_index]
        while current_player.status == 'lost':
            current_player_index += 1
            current_player_index = current_player_index % len(game_elements['players'])
            current_player = game_elements['players'][current_player_index]
        current_player.status = 'current_move'

        # pre-roll for current player + out-of-turn moves for everybody else,
        # till we get num_active_players skip turns in a row.

        skip_turn = 0
        if current_player.make_pre_roll_moves(game_elements) == 2: # 2 is the special skip-turn code
            skip_turn += 1
        out_of_turn_player_index = current_player_index + 1
        out_of_turn_count = 0
        while skip_turn != num_active_players and out_of_turn_count<=200:
            out_of_turn_count += 1
            # print('checkpoint 1')
            out_of_turn_player = game_elements['players'][out_of_turn_player_index%len(game_elements['players'])]
            if out_of_turn_player.status == 'lost':
                out_of_turn_player_index += 1
                continue
            oot_code = out_of_turn_player.make_out_of_turn_moves(game_elements)
            # add to game history
            game_elements['history']['function'].append(out_of_turn_player.make_out_of_turn_moves)
            params = dict()
            params['self']=out_of_turn_player
            params['current_gameboard']=game_elements
            game_elements['history']['param'].append(params)
            game_elements['history']['return'].append(oot_code)

            if  oot_code == 2:
                skip_turn += 1
            else:
                skip_turn = 0
            out_of_turn_player_index += 1

        # now we roll the dice and get into the post_roll phase,
        # but only if we're not in jail.


        r = roll_die(game_elements['dies'], np.random.choice)
        # add to game history
        game_elements['history']['function'].append(roll_die)
        params = dict()
        params['die_objects'] = game_elements['dies']
        params['choice'] = np.random.choice
        game_elements['history']['param'].append(params)
        game_elements['history']['return'].append(r)

        num_die_rolls += 1
        game_elements['current_die_total'] = sum(r)
        print('dies have come up ',str(r))
        if not current_player.currently_in_jail:
            check_for_go = True
            move_player_after_die_roll(current_player, sum(r), game_elements, check_for_go)
            # add to game history
            game_elements['history']['function'].append(move_player_after_die_roll)
            params = dict()
            params['player'] = current_player
            params['rel_move'] = sum(r)
            params['current_gameboard'] = game_elements
            params['check_for_go'] = check_for_go
            game_elements['history']['param'].append(params)
            game_elements['history']['return'].append(None)

            current_player.process_move_consequences(game_elements)
            # add to game history
            game_elements['history']['function'].append(current_player.process_move_consequences)
            params = dict()
            params['self'] = current_player
            params['current_gameboard'] = game_elements
            game_elements['history']['param'].append(params)
            game_elements['history']['return'].append(None)

            # post-roll for current player. No out-of-turn moves allowed at this point.
            current_player.make_post_roll_moves(game_elements)
            # add to game history
            game_elements['history']['function'].append(current_player.make_post_roll_moves)
            params = dict()
            params['self'] = current_player
            params['current_gameboard'] = game_elements
            game_elements['history']['param'].append(params)
            game_elements['history']['return'].append(None)

        else:
            current_player.currently_in_jail = False # the player is only allowed to skip one turn (i.e. this one)

        if current_player.current_cash < 0:
            code = current_player.agent.handle_negative_cash_balance(current_player, game_elements)
            # add to game history
            game_elements['history']['function'].append(current_player.agent.handle_negative_cash_balance)
            params = dict()
            params['player'] = current_player
            params['current_gameboard'] = game_elements
            game_elements['history']['param'].append(params)
            game_elements['history']['return'].append(code)
            if code == -1 or current_player.current_cash < 0:
                current_player.begin_bankruptcy_proceedings(game_elements)
                # add to game history
                game_elements['history']['function'].append(current_player.begin_bankruptcy_proceedings)
                params = dict()
                params['self'] = current_player
                params['current_gameboard'] = game_elements
                game_elements['history']['param'].append(params)
                game_elements['history']['return'].append(None)

                num_active_players -= 1
                diagnostics.print_asset_owners(game_elements)
                diagnostics.print_player_cash_balances(game_elements)

                if num_active_players == 1:
                    for p in game_elements['players']:
                        if p.status != 'lost':
                            winner = p
                            p.status = 'won'
        else:
            current_player.status = 'waiting_for_move'

        current_player_index = (current_player_index+1)%len(game_elements['players'])

        if diagnostics.max_cash_balance(game_elements) > 300000: # this is our limit for runaway cash for testing purposes only.
                                                                 # We print some diagnostics and return if any player exceeds this.
            diagnostics.print_asset_owners(game_elements)
            diagnostics.print_player_cash_balances(game_elements)
            return

    if workbook:
        write_history_to_file(game_elements, workbook)
    # let's print some numbers
    print('printing final asset owners: ')
    diagnostics.print_asset_owners(game_elements)
    print('number of dice rolls: ',str(num_die_rolls))
    print('printing final cash balances: ')
    diagnostics.print_player_cash_balances(game_elements)

    if winner:
        print('We have a winner: ', winner.player_name)

    return


def set_up_board(game_schema_file_path, player_decision_agents):
    game_schema = json.load(open(game_schema_file_path, 'r'))
    return initialize_game_elements.initialize_board(game_schema, player_decision_agents)


# this is where everything begins. Assign decision agents to your players, set up the board and start simulating! You can
# control any number of players you like, and assign the rest to the simple agent. We plan to release a more sophisticated
# but still relatively simple agent soon.
player_decision_agents = dict()
# for p in ['player_1','player_3']:
#     player_decision_agents[p] = simple_decision_agent_1.decision_agent_methods
player_decision_agents['player_1'] = Agent(**background_agent_v1.decision_agent_methods)
player_decision_agents['player_2'] = Agent(**background_agent_v1.decision_agent_methods)
player_decision_agents['player_3'] = Agent(**background_agent_v1.decision_agent_methods)
player_decision_agents['player_4'] = Agent(**background_agent_v1.decision_agent_methods)
game_elements = set_up_board('/Users/mayankkejriwal/git-projects/GNOME-p3/monopoly_game_schema_v1-2.json',
                             player_decision_agents)
simulate_game_instance(game_elements)

#just testing history.
# print(len(game_elements['history']['function']))
# print(len(game_elements['history']['param']))
# print(len(game_elements['history']['return']))