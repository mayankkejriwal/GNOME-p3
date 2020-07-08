import pprint
import copy, json
import numpy
import diagnostics
from card_utility_actions import move_player_after_die_roll


def initialize_hypothetical_universe(current_gameboard, player_decision_agents, seed=3):
    # you should always use your own seed, rather than using ours, since it would be like looking into the future.
    hypothetical_gameboard = copy.deepcopy(current_gameboard)
    player_name_obj = dict()
    for p in hypothetical_gameboard['players']:
        player_name_obj[p.player_name] = p
        # pprint.pprint(p.__dict__)
    for k,v in player_name_obj.items(): # k,v is player name, player object
        v.change_decision_agent(player_decision_agents[k])
    # for p in hypothetical_gameboard['players']:
    #     pprint.pprint(p.__dict__) # we've run the check and verified the function pointer changes
    hypothetical_gameboard['seed'] = seed
    hypothetical_gameboard['choice_function'] = numpy.random.choice # you can set these with your own, or you could ignore these fields (our recommended option since this field might be removed in the near future)

    hypothetical_gameboard['randomState'] = numpy.random.RandomState(seed=hypothetical_gameboard['seed']) # this is a new field that I am injecting into the hypothetical gameboard
    # to be used in my die_roll_substitute function. In general, you should feel free to add stuff to hypothetical_gameboard as necessary
    # with the understanding that it won't be used in the main game simulation, but only in functions you control (agent decision making

    randstate1 = numpy.random.RandomState(seed=seed)
    randstate2 = numpy.random.RandomState(seed=seed)
    hypothetical_gameboard['chance_choice_function'] = randstate1.choice
    hypothetical_gameboard['cc_choice_function'] = randstate2.choice

    # and in your die_roll_substitute function.
    return hypothetical_gameboard


def simulate_hypothetical_game(hypothetical_gameboard, die_roll_substitute, num_total_die_rolls=-1):
    """
    If you want to simulate the game from a different 'starting' point than when you spawned the hypothetical universe,
    then you should make those changes (e.g., you could change the current_player, but you should do so safely i.e.
    make sure there aren't 'two' current players!) before calling simulate.

    :param hypothetical_gameboard:
    :param die_roll_substitute: This is a function that takes the list of Dice objects in the hypothetical gameboard as
    its argument. See expected function signature (and example) at the end of this file
    :param num_total_die_rolls: If -1, then the 'hypothetical' game will play out till the end. Otherwise, specify the total
    number of die rolls that the game should run for (following which, it will terminate with no winner, assuming there is
    more than one active player still).
    :return: A player instance representing the winner, or None
    """
    num_die_rolls = 0 # this field will start from 0 i.e. it is counting how many 'die rolls' have happened only in the alternate universe

    current_player_index = -1
    num_active_players = 0
    winner = None
    for i, p in enumerate(hypothetical_gameboard['players']):
        if p.status == 'won':
            print('there is already a winner here. returning...')
            winner = p
            return winner
        elif p.status != 'lost':
            num_active_players += 1
            if p.status == 'current_move':
                if current_player_index != -1:
                    print('there is more than one current player. Terminating with no winner...')
                    return winner
                current_player_index = i

    print('In your alternate universe, the current player is ',hypothetical_gameboard['players'][current_player_index].player_name)
    print('Number of active players is ',num_active_players)

    print('STARTING HYPOTHETICAL GAMEPLAY...')
    while num_active_players > 1 and (num_total_die_rolls==-1 or num_total_die_rolls>num_die_rolls):
        current_player = hypothetical_gameboard['players'][current_player_index]
        while current_player.status == 'lost':
            current_player_index += 1
            current_player_index = current_player_index % len(hypothetical_gameboard['players'])
            current_player = hypothetical_gameboard['players'][current_player_index]
        current_player.status = 'current_move'

        # pre-roll for current player + out-of-turn moves for everybody else,
        # till we get num_active_players skip turns in a row.

        skip_turn = 0
        if current_player.make_pre_roll_moves(hypothetical_gameboard) == 2: # 2 is the special skip-turn code
            skip_turn += 1
        out_of_turn_player_index = current_player_index + 1
        out_of_turn_count = 0
        while skip_turn != num_active_players and out_of_turn_count<=200:
            out_of_turn_count += 1
            # print('checkpoint 1')
            out_of_turn_player = hypothetical_gameboard['players'][out_of_turn_player_index%len(hypothetical_gameboard['players'])]
            if out_of_turn_player.status == 'lost':
                out_of_turn_player_index += 1
                continue
            oot_code = out_of_turn_player.make_out_of_turn_moves(hypothetical_gameboard)
            # add to game history
            hypothetical_gameboard['history']['function'].append(out_of_turn_player.make_out_of_turn_moves)
            params = dict()
            params['self']=out_of_turn_player
            params['current_gameboard']=hypothetical_gameboard
            hypothetical_gameboard['history']['param'].append(params)
            hypothetical_gameboard['history']['return'].append(oot_code)

            if  oot_code == 2:
                skip_turn += 1
            else:
                skip_turn = 0
            out_of_turn_player_index += 1

        # now we roll the dice and get into the post_roll phase,
        # but only if we're not in jail.


        r = die_roll_substitute(hypothetical_gameboard['dies'], hypothetical_gameboard)
        # add to game history
        hypothetical_gameboard['history']['function'].append(die_roll_substitute)
        params = dict()
        params['die_objects'] = hypothetical_gameboard['dies']
        params['hypothetical_gameboard'] = hypothetical_gameboard
        hypothetical_gameboard['history']['param'].append(params)
        hypothetical_gameboard['history']['return'].append(r)

        num_die_rolls += 1
        hypothetical_gameboard['current_die_total'] = sum(r)
        print('dies have come up ',str(r))
        if not current_player.currently_in_jail:
            check_for_go = True
            move_player_after_die_roll(current_player, sum(r), hypothetical_gameboard, check_for_go)
            # add to game history
            hypothetical_gameboard['history']['function'].append(move_player_after_die_roll)
            params = dict()
            params['player'] = current_player
            params['rel_move'] = sum(r)
            params['current_gameboard'] = hypothetical_gameboard
            params['check_for_go'] = check_for_go
            hypothetical_gameboard['history']['param'].append(params)
            hypothetical_gameboard['history']['return'].append(None)

            current_player.process_move_consequences(hypothetical_gameboard)
            # add to game history
            hypothetical_gameboard['history']['function'].append(current_player.process_move_consequences)
            params = dict()
            params['self'] = current_player
            params['current_gameboard'] = hypothetical_gameboard
            hypothetical_gameboard['history']['param'].append(params)
            hypothetical_gameboard['history']['return'].append(None)

            # post-roll for current player. No out-of-turn moves allowed at this point.
            current_player.make_post_roll_moves(hypothetical_gameboard)
            # add to game history
            hypothetical_gameboard['history']['function'].append(current_player.make_post_roll_moves)
            params = dict()
            params['self'] = current_player
            params['current_gameboard'] = hypothetical_gameboard
            hypothetical_gameboard['history']['param'].append(params)
            hypothetical_gameboard['history']['return'].append(None)

        else:
            current_player.currently_in_jail = False # the player is only allowed to skip one turn (i.e. this one)

        if current_player.current_cash < 0:
            code = current_player.handle_negative_cash_balance(current_player, hypothetical_gameboard)
            # add to game history
            hypothetical_gameboard['history']['function'].append(current_player.handle_negative_cash_balance)
            params = dict()
            params['player'] = current_player
            params['current_gameboard'] = hypothetical_gameboard
            hypothetical_gameboard['history']['param'].append(params)
            hypothetical_gameboard['history']['return'].append(code)
            if code == -1 or current_player.current_cash < 0:
                current_player.begin_bankruptcy_proceedings(hypothetical_gameboard)
                # add to game history
                hypothetical_gameboard['history']['function'].append(current_player.begin_bankruptcy_proceedings)
                params = dict()
                params['self'] = current_player
                params['current_gameboard'] = hypothetical_gameboard
                hypothetical_gameboard['history']['param'].append(params)
                hypothetical_gameboard['history']['return'].append(None)

                num_active_players -= 1
                diagnostics.print_asset_owners(hypothetical_gameboard)
                diagnostics.print_player_cash_balances(hypothetical_gameboard)

                if num_active_players == 1:
                    for p in hypothetical_gameboard['players']:
                        if p.status != 'lost':
                            winner = p
                            p.status = 'won'
        else:
            current_player.status = 'waiting_for_move'

        current_player_index = (current_player_index+1)%len(hypothetical_gameboard['players'])
    print('ENDING HYPOTHETICAL GAMEPLAY AND RETURNING...')
    return winner


# def test_gameboard(game_schema_file): # we use this function for testing various things. Make sure to leave it commented, since otherwise, circular import dependencies will be introduced.
#
#     import initialize_game_elements
#     import background_agent_v1
#     import simple_decision_agent_1
#
#     player_decision_agents = dict()
#     player_decision_agents['player_1'] = background_agent_v1.decision_agent_methods
#     player_decision_agents['player_2'] = background_agent_v1.decision_agent_methods
#     player_decision_agents['player_3'] = background_agent_v1.decision_agent_methods
#     player_decision_agents['player_4'] = background_agent_v1.decision_agent_methods
#
#     game_schema = json.load(open(game_schema_file, 'r'))
#     game_elements_orig = initialize_game_elements.initialize_board(game_schema, player_decision_agents)
#     # pprint.pprint(game_elements_orig,indent=4)
#
#     player_decision_agents2 = dict()
#     player_decision_agents2['player_1'] = simple_decision_agent_1.decision_agent_methods
#     player_decision_agents2['player_2'] = simple_decision_agent_1.decision_agent_methods
#     player_decision_agents2['player_3'] = simple_decision_agent_1.decision_agent_methods
#     player_decision_agents2['player_4'] = background_agent_v1.decision_agent_methods
#
#     initialize_hypothetical_universe(game_elements_orig,player_decision_agents2)
#
#     # game_elements_copy = copy.deepcopy(game_elements_orig)
#     # print('printing copy')
#     # pprint.pprint(game_elements_copy, indent=4)


def die_roll_substitute(die_objects, hypothetical_gameboard):
    """
    In the alternate universe, this function is completely in your control, and you can implement other versions (making sure to pass
    it in as an argument in simulate_hypothetical_game), including in your decision agent file. For example, you could remove randomness altogether by deciding
     what the die values should be based on the hypothetical gameboard.
    :param die_objects: The list of dies
    :param hypothetical_gameboard: the hypothetical_gameboard dict.
    :return:
    """
    print('rolling die...')
    return [hypothetical_gameboard['randomState'].choice(d.die_state) for d in die_objects]

# test_gameboard('/Users/mayankkejriwal/git-projects/GNOME/monopoly_game_schema_v1-2.json') # use this to set up a gameboard and test various things

# die_objects = [[1,2,3,4,5,6],[1,2,3,4,5,6]]
# count = 0
# # numpy.random.seed(3)
# r = numpy.random.RandomState(seed=3)
# while count < 100:
#      k = [r.choice(d) for d in die_objects]
#      print(k)
#      count += 1


