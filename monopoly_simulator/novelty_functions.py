import logging
logger = logging.getLogger('monopoly_simulator.logging_info.novelty_func')

def alternate_contingency_function_1(player, card, current_gameboard):
    """
    This function has the exact signature as calculate_street_repair_cost.

    Note that this function is being provided as an example. There may be other alternate contingency functions that will
    be written in this file with the exact same syntax but with different logic or values. This function may itself
    undergo changes (but the syntax and function it substitutes will not change).
    :return:
    """
    logger.debug('calculating alternative street repair cost for '+ player.player_name)
    cost_per_house = 70
    cost_per_hotel = 145
    cost = player.num_total_houses * cost_per_house + player.num_total_hotels * cost_per_hotel
    player.charge_player(cost, current_gameboard, bank_flag=True)
    # add to game history
    current_gameboard['history']['function'].append(player.charge_player)
    params = dict()
    params['self'] = player
    params['amount'] = cost
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
