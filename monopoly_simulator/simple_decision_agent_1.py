from . import action_choices
from monopoly_simulator.action_choices import *
from monopoly_simulator.location import  RealEstateLocation, UtilityLocation, RailroadLocation
from monopoly_simulator.flag_config import flag_config_dict
import logging
logger = logging.getLogger('monopoly_simulator.logging_info.simple_decision_agent')
"""
All external decision_agent functions must have the exact signatures we have indicated in this document. Beyond
that, we impose no restrictions (you can make the decision agent as complex as you like (including maintaining state), and we use good faith to ensure
you do not manipulate the gameboard. We will have mechanisms to check for inadvertent changes or inconsistencies that
get introduced in the gameboard (due to any reason, including possible subtle errors in the simulator itself) a short
while later.

If you decision agent does maintain state, or some kind of global data structure, please be careful when assigning the
same decision agent (as we do) to each player. We do provide some basic state to you already via 'code' in the make_*_move
functions. Specifically, if code is 1 it means the 'previous' move selected by the player was successful,
and if -1 it means it was unsuccessful. code of -1 is usually returned when an allowable move is invoked with parameters
that preempt the action from happening e.g., the player may decide to mortgage property that is already mortgaged,
which will return the failure code of -1 when the game actually tries to mortgage the property in action_choices.

Be careful to note what each function is supposed to return in addition to adhering to the expected signature. The examples
here are good guides.

Your functions can be called whatever you like, but the keys in decision_agent_methods should not be changed. The
respective functions must adhere in their signatures to the examples here. The agent in this file is very simple, and is
for illustrative purposes only. We describe the logic behind each decision in the respective function.

"""


def make_pre_roll_move(player, current_gameboard, allowable_moves, code):
    """
    The agent is in the pre-roll phase and must decide what to do (next). This simple dummy agent skips the turn, and
     doesn't do anything.
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
    if action_choices.skip_turn in allowable_moves:

        return (action_choices.skip_turn, dict())
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
    if action_choices.skip_turn in allowable_moves:
        return (action_choices.skip_turn, dict())
    else:
        logger.error("Exception")
        raise Exception


def make_post_roll_move(player, current_gameboard, allowable_moves, code):
    """
    The agent is in the post-roll phase and must decide what to do (next). This simple dummy agent buys the property if it
    can afford it, otherwise it skips the turn. If we do buy the property, we end the phase by concluding the turn.

    Note that if your agent decides not to buy the property before concluding the turn, the property will move to
    auction before your turn formally concludes.

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
    if action_choices.buy_property in allowable_moves and current_location.price < player.current_cash:
        logger.debug(player.player_name+': We will attempt to buy '+current_gameboard['location_sequence'][player.current_position].name+' from the bank.')
        if code == -1:
            logger.debug('Did not succeed the last time. Concluding actions...')
            return (action_choices.concluded_actions, dict())
        params = dict()
        params['player'] = player
        params['asset'] = current_gameboard['location_sequence'][player.current_position]
        params['current_gameboard'] = current_gameboard
        return (action_choices.buy_property, params)
    elif action_choices.concluded_actions in allowable_moves:
        return (action_choices.concluded_actions, dict())
    else:
        logger.error("Exception")
        raise Exception


def make_buy_property_decision(player, current_gameboard, asset):
    """
    The decision to be made when the player lands on a location representing a purchaseable asset that is currently
    owned by the bank. The dummy agent here returns True only if its current cash reserves are not less than the
    asset's current price. A more sophisticated agent would consider other features in current_gameboard, including
    whether it would be able to complete the color-set by purchasing the asset etc.
    :param player: A Player instance. You should expect this to be the player that is 'making' the decision (i.e. the player
    instantiated with the functions specified by this decision agent).
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: A Boolean. If True, then you decided to purchase asset from the bank, otherwise False. We allow you to
    purchase the asset even if you don't have enough cash; however, if you do you will end up with a negative
    cash balance and will have to handle that if you don't want to lose the game at the end of your move (see notes
    in handle_negative_cash_balance)
    """
    decision = False
    if player.current_cash >= asset.price:
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
    else:
        return 0 # this agent never bids more than the price of the asset




def handle_negative_cash_balance(player, current_gameboard):
    """
    You have a negative cash balance at the end of your move (i.e. your post-roll phase is over) and you must handle
    this issue before we move to the next player's pre-roll. If you do not succeed in restoring your cash balance to
    0 or positive, bankruptcy proceeds will begin and you will lost the game.

    The dummy agent in this case just decides to go bankrupt by returning -1. A more sophisticated agent would try to
    do things like selling houses and hotels, properties etc. You must invoke all of these functions yourself since
    we want to give you maximum flexibility when you are in this situation. Once done, return 1 if you believe you
    succeeded (see the :return description for a caveat on this)

    :param player: A Player instance. You should expect this to be the player that is 'making' the decision (i.e. the player
    instantiated with the functions specified by this decision agent).
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: -1 if you do not try to address your negative cash balance, or 1 if you tried and believed you succeeded.
    Note that even if you do return 1, we will check to see whether you have non-negative cash balance. The rule of thumb
    is to return 1 as long as you 'try', or -1 if you don't try (in which case you will be declared bankrupt and lose the game)
    """
    return flag_config_dict['failure_code']


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


