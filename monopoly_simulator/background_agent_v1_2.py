from monopoly_simulator import action_choices
from monopoly_simulator import agent_helper_functions_v2 as agent_helper_functions# helper functions are internal to the agent and will not be recorded in the function log.
from monopoly_simulator.bank import Bank
from monopoly_simulator.flag_config import flag_config_dict
import logging
logger = logging.getLogger('monopoly_simulator.logging_info.background_agent')


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


def make_pre_roll_move(player, current_gameboard, allowable_moves, code):
    """
    Many actions are possible in pre_roll but we prefer to save the logic for out_of_turn. The only decision
    we'll make here is whether we want to leave jail (if we're in jail).
    :param player: A Player instance. You should expect this to be the player that is 'making' the decision (i.e. the player
    instantiated with the functions specified by this decision agent).
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :param allowable_moves: A set of functions, each of which is defined in action_choices (imported in this file), and that
    will always be a subset of the action choices for pre_die_roll in the game schema. Your returned action choice must be from
    allowable_moves; we will check for this when you return.
    :param code: See the preamble of this file for an explanation of this code
    :return: A 2-element tuple, the first of which is the action you want to take, and the second is a dictionary of
    parameters that will be passed into the function representing that action when it is executed.
    The dictionary must exactly contain the keys and expected value types expected by that action in
    action_choices
    """
    if player.current_cash >= current_gameboard['go_increment']: # if we don't have enough money, best to stay put.
        param = dict()
        param['player'] = player.player_name
        param['current_gameboard'] = "current_gameboard"
        if "use_get_out_of_jail_card" in allowable_moves:
            logger.debug(player.player_name+': I am using get out of jail card.')
            player.agent._agent_memory['previous_action'] = action_choices.use_get_out_of_jail_card
            return ("use_get_out_of_jail_card", param)
        elif "pay_jail_fine" in allowable_moves:
            logger.debug(player.player_name+': I am going to pay jail fine.')
            player.agent._agent_memory['previous_action'] = action_choices.pay_jail_fine
            return ("pay_jail_fine", param)

    # if we ran the gamut, and did not return, then it's time to skip turn or conclude actions
    if "skip_turn" in allowable_moves:
        logger.debug(player.player_name+ ': I am skipping turn')
        player.agent._agent_memory['previous_action'] = action_choices.skip_turn
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
    :param allowable_moves: A set of functions, each of which is defined in action_choices (imported in this file), and that
    will always be a subset of the action choices for out_of_turn in the game schema. Your returned action choice must be from
    allowable_moves; we will check for this when you return.
    :param code: See the preamble of this file for an explanation of this code
    :return: A 2-element tuple, the first of which is the action you want to take, and the second is a dictionary of
    parameters that will be passed into the function representing that action when it is executed.
    The dictionary must exactly contain the keys and expected value types expected by that action in
    action_choices
    """

    '''
    NOTE: The background agent that could make_sell_property_offer is deprecated (available as background_agent_v1_deprecated.py)
    This version of the agent can only make_trade_offer and accept trade offer. Trade involves buy or sell or exchange property offers.
    Accept_sell_property_offer function is still available in case some different agent decides to make a sell property offer.
    Ideally, accept_sell_property_offer() function should never enter allowable moves.
    Make sell property offer can be replicated by making a trade offer that only offers to sell properties in return for cash
    and doesnot involve a buy property or exchange property offer.
    A buy property offer can be duplicated by including only requested properties by offering cash without offering properties.
    Properties and cash can be exchanged which lets both players get an advantage of increasing their respective number of monopolies.
    This version of the agent background_agent_v1 only supports making sell property offers in return for cash via make_trade_offer. 
    Buy and exchange property offers are not involved in the trade.
    '''

    if "accept_trade_offer" in allowable_moves:
        if len(player.outstanding_trade_offer["property_set_wanted"]) or player.outstanding_trade_offer["cash_offered"]>0:
            logger.debug("I am background_agent_v1 and I can only accept trade offers that involve buying others properties in return for cash to increase"+
                         "my monopolies. I donot sell my properties to others.")
    elif "accept_trade_offer" in allowable_moves:
        param = dict()
        param['player'] = player.player_name
        param['current_gameboard'] = "current_gameboard"
        logger.debug(player.player_name+ ': Should I accept the offer by '+player.outstanding_trade_offer['from_player'].player_name+' to buy '+\
            list(player.outstanding_trade_offer['property_set_offered'])[0].name+' for '+str(player.outstanding_trade_offer['cash_wanted'])+'?')
        logger.debug('('+player.player_name+' currently has cash balance of '+str(player.current_cash)+')')
        if list(player.outstanding_trade_offer['property_set_offered'])[0].is_mortgaged or player.outstanding_trade_offer['cash_wanted']>player.current_cash:
            pass # ignore the offer if the property is mortgaged or will result in insolvency. This pass doesn't require 'filling' in.
        elif player.current_cash-player.outstanding_trade_offer['cash_wanted'] >= current_gameboard['go_increment'] and \
            player.outstanding_trade_offer['cash_wanted']<=list(player.outstanding_trade_offer['property_set_offered'])[0].price:
            # 1. we can afford it, and it's at or below market rate so let's buy it
            logger.debug(player.player_name+ ': I am accepting the offer to buy '+list(player.outstanding_trade_offer['property_set_offered'])[0].name+' since I can afford' \
                                                    'it and it is being offered at or below market rate.')
            player.agent._agent_memory['previous_action'] = action_choices.accept_sell_property_offer
            return ("accept_trade_offer", param)
        elif agent_helper_functions.will_property_complete_set(player, list(player.outstanding_trade_offer['property_set_offered'])[0],current_gameboard):
            # 2. less affordable, but we stand to gain by monopoly
            if player.current_cash - player.outstanding_trade_offer['cash_wanted'] >= current_gameboard['go_increment']/2: # risky, but worth it
                logger.debug(player.player_name+ ': I am accepting the offer to buy '+ list(player.outstanding_trade_offer['property_set_offered'])[0].name+ ' since I can afford ' \
                                   'it (albeit barely so) and it will let me complete my color set.')
                player.agent._agent_memory['previous_action'] = action_choices.accept_trade_offer
                return ("accept_trade_offer", param)

    if "accept_sell_property_offer" in allowable_moves:
        ## Ideally accept_sell_offer should never enter allowable moves since henceforth make_trade_offer also takes care of make_sell_offer and
        ## accept_trade_offer takes care of accept_sell_offer.
        param = dict()
        param['player'] = player.player_name
        param['current_gameboard'] = "current_gameboard"
        # we accept an offer under one of two conditions:
        logger.debug(player.player_name+ ': Should I accept the offer by '+player.outstanding_property_offer['from_player'].player_name+' to buy '+\
            player.outstanding_property_offer['asset'].name+' for '+str(player.outstanding_property_offer['price'])+'?')
        logger.debug('('+player.player_name+' currently has cash balance of '+str(player.current_cash)+')')
        if player.outstanding_property_offer['asset'].is_mortgaged or player.outstanding_property_offer['price']>player.current_cash:
            pass # ignore the offer if the property is mortgaged or will result in insolvency. This pass doesn't require 'filling' in.
        elif player.current_cash-player.outstanding_property_offer['price'] >= current_gameboard['go_increment'] and \
            player.outstanding_property_offer['price']<=player.outstanding_property_offer['asset'].price:
            # 1. we can afford it, and it's at or below market rate so let's buy it
            logger.debug(player.player_name+ ': I am accepting the offer to buy '+player.outstanding_property_offer['asset'].name+' since I can afford' \
                                                    'it and it is being offered at or below market rate.')
            player.agent._agent_memory['previous_action'] = action_choices.accept_sell_property_offer
            return ("accept_sell_property_offer", param)
        elif agent_helper_functions.will_property_complete_set(player, player.outstanding_property_offer['asset'],current_gameboard):
            # 2. less affordable, but we stand to gain by monopoly
            if player.current_cash - player.outstanding_property_offer['price'] >= current_gameboard['go_increment']/2: # risky, but worth it
                logger.debug(player.player_name+ ': I am accepting the offer to buy '+ player.outstanding_property_offer[
                    'asset'].name+ ' since I can afford ' \
                                   'it (albeit barely so) and it will let me complete my color set.')
                player.agent._agent_memory['previous_action'] = action_choices.accept_sell_property_offer
                return ("accept_sell_property_offer", param)

    if player.status != 'current_move': # these actions are considered only if it's NOT our turn to roll the dice.
        if "improve_property" in allowable_moves: # beef up full color sets to maximize rent potential.
            param = agent_helper_functions.identify_improvement_opportunity(player, current_gameboard)
            if param:
                if player.agent._agent_memory['previous_action'] == action_choices.improve_property and code == flag_config_dict['failure_code']:
                    logger.debug(player.player_name+ ': I want to improve property '+param['asset'].name+ ' but I cannot, due to reasons I do not understand. Aborting improvement attempt...')
                else:
                    logger.debug(player.player_name+ ': I am going to improve property '+param['asset'].name)
                    player.agent._agent_memory['previous_action'] = action_choices.improve_property
                    param['player'] = param['player'].player_name
                    param['asset'] = param['asset'].name
                    param['current_gameboard'] = "current_gameboard"
                    return ("improve_property", param)

        player_mortgaged_assets_list = list()
        if "mortgaged_assets":
            player_mortgaged_assets_list = _set_to_sorted_list_mortgaged_assets(player.mortgaged_assets)
        for m in player_mortgaged_assets_list:
            if player.current_cash-(Bank.calculate_mortgage_owed(m, current_gameboard)) >= current_gameboard['go_increment'] and \
                    "free_mortgage" in allowable_moves:
                # free mortgages till we can afford it. the second condition should not be necessary but just in case.
                param = dict()
                param['player'] = player.player_name
                param['asset'] = m.name
                param['current_gameboard'] = "current_gameboard"
                logger.debug(player.player_name+ ': I am going to free mortgage on '+ param['asset'])
                player.agent._agent_memory['previous_action'] = action_choices.free_mortgage
                return ("free_mortgage", param)


    else: # it is our current move. We should raise money if necessary, especially if we're low on cash.
        if player.current_cash < current_gameboard['go_increment'] and "make_trade_offer" in allowable_moves:
            # let's try to see if we can sell property to other players at a premium using make_trade_offer without wanting any properties
            # the current agent does not try to raise money any other way. The reason is that selling houses, hotels, properties
            # or mortgaging properties are all available to us both in post-roll and also in handle_negative_cash_balance. A more proactive
            # agent (which isn't us) may want to make sure cash reserves are high before rolling the dice. Similarly, a more opportunistic
            # agent may choose to make a sell offer even if cash reserves aren't too low.
            potential_offer_list = agent_helper_functions.identify_property_trade_offer_to_player(player, current_gameboard)
            potential_request_list = None
            param = agent_helper_functions.curate_trade_offer(player, potential_offer_list, potential_request_list, current_gameboard, purpose_flag=1)
            logger.debug(player.agent._agent_memory['previous_action'])
            if param and player.agent._agent_memory['previous_action'] != "make_trade_offer": # we only make one offer per turn. Otherwise we'd
                # be stuck in a loop
                logger.debug(player.player_name+ ': I am making an offer to trade '+list(param['offer']['property_set_offered'])[0].name+' to '+
                         param['to_player'].player_name+' for '+str(param['offer']['cash_wanted'])+' dollars')
                player.agent._agent_memory['previous_action'] = action_choices.make_trade_offer
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

                player.agent._agent_memory['previous_action'] = "make_trade_offer"
                return ("make_trade_offer", param)
        elif "make_trade_offer" in allowable_moves: # let's try to see if we can sell property to other players at an insane premium
            # even though we don't 'need' the money
            potential_offer_list = agent_helper_functions.identify_property_trade_offer_to_player(player, current_gameboard)
            potential_request_list = None
            param = agent_helper_functions.curate_trade_offer(player, potential_offer_list, potential_request_list, current_gameboard, purpose_flag=1)
            if param and player.agent._agent_memory['previous_action'] != "make_trade_offer": # we only make one offer per turn. Otherwise we'd
                # be stuck in a loop
                logger.debug(player.player_name+ ': I am making an offer to trade '+list(param['offer']['property_set_offered'])[0].name+' to '+
                         param['to_player'].player_name+' for '+str(param['offer']['cash_wanted'])+' dollars')
                player.agent._agent_memory['previous_action'] = action_choices.make_trade_offer
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

                player.agent._agent_memory['previous_action'] = "make_trade_offer"
                return ("make_trade_offer", param)


    # if we ran the gamut, and did not return, then it's time to skip turn or conclude actions
    if "skip_turn" in allowable_moves:
        logger.debug(player.player_name+ ': I am skipping turn')
        player.agent._agent_memory['previous_action'] = action_choices.skip_turn
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
            logger.debug(player.player_name+ ': I am attempting to buy property '+params['asset'])
            player.agent._agent_memory['previous_action'] = action_choices.buy_property
            return ("buy_property", params)
        else:
            # make_buy returned false, but is there still a chance?
            if agent_helper_functions.will_property_complete_set(player,current_location,current_gameboard):
                # if we can raise enough money, then the 'next' time around we'll succeed in buying
                to_mortgage = agent_helper_functions.identify_potential_mortgage(player,current_location.price,True)
                if to_mortgage:
                    params['asset'] = to_mortgage.name
                    logger.debug(player.player_name+ ': I am attempting to mortgage property '+ params['asset'])
                    player.agent._agent_memory['previous_action'] = action_choices.mortgage_property
                    return ("mortgage_property", params)

                else: # last chance.
                    to_sell = agent_helper_functions.identify_potential_sale(player, current_gameboard, current_location.price,True)
                    if to_sell:
                        params['asset'] = to_sell.name
                        logger.debug(player.player_name+ ': I am attempting to sell property '+ params['asset']+' to the bank')
                        player.agent._agent_memory['previous_action'] = action_choices.sell_property
                        return ("sell_property", params)

    if "concluded_actions" in allowable_moves:
        # player.agent._agent_memory['previous_action'] = action_choices.concluded_actions
        return ("concluded_actions", dict())

    else:
        logger.error("Exception")
        raise Exception


def make_buy_property_decision(player, current_gameboard, asset):
    """
    The agent decides to buy the property if:
    (i) it can 'afford' it. Our definition of afford is that we must have at least go_increment cash balance after
    the purchase.
    (ii) we can obtain a full color set through the purchase, and still have positive cash balance afterwards (though
    it may be less than go_increment).
    :param player: A Player instance. You should expect this to be the player that is 'making' the decision (i.e. the player
    instantiated with the functions specified by this decision agent).
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: A Boolean. If True, then you decided to purchase asset from the bank, otherwise False. We allow you to
    purchase the asset even if you don't have enough cash; however, if you do you will end up with a negative
    cash balance and will have to handle that if you don't want to lose the game at the end of your move (see notes
    in handle_negative_cash_balance)
    """
    decision = False
    if player.current_cash - asset.price >= current_gameboard['go_increment']:  # case 1: can we afford it?
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

    if current_bid < asset.price:
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
    :return: -1 (failure code) if you do not try to address your negative cash balance, or 1 if you tried and believed you succeeded.
    Note that even if you do return 1 (successful move action), we will check to see whether you have non-negative cash balance. The rule of thumb
    is to return 1 (successful move action) as long as you 'try', or -1 if you don't try (in which case you will be declared bankrupt and lose the game)
    """

    if player.current_cash >= 0:   # prelim check to see if player has negative cash balance
        return (None, flag_config_dict['successful_action'])

    #player should evaluate all the possible options that can save it from bankruptcy and take most promising actions

    mortgage_potentials = list()
    max_sum = 0
    sorted_player_assets_list = _set_to_sorted_list_assets(player.assets)
    for a in sorted_player_assets_list:
        if a.is_mortgaged:
            continue
        elif a.loc_class=='real_estate' and (a.num_houses>0 or a.num_hotels>0):
            continue
        else:
            mortgage_potentials.append((a, a.mortgage))
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
            sale_potentials.append((a, (a.price*current_gameboard['bank'].property_sell_percentage)-Bank.calculate_mortgage_owed(a, current_gameboard)))
            # Since its a weak agent, we don't want it to think so much as the below code
            # if (a.price*current_gameboard['bank'].property_sell_percentage)-Bank.calculate_mortgage_owed(a, current_gameboard) > 0:
            #     # default case, this will never be > 0 unless novelty is introduced
            #     sale_potentials.append((a, (a.price*current_gameboard['bank'].property_sell_percentage)-Bank.calculate_mortgage_owed(a, current_gameboard)))
            # else:
            #     continue        # no point selling a mortgaged property if you dont anything out of it
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

    # if selling properties from non monopolized color groups doesnot relieve the player from debt, then only we start thinking about giving up monopolized groups.
    # If we come across a unimproved property which belongs to a monopoly, we still have to loop through the other properties from the same color group and
    # sell the houses and hotels first because we cannot sell this property when the color group has improved properties
    # We first check if selling houses and hotels one by one on the other improved properties of the same color group relieves the player of his debt. If it does
    # then we return without selling the current property else we sell the property and the player loses monopoly of that color group.
    max_sum = 0
    sale_potentials = list()
    sorted_player_assets_list = _set_to_sorted_list_assets(player.assets)
    for a in sorted_player_assets_list:
        if a.is_mortgaged:
            sale_potentials.append((a, (a.price*current_gameboard['bank'].property_sell_percentage)-Bank.calculate_mortgage_owed(a, current_gameboard)))
            # Since its a weak agent, we don't want it to think so much as the below code
            # if a.price*current_gameboard['bank'].property_sell_percentage-Bank.calculate_mortgage_owed(a, current_gameboard) > 0:
            #     # default case, this will never be > 0 unless novelty is introduced
            #     sale_potentials.append((a, (a.price*current_gameboard['bank'].property_sell_percentage)-Bank.calculate_mortgage_owed(a, current_gameboard)))
            # else:
            #     continue   # no point selling mortgaged property if you dont get anything out of it
        elif a.loc_class=='real_estate' and (a.num_houses > 0 or a.num_hotels > 0):
            continue
        else:
            sale_potentials.append((a, a.price*current_gameboard['bank'].property_sell_percentage))

    if sale_potentials:
        sorted_potentials = sorted(sale_potentials, key=lambda x: x[1])  # sort by sell value in ascending order
        for p in sorted_potentials:
            if player.current_cash >= 0:
                return (None, flag_config_dict['successful_action']) # we're done

            sorted_player_assets_list = _set_to_sorted_list_assets(player.assets)
            for prop in sorted_player_assets_list:
                if prop != p[0] and prop.color == p[0].color and p[0].color in player.full_color_sets_possessed:
                    if hasattr(prop, 'num_hotels'):  # add by Peter, for composite novelty
                        if prop.num_hotels > 0:    # if current asset has no hotels, prop can only have max of 1 hotel (uniform improvement rule)
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

                        elif prop.num_houses > 0:     # if current asset has no houses, prop can only have max of 1 house (uniform improvement rule)
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

    # mortgage_potentials = list()
    # sorted_player_assets_list = _set_to_sorted_list_assets(player.assets)
    # for a in sorted_player_assets_list:
    #     if a.is_mortgaged:
    #         continue
    #     elif a.loc_class=='real_estate' and (a.num_houses>0 or a.num_hotels>0):
    #         continue
    #     else:
    #         mortgage_potentials.append((a,a.mortgage))
    #
    # if mortgage_potentials and max_sum+player.current_cash >= 0: # if the second condition is not met, no point in mortgaging
    #     sorted_potentials = sorted(mortgage_potentials, key=lambda x: x[1])  # sort by mortgage in ascending order
    #     for p in sorted_potentials:
    #         if player.current_cash >= 0:
    #             return (None, flag_config_dict['successful_action']) # we're done
    #
    #         params = dict()
    #         params['player'] = player.player_name
    #         params['asset'] = p[0].name
    #         params['current_gameboard'] = "current_gameboard"
    #         logger.debug(player.player_name+ ': I am attempting to mortgage property '+ params['asset'])
    #         player.agent._agent_memory['previous_action'] = "mortgage_property"
    #         return ("mortgage_property", params)
    #
    # # following sale potentials loops through the properties that have become unmonopolized due to the above loops and
    # # doesnot include properties from monopolized color groups
    # sale_potentials = list()
    # sorted_player_assets_list = _set_to_sorted_list_assets(player.assets)
    #
    # for a in sorted_player_assets_list:
    #     if a.color in player.full_color_sets_possessed:
    #         continue
    #     elif a.is_mortgaged:
    #         if (a.price*current_gameboard['bank'].property_sell_percentage)-Bank.calculate_mortgage_owed(a, current_gameboard) > 0:
    #             sale_potentials.append((a, (a.price*current_gameboard['bank'].property_sell_percentage)-Bank.calculate_mortgage_owed(a, current_gameboard)))
    #         else:
    #             continue
    #     elif a.loc_class=='real_estate' and (a.num_houses>0 or a.num_hotels>0):
    #         continue
    #     else:
    #         sale_potentials.append((a, a.price*current_gameboard['bank'].property_sell_percentage))
    #
    # if sale_potentials: # if the second condition is not met, no point in mortgaging
    #     sorted_potentials = sorted(sale_potentials, key=lambda x: x[1])  # sort by mortgage in ascending order
    #     for p in sorted_potentials:
    #         if player.current_cash >= 0:
    #             return (None, flag_config_dict['successful_action']) # we're done
    #
    #         params = dict()
    #         params['player'] = player.player_name
    #         params['asset'] = p[0].name
    #         params['current_gameboard'] = "current_gameboard"
    #         logger.debug(player.player_name + ': I am attempting to sell property '+ p[0].name + ' to the bank')
    #         player.agent._agent_memory['previous_action'] = "sell_property"
    #         return ("sell_property", params)
    #
    # count = 0
    # # if we're STILL not done, then the only option is to start selling houses and hotels from the remaining improved monopolized properties, if we have 'em
    # while (player.num_total_houses > 0 or player.num_total_hotels > 0) and count <3: # often times, a sale may not succeed due to uniformity requirements. We keep trying till everything is sold,
    #     # or cash balance turns non-negative.
    #     count += 1 # there is a slim chance that it is impossible to sell an improvement unless the player does something first (e.g., replace 4 houses with a hotel).
    #     # The count ensures we terminate at some point, regardless.
    #     sorted_assets_list = _set_to_sorted_list_assets(player.assets)
    #
    #     for a in sorted_assets_list:
    #         if a.loc_class == 'real_estate' and a.num_houses > 0:
    #             if player.current_cash >= 0:
    #                 return (None, flag_config_dict['successful_action']) # we're done
    #             flag = True
    #             for same_colored_asset in current_gameboard['color_assets'][a.color]:
    #                 if same_colored_asset == a:
    #                     continue
    #                 if same_colored_asset.num_houses > a.num_houses or a.num_hotels == 1:
    #                     flag = False
    #                     break
    #             if flag:
    #                 params = dict()
    #                 params['player'] = player.player_name
    #                 params['asset'] = a.name
    #                 params['current_gameboard'] = "current_gameboard"
    #                 params['sell_house'] = True
    #                 params['sell_hotel'] = False
    #                 logger.debug(player.player_name+ ': I am attempting to sell house on '+ a.name + ' to the bank')
    #                 player.agent._agent_memory['previous_action'] = "sell_house_hotel"
    #                 return ("sell_house_hotel", params)
    #
    #         elif a.loc_class == 'real_estate' and a.num_hotels > 0:
    #             if player.current_cash >= 0:
    #                 return (None, flag_config_dict['successful_action']) # we're done
    #             flag = True
    #             for same_colored_asset in current_gameboard['color_assets'][a.color]:
    #                 if same_colored_asset == a:
    #                     continue
    #                 if a.num_hotels == 1 and not (same_colored_asset.num_hotels == 1 or (same_colored_asset.num_hotels == 0 and
    #                                         same_colored_asset.num_houses == 0)) : # if there are no hotels on other properties,
    #                     # there must not be houses either, otherwise  the uniform improvement rule gets broken. The not on the
    #                     # outside enforces this rule.
    #                     flag = False
    #                     break
    #                 elif a.num_hotels < same_colored_asset.num_hotels:    # need to follow uniform improvement rule
    #                     flag = False
    #                     break
    #             if flag:
    #                 params = dict()
    #                 params['player'] = player.player_name
    #                 params['asset'] = a.name
    #                 params['current_gameboard'] = "current_gameboard"
    #                 params['sell_house'] = False
    #                 params['sell_hotel'] = True
    #                 logger.debug(player.player_name+ ': I am attempting to sell house on '+ a.name + ' to the bank')
    #                 player.agent._agent_memory['previous_action'] = "sell_house_hotel"
    #                 return ("sell_house_hotel", params)
    #
    # # final straw
    # final_sale_assets = player.assets.copy()
    # sorted_player_assets_list = _set_to_sorted_list_assets(final_sale_assets)
    # for a in sorted_player_assets_list:
    #     if player.current_cash >= 0:
    #         return (None, flag_config_dict['successful_action'])  # we're done
    #     if a.is_mortgaged:
    #         continue
    #     elif a.loc_class=='real_estate' and (a.num_houses>0 or a.num_hotels>0):
    #         continue
    #     params = dict()
    #     params['player'] = player.player_name
    #     params['asset'] = a.name
    #     params['current_gameboard'] = "current_gameboard"
    #     logger.debug(player.player_name + ': I am attempting to sell property '+ a.name + ' to the bank')
    #     player.agent._agent_memory['previous_action'] = "sell_property"
    #     return ("sell_property", params)

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
    ans['make_out_of_turn_move'] =  make_out_of_turn_move
    ans['make_post_roll_move'] = make_post_roll_move
    ans['make_buy_property_decision'] = make_buy_property_decision
    ans['make_bid'] = make_bid
    ans['type'] = "decision_agent_methods"
    return ans


decision_agent_methods = _build_decision_agent_methods_dict() # this is the main data structure that is needed by gameplay
