import logging
logger = logging.getLogger('monopoly_simulator.logging_info.diagnostics')
"""
This file is imported into gameplay and primarily used for printing diagnostics. Expand as necessary for your own
use cases.
"""

def print_asset_owners(game_elements):
    """
    Print a list of all purchaseable assets, and who owns them.
    :param game_elements: A dict. Specifies global gameboard data structure
    :return: None
    """
    for k,v in game_elements['location_objects'].items():
        if v.loc_class == 'railroad' or v.loc_class == 'utility' or v.loc_class == 'real_estate':
            if v.owned_by == game_elements['bank']:
                logger.debug('Owner of '+ k+ ' is bank')
            else:
                logger.debug('Owner of '+ k+ ' is '+v.owned_by.player_name)


def print_player_cash_balances(game_elements):
    """
    Print cash balances of the players. Insert additional code as necessary (e.g., to check if cash balance is
    exceeding a certain amount for some player etc.)
    :param game_elements: A dict. Specifies global gameboard data structure
    :return: None
    """

    for p in game_elements['players']:
        logger.debug(p.player_name+ ' has cash balance '+str(p.current_cash))


def max_cash_balance(game_elements):
    """
    Return the maximum cash balance out of all players
    :param game_elements: A dict. Specifies global gameboard data structure
    :return: An integer. The maximum cash balance out of all players
    """
    max = -1
    for p in game_elements['players']:
        if max < p.current_cash:
            max = p.current_cash
    return max


def print_player_net_worths_and_cash_bal(game_elements):
    """
    Print net worth and cash bal of the players. Calculated by liquidating properties (based on then prices) and adding cash balance.
    :param game_elements: A dict. Specifies global gameboard data structure
    :return: None
    """
    for pl in game_elements['players']:
        networth_p1ayer = 0
        networth_p1ayer += pl.current_cash
        if pl.assets:
            for prop in pl.assets:
                if prop.loc_class == 'real_estate':
                    networth_p1ayer += prop.price
                    networth_p1ayer += prop.num_houses*prop.price_per_house
                    networth_p1ayer += prop.num_hotels*prop.price_per_house*(game_elements['bank'].house_limit_before_hotel + 1)
                elif prop.loc_class == 'railroad':
                    networth_p1ayer += prop.price
                elif prop.loc_class == 'utility':
                    networth_p1ayer += prop.price
        logger.debug(pl.player_name + ' has a cash balance of $' + str(pl.current_cash) + ' and a net worth of $' + str(networth_p1ayer))


def print_player_net_worths(game_elements):
    """
    Print only net worth of the players. Calculated by liquidating properties (based on then prices) and adding cash balance.
    :param game_elements: A dict. Specifies global gameboard data structure
    :return: None
    """
    for pl in game_elements['players']:
        networth_p1ayer = 0
        networth_p1ayer += pl.current_cash
        if pl.assets:
            for prop in pl.assets:
                if prop.loc_class == 'real_estate':
                    networth_p1ayer += prop.price
                    networth_p1ayer += prop.num_houses*prop.price_per_house
                    networth_p1ayer += prop.num_hotels*prop.price_per_house*(game_elements['bank'].house_limit_before_hotel + 1)
                elif prop.loc_class == 'railroad':
                    networth_p1ayer += prop.price
                elif prop.loc_class == 'utility':
                    networth_p1ayer += prop.price
        logger.debug(pl.player_name + ' has a net worth of ' + str(networth_p1ayer))
