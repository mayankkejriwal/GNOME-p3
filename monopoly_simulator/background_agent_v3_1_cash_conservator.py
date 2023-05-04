from monopoly_simulator import agent_helper_functions_v3 as agent_helper_functions# helper functions are internal to the agent and will not be recorded in the function log.
from monopoly_simulator import diagnostics
from monopoly_simulator.flag_config import flag_config_dict
import logging
logger = logging.getLogger('monopoly_simulator.logging_info.background_agent')

UNSUCCESSFUL_LIMIT = 2

"""
All external decision_agent functions must have the exact signatures we have indicated in this document. Beyond
that, we impose no restrictions (you can make the decision agent as complex as you like (including maintaining state),
and we use good faith to ensure you do not manipulate the gameboard. We will have mechanisms to check for inadvertent
changes or inconsistencies that get introduced in the gameboard (due to any reason, including possible subtle errors
in the simulator itself) a short while later.
If you decision agent does maintain state, or some kind of global data structure, please be careful when assigning the
same decision agent (as we do) to each player. We do provide some basic state to you already via 'code' in the make_*_move
functions. Specifically, if code is 1 it means the 'previous' move selected by the player was successful,
and if -1 it means it was unsuccessful. code of -1 is usually returned when an allowable move is invoked with parameters
that preempt the action from happening e.g., the player may decide to mortgage property that is already mortgaged,
which will return the failure code of -1 when the game actually tries to mortgage the property in action_choices.
Be careful to note what each function is supposed to return in addition to adhering to the expected signature. The examples
here are good guides.
Your functions can be called whatever you like, but the keys in decision_agent_methods should not be changed. The
respective functions must adhere in their signatures to the examples here. The agent in this file is simple and rule-based,
 rather than adaptive but capable of taking good actions in a number of eventualities.
 We detail the logic behind each decision in a separate document. This is the agent that will serve as the 'background'
 agent for purposes of evaluation.
 
 
 
 
Agent's detail:
 This is the agent used for the goal novelty in phase 3.
 Main goal: This agent is cash conservative, so it will try it's best to conserve it's cash.
 modified functions: 
 1. auction: never attend in auction
 2. trade: never make or accept trade with others
 3. free_mortgage: never free mortgage
 4. pay_jail_fine: never pay jail fine, rather stay in jail
 5. buy property: in function make_buy_property_decision
    only buy property if the price <=  10% cash
 6. improve_property: function agent_helper_functions_v3.identify_improvement_opportunity_cash_conservator
    only improve if the price <=  10% cash
 
"""


def make_pre_roll_move(player, current_gameboard, allowable_moves, code):
    """
    Many actions are possible in pre_roll but we prefer to save the logic for out_of_turn. The only decision
    we'll make here is whether we want to leave jail (if we're in jail).
    :param player: A Player instance. You should expect this to be the player that is 'making' the decision (i.e. the player
    instantiated with the functions specified by this decision agent).
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :param allowable_moves: A set of function names, each of which is defined in action_choices (imported in this file), and that
    will always be a subset of the action choices for pre_die_roll in the game schema. Your returned action choice name must be from
    allowable_moves; we will check for this when you return.
    :param code: See the preamble of this file for an explanation of this code
    :return: A 2-element tuple, the first of which is the name of the action you want to take, and the second is a dictionary of
    parameters that will be passed into the function representing that action when it is executed.
    The dictionary must exactly contain the keys and expected value types expected by that action in
    action_choices
    """

    '''
    phase_game defines which phase the player is in during the game
    0 -> preroll
    1 -> out of turn
    2 -> postroll
    count_unsuccessful_tries in the agent memory keeps a record of unsuccessful actions executed by that player agent in each phase_game.
    If this count reaches UNSUCCESSFUL_LIMIT before a phase_game change, then the player has no option but to either skip_turn or
    conclude_actions. This count resets to 0 when the phase_game changes.
    This ensures that the game doesnot go on for too long trying to execute unsuccessful actions.
    '''
    for p in current_gameboard['players']:
        if 'phase_game' not in p.agent._agent_memory:
            p.agent._agent_memory['phase_game'] = 0
            p.agent._agent_memory['count_unsuccessful_tries'] = 0

    if player.agent._agent_memory['phase_game'] != 0:
        player.agent._agent_memory['phase_game'] = 0
        for p in current_gameboard['players']:
            if p.status != 'lost':
                p.agent._agent_memory['count_unsuccessful_tries'] = 0

    if code == flag_config_dict['failure_code']:
        player.agent._agent_memory['count_unsuccessful_tries'] += 1
        logger.debug(player.player_name + ' has executed an unsuccessful preroll action, incrementing unsuccessful_tries ' +
                                          'counter to ' + str(player.agent._agent_memory['count_unsuccessful_tries']))


    if player.agent._agent_memory['count_unsuccessful_tries'] >= UNSUCCESSFUL_LIMIT:
        logger.debug(player.player_name + ' has reached preroll unsuccessful action limits.')
        if "skip_turn" in allowable_moves:
            logger.debug(player.player_name+ ': I am skipping turn since I have crossed unsuccessful limits.')
            player.agent._agent_memory['previous_action'] = "skip_turn"
            return ("skip_turn", dict())
        elif "concluded_actions" in allowable_moves:
            # player.agent._agent_memory['previous_action'] = action_choices.concluded_actions
            logger.debug(player.player_name+ ': I am concluding actions since I have crossed unsuccessful limits.')
            return ("concluded_actions", dict())
        else:
            logger.error("Exception")
            raise Exception


    '''
    #----------------------dummy action example---------------------------------------
    if 'pre_roll_arbitrary_action_schema' in current_gameboard:
        print(" ")
        print("-----------------Arbitrary action schema:----------------------")
        print(" ")
        param = dict()
        param['schema_type'] = 'pre_roll_arbitrary_action'
        param['current_gameboard'] = 'current_gameboard'
        return ("print_schema", param)


    if player.current_cash < 1000:
        print(player.player_name + " cash bal < 1000, printing Hello world through arbitrary action.")
        param = dict()
        param['action_params_dict'] = dict()
        param['action_params_dict']['location'] = current_gameboard['location_sequence'][player.current_position].name
            # send back name of property, resolved into location pointer in the player._populate_param_dict() function like the other action choice params.
        return ("pre_roll_arbitrary_action", param)
    else:
        print("Condition not satisfied")
    #----------------------------------------------------------------------
    '''

    if player.current_cash >= current_gameboard['go_increment']: # if we don't have enough money, best to stay put.
        param = dict()
        param['player'] = player.player_name
        param['current_gameboard'] = "current_gameboard"
        if "use_get_out_of_jail_card" in allowable_moves:
            logger.debug(player.player_name+': I am using get out of jail card.')
            player.agent._agent_memory['previous_action'] = "use_get_out_of_jail_card"
            return ("use_get_out_of_jail_card", param)
        elif "pay_jail_fine" in allowable_moves:
            logger.debug(player.player_name+': I will never pay jail fine, I rather stay in jail because I am a cash conservator to pay jail.')
            pass

    # if we ran the gamut, and did not return, then it's time to skip turn or conclude actions
    if "skip_turn" in allowable_moves:
        # testing hypothetical simulator (will comment when done testing). Note that this was written for the Python 2
        # version (the GNOME repo). Make sure to appropriately modify by instantiating agent instead of sending in the
        # decision agent methods as being done below.
        # player_decision_agents = dict()
        # import simple_decision_agent_1
        # player_decision_agents['player_1'] = simple_decision_agent_1.decision_agent_methods # the reason I am doing this for all agents is to avoid infinite loops.
        # player_decision_agents['player_2'] = simple_decision_agent_1.decision_agent_methods
        # player_decision_agents['player_3'] = simple_decision_agent_1.decision_agent_methods
        # player_decision_agents['player_4'] = simple_decision_agent_1.decision_agent_methods
        # alternate_univ = hypothetical_simulator.initialize_hypothetical_universe(current_gameboard, player_decision_agents)
        # logger.debug(player.player_name,' has spawned alternate universe to try out things.')
        # hypothetical_winner = hypothetical_simulator.simulate_hypothetical_game(hypothetical_gameboard=alternate_univ,
        #                         die_roll_substitute=hypothetical_simulator.die_roll_substitute,num_total_die_rolls=15) # we will only run for fifteen die rolls.
        # if hypothetical_winner is None:
        #     logger.debug(diagnostics.logger.debug_player_cash_balances(alternate_univ))
        # else:
        #     logger.debug(hypothetical_winner.player_name)
        logger.debug(player.player_name+ ': I am skipping turn')
        player.agent._agent_memory['previous_action'] = "skip_turn"
        return ("skip_turn", dict())
    elif "concluded_actions" in allowable_moves:
        # player.agent._agent_memory['previous_action'] = action_choices.concluded_actions
        logger.debug(player.player_name+ ': I am concluding actions')
        return ("concluded_actions", dict())
    else:
        logger.error("Exception")
        raise Exception


def make_out_of_turn_move(player, current_gameboard, allowable_moves, code):
    """
    The agent is in the out-of-turn phase and must decide what to do (next). This simple dummy agent skips the turn, and
    doesn't do anything.
    :param player: A Player instance. You should expect this to be the player that is 'making' the decision (i.e. the player
    instantiated with the functions specified by this decision agent).
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :param allowable_moves: A set of function names, each of which is defined in action_choices (imported in this file), and that
    will always be a subset of the action choices for out_of_turn in the game schema. Your returned action choice must be from
    allowable_moves; we will check for this when you return.
    :param code: See the preamble of this file for an explanation of this code
    :return: A 2-element tuple, the first of which is the name of the action you want to take, and the second is a dictionary of
    parameters that will be passed into the function representing that action when it is executed.
    The dictionary must exactly contain the keys and expected value types expected by that action in
    action_choices
    """
    '''
    Agent V3
    This updated version of the agent can make trade offers with MULTIPLE players simultaneously.
    All strategies available in Agent V2 is still available in V3
    Note that this version of the agent also engages in the trade of only one set of properties like the previous version, ie 
    - only one property will be requested if it is a buy property offer or
    - only one property will be offered if it is a sell property offer or
    - only one property will be offered and one property requested during an exchange property offer.
    
    Agent V2
    NOTE: The background agent that could make_sell_property_offer is deprecated (available as background_agent_v1_deprecated.py)
    This version of the agent can only make_trade_offer and accept trade offer. Trade involves buy or sell or exchange property offers.
    Accept_sell_property_offer function is still available in case some different agent decides to make a sell property offer.
    Ideally, accept_sell_property_offer() function should never enter allowable moves.
    Make sell property offer can be replicated by making a trade offer that only offers to sell properties in return for cash
    and doesnot involve a buy property or exchange property offer.
    A buy property offer can be duplicated by including only requested properties by offering cash without offering properties.
    Properties and cash can be exchanged which lets both players get an advantage of increasing their respective number of monopolies.
    This version of the agent background_agent_v1 supports making sell property offers in return for cash via make_trade_offer, 
    buy trade offers and exchange property offers.
    Note that this version of the agent engages in the trade of only one set of properties, ie 
    - only one property will be requested if it is a buy property offer or
    - only one property will be offered if it is a sell property offer or
    - only one property will be offered and one property requested during an exchange property offer.
    '''

    '''
    phase_game defines which phase the player is in during the game
    0 -> preroll
    1 -> out of turn
    2 -> postroll
    count_unsuccessful_tries in the agent memory keeps a record of unsuccessful actions executed by that player agent in each phase_game.
    If this count reaches UNSUCCESSFUL_LIMIT before a phase_game change, then the player has no option but to either skip_turn or
    conclude_actions. This count resets to 0 when the phase_game changes.
    This ensures that the game doesnot go on for too long trying to execute unsuccessful actions.
    '''

    for p in current_gameboard['players']:
        if 'phase_game' not in p.agent._agent_memory:
            p.agent._agent_memory['phase_game'] = 1
            p.agent._agent_memory['count_unsuccessful_tries'] = 0

    if player.agent._agent_memory['phase_game'] != 1:
        player.agent._agent_memory['phase_game'] = 1
        player.agent._agent_memory['count_unsuccessful_tries'] = 0

    if isinstance(code, list):
        code_flag = 0
        for c in code:
            if c == flag_config_dict['failure_code']:
                code_flag = 1
                break
        if code_flag:
            player.agent._agent_memory['count_unsuccessful_tries'] += 1
            logger.debug(player.player_name + ' has executed an unsuccessful out of turn action, incrementing unsuccessful_tries ' +
                                          'counter to ' + str(player.agent._agent_memory['count_unsuccessful_tries']))
    elif code == flag_config_dict['failure_code']:
        player.agent._agent_memory['count_unsuccessful_tries'] += 1
        logger.debug(player.player_name + ' has executed an unsuccessful out of turn action, incrementing unsuccessful_tries ' +
                                          'counter to ' + str(player.agent._agent_memory['count_unsuccessful_tries']))

    if player.agent._agent_memory['count_unsuccessful_tries'] >= UNSUCCESSFUL_LIMIT:
        logger.debug(player.player_name + ' has reached out of turn unsuccessful action limits.')
        if "skip_turn" in allowable_moves:
            logger.debug(player.player_name+ ': I am skipping turn since I have crossed unsuccessful limits.')
            player.agent._agent_memory['previous_action'] = "skip_turn"
            return ("skip_turn", dict())
        elif "concluded_actions" in allowable_moves:
            # player.agent._agent_memory['previous_action'] = action_choices.concluded_actions
            logger.debug(player.player_name+ ': I am concluding actions since I have crossed unsuccessful limits.')
            return ("concluded_actions", dict())
        else:
            logger.error("Exception")
            raise Exception

    if "accept_trade_offer" in allowable_moves:
        logger.debug(player.player_name + ': Should I accept the trade offer by ' + player.outstanding_trade_offer[
            'from_player'].player_name + '?')
        logger.debug(player.player_name + ': I would never accept any trade_offer because I am a cash conservator')
        pass

    if "accept_sell_property_offer" in allowable_moves:
        logger.debug(player.player_name + ': Should I accept the offer by ' + player.outstanding_property_offer[
            'from_player'].player_name + ' to buy ' + \
                     player.outstanding_property_offer['asset'].name + ' for ' + str(
            player.outstanding_property_offer['price']) + '?')
        logger.debug(player.player_name + ': I would never accept any sell_property_offer because I am a cash conservator')
        pass

    if player.status != 'current_move': # these actions are considered only if it's NOT our turn to roll the dice.
        if "improve_property" in allowable_moves: # beef up full color sets to maximize rent potential.
            param = agent_helper_functions.identify_improvement_opportunity_cash_conservator(player, current_gameboard)
            if param:
                if player.agent._agent_memory['previous_action'] == "improve_property" and code == flag_config_dict['failure_code']:
                    logger.debug(player.player_name+ ': I want to improve property '+param['asset'].name+ ' but I cannot, due to reasons I do not understand. Aborting improvement attempt...')
                else:
                    logger.debug(player.player_name + ' has cash = ' + str(player.current_cash))
                    logger.debug(param['asset'].name + '\'s price_per_house = ' + str(param['asset'].price_per_house))
                    logger.debug(player.player_name+ ': I am going to improve property on '+param['asset'].name + ' because I am a cash conservator to improve property')
                    player.agent._agent_memory['previous_action'] = "improve_property"
                    param['player'] = param['player'].player_name
                    param['asset'] = param['asset'].name
                    param['current_gameboard'] = "current_gameboard"
                    return ("improve_property", param)

        player_mortgaged_assets_list = list()
        if player.mortgaged_assets:
            player_mortgaged_assets_list = _set_to_sorted_list_mortgaged_assets(player.mortgaged_assets)
        for m in player_mortgaged_assets_list:
            if player.current_cash-(m.mortgage*(1+current_gameboard['bank'].mortgage_percentage)) >= current_gameboard['go_increment'] and "free_mortgage" in allowable_moves:
                logger.debug(player.player_name+ ': I can free mortgage on '+ m.name + ', but I choose not to do so because I am a cash conservator to free mortgage')
                pass


    else:
        if "make_trade_offer" in allowable_moves:
            logger.debug(player.player_name + ': I would never make my own trade_offer because I am a cash conservator')
            pass


    # if we ran the gamut, and did not return, then it's time to skip turn or conclude actions
    if "skip_turn" in allowable_moves:
        logger.debug(player.player_name+ ': I am skipping turn')
        player.agent._agent_memory['previous_action'] = "skip_turn"
        return ("skip_turn", dict())
    elif "concluded_actions" in allowable_moves:
        logger.debug(player.player_name+ ': I am concluding actions')
        # player.agent._agent_memory['previous_action'] = action_choices.concluded_actions
        return ("concluded_actions", dict())
    else:
        logger.error("Exception")
        raise Exception


def make_post_roll_move(player, current_gameboard, allowable_moves, code):
    """
    The agent is in the post-roll phase and must decide what to do (next). The main decision we make here is singular:
    should we buy the property we landed on, if that option is available?
    --If we do buy the property, we end the phase by concluding the turn.
    --If we cannot buy a property, we conclude the turn. If we have negative cash balance, we do not handle it here, but
    in the handle_negative_cash_balance function. This means that the background agent never calls any of
    the mortgage or sell properties here UNLESS we need to mortgage or sell a property in order to buy the current
     one and it is well worth our while.
    Note that if your agent decides not to buy the property before concluding the turn, the property will move to
    auction before your turn formally concludes.
    This background agent never sells a house or hotel in post_roll.
    :param player: A Player instance. You should expect this to be the player that is 'making' the decision (i.e. the player
    instantiated with the functions specified by this decision agent).
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :param allowable_moves: A set of functions, each of which is defined in action_choices (imported in this file), and that
    will always be a subset of the action choices for post-die-roll in the game schema. Your returned action choice must be from
    allowable_moves; we will check for this when you return.
    :param code: See the preamble of this file for an explanation of this code
    :return: A 2-element tuple, the first of which is the action you want to take, and the second is a dictionary of
    parameters that will be passed into the function representing that action when it is executed.
    The dictionary must exactly contain the keys and expected value types expected by that action in
    action_choices
    """

    '''
    phase_game defines which phase the player is in during the game
    0 -> preroll
    1 -> out of turn
    2 -> postroll
    count_unsuccessful_tries in the agent memory keeps a record of unsuccessful actions executed by that player agent in each phase_game.
    If this count reaches UNSUCCESSFUL_LIMIT before a phase_game change, then the player has no option but to either skip_turn or
    conclude_actions. This count resets to 0 when the phase_game changes.
    This ensures that the game doesnot go on for too long trying to execute unsuccessful actions.
    '''

    for p in current_gameboard['players']:
        if 'phase_game' not in p.agent._agent_memory:
            p.agent._agent_memory['phase_game'] = 2
            p.agent._agent_memory['count_unsuccessful_tries'] = 0

    if player.agent._agent_memory['phase_game'] != 2:
        player.agent._agent_memory['phase_game'] = 2
        for p in current_gameboard['players']:
            if p.status != 'lost':
                p.agent._agent_memory['count_unsuccessful_tries'] = 0

    if code == flag_config_dict['failure_code']:
        player.agent._agent_memory['count_unsuccessful_tries'] += 1
        logger.debug(player.player_name + ' has executed an unsuccessful postroll action, incrementing unsuccessful_tries ' +
                                          'counter to ' + str(player.agent._agent_memory['count_unsuccessful_tries']))

    if player.agent._agent_memory['count_unsuccessful_tries'] >= UNSUCCESSFUL_LIMIT:
        logger.debug(player.player_name + ' has reached postroll unsuccessful action limits.')
        if "concluded_actions" in allowable_moves:
            # player.agent._agent_memory['previous_action'] = action_choices.concluded_actions
            logger.debug(player.player_name+ ': I am concluding actions since I have crossed unsuccessful limits.')
            return ("concluded_actions", dict())
        else:
            logger.error("Exception")
            raise Exception
    current_location = current_gameboard['location_sequence'][player.current_position]
    if "buy_property" in allowable_moves:
        if code == flag_config_dict['failure_code']:
            logger.debug(player.player_name+': I did not succeed the last time in buying this property. Concluding actions...')
            return ("concluded_actions", dict())

        params = dict()
        params['player'] = player.player_name
        params['asset'] = current_location.name
        params['current_gameboard'] = "current_gameboard"

        if make_buy_property_decision(player, current_gameboard, current_location):
            logger.debug(player.player_name+ ': I am attempting to buy property '+current_location.name)
            player.agent._agent_memory['previous_action'] = "buy_property"
            return ("buy_property", params)
        else:
            # make_buy returned false, but is there still a chance?
            if agent_helper_functions.will_property_complete_set(player,current_location,current_gameboard):
                # if we can raise enough money, then the 'next' time around we'll succeed in buying
                to_mortgage = agent_helper_functions.identify_potential_mortgage(player,current_location.price,True)
                if to_mortgage:
                    params['asset'] = to_mortgage.name
                    logger.debug(player.player_name+ ': I am attempting to mortgage property '+ params['asset'])
                    player.agent._agent_memory['previous_action'] = "mortgage_property"
                    return ("mortgage_property", params)

                else: # last chance.
                    to_sell = agent_helper_functions.identify_potential_sale(player, current_gameboard, current_location.price,True)
                    if to_sell:
                        params['asset'] = to_sell.name
                        logger.debug(player.player_name+ ': I am attempting to sell property '+ current_location.name+' to the bank')
                        player.agent._agent_memory['previous_action'] = "sell_property"
                        return ("sell_property", params)

    if "concluded_actions" in allowable_moves:
        # player.agent._agent_memory['previous_action'] = action_choices.concluded_actions
        return ("concluded_actions", dict())

    else:
        logger.error("Exception")
        raise Exception


def make_buy_property_decision(player, current_gameboard, asset):
    """
    The agent decides to buy the property if the price of asset <= 10% cash

    :param player: A Player instance. You should expect this to be the player that is 'making' the decision (i.e. the player
    instantiated with the functions specified by this decision agent).
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: A Boolean. If True, then you decided to purchase asset from the bank, otherwise False. We allow you to
    purchase the asset even if you don't have enough cash; however, if you do you will end up with a negative
    cash balance and will have to handle that if you don't want to lose the game at the end of your move (see notes
    in handle_negative_cash_balance)
    """
    decision = False
    ####
    #if not hasattr(asset, 'price'):
    #    return(decision)
    ###
    if asset.price <= player.current_cash * 0.1:
        logger.debug(player.player_name + ' has cash = ' + str(player.current_cash))
        logger.debug(asset.name + '\'s price = ' + str(asset.price))
        logger.debug(player.player_name + ': I will attempt to buy ' + asset.name + ' from the bank. I can only afford the property costing 10% of cash because I am a cash conservator.')
        decision = True


    return decision


def make_bid(player, current_gameboard, asset, current_bid):
    """
    Never attend acution, so just return 0
    :param player: A Player instance. You should expect this to be the player that is 'making' the decision (i.e. the player
    instantiated with the functions specified by this decision agent).
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :param asset: An purchaseable instance of Location (i.e. real estate, utility or railroad)
    :param current_bid: The current bid that is going in the auction. If you don't bid higher than this amount, the bank
    will remove you from the auction proceedings. You could also always return 0 to voluntarily exit the auction.
    :return: An integer that indicates what you wish to bid for asset
    """
    decision = False
    ####
    #if not hasattr(asset, 'price'):
    #    return(decision)
    ###
    logger.debug(
        player.player_name + ': I will never attend in auction because I am a cash conservator.')

    return 0


def handle_negative_cash_balance(player, current_gameboard):
    """
    You have a negative cash balance at the end of your move (i.e. your post-roll phase is over) and you must handle
    this issue before we move to the next player's pre-roll. If you do not succeed in restoring your cash balance to
    0 or positive, bankruptcy proceeds will begin and you will lost the game.
    The background agent tries a number of things to get itself out of a financial hole. First, it checks whether
    mortgaging alone can save it. If not, then it begins selling unimproved properties in ascending order of price, the idea being
    that it might as well get rid of cheap properties. This may not be the most optimal move but it is reasonable.
    If it ends up selling all unimproved properties and is still insolvent, it starts selling improvements, followed
    by a sale of the (now) unimproved properties.
    :param player: A Player instance. You should expect this to be the player that is 'making' the decision (i.e. the player
    instantiated with the functions specified by this decision agent).
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: -1 if you do not try to address your negative cash balance, or 1 if you tried and believed you succeeded.
    Note that even if you do return 1, we will check to see whether you have non-negative cash balance. The rule of thumb
    is to return 1 as long as you 'try', or -1 if you don't try (in which case you will be declared bankrupt and lose the game)
    """
    if player.current_cash >= 0:   # prelim check to see if player has negative cash balance
        return (None, flag_config_dict['successful_action'])

    mortgage_potentials = list()
    max_sum = 0
    sorted_player_assets_list = _set_to_sorted_list_assets(player.assets)
    for a in sorted_player_assets_list:
        if a.is_mortgaged:
            continue
        elif a.loc_class=='real_estate' and (a.num_houses>0 or a.num_hotels>0):
            continue
        else:
            mortgage_potentials.append((a,a.mortgage))
            max_sum += a.mortgage
    if mortgage_potentials and max_sum+player.current_cash >= 0: # if the second condition is not met, no point in mortgaging
        sorted_potentials = sorted(mortgage_potentials, key=lambda x: x[1])  # sort by mortgage in ascending order
        for p in sorted_potentials:
            if player.current_cash >= 0:
                return (None, flag_config_dict['successful_action']) # we're done

            params = dict()
            params['player'] = player.player_name
            params['asset'] = p[0].name
            params['current_gameboard'] = "current_gameboard"
            logger.debug(player.player_name+ ': I am attempting to mortgage property '+ params['asset'])
            player.agent._agent_memory['previous_action'] = "mortgage_property"
            return ("mortgage_property", params)


    # if we got here, it means we're still in trouble. Next move is to sell unimproved properties. We don't check if
    # the total will cover our debts, since we're desperate at this point.

    # following sale potentials doesnot include properties from monopolized color groups
    sale_potentials = list()
    sorted_player_assets_list = _set_to_sorted_list_assets(player.assets)
    for a in sorted_player_assets_list:
        if a.color in player.full_color_sets_possessed:
            continue
        elif a.is_mortgaged:
            sale_potentials.append((a, (a.price*current_gameboard['bank'].property_sell_percentage)-((1+current_gameboard['bank'].mortgage_percentage)*a.mortgage)))
        elif a.loc_class=='real_estate' and (a.num_houses>0 or a.num_hotels>0):
            continue
        else:
            sale_potentials.append((a,a.price*current_gameboard['bank'].property_sell_percentage))

    if sale_potentials: # if the second condition is not met, no point in mortgaging
        sorted_potentials = sorted(sale_potentials, key=lambda x: x[1])  # sort by mortgage in ascending order
        for p in sorted_potentials:
            if player.current_cash >= 0:
                return (None, flag_config_dict['successful_action']) # we're done

            params = dict()
            params['player'] = player.player_name
            params['asset'] = p[0].name
            params['current_gameboard'] = "current_gameboard"
            logger.debug(player.player_name + ': I am attempting to sell property '+ p[0].name + ' to the bank')
            player.agent._agent_memory['previous_action'] = "sell_property"
            return ("sell_property", params)


    # if selling properties from non monopolized color groups doesnot relieve the player from debt, then only we start thinking about giving up monopolized groups.
    # If we come across a unimproved property which belongs to a monopoly, we still have to loop through the other properties from the same color group and
    # sell the houses and hotels first because we cannot sell this property when the color group has improved properties
    # We first check if selling houses and hotels one by one on the other improved properties of the same color group relieves the player of his debt. If it does
    # then we return without selling the current property else we sell the property and the player loses monopoly of that color group.
    sale_potentials = list()
    sorted_player_assets_list = _set_to_sorted_list_assets(player.assets)
    for a in sorted_player_assets_list:
        if a.is_mortgaged:
            sale_potentials.append((a, (a.price*current_gameboard['bank'].property_sell_percentage)-((1+current_gameboard['bank'].mortgage_percentage)*a.mortgage)))
        elif a.loc_class=='real_estate' and (a.num_houses>0 or a.num_hotels>0):
            continue
        else:
            sale_potentials.append((a,a.price*current_gameboard['bank'].property_sell_percentage))

    if sale_potentials:
        sorted_potentials = sorted(sale_potentials, key=lambda x: x[1])  # sort by sell value in ascending order
        for p in sorted_potentials:
            if player.current_cash >= 0:
                return (None, flag_config_dict['successful_action']) # we're done

            sorted_player_assets_list = _set_to_sorted_list_assets(player.assets)
            for prop in sorted_player_assets_list:
                if prop!=p[0] and prop.color==p[0].color and p[0].color in player.full_color_sets_possessed:
                    if hasattr(prop, 'num_hotels'):  # add by Peter, for composite novelty
                        if prop.num_hotels>0:
                            if player.current_cash >= 0:
                                return (None, flag_config_dict['successful_action'])
                            params = dict()
                            params['player'] = player.player_name
                            params['asset'] = prop.name
                            params['current_gameboard'] = "current_gameboard"
                            params['sell_house'] = False
                            params['sell_hotel'] = True
                            logger.debug(player.player_name+ ': I am attempting to sell hotel on '+ prop.name + ' to the bank')
                            player.agent._agent_memory['previous_action'] = "sell_house_hotel"
                            return ("sell_house_hotel", params)

                        elif prop.num_houses>0:
                            if player.current_cash >= 0:
                                return (None, flag_config_dict['successful_action'])
                            params = dict()
                            params['player'] = player.player_name
                            params['asset'] = prop.name
                            params['current_gameboard'] = "current_gameboard"
                            params['sell_house'] = True
                            params['sell_hotel'] = False
                            logger.debug(player.player_name+ ': I am attempting to sell house on '+ prop.name + ' to the bank')
                            player.agent._agent_memory['previous_action'] = "sell_house_hotel"
                            return ("sell_house_hotel", params)
                        else:
                            continue

            params = dict()
            params['player'] = player.player_name
            params['asset'] = p[0].name
            params['current_gameboard'] = "current_gameboard"
            logger.debug(player.player_name + ': I am attempting to sell property '+ p[0].name + ' to the bank')
            player.agent._agent_memory['previous_action'] = "sell_property"
            return ("sell_property", params)



    #we reach here if the player still hasnot cleared his debt. The above loop has now resulted in some more non monopolized properties.
    #Hence we have to go through the process of looping through these properties once again to decide on the potential properties that can be mortgaged or sold.

    mortgage_potentials = list()
    max_sum = 0
    sorted_player_assets_list = _set_to_sorted_list_assets(player.assets)
    for a in sorted_player_assets_list:
        if a.is_mortgaged:
            continue
        elif a.loc_class=='real_estate' and (a.num_houses>0 or a.num_hotels>0):
            continue
        else:
            mortgage_potentials.append((a,a.mortgage))
            max_sum += a.mortgage
    if mortgage_potentials and max_sum+player.current_cash >= 0: # if the second condition is not met, no point in mortgaging
        sorted_potentials = sorted(mortgage_potentials, key=lambda x: x[1])  # sort by mortgage in ascending order
        for p in sorted_potentials:
            if player.current_cash >= 0:
                return (None, flag_config_dict['successful_action']) # we're done

            params = dict()
            params['player'] = player.player_name
            params['asset'] = p[0].name
            params['current_gameboard'] = "current_gameboard"
            logger.debug(player.player_name+ ': I am attempting to mortgage property '+ params['asset'])
            player.agent._agent_memory['previous_action'] = "mortgage_property"
            return ("mortgage_property", params)

    # following sale potentials loops through the properties that have become unmonopolized due to the above loops and
    # doesnot include properties from monopolized color groups
    sale_potentials = list()
    sorted_player_assets_list = _set_to_sorted_list_assets(player.assets)
    for a in sorted_player_assets_list:
        if a.color in player.full_color_sets_possessed:
            continue
        elif a.is_mortgaged:
            sale_potentials.append((a, (a.price*current_gameboard['bank'].property_sell_percentage)-((1+current_gameboard['bank'].mortgage_percentage)*a.mortgage)))
        elif a.loc_class=='real_estate' and (a.num_houses>0 or a.num_hotels>0):
            continue
        else:
            sale_potentials.append((a, a.price*current_gameboard['bank'].property_sell_percentage))

    if sale_potentials: # if the second condition is not met, no point in mortgaging
        sorted_potentials = sorted(sale_potentials, key=lambda x: x[1])  # sort by mortgage in ascending order
        for p in sorted_potentials:
            if player.current_cash >= 0:
                return (None, flag_config_dict['successful_action']) # we're done

            params = dict()
            params['player'] = player.player_name
            params['asset'] = p[0].name
            params['current_gameboard'] = "current_gameboard"
            logger.debug(player.player_name + ': I am attempting to sell property '+ p[0].name + ' to the bank')
            player.agent._agent_memory['previous_action'] = "sell_property"
            return ("sell_property", params)

    count = 0
    # if we're STILL not done, then the only option is to start selling houses and hotels from the remaining improved monopolized properties, if we have 'em
    while (player.num_total_houses > 0 or player.num_total_hotels > 0) and count <3: # often times, a sale may not succeed due to uniformity requirements. We keep trying till everything is sold,
        # or cash balance turns non-negative.
        count += 1 # there is a slim chance that it is impossible to sell an improvement unless the player does something first (e.g., replace 4 houses with a hotel).
        # The count ensures we terminate at some point, regardless.
        sorted_assets_list = _set_to_sorted_list_assets(player.assets)

        for a in sorted_assets_list:
            if a.loc_class == 'real_estate' and a.num_houses > 0:
                if player.current_cash >= 0:
                    return (None, flag_config_dict['successful_action']) # we're done

                params = dict()
                params['player'] = player.player_name
                params['asset'] = a.name
                params['current_gameboard'] = "current_gameboard"
                params['sell_house'] = True
                params['sell_hotel'] = False
                logger.debug(player.player_name+ ': I am attempting to sell house on '+ a.name + ' to the bank')
                player.agent._agent_memory['previous_action'] = "sell_house_hotel"
                return ("sell_house_hotel", params)

            elif a.loc_class == 'real_estate' and a.num_hotels > 0:
                if player.current_cash >= 0:
                    return (None, flag_config_dict['successful_action']) # we're done
                params = dict()
                params['player'] = player.player_name
                params['asset'] = a.name
                params['current_gameboard'] = "current_gameboard"
                params['sell_house'] = False
                params['sell_hotel'] = True
                logger.debug(player.player_name+ ': I am attempting to sell house on '+ a.name + ' to the bank')
                player.agent._agent_memory['previous_action'] = "sell_house_hotel"
                return ("sell_house_hotel", params)

    # final straw
    final_sale_assets = player.assets.copy()
    sorted_player_assets_list = _set_to_sorted_list_assets(final_sale_assets)
    for a in sorted_player_assets_list:
        if player.current_cash >= 0:
            return (None, flag_config_dict['successful_action'])  # we're done
        params = dict()
        params['player'] = player.player_name
        params['asset'] = a.name
        params['current_gameboard'] = "current_gameboard"
        logger.debug(player.player_name + ': I am attempting to sell property '+ a.name + ' to the bank')
        player.agent._agent_memory['previous_action'] = "sell_property"
        return ("sell_property", params)

    return (None, flag_config_dict['successful_action']) # if we didn't succeed in establishing solvency, it will get caught by the simulator. Since we tried, we return 1.


def _set_to_sorted_list_mortgaged_assets(player_mortgaged_assets):
    player_m_assets_list = list()
    player_m_assets_dict = dict()
    for item in player_mortgaged_assets:
        player_m_assets_dict[item.name] = item
    for sorted_key in sorted(player_m_assets_dict):
        player_m_assets_list.append(player_m_assets_dict[sorted_key])
    return player_m_assets_list


def _set_to_sorted_list_assets(player_assets):
    player_assets_list = list()
    player_assets_dict = dict()
    for item in player_assets:
        player_assets_dict[item.name] = item
    for sorted_key in sorted(player_assets_dict):
        player_assets_list.append(player_assets_dict[sorted_key])
    return player_assets_list


def _build_decision_agent_methods_dict():
    """
    This function builds the decision agent methods dictionary.
    :return: The decision agent dict. Keys should be exactly as stated in this example, but the functions can be anything
    as long as you use/expect the exact function signatures we have indicated in this document.
    """
    ans = dict()
    ans['handle_negative_cash_balance'] = handle_negative_cash_balance
    ans['make_pre_roll_move'] = make_pre_roll_move
    ans['make_out_of_turn_move'] = make_out_of_turn_move
    ans['make_post_roll_move'] = make_post_roll_move
    ans['make_buy_property_decision'] = make_buy_property_decision
    ans['make_bid'] = make_bid
    ans['type'] = "decision_agent_methods"
    return ans


decision_agent_methods = _build_decision_agent_methods_dict() # this is the main data structure that is needed by gameplay
