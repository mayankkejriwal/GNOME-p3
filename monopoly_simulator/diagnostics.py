import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

#file_handler = logging.FileHandler('gameplay_logs.log', mode='a')
#file_handler.setLevel(logging.DEBUG)
#file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

#logger.addHandler(file_handler)
logger.addHandler(stream_handler)
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



