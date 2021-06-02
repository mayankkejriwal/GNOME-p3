from monopoly_simulator import initialize_game_elements
# from monopoly_simulator.action_choices import roll_die
from monopoly_simulator import action_choices
import numpy as np
from monopoly_simulator import card_utility_actions
from monopoly_simulator import background_agent_v3_1
from monopoly_simulator import read_write_current_state
import json
from monopoly_simulator import novelty_generator
from monopoly_simulator import diagnostics
from monopoly_simulator.agent import Agent
import xlsxwriter
from monopoly_simulator.flag_config import flag_config_dict
from monopoly_simulator.logging_info import log_file_create
import os
import time
import logging
logger = logging.getLogger('monopoly_simulator.logging_info')


def write_history_to_file(game_board, workbook):
    worksheet = workbook.add_worksheet()
    col = 0
    for key in game_board['history']:
        if key == 'param':
            col += 1
            row = 0
            worksheet.write(row, col, key)
            worksheet.write(row, col + 1, 'current_player')
            for item in game_board['history'][key]:
                worksheet.write(row + 1, col, str(item))
                try:
                    worksheet.write(row + 1, col + 1, item['player'].player_name)
                except:
                    pass
                row += 1
            col += 1
        else:
            col += 1
            row = 0
            worksheet.write(row, col, key)
            for item in game_board['history'][key]:
                worksheet.write(row + 1, col, str(item))
                row += 1
    workbook.close()
    print("History logged into history_log.xlsx file.")


def disable_history(game_elements):
    game_elements['history'] = dict()
    game_elements['history']['function'] = list()
    game_elements['history']['param'] = list()
    game_elements['history']['return'] = list()
    game_elements['history']['time_step'] = list()


def simulate_game_instance(game_elements, history_log_file=None, np_seed=2):
    """
    Simulate a game instance.
    :param game_elements: The dict output by set_up_board
    :param np_seed: The numpy seed to use to control randomness.
    :return: None
    """
    logger.debug("size of board " + str(len(game_elements['location_sequence'])))
    np.random.seed(np_seed)
    np.random.shuffle(game_elements['players'])
    game_elements['seed'] = np_seed
    game_elements['card_seed'] = np_seed
    game_elements['choice_function'] = np.random.choice
    count_json = 0   # a counter to keep track of how many rounds the game has to be played before storing the current_state of gameboard to file.
    num_die_rolls = 0
    tot_time = 0
    # game_elements['go_increment'] = 100 # we should not be modifying this here. It is only for testing purposes.
    # One reason to modify go_increment is if your decision agent is not aggressively trying to monopolize. Since go_increment
    # by default is 200 it can lead to runaway cash increases for simple agents like ours.

    logger.debug(
        'players will play in the following order: ' + '->'.join([p.player_name for p in game_elements['players']]))
    logger.debug('Beginning play. Rolling first die...')
    current_player_index = 0
    num_active_players = 4
    winner = None
    workbook = None
    if history_log_file:
        workbook = xlsxwriter.Workbook(history_log_file)
    game_elements['start_time'] = time.time()
    game_elements['time_step_indicator'] = 0

    while num_active_players > 1:
        disable_history(
            game_elements)  # comment this out when you want history to stay. Currently, it has high memory consumption, we are working to solve the problem (most likely due to deep copy run-off).
        current_player = game_elements['players'][current_player_index]
        while current_player.status == 'lost':
            current_player_index += 1
            current_player_index = current_player_index % len(game_elements['players'])
            current_player = game_elements['players'][current_player_index]
        current_player.status = 'current_move'

        # pre-roll for current player + out-of-turn moves for everybody else,
        # till we get num_active_players skip turns in a row.

        skip_turn = 0
        if current_player.make_pre_roll_moves(game_elements) == 2:  # 2 is the special skip-turn code
            skip_turn += 1
        out_of_turn_player_index = current_player_index + 1
        out_of_turn_count = 0
        while skip_turn != num_active_players and out_of_turn_count <= 5:  ##oot count reduced to 20 from 200 to keep the game short
            out_of_turn_count += 1
            # print('checkpoint 1')
            out_of_turn_player = game_elements['players'][out_of_turn_player_index % len(game_elements['players'])]
            if out_of_turn_player.status == 'lost':
                out_of_turn_player_index += 1
                continue

            oot_code = out_of_turn_player.make_out_of_turn_moves(game_elements)
            # add to game history
            game_elements['history']['function'].append(out_of_turn_player.make_out_of_turn_moves)
            params = dict()
            params['self'] = out_of_turn_player
            params['current_gameboard'] = game_elements
            game_elements['history']['param'].append(params)
            game_elements['history']['return'].append(oot_code)
            game_elements['history']['time_step'].append(game_elements['time_step_indicator'])

            if oot_code == 2:
                skip_turn += 1
            else:
                skip_turn = 0
            out_of_turn_player_index += 1

        # now we roll the dice and get into the post_roll phase,
        # but only if we're not in jail.
        # but only if we're not in jail.

        logger.debug("Printing cash balance and net worth of each player: ")
        diagnostics.print_player_net_worths_and_cash_bal(game_elements)

        r = action_choices.roll_die(game_elements['dies'], np.random.choice, game_elements)        # change
        for i in range(len(r)):
            game_elements['die_sequence'][i].append(r[i])

        # add to game history
        game_elements['history']['function'].append(action_choices.roll_die)
        params = dict()
        params['die_objects'] = game_elements['dies']
        params['choice'] = np.random.choice
        params['current_gameboard'] = game_elements
        game_elements['history']['param'].append(params)
        game_elements['history']['return'].append(r)
        game_elements['history']['time_step'].append(game_elements['time_step_indicator'])

        num_die_rolls += 1
        game_elements['current_die_total'] = sum(r)
        logger.debug('dies have come up ' + str(r))
        if not current_player.currently_in_jail:
            check_for_go = True
            game_elements['move_player_after_die_roll'](current_player, sum(r), game_elements, check_for_go)
            # add to game history
            game_elements['history']['function'].append(game_elements['move_player_after_die_roll'])
            params = dict()
            params['player'] = current_player
            params['rel_move'] = sum(r)
            params['current_gameboard'] = game_elements
            params['check_for_go'] = check_for_go
            game_elements['history']['param'].append(params)
            game_elements['history']['return'].append(None)
            game_elements['history']['time_step'].append(game_elements['time_step_indicator'])

            current_player.process_move_consequences(game_elements)
            # add to game history
            game_elements['history']['function'].append(current_player.process_move_consequences)
            params = dict()
            params['self'] = current_player
            params['current_gameboard'] = game_elements
            game_elements['history']['param'].append(params)
            game_elements['history']['return'].append(None)
            game_elements['history']['time_step'].append(game_elements['time_step_indicator'])

            # post-roll for current player. No out-of-turn moves allowed at this point.
            current_player.make_post_roll_moves(game_elements)
            # add to game history
            game_elements['history']['function'].append(current_player.make_post_roll_moves)
            params = dict()
            params['self'] = current_player
            params['current_gameboard'] = game_elements
            game_elements['history']['param'].append(params)
            game_elements['history']['param'].append(params)
            game_elements['history']['return'].append(None)
            game_elements['history']['time_step'].append(game_elements['time_step_indicator'])

        else:
            # current_player.currently_in_jail = False  # the player is only allowed to skip one turn (i.e. this one)
            card_utility_actions.set_currently_in_jail_to_false(current_player, game_elements)      # change

        if current_player.current_cash < 0:
            code = current_player.handle_negative_cash_balance(game_elements)
            # add to game history
            game_elements['history']['function'].append(current_player.handle_negative_cash_balance)
            params = dict()
            params['self'] = current_player
            params['current_gameboard'] = game_elements
            game_elements['history']['param'].append(params)
            game_elements['history']['return'].append(code)
            game_elements['history']['time_step'].append(game_elements['time_step_indicator'])

            if code == flag_config_dict['failure_code'] or current_player.current_cash < 0:
                current_player.begin_bankruptcy_proceedings(game_elements)
                # add to game history
                game_elements['history']['function'].append(current_player.begin_bankruptcy_proceedings)
                params = dict()
                params['self'] = current_player
                params['current_gameboard'] = game_elements
                game_elements['history']['param'].append(params)
                game_elements['history']['return'].append(None)
                game_elements['history']['time_step'].append(game_elements['time_step_indicator'])

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
        else:
            current_player.status = 'waiting_for_move'

        current_player_index = (current_player_index + 1) % len(game_elements['players'])
        tot_time = time.time() - game_elements['start_time']

        if card_utility_actions.check_for_game_termination(game_elements, tot_time):
            # game terminates if check_for_game_termination returns true.
            # We print some diagnostics and return if any player exceeds this.
            diagnostics.print_asset_owners(game_elements)
            diagnostics.print_player_cash_balances(game_elements)
            logger.debug("Game ran for " + str(tot_time) + " seconds.")
            break

        #This is an example of how you may want to write out gameboard state to file.
        #Uncomment the following piece of code to write out the gameboard current_state to file at the "count_json" iteration.
        #All the data from game_elements will be written to a .json file which can be read back to intialize a new game with
        #those gameboard values to start the game from that point onwards.
        '''
        if count_json == 50:
            outfile = '../current_gameboard_state.json'
            oot_code = read_write_current_state.write_out_current_state_to_file(game_elements, outfile)
            if oot_code == 1:
                print("Successfully written gameboard current state to file.")
                logger.debug("Successfully written gameboard current state to file.")
                print("Cash in hand with players when writing gameboard state to file: ")
                for player in game_elements['players']:
                    print(player.player_name, " current cash=", player.current_cash)
            else:
                print("Something went wrong when trying to write gameboard state to file. "
                      "Rest of the game will be played as normal but will not log state to file.")
        '''
        count_json += 1

    logger.debug('Liquid Cash remaining with Bank = ' + str(game_elements['bank'].total_cash_with_bank))

    if workbook:
        write_history_to_file(game_elements, workbook)
    # let's print some numbers
    logger.debug('printing final asset owners: ')
    diagnostics.print_asset_owners(game_elements)
    logger.debug('number of dice rolls: ' + str(num_die_rolls))
    logger.debug('printing final cash balances: ')
    diagnostics.print_player_cash_balances(game_elements)
    logger.debug("printing net worth of each player: ")
    diagnostics.print_player_net_worths(game_elements)
    logger.debug("Game ran for " + str(tot_time) + " seconds.")

    if winner:
        logger.debug('We have a winner: ' + winner.player_name)
        return winner.player_name
    else:
        winner = card_utility_actions.check_for_winner(game_elements)
        if winner is not None:
            logger.debug('We have a winner: ' + winner.player_name)
            return winner.player_name
        else:
            logger.debug('Game has no winner, do not know what went wrong!!!')
            return None     # ideally should never get here


def set_up_board(game_schema_file_path, player_decision_agents):
    game_schema = json.load(open(game_schema_file_path, 'r'))
    return initialize_game_elements.initialize_board(game_schema, player_decision_agents)


def inject_novelty(current_gameboard, novelty_schema=None):
    """
    Function for illustrating how we inject novelty
    ONLY FOR ILLUSTRATIVE PURPOSES
    :param current_gameboard: the current gameboard into which novelty will be injected. This gameboard will be modified
    :param novelty_schema: the novelty schema json, read in from file. It is more useful for running experiments at scale
    rather than in functions like these. For the most part, we advise writing your novelty generation routines, just like
    we do below, and for using the novelty schema for informational purposes (i.e. for making sense of the novelty_generator.py
    file and its functions.
    :return: None
    """

    ###Below are examples of Level 1, Level 2 and Level 3 Novelties
    ###Uncomment only the Level of novelty that needs to run (i.e, either Level1 or Level 2 or Level 3). Do not mix up novelties from different levels.

    '''
    #Level 1 Novelty
    numberDieNovelty = novelty_generator.NumberClassNovelty()
    numberDieNovelty.die_novelty(current_gameboard, 4, die_state_vector=[[1,2,3,4,5],[1,2,3,4],[5,6,7],[2,3,4]])
    
    classDieNovelty = novelty_generator.TypeClassNovelty()
    die_state_distribution_vector = ['uniform','uniform','biased','biased']
    die_type_vector = ['odd_only','even_only','consecutive','consecutive']
    classDieNovelty.die_novelty(current_gameboard, die_state_distribution_vector, die_type_vector)
    
    classCardNovelty = novelty_generator.TypeClassNovelty()
    novel_cc = dict()
    novel_cc["street_repairs"] = "alternate_contingency_function_1"
    novel_chance = dict()
    novel_chance["general_repairs"] = "alternate_contingency_function_1"
    classCardNovelty.card_novelty(current_gameboard, novel_cc, novel_chance)
    '''

    '''
    #Level 2 Novelty
    #The below combination reassigns property groups and individual properties to different colors.
    #On playing the game it is verified that the newly added property to the color group is taken into account for monopolizing a color group,
    # i,e the orchid color group now has Baltic Avenue besides St. Charles Place, States Avenue and Virginia Avenue. The player acquires a monopoly
    # only on the ownership of all the 4 properties in this case.
    
    inanimateNovelty = novelty_generator.InanimateAttributeNovelty()
    inanimateNovelty.map_property_set_to_color(current_gameboard, [current_gameboard['location_objects']['Park Place'], current_gameboard['location_objects']['Boardwalk']], 'Brown')
    inanimateNovelty.map_property_to_color(current_gameboard, current_gameboard['location_objects']['Baltic Avenue'], 'Orchid')
    #setting new rents for Indiana Avenue
    inanimateNovelty.rent_novelty(current_gameboard['location_objects']['Indiana Avenue'], {'rent': 50, 'rent_1_house': 150})
    '''

    '''
    #Level 3 Novelty
    granularityNovelty = novelty_generator.GranularityRepresentationNovelty()
    granularityNovelty.granularity_novelty(current_gameboard, current_gameboard['location_objects']['Baltic Avenue'], 6)
    granularityNovelty.granularity_novelty(current_gameboard, current_gameboard['location_objects']['States Avenue'], 20)
    granularityNovelty.granularity_novelty(current_gameboard, current_gameboard['location_objects']['Tennessee Avenue'], 27)
    spatialNovelty = novelty_generator.SpatialRepresentationNovelty()
    spatialNovelty.color_reordering(current_gameboard, ['Boardwalk', 'Park Place'], 'Blue')
    granularityNovelty.granularity_novelty(current_gameboard, current_gameboard['location_objects']['Park Place'], 52)
    '''


def play_game():
    """
    Use this function if you want to test a single game instance and control lots of things. For experiments, we will directly
    call some of the functions in gameplay from test_harness.py.
    This is where everything begins. Assign decision agents to your players, set up the board and start simulating! You can
    control any number of players you like, and assign the rest to the simple agent. We plan to release a more sophisticated
    but still relatively simple agent soon.
    :return: String. the name of the player who won the game, if there was a winner, otherwise None.
    """

    try:
        os.makedirs('../single_tournament/')
        print('Creating folder and logging gameplay.')
    except:
        print('Logging gameplay.')

    logger = log_file_create('../single_tournament/seed_6.log')
    player_decision_agents = dict()
    # for p in ['player_1','player_3']:
    #     player_decision_agents[p] = simple_decision_agent_1.decision_agent_methods

    player_decision_agents['player_1'] = Agent(**background_agent_v3_1.decision_agent_methods)
    player_decision_agents['player_2'] = Agent(**background_agent_v3_1.decision_agent_methods)
    player_decision_agents['player_3'] = Agent(**background_agent_v3_1.decision_agent_methods)
    player_decision_agents['player_4'] = Agent(**background_agent_v3_1.decision_agent_methods)

    game_elements = set_up_board('../monopoly_game_schema_v1-2.json',
                                 player_decision_agents)

    #Comment out the above line and uncomment the piece of code to read the gameboard state from an existing json file so that
    #the game starts from a particular game state instead of initializing the gameboard with default start values.
    #Note that the novelties introduced in that particular game which was saved to file will be loaded into this game board as well.
    '''
    logger.debug("Loading gameboard from an existing game state that was saved to file.")
    infile = '../current_gameboard_state.json'
    game_elements = read_write_current_state.read_in_current_state_from_file(infile, player_decision_agents)
    '''

    inject_novelty(game_elements)

    if player_decision_agents['player_1'].startup(game_elements) == flag_config_dict['failure_code'] or \
            player_decision_agents['player_2'].startup(game_elements) == flag_config_dict['failure_code'] or \
            player_decision_agents['player_3'].startup(game_elements) == flag_config_dict['failure_code'] or \
            player_decision_agents['player_4'].startup(game_elements) == flag_config_dict['failure_code']:
        logger.error("Error in initializing agents. Cannot play the game.")
        return None
    else:
        logger.debug("Sucessfully initialized all player agents.")
        winner = simulate_game_instance(game_elements)
        if player_decision_agents['player_1'].shutdown() == flag_config_dict['failure_code'] or \
            player_decision_agents['player_2'].shutdown() == flag_config_dict['failure_code'] or \
            player_decision_agents['player_3'].shutdown() == flag_config_dict['failure_code'] or \
            player_decision_agents['player_4'].shutdown() == flag_config_dict['failure_code']:
            logger.error("Error in agent shutdown.")
            handlers_copy = logger.handlers[:]
            for handler in handlers_copy:
                logger.removeHandler(handler)
                handler.close()
                handler.flush()
            return None
        else:
            logger.debug("All player agents have been shutdown. ")
            logger.debug("GAME OVER")
            handlers_copy = logger.handlers[:]
            for handler in handlers_copy:
                logger.removeHandler(handler)
                handler.close()
                handler.flush()
            return winner


def play_game_in_tournament(game_seed, novelty_info=False, inject_novelty_function=None):
    logger.debug('seed used: ' + str(game_seed))
    player_decision_agents = dict()
    # for p in ['player_1','player_3']:
    #     player_decision_agents[p] = simple_decision_agent_1.decision_agent_methods
    player_decision_agents['player_1'] = Agent(**background_agent_v3_1.decision_agent_methods)
    player_decision_agents['player_2'] = Agent(**background_agent_v3_1.decision_agent_methods)
    player_decision_agents['player_3'] = Agent(**background_agent_v3_1.decision_agent_methods)
    player_decision_agents['player_4'] = Agent(**background_agent_v3_1.decision_agent_methods)

    game_elements = set_up_board('../monopoly_game_schema_v1-2.json',
                                 player_decision_agents)

    #Comment out the above line and uncomment the piece of code to read the gameboard state from an existing json file so that
    #the game starts from a particular game state instead of initializing the gameboard with default start values.
    #Note that the novelties introduced in that particular game which was saved to file will be loaded into this game board as well.
    '''
    logger.debug("Loading gameboard from an existing game state that was saved to file.")
    infile = '../current_gameboard_state.json'
    game_elements = read_write_current_state.read_in_current_state_from_file(infile, player_decision_agents)
    '''

    if inject_novelty_function:
        inject_novelty_function(game_elements)

    if not novelty_info:
        if player_decision_agents['player_1'].startup(game_elements) == flag_config_dict['failure_code'] or \
                player_decision_agents['player_2'].startup(game_elements) == flag_config_dict['failure_code'] or \
                player_decision_agents['player_3'].startup(game_elements) == flag_config_dict['failure_code'] or \
                player_decision_agents['player_4'].startup(game_elements) == flag_config_dict['failure_code']:
            logger.error("Error in initializing agents. Cannot play the game.")
            return None
        else:
            logger.debug("Sucessfully initialized all player agents.")
            winner = simulate_game_instance(game_elements, history_log_file=None, np_seed=game_seed)
            if player_decision_agents['player_1'].shutdown() == flag_config_dict['failure_code'] or \
                    player_decision_agents['player_2'].shutdown() == flag_config_dict['failure_code'] or \
                    player_decision_agents['player_3'].shutdown() == flag_config_dict['failure_code'] or \
                    player_decision_agents['player_4'].shutdown() == flag_config_dict['failure_code']:
                logger.error("Error in agent shutdown.")
                return None
            else:
                logger.debug("All player agents have been shutdown. ")
                logger.debug("GAME OVER")
                return winner
    else:
        if inject_novelty_function:
            if player_decision_agents['player_1'].startup(game_elements, indicator=True) == flag_config_dict['failure_code'] or \
                    player_decision_agents['player_2'].startup(game_elements, indicator=True) == flag_config_dict['failure_code'] or \
                    player_decision_agents['player_3'].startup(game_elements, indicator=True) == flag_config_dict['failure_code'] or \
                    player_decision_agents['player_4'].startup(game_elements, indicator=True) == flag_config_dict['failure_code']:
                logger.error("Error in initializing agents. Cannot play the game.")
                return None
            else:
                logger.debug("Sucessfully initialized all player agents.")
                winner = simulate_game_instance(game_elements, history_log_file=None, np_seed=game_seed)
                if player_decision_agents['player_1'].shutdown() == flag_config_dict['failure_code'] or \
                        player_decision_agents['player_2'].shutdown() == flag_config_dict['failure_code'] or \
                        player_decision_agents['player_3'].shutdown() == flag_config_dict['failure_code'] or \
                        player_decision_agents['player_4'].shutdown() == flag_config_dict['failure_code']:
                    logger.error("Error in agent shutdown.")
                    return None
                else:
                    logger.debug("All player agents have been shutdown. ")
                    logger.debug("GAME OVER")
                    return winner
        else:
            if player_decision_agents['player_1'].startup(game_elements, indicator=False) == flag_config_dict['failure_code'] or \
                    player_decision_agents['player_2'].startup(game_elements, indicator=False) == flag_config_dict['failure_code'] or \
                    player_decision_agents['player_3'].startup(game_elements, indicator=False) == flag_config_dict['failure_code'] or \
                    player_decision_agents['player_4'].startup(game_elements, indicator=False) == flag_config_dict['failure_code']:
                logger.error("Error in initializing agents. Cannot play the game.")
                return None
            else:
                logger.debug("Sucessfully initialized all player agents.")
                winner = simulate_game_instance(game_elements, history_log_file=None, np_seed=game_seed)
                if player_decision_agents['player_1'].shutdown() == flag_config_dict['failure_code'] or \
                        player_decision_agents['player_2'].shutdown() == flag_config_dict['failure_code'] or \
                        player_decision_agents['player_3'].shutdown() == flag_config_dict['failure_code'] or \
                        player_decision_agents['player_4'].shutdown() == flag_config_dict['failure_code']:
                    logger.error("Error in agent shutdown.")
                    return None
                else:
                    logger.debug("All player agents have been shutdown. ")
                    logger.debug("GAME OVER")
                    return winner

# play_game()
