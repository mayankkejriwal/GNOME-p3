from monopoly_simulator import agent_helper_functions_v2 as agent_helper_functions # helper functions are internal to the agent and will not be recorded in the function log.
from monopoly_simulator import diagnostics
from monopoly_simulator.flag_config import flag_config_dict
import logging
logger = logging.getLogger('monopoly_simulator.logging_info.background_agent')

UNSUCCESSFUL_LIMIT = 2

"""
This is the testing agent that avoid umass's agent perform make_trade_offer with 
1. cash_wanted = 0
2. cash_offered = 7.5e-06
3. property_set_wanted = Oriental Avenue
4. property_set_offered = None

change the strategies:
if wealthiest player == from_player-> reject the offer!



"""


"""Agent v4_1
Based on agent v4, add one strategy to never bud/bid/trade utilities.
"""

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

"""

"""
phase_game defines which phase the player is in during the game
0 -> preroll
1 -> out of turn
2 -> postroll
count_unsuccessful_tries in the agent memory keeps a record of unsuccessful actions executed by that player agent in each phase_game.
If this count reaches UNSUCCESSFUL_LIMIT before a phase_game change, then the player has no option but to either skip_turn or
conclude_actions. This count resets to 0 when the phase_game changes.
This ensures that the game doesnot go on for too long trying to execute unsuccessful actions.
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

    skip_or_conclude = _check_before_turn(player, current_gameboard, allowable_moves, code, 0, 'pre_roll')
    if skip_or_conclude:
        return skip_or_conclude[0], skip_or_conclude[1]  # (action, param) for skip/conclude

    if player.current_cash >= current_gameboard['go_increment']: # if we don't have enough money, best to stay put.
        param = dict()
        param['player'] = player.player_name
        param['current_gameboard'] = "current_gameboard"
        if "use_get_out_of_jail_card" in allowable_moves:
            logger.debug(player.player_name+': I am using get out of jail card.')
            player.agent._agent_memory['previous_action'] = "use_get_out_of_jail_card"
            return "use_get_out_of_jail_card", param
        elif "pay_jail_fine" in allowable_moves:
            logger.debug(player.player_name+': I am going to pay jail fine.')
            player.agent._agent_memory['previous_action'] = "pay_jail_fine"
            return "pay_jail_fine", param

    # if we ran the gamut, and did not return, then it's time to skip turn or conclude actions
    final_check = _final_check(player, allowable_moves, 'pre_roll')
    if final_check:
        return final_check[0], final_check[1]


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

    skip_or_conclude = _check_before_turn(player, current_gameboard, allowable_moves, code, 1, 'out_of_turn')
    if skip_or_conclude:
        return skip_or_conclude[0], skip_or_conclude[1]  # (action, param) for skip/conclude

    # Should we accept trade offer from other players
    if "accept_trade_offer" in allowable_moves:
        ans_accept_trade_offer = _ask_for_accept_trade_offer(player, current_gameboard)
        if ans_accept_trade_offer:
            return ans_accept_trade_offer[0], ans_accept_trade_offer[1]

    # Should we accept sell trade offer from other players
    # if "accept_sell_property_offer" in allowable_moves:
        # ans_accept_sell_trade_offer = _ask_for_accept_sell_trade_offer()

    # If status not in current move, we could improve properties or free mortgages
    if player.status != 'current_move':
        # chances to improve properties
        if "improve_property" in allowable_moves: # beef up full color sets to maximize rent potential.
            ans_improve_property = _ask_for_improve_property(player, current_gameboard, code)
            if ans_improve_property:
                return ans_improve_property[0], ans_improve_property[1]
        # chances to free any mortgaged properties
        if "free_mortgage" in allowable_moves:
            ans_free_mortgage = _try_to_free_mortgage(player, current_gameboard)
            if ans_free_mortgage:
                return ans_free_mortgage[0], ans_free_mortgage[1]
    # If status in current move, we could try to make trade offers with others
    else:
        if "make_trade_offer" in allowable_moves:
            ans_make_trade_offer = _ask_for_make_trade_offer(player, current_gameboard)
            if ans_make_trade_offer:
                return ans_make_trade_offer[0], ans_make_trade_offer[1]

    final_check = _final_check(player, allowable_moves, 'out_of_turn')
    if final_check:
        return final_check[0], final_check[1]


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

    # Agent4
    # check game phase if not correct reset it
    # check if we need to skip game or conclude game for the player
    skip_or_conclude = _check_before_turn(player, current_gameboard, allowable_moves, code, 2, 'post_roll')
    if skip_or_conclude:
        return skip_or_conclude[0], skip_or_conclude[1]  # (action, param) for skip/conclude

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
            return "buy_property", params
        else:
            # make_buy returned false, but is there still a chance?
            if agent_helper_functions.will_property_complete_set(player,current_location,current_gameboard):
                # if we can raise enough money, then the 'next' time around we'll succeed in buying
                to_mortgage = agent_helper_functions.identify_potential_mortgage(player, current_location.price, True)
                if to_mortgage:
                    # if to_mortgage.name in properties_you_wanted:
                    #     logger.debug(f'{player.player_name} tries to sell {to_mortgage.name}. Deny!')
                    # else:
                    params['asset'] = to_mortgage.name
                    logger.debug(player.player_name+ ': I am attempting to mortgage property ' + params['asset'])
                    player.agent._agent_memory['previous_action'] = "mortgage_property"
                    return "mortgage_property", params

                else: # last chance.
                    to_sell = agent_helper_functions.identify_potential_sale(player, current_gameboard, current_location.price,True)
                    if to_sell:
                        params['asset'] = to_sell.name
                        logger.debug(player.player_name+ ': I am attempting to sell property '+ current_location.name+' to the bank')
                        player.agent._agent_memory['previous_action'] = "sell_property"
                        return "sell_property", params

    # Final Check if agent should conclude
    final_check = _final_check(player, allowable_moves, 'post_roll')
    if final_check:
        return final_check[0], final_check[1]


def make_buy_property_decision(player, current_gameboard, asset):
    """
    The agent decides to buy the property if:
    (i) it can 'afford' it. Our definition of afford is that we must have at least go_increment cash balance after
    the purchase.
    (ii) we can obtain a full color set through the purchase, and still have positive cash balance afterwards (though
    it may be less than go_increment).
    (iii) For agent v4, buy park place, boardwalk, and railroads if you have enough cash

    :param player: A Player instance. You should expect this to be the player that is 'making' the decision (i.e. the player
    instantiated with the functions specified by this decision agent).
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: A Boolean. If True, then you decided to purchase asset from the bank, otherwise False. We allow you to
    purchase the asset even if you don't have enough cash; however, if you do you will end up with a negative
    cash balance and will have to handle that if you don't want to lose the game at the end of your move (see notes
    in handle_negative_cash_balance)
    """
    decision = False

    if asset.name in properties_you_dont_wanted:
        decision = False
    elif asset.name in properties_you_wanted and player.current_cash >= asset.price:
        logger.debug(f'{player.player_name}: I will attempt to buy {asset.name} from the bank with price {asset.price}.')
        decision = True
    elif player.current_cash - asset.price >= current_gameboard['go_increment']:  # case 1: can we afford it?
        logger.debug(player.player_name+ ': I will attempt to buy '+ asset.name+ ' from the bank.')
        decision = True
    elif asset.price <= player.current_cash and \
            agent_helper_functions.will_property_complete_set(player,asset,current_gameboard):
        logger.debug(player.player_name+ ': I will attempt to buy '+ asset.name+ ' from the bank.')
        decision = True

    return decision


def make_bid(player, current_gameboard, asset, current_bid):
    """
    Decide the amount you wish to bid for asset in auction, given the current_bid that is currently going. If you don't
    return a bid that is strictly higher than current_bid you will be removed from the auction and won't be able to
    bid anymore. Note that it is not necessary that you are actually on the location on the board representing asset, since
    you will be invited to the auction automatically once a player who lands on a bank-owned asset rejects buying that asset
    (this could be you or anyone else).
    :param player: A Player instance. You should expect this to be the player that is 'making' the decision (i.e. the player
    instantiated with the functions specified by this decision agent).
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :param asset: An purchaseable instance of Location (i.e. real estate, utility or railroad)
    :param current_bid: The current bid that is going in the auction. If you don't bid higher than this amount, the bank
    will remove you from the auction proceedings. You could also always return 0 to voluntarily exit the auction.
    :return: An integer that indicates what you wish to bid for asset
    """

    if asset.name in properties_you_dont_wanted:
        return 0
    elif asset.name in properties_you_wanted and player.current_cash >= current_bid:
        return current_bid + (player.current_cash - current_bid) / 6
    elif current_bid < asset.price:
        new_bid = current_bid + (asset.price-current_bid)/2
        if new_bid < player.current_cash:
            return new_bid
        else:   # We are aware that this can be simplified with a simple return 0 statement at the end. However in the final baseline agent
                # the return 0's would be replaced with more sophisticated rules. Think of them as placeholders.
            return 0 # this will lead to a rejection of the bid downstream automatically
    elif current_bid < player.current_cash and agent_helper_functions.will_property_complete_set(player,asset,current_gameboard):
            # We are prepared to bid more than the price of the asset only if it doesn't result in insolvency, and
                # if we can get a monopoly this way
        return current_bid+(player.current_cash-current_bid)/4
    else:
        return 0 # no reason to bid


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
            sale_potentials.append((a, (a.price*current_gameboard['bank'].total_cash_with_bank)-((1+current_gameboard['bank'].mortgage_percentage)*a.mortgage)))
        elif a.loc_class=='real_estate' and (a.num_houses>0 or a.num_hotels>0):
            continue
        else:
            sale_potentials.append((a,a.price*current_gameboard['bank'].total_cash_with_bank))

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
            sale_potentials.append((a, (a.price*current_gameboard['bank'].total_cash_with_bank)-((1+current_gameboard['bank'].mortgage_percentage)*a.mortgage)))
        elif a.loc_class=='real_estate' and (a.num_houses>0 or a.num_hotels>0):
            continue
        else:
            sale_potentials.append((a,a.price*current_gameboard['bank'].total_cash_with_bank))

    if sale_potentials:
        sorted_potentials = sorted(sale_potentials, key=lambda x: x[1])  # sort by sell value in ascending order
        for p in sorted_potentials:
            if player.current_cash >= 0:
                return (None, flag_config_dict['successful_action']) # we're done

            sorted_player_assets_list = _set_to_sorted_list_assets(player.assets)
            for prop in sorted_player_assets_list:
                if prop!=p[0] and prop.color==p[0].color and p[0].color in player.full_color_sets_possessed:
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
            sale_potentials.append((a, (a.price*current_gameboard['bank'].total_cash_with_bank)-((1+current_gameboard['bank'].mortgage_percentage)*a.mortgage)))
        elif a.loc_class=='real_estate' and (a.num_houses>0 or a.num_hotels>0):
            continue
        else:
            sale_potentials.append((a, a.price*current_gameboard['bank'].total_cash_with_bank))

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


def _check_before_turn(player, current_gameboard, allowable_moves, code, turn_num, turn_name):
    """Before each turn, agent need to reset phase_game corresponding to current turn
    :param player: current player
    :param current_gameboard: dict() which stores current gameboard info
    :param allowable_moves: moves current player could act
    :param code: fail code or not
    :param turn_num: a int number representing current turn: 1, 2, or 3
    :param turn_name: a string name representing current turn: 'pre_roll', 'out_of_turn', or 'post_roll'
    :return:
    """
    for p in current_gameboard['players']:
        if 'phase_game' not in p.agent._agent_memory:
            p.agent._agent_memory['phase_game'] = turn_num
            p.agent._agent_memory['count_unsuccessful_tries'] = 0

    if player.agent._agent_memory['phase_game'] != turn_num:
        player.agent._agent_memory['phase_game'] = turn_num
        player.agent._agent_memory['count_unsuccessful_tries'] = 0

    if turn_name == 'out_of_turn':
        if isinstance(code, list):
            code_flag = 0
            for c in code:
                if c == flag_config_dict['failure_code']:
                    code_flag = 1
                    break
            if code_flag:
                player.agent._agent_memory['count_unsuccessful_tries'] += 1
                logger.debug(f'{player.player_name} has executed an unsuccessful {turn_name} action, incrementing '
                             f'unsuccessful_tries counter to {str(player.agent._agent_memory["count_unsuccessful_tries"])}')
        elif code == flag_config_dict['failure_code']:
            player.agent._agent_memory['count_unsuccessful_tries'] += 1
            logger.debug(f'{player.player_name} has executed an unsuccessful {turn_name} action, incrementing '
                         f'unsuccessful_tries counter to {str(player.agent._agent_memory["count_unsuccessful_tries"])}')
    elif code == flag_config_dict['failure_code']:
        player.agent._agent_memory['count_unsuccessful_tries'] += 1
        logger.debug(f'{player.player_name} has executed an unsuccessful {turn_name} action, incrementing '
                     f'unsuccessful_tries counter to {str(player.agent._agent_memory["count_unsuccessful_tries"])}')

    if player.agent._agent_memory['count_unsuccessful_tries'] >= UNSUCCESSFUL_LIMIT:
        logger.debug(player.player_name + ' has reached out of turn unsuccessful action limits.')
        if "skip_turn" in allowable_moves and turn_name != 'post_roll':
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


def _final_check(player, allowable_moves, turn_name):
    """Before finishing each turn, it's time to check if agent should skip or conclude current turn
    :param player: current player
    :param allowable_moves: moves current player could act
    :param turn_name: string name for current turn: 'pre_roll', 'out_of_turn', or 'post_roll'
    :return: tuple(action, empty dict() since no more action need to be done)
    """

    if "skip_turn" in allowable_moves and turn_name != 'post_roll':
        logger.debug(player.player_name+ ': I am skipping turn')
        player.agent._agent_memory['previous_action'] = "skip_turn"
        return "skip_turn", dict()
    elif "concluded_actions" in allowable_moves:
        # player.agent._agent_memory['previous_action'] = action_choices.concluded_actions
        logger.debug(player.player_name+ ': I am concluding actions')
        return "concluded_actions", dict()
    else:
        logger.error("Exception")
        raise Exception


# def _set_to_sorted_list_mortgaged_assets(player_mortgaged_assets):
#     player_m_assets_list = list()
#     player_m_assets_dict = dict()
#     for item in player_mortgaged_assets:
#         player_m_assets_dict[item.name] = item
#     for sorted_key in sorted(player_m_assets_dict):
#         player_m_assets_list.append(player_m_assets_dict[sorted_key])
#     return player_m_assets_list


def _set_to_sorted_list_assets(player_assets):
    """
    Sort current player's assets according to assets' names
    :param player_assets: list of player's assets
    :return: a list of sorted assets for current player
    """
    player_assets_list = list()
    player_assets_dict = dict()
    for item in player_assets:
        player_assets_dict[item.name] = item
    for sorted_key in sorted(player_assets_dict):
        player_assets_list.append(player_assets_dict[sorted_key])
    return player_assets_list


def _ask_for_accept_trade_offer(player, current_gameboard):
    param = dict()
    param['player'] = player.player_name
    param['current_gameboard'] = "current_gameboard"
    logger.debug(player.player_name+ ': Should I accept the trade offer by '+player.outstanding_trade_offer['from_player'].player_name+'?')
    logger.debug('('+player.player_name+' currently has cash balance of '+str(player.current_cash)+')')



    if (player.outstanding_trade_offer['cash_offered'] <= 0 and len(player.outstanding_trade_offer['property_set_offered'])==0) \
            and (player.outstanding_trade_offer['cash_wanted'] > 0 or len(player.outstanding_trade_offer['property_set_wanted']) > 0):
        logger.debug('Asking for free money or property without money or property in return.')
        logger.debug(player.player_name + " rejected trade offer from " + player.outstanding_trade_offer['from_player'].player_name)
        pass   #asking for free money or property without anything in return(ie no money and no property offered), -->reject the trade offer

    elif player.outstanding_trade_offer['cash_wanted'] - player.outstanding_trade_offer['cash_offered'] > player.current_cash:
        logger.debug('Cash wanted from me in the trade offer is more than the cash in hand with me or I am near bankruptcy situation and need to play safe.')
        logger.debug(player.player_name + " rejected trade offer from " + player.outstanding_trade_offer['from_player'].player_name)
        pass  #cash wanted is more than that offered and the net difference exceeds the cash that the player has --> then reject the tade offer

    else:
        reject_flag = 0
        offered_properties_net_worth = 0
        wanted_properties_net_worth = 0
        for prop in player.outstanding_trade_offer['property_set_wanted']:
            if prop.is_mortgaged:
                reject_flag = 1  #cannot trade mortgaged properties, reject trade offer
                logger.debug('Trade offer invovlves mortgaged properties.')
                logger.debug(player.player_name + " rejected trade offer from " + player.outstanding_trade_offer['from_player'].player_name)
                break
            else:
                wanted_properties_net_worth += prop.price

        if not reject_flag:
            for offer in player.outstanding_trade_offer['property_set_offered']:
                if offer.name in properties_you_dont_wanted:
                    reject_flag = 1
                    break

        if reject_flag == 0:
            for prop in player.outstanding_trade_offer['property_set_offered']:
                if prop.is_mortgaged:
                    reject_flag = 1  #from_player cannot offer mortgaged properties, reject trade offer
                    logger.debug('Trade offer invovlves mortgaged properties.')
                    logger.debug(player.player_name + " rejected trade offer from " + player.outstanding_trade_offer['from_player'].player_name)
                    break
                else:
                    offered_properties_net_worth += prop.price
        if reject_flag == 0:
            #GOAL -- increase monopolies
            #calculate the net worth of offer vs net worth of request --> makes sense to accept trade only if the offer is greater than request
            #net worth of offer = cash + total price of all houses
            #positive net_amount_requested implies that the requested net amount is greater than offered net amount
            net_offer_worth = (offered_properties_net_worth + player.outstanding_trade_offer['cash_offered']) - \
                              (wanted_properties_net_worth + player.outstanding_trade_offer['cash_wanted'])
            net_amount_requested = -1*net_offer_worth

            count_create_new_monopoly = 0
            count_lose_existing_monopoly = 0 ##ideally player doesnot have to worry about losing monopolies since the player who makes the offer
            #only requests for lone properties
            for prop in player.outstanding_trade_offer['property_set_offered']:
                if agent_helper_functions.will_property_complete_set(player,prop,current_gameboard):
                    count_create_new_monopoly += 1
            for prop in player.outstanding_trade_offer['property_set_wanted']:
                if prop.color in player.full_color_sets_possessed:
                    count_lose_existing_monopoly += 1

            #if you end up losing more monopolies than gaining monopolies (although this condition should never come up) then reject trade offer
            if count_lose_existing_monopoly - count_create_new_monopoly > 0:
                logger.debug('Player loses more monopolies than he gains.')
                logger.debug(player.player_name + " rejected trade offer from " + player.outstanding_trade_offer['from_player'].player_name)
                reject_flag = 1

            #if you end up losing the same number of monopolies as you gain, then accept the offer based on the following multiple conditions.
            #Basically you get no new monopolies since ideally you dont lose monopolies (only properties that dont belong to your monopolized color
            # groups are only requested from you in the trade.)
            elif count_lose_existing_monopoly - count_create_new_monopoly == 0:
                # ------------------------------------
                # anti umass strategy
                # if wealthiest player == from_player-> reject the offer!
                wealthy_player = _find_most_wealthy_agent(player, current_gameboard)
                if wealthy_player.player_name == player.outstanding_trade_offer['from_player'].player_name:
                    logger.debug(player.player_name + " rejected trade offer from " + player.outstanding_trade_offer['from_player'].player_name + "because of umass strategy")
                    reject_flag = 1
                elif (player.outstanding_trade_offer['cash_wanted'] - player.outstanding_trade_offer['cash_offered']) >= player.current_cash:
                # ------------------------------------
                #if (player.outstanding_trade_offer['cash_wanted'] - player.outstanding_trade_offer['cash_offered']) >= player.current_cash:
                    logger.debug('Cash wanted from me in the trade offer is more than the cash in hand with me or I am near bankruptcy situation and need to play safe.')
                    logger.debug(player.player_name + " rejected trade offer from " + player.outstanding_trade_offer['from_player'].player_name)
                    reject_flag = 1  ##just double checking although this condition was verified before getting here.
                elif player.current_cash - (player.outstanding_trade_offer['cash_wanted'] - player.outstanding_trade_offer['cash_offered']) < current_gameboard['go_increment']/2:
                    logger.debug('Cash wanted from me in the trade offer is more than the cash in hand with me or I am near bankruptcy situation and need to play safe.')
                    logger.debug(player.player_name + " rejected trade offer from " + player.outstanding_trade_offer['from_player'].player_name)
                    reject_flag = 1  ##too risky if players cash after transaction drops below half of go_increment value --> hence reject trade offer
                elif (player.current_cash - (player.outstanding_trade_offer['cash_wanted'] - player.outstanding_trade_offer['cash_offered']) < current_gameboard['go_increment']) \
                        and net_offer_worth <= 0:
                    logger.debug('No gain from accepting trade offer.')
                    logger.debug(player.player_name + " rejected trade offer from " + player.outstanding_trade_offer['from_player'].player_name)
                    reject_flag =1  ##if player has cash > go_increement/2 and < go_increement but net worth of total transaction is negative --> reject trade offer
                else:
                    reject_flag =0  ##accept only if you end up getting a higher net worth by accepting the trade although you get no new monopolies


            #else you get to monopolize more locations than you had before --> then ACCEPT THE TRADE OFFER
            elif count_create_new_monopoly - count_lose_existing_monopoly > 0:
                if (player.outstanding_trade_offer['cash_wanted'] - player.outstanding_trade_offer['cash_offered']) >= player.current_cash:
                    logger.debug('Cash wanted from me in the trade offer is more than the cash in hand with me or I am near bankruptcy situation and need to play safe.')
                    logger.debug(player.player_name + " rejected trade offer from " + player.outstanding_trade_offer['from_player'].player_name)
                    reject_flag = 1  ##just double checking although this condition was verified before getting here.
                else:
                    reject_flag = 0

        if reject_flag == 0:
            # -----------
            # debugging May.5, 2022
            if player.player_name == 'player_2':
                logger.debug('I am here! aaaaaaaaaaaa')
                logger.debug('cash_wanted = ' + str(player.outstanding_trade_offer['cash_wanted']))
                logger.debug('cash_offered = ' + str(player.outstanding_trade_offer['cash_offered']))
                logger.debug('---')
                logger.debug('property_set_wanted = ')
                for pw in player.outstanding_trade_offer['property_set_wanted']:
                    logger.debug(str(pw.name))
                logger.debug('---')
                logger.debug('property_set_offered = ' + str(player.outstanding_trade_offer['property_set_offered']))

                logger.debug('determining params---')
                logger.debug('cash = ' + str(player.current_cash))
                logger.debug('net_offer_worth = ' + str(net_offer_worth))
                logger.debug('count_create_new_monopoly = ' + str(count_create_new_monopoly))
                logger.debug('count_lose_existing_monopoly = ' + str(count_lose_existing_monopoly))
                logger.debug('I am here! aaaaaaaaaaaa')
            # -----------
            logger.debug(player.player_name + " accepted trade offer from " + player.outstanding_trade_offer['from_player'].player_name)
            logger.debug(player.player_name + " recieved amount = " + str(player.outstanding_trade_offer['cash_offered']) + " and offered amount = " +
                         str(player.outstanding_trade_offer['cash_wanted']) + " during trade")
            player.agent._agent_memory['previous_action'] = "accept_trade_offer"
            return ("accept_trade_offer", param)
        elif reject_flag == 1:
            #logger.debug(player.player_name + " rejected trade offer from " + player.outstanding_trade_offer['from_player'].player_name)
            pass


def _ask_for_accept_sell_trade_offer():
    # if "accept_sell_property_offer" in allowable_moves:
    #     ## Ideally accept_sell_offer should never enter allowable moves since henceforth make_trade_offer also takes care of make_sell_offer and
    #     ## accept_trade_offer takes care of accept_sell_offer.
    #     ## This case is included to accomodate a make_sell_property offer raised by an external agent.
    #     ## Our agent will never make a sell property offer, only makes trade offers which raises an accpet_trade_offer action.
    #     param = dict()
    #     param['player'] = player.player_name
    #     param['current_gameboard'] = "current_gameboard"
    #     print('Find accept_sell_property_offer')
    #     # we accept an offer under one of two conditions:
    #     logger.debug(player.player_name+ ': Should I accept the offer by '+player.outstanding_property_offer['from_player'].player_name+' to buy '+\
    #         player.outstanding_property_offer['asset'].name+' for '+str(player.outstanding_property_offer['price'])+'?')
    #     logger.debug('('+player.player_name+' currently has cash balance of '+str(player.current_cash)+')')
    #     if player.outstanding_property_offer['asset'].is_mortgaged or player.outstanding_property_offer['price']>player.current_cash:
    #         pass # ignore the offer if the property is mortgaged or will result in insolvency. This pass doesn't require 'filling' in.
    #     elif player.current_cash-player.outstanding_property_offer['price'] >= current_gameboard['go_increment'] and \
    #         player.outstanding_property_offer['price']<=player.outstanding_property_offer['asset'].price:
    #         # 1. we can afford it, and it's at or below market rate so let's buy it
    #         logger.debug(player.player_name+ ': I am accepting the offer to buy '+player.outstanding_property_offer['asset'].name+' since I can afford' \
    #                                                 'it and it is being offered at or below market rate.')
    #         player.agent._agent_memory['previous_action'] = "accept_sell_property_offer"
    #         return ("accept_sell_property_offer", param)
    #     elif agent_helper_functions.will_property_complete_set(player, player.outstanding_property_offer['asset'],current_gameboard):
    #         # 2. less affordable, but we stand to gain by monopoly
    #         if player.current_cash - player.outstanding_property_offer['price'] >= current_gameboard['go_increment']/2: # risky, but worth it
    #             logger.debug(player.player_name+ ': I am accepting the offer to buy '+ player.outstanding_property_offer[
    #                 'asset'].name+ ' since I can afford ' \
    #                                'it (albeit barely so) and it will let me complete my color set.')
    #             player.agent._agent_memory['previous_action'] = "accept_sell_property_offer"
    #             return ("accept_sell_property_offer", param)
    return None


def _ask_for_improve_property(player, current_gameboard, code):
    """Improve any properties if:
    1. have at least one full color set
    2. have enough money to upgrade
    :param player: current player
    :param current_gameboard: dict() which stores current gameboard info
    :param code: fail code or not
    :return: tuple(action, param)
    """
    param = agent_helper_functions.identify_improvement_opportunity(player, current_gameboard)
    if param:
        if player.agent._agent_memory['previous_action'] == "improve_property" and code == flag_config_dict['failure_code']:
            logger.debug(player.player_name+ ': I want to improve property '+param['asset'].name + ' but I cannot, due to reasons I do not understand. Aborting improvement attempt...')
        else:
            logger.debug(player.player_name+ ': I am going to improve property '+param['asset'].name)
            player.agent._agent_memory['previous_action'] = "improve_property"
            param['player'] = param['player'].player_name
            param['asset'] = param['asset'].name
            param['current_gameboard'] = "current_gameboard"
            return "improve_property", param


def _try_to_free_mortgage(player, current_gameboard):
    """Free any mortgages if current player have enough money
    :param player: current player
    :param current_gameboard: dict() which stores current gameboard info
    :return: tuple(action, param)
    """
    player_mortgaged_assets_list = list()
    if player.mortgaged_assets:
        player_mortgaged_assets_list = _set_to_sorted_list_assets(player.mortgaged_assets)
    for m in player_mortgaged_assets_list:
        if player.current_cash - (m.mortgage * (1 + current_gameboard['bank'].mortgage_percentage)) >= current_gameboard['go_increment']:
            # free mortgages till we can afford it. the second condition should not be necessary but just in case.
            param = dict()
            param['player'] = player.player_name
            param['asset'] = m.name
            param['current_gameboard'] = "current_gameboard"
            logger.debug(player.player_name+ ': I am going to free mortgage on ' + m.name)
            player.agent._agent_memory['previous_action'] = "free_mortgage"
            return "free_mortgage", param


def _make_trade_offer(player, current_gameboard, purpose_flag, want_properties_aggressively=False):
    """Decide what kind of offer we would like to make with other players:
    1. sell properties with wanted price
    2. buy railroads, Boardwalk, and Park Place from others
    3. to complete color set monopoly
    :param player: current player in out_of_turn
    :param current_gameboard: dict() which stores current gameboard info
    :param purpose_flag: 1 or 2 to identify trade offers
    :param want_properties_aggressively: True when you have purpose to buy some properties; otherwises, False
    :return: tuple(action_list, param_list)
    """

    if want_properties_aggressively:
        potential_request_list = agent_helper_functions.identify_property_trade_wanted_from_player_aggressively(player, current_gameboard, properties_you_wanted)
    else:
        potential_request_list = agent_helper_functions.identify_property_trade_wanted_from_player(player, current_gameboard)
    potential_offer_list = agent_helper_functions.identify_property_trade_offer_to_player(player, current_gameboard)
    param_list = agent_helper_functions.curate_trade_offer_multiple_players(player, potential_offer_list, potential_request_list, current_gameboard, purpose_flag=purpose_flag)

    return_action_list = []
    return_param_list = []

    # we only make one offer per turn. Otherwise we'd be stuck in a loop
    if param_list and player.agent._agent_memory['previous_action'] != "make_trade_offer":
        if len(param_list)>1:
            logger.debug(player.player_name + ": I am going to make trade offers to multiple players, ie " + str(len(param_list)) + " players.")
        for param in param_list:
            if purpose_flag == 1:
                logger.debug(player.player_name+ ': I am making an offer to trade '+list(param['offer']['property_set_offered'])[0].name+' to '+
                             param['to_player'].player_name+' for '+str(param['offer']['cash_wanted'])+' dollars')
            elif purpose_flag == 2:
                if param and param["offer"]["property_set_wanted"]:
                    logger.debug(f'{player.player_name}: I am making a trade offer with {param["to_player"].player_name} '
                                 f'for {list(param["offer"]["property_set_wanted"])[0].name}.')
                else:
                    logger.debug(f'{player.player_name}: I am making a trade offer with {param["to_player"].player_name}.')

            param['from_player'] = param['from_player'].player_name
            param['to_player'] = param['to_player'].player_name
            prop_set_offered = set()
            for item in param['offer']['property_set_offered']:
                prop_set_offered.add(item.name)
            param['offer']['property_set_offered'] = prop_set_offered
            prop_set_wanted = set()
            for item in param['offer']['property_set_wanted']:
                prop_set_wanted.add(item.name)
            param['offer']['property_set_wanted'] = prop_set_wanted

            # Peter added
            param['current_gameboard'] = current_gameboard
            #

            player.agent._agent_memory['previous_action'] = "make_trade_offer"
            return_action_list.append("make_trade_offer")
            return_param_list.append(param)

        return return_action_list, return_param_list


def _ask_for_make_trade_offer(player, current_gameboard):
    """Should We make a trade offer with others?
    :param player: currently out_of_turn player
    :param current_gameboard: dict() of current gameboard
    :return: tuple(action list, param_list)
    """

    # 1. Urgent for cash, sell properties for cash
    if player.current_cash < current_gameboard['go_increment']:
        return _make_trade_offer(player, current_gameboard, purpose_flag=1, want_properties_aggressively=False)
    # 2. Aggressively to buy railroads, Boardwalk, and Park Place
    elif player.num_railroads_possessed > 0:
        return _make_trade_offer(player, current_gameboard, purpose_flag=2, want_properties_aggressively=True)
    # 3. For complete color set monopoly
    else:
        return _make_trade_offer(player, current_gameboard, purpose_flag=2, want_properties_aggressively=False)


def _find_most_wealthy_agent(player, current_gameboard):
    """
    this function return the most wealthy agent currently in the game board. Wealthiness is determined by the net worth.
    net worth
    the most wealthy agent is the target this player would target on, if the most wealthy agent is the player itself,
    then nothing need to be done
    :param player: this agent
    :param current_gameboard:
    :return:
    """

    most_wealth_player = None
    cur_max_wealth = float('-inf')
    for p in current_gameboard['players']:
        if p.player_name != player.player_name and p.status != 'lost':
            cur_player_wealth = 0

            # compute net worth of this player
            cur_player_wealth += p.current_cash
            if p.assets:
                for prop in p.assets:
                    if prop.loc_class == 'real_estate':
                        cur_player_wealth += prop.price
                        cur_player_wealth += prop.num_houses*prop.price_per_house
                        cur_player_wealth += prop.num_hotels*prop.price_per_house*(current_gameboard['bank'].house_limit_before_hotel + 1)
                    elif prop.loc_class == 'railroad':
                        cur_player_wealth += prop.price
                    elif prop.loc_class == 'utility':
                        cur_player_wealth += prop.price

            if cur_player_wealth > cur_max_wealth:
                most_wealth_player = p
                cur_max_wealth = cur_player_wealth

    # compare the agent itself to see if it is the most wealthy one
    agent_itself_wealth = player.current_cash
    if player.assets:
        for prop in player.assets:
            if prop.loc_class == 'real_estate':
                agent_itself_wealth += prop.price
                agent_itself_wealth += prop.num_houses*prop.price_per_house
                agent_itself_wealth += prop.num_hotels*prop.price_per_house*(current_gameboard['bank'].house_limit_before_hotel + 1)
            elif prop.loc_class == 'railroad':
                agent_itself_wealth += prop.price
            elif prop.loc_class == 'utility':
                agent_itself_wealth += prop.price

    # find the most wealthy player in the game board
    if agent_itself_wealth < cur_max_wealth:
        return most_wealth_player
    # the most wealth player is itself
    else:
        return player

def _build_decision_agent_methods_dict():
    """This function builds the decision agent methods dictionary.
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


# List of properties agent v4 would like to buy, trade, and bid during the game
properties_you_wanted = ('Boardwalk', 'Park Place',     # High rent properties
                         'Reading Railroad', 'Pennsylvania Railroad', 'B&O Railroad', 'Short Line')  # Railroads
# List of properties agent v4_1 don't want to purchase
properties_you_dont_wanted = ('Electric Company', 'Water Works')

# this is the main data structure that is needed by gameplay
decision_agent_methods = _build_decision_agent_methods_dict()


