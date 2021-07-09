from monopoly_simulator.flag_config import flag_config_dict
from monopoly_simulator.bank import Bank
from monopoly_simulator.dice import Dice
from monopoly_simulator.location import Location
# from monopoly_simulator.novelty_functions_v3 import *
import sys

import logging
logger = logging.getLogger('monopoly_simulator.logging_info.action_choices')


def free_mortgage(player, asset, current_gameboard):
    """
    Action for freeing player's mortgage on asset.
    :param player: A Player instance.
    :param asset:  A Location instance that is purchaseable (real estate, railroad or utility). If the asset is not
    purchaseable an Exception will automatically be raised.
    :return: successful action code if the player has succeeded in freeing the mortgage on asset, otherwise failure code
    """
    logger.debug(player.player_name+' is attempting to free up mortgage on asset '+asset.name)
    if asset.owned_by != player:
        logger.debug(player.player_name+' is trying to free up mortgage on property that is not theirs. Returning failure code')
        return flag_config_dict['failure_code']
    elif asset.is_mortgaged is False or asset not in player.mortgaged_assets:  # the or is unnecessary but serves as a check
        logger.debug(asset.name+'  is not mortgaged to begin with. Returning failure code')
        return flag_config_dict['failure_code']
    elif player.current_cash <= asset.calculate_mortgage_owed(asset, current_gameboard):
        logger.debug(player.player_name+ ' does not have cash to free mortgage on asset '+str(asset.name)+'. Returning failure code')
        return flag_config_dict['failure_code']
    else:
        player.charge_player(asset.calculate_mortgage_owed(asset, current_gameboard), current_gameboard, bank_flag=True)  # 交钱赎回典押资产
        logger.debug(player.player_name+"Player has paid down mortgage with interest. Setting status of asset to unmortgaged, and removing asset from player's mortgaged set")
        asset.is_mortgaged = False
        player.mortgaged_assets.remove(asset)
        logger.debug('Mortgage has successfully been freed. Returning successful action code')
        return flag_config_dict['successful_action']


def make_sell_property_offer(from_player, asset, to_player, price):
    """
    Action for one player to make an offer to another player to see an asset they possess at an offering price. Note that
    the property is only sold and exchanges hands if to_player invokes accept_sell_property_offer when it is their turn next
    :param from_player: Player instance. The player who is offering to sell.
    :param asset: purchaseable Location instance. The asset on which the offer is being made.
    :param to_player: Player instance. The player to whom the offer is being made.
    :param price: An integer. The price at which from_player is offering to sell asset to to_player
    :return: successful action code if the player succeeds in making the offer (doesn't mean the other player has to accept), otherwise failure code
    """

    if to_player.is_property_offer_outstanding:
        logger.debug(to_player.player_name+' already has a property offer. You must wait. Returning failure code')
        return flag_config_dict['failure_code']
    elif asset.owned_by != from_player:
        logger.debug(from_player.player_name+'player does not own this property and cannot make an offer. Returning failure code')
        return flag_config_dict['failure_code']
    elif asset.loc_class == 'real_estate' and (asset.num_houses > 0 or asset.num_hotels > 0):
        logger.debug(asset.name+' has improvements. Clear them before making an offer! Returning failure code') # note that this entails a risk since you
        # could clear the improvements, and still not get an offer accepted. Decide at your own peril!
        return flag_config_dict['failure_code']
    else:
        logger.debug('Instantiating data structures outstanding_property_offer and setting is_property_offer_outstanding to True to enable property offer to '+to_player.player_name)
        to_player.outstanding_property_offer['asset'] = asset
        to_player.outstanding_property_offer['from_player'] = from_player
        to_player.outstanding_property_offer['price'] = price
        to_player.is_property_offer_outstanding = True
        logger.debug('Offer has been made.')

        return flag_config_dict['successful_action'] # offer has been made


def sell_property(player, asset, current_gameboard):
    """
    Action to sell asset to bank. Note that while we allow you to sell mortgaged properties, the bank will deduct what
    it is due before paying you if the property is mortgaged.
    :param player: Player instance. Player who is attempting to sell the property
    :param asset: purchaseable Location instance. The asset to be sold to the bank.
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: successful action code if the sale is successful, failure code otherwise.
    """

    if asset.owned_by != player:
        logger.debug(player.player_name+' does not own this property and cannot sell it. Returning failure code')
        return flag_config_dict['failure_code']

    elif asset.loc_class == 'real_estate' and (asset.num_houses > 0 or asset.num_hotels > 0) :
        logger.debug(asset.name+' has improvements. Clear them before trying to sell! Returning failure code')
        return flag_config_dict['failure_code']

    else:
        logger.debug('Trying to transfer property to bank')
        cash_due = asset.transfer_property_to_bank(player, current_gameboard)
        if cash_due == flag_config_dict['failure_code']:
            logger.debug("Unable to transfer property to Bank. Bank unable to buy back player's property due to insufficient funds!!")
            return flag_config_dict['failure_code']
        else:
            # add to game history
            current_gameboard['history']['function'].append(asset.transfer_property_to_bank)
            params = dict()
            params['self'] = asset
            params['player'] = player
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(cash_due)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            logger.debug('Transfer successful. Paying player what they are due for the property and returning successful action code...')
            code = player.receive_cash(cash_due, current_gameboard, bank_flag=True)
            # add to game history
            if code == flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(player.receive_cash)
                params = dict()
                params['self'] = player
                params['amount'] = cash_due
                params['description'] = 'sell property'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
                return flag_config_dict['successful_action']     # property has been successfully sold
            else:
                logger.debug("Not sure what happened! Something broke although bank had sufficient funds !")
                logger.error("Exception")
                raise Exception


def sell_house_hotel(player, asset, current_gameboard, sell_house=True, sell_hotel=False):
    """
    Action for player to see either house or hotel on asset that they own. Note that player can only sell houses or hotels to the bank.
    :param player: Player instance.
    :param asset: RealEstateLocation instance.
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :param sell_house: A boolean. True if player wants to sell a house on asset.
    :param sell_hotel: A boolean. True if player wants to sell a hotel on asset.
    :return: successful action code if sale goes through, otherwise failure code
    """

    if asset.owned_by != player:
        logger.debug(player.player_name+' does not own this property and cannot make an offer. Returning failure code')
        return flag_config_dict['failure_code']
    elif asset.loc_class != 'real_estate':
        logger.debug(asset.name+' is not real estate. Returning failure code')
        return flag_config_dict['failure_code']
    elif asset.num_hotels == 0 and sell_hotel:
        logger.debug('There are no hotels to sell. Returning failure code')
        return flag_config_dict['failure_code']
    elif asset.num_houses == 0 and sell_house:
        logger.debug('There are no houses to sell. Returning failure code')
        return flag_config_dict['failure_code']

    if sell_hotel: # this is the simpler case
        logger.debug('Looking to sell hotel on '+asset.name)
        flag = True
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if asset.num_hotels == 1 and not (same_colored_asset.num_hotels == 1 or (same_colored_asset.num_hotels == 0 and
                                    same_colored_asset.num_houses == 0)) : # if there are no hotels on other properties,
                # there must not be houses either, otherwise  the uniform improvement rule gets broken. The not on the
                # outside enforces this rule.
                flag = False
                break
            elif asset.num_hotels < same_colored_asset.num_hotels:    # need to follow uniform improvement rule
                flag = False
                break

        if flag:
            logger.debug('Trying to sell a hotel to the bank')
            code = player.receive_cash((asset.price_per_house*(current_gameboard['bank'].house_limit_before_hotel + 1))*current_gameboard['bank'].hotel_sell_percentage, current_gameboard, bank_flag=True) # player only gets half the initial cost back. Recall that you can sell the entire hotel or not at all.
            if code == flag_config_dict['successful_action']:
                logger.debug('Bank Paid player for sale of hotel.')
                logger.debug('Transferring hotel to bank and updating num_total_hotels and num_total_houses.')
                player.num_total_hotels -= 1
                logger.debug(player.player_name+' now has num_total_hotels '+str(player.num_total_hotels)+' and num_total_houses '+str(player.num_total_houses))

                current_gameboard['bank'].total_hotels += 1   #incrementing the bank's total_hotels number since a hotel has been returned.
                # add to game history
                current_gameboard['history']['function'].append(player.receive_cash)
                params = dict()
                params['self'] = player
                params['amount'] = (asset.price_per_house*(current_gameboard['bank'].house_limit_before_hotel + 1))*current_gameboard['bank'].hotel_sell_percentage   # changed hardcoded value to a bank parameter
                params['description'] = 'sell improvements'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                logger.debug('Updating houses and hotels on the asset')
                asset.num_houses = 0 # this should already be 0 but just in case
                asset.num_hotels -= 1
                logger.debug('Player has successfully sold hotel. Returning 1')
                return flag_config_dict['successful_action']

            elif code == flag_config_dict['failure_code']:
                logger.debug('Tried selling hotel to bank, but bank rejected it because it had no sufficient funds to pay me. Unable to currently sell hotel.')
                return flag_config_dict['failure_code']

        else:
            logger.debug('All same-colored properties must stay uniformly improved for you to sell a hotel on this property. ' \
                  'You may need to build hotels on other properties of the same color before attempting to sell this one. Returning failure code')
            return flag_config_dict['failure_code']

    elif sell_house:
        logger.debug('Looking to sell house on '+ asset.name)
        flag = True
        current_asset_num_houses = asset.num_houses
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if same_colored_asset.num_houses > current_asset_num_houses or same_colored_asset.num_hotels == 1:
                flag = False
                break
        if flag:
            logger.debug('Trying to sell a house to the bank')
            code = player.receive_cash(asset.price_per_house*current_gameboard['bank'].house_sell_percentage, current_gameboard, bank_flag=True)
            if code == flag_config_dict['successful_action']:
                logger.debug('Bank Paid player for sale of house.')
                logger.debug('Transferring house to bank and updating num_total_houses.')
                player.num_total_houses -= 1
                logger.debug(player.player_name+ ' now has num_total_hotels '+ str(
                    player.num_total_hotels)+ ' and num_total_houses '+ str(player.num_total_houses))

                current_gameboard['bank'].total_houses += 1   #incrementing the bank's total_houses number since a house has been returned.
                # add to game history
                current_gameboard['history']['function'].append(player.receive_cash)
                params = dict()
                params['self'] = player
                params['amount'] = asset.price_per_house * current_gameboard['bank'].house_sell_percentage    # changed hardcoded value to a bank parameter
                params['description'] = 'sell improvements'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                logger.debug('Updating houses and hotels on the asset')
                asset.num_houses -= 1
                logger.debug('Player has successfully sold house. Returning successful action code')
                return flag_config_dict['successful_action']

            elif code == flag_config_dict['failure_code']:
                logger.debug('Tried selling house to bank, but bank rejected it because it had no sufficient funds to pay me. Unable to currently sell house.')
                return flag_config_dict['failure_code']

        else:
            logger.debug('All same-colored properties must stay uniformly improved for you to sell a house on this property. ' \
                  'You may need to build houses on other properties of the same color before attempting to sell this one. Returning failure code')
            return flag_config_dict['failure_code']

    else:
        #should never reach here unless both sell_house and sell_hotel are False, if it does then return failure code.
        logger.debug("Dont know how I reached here but I didnot succeed in selling house/hotel. Returning failure code.")
        return flag_config_dict['failure_code']


def accept_sell_property_offer(player, current_gameboard):
    """
    Action for player to decide whether they should accept an outstanding property offer.
    :param player: Player instance. player must decide whether to accept an outstanding property offer. If the offer is accepted,
    we will begin property transfer.
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: successful action code if the property offer is accepted and property is successfully transferred, otherwise failure code.
    """
    if not player.is_property_offer_outstanding:
        logger.debug(player.player_name+' does not have outstanding property offers to accept. Returning failure code')
        return flag_config_dict['failure_code']
    elif player.current_cash <= player.outstanding_property_offer['price']:
        logger.debug(player.player_name+' does not have the cash necessary to accept. Nulling outstanding property offers data structures and returning failure code')
        player.is_property_offer_outstanding = False
        player.outstanding_property_offer['from_player'] = None
        player.outstanding_property_offer['asset'] = None
        player.outstanding_property_offer['price'] = flag_config_dict['failure_code']
        return flag_config_dict['failure_code']
    else:
        logger.debug('Initiating property transfer...')
        func_asset = player.outstanding_property_offer['asset']
        func = func_asset.transfer_property_between_players
        func(player.outstanding_property_offer['from_player'],
                           player, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(func)
        params = dict()
        params['self'] = func_asset
        params['from_player'] = player.outstanding_property_offer['from_player']
        params['to_player'] = player
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        logger.debug('Initiating cash transfer from one player to another')
        player.charge_player(player.outstanding_property_offer['price'], current_gameboard, bank_flag=False)
        # add to game history
        current_gameboard['history']['function'].append(player.charge_player)
        params = dict()
        params['self'] = player
        params['amount'] = player.outstanding_property_offer['price']
        params['description'] = 'accept sell property offer'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        code = player.outstanding_property_offer['from_player'].receive_cash(player.outstanding_property_offer['price'], current_gameboard, bank_flag=False)
        # add to game history
        if code == flag_config_dict['successful_action']:
            current_gameboard['history']['function'].append(player.outstanding_property_offer['from_player'].receive_cash)
            params = dict()
            params['self'] = player.outstanding_property_offer['from_player']
            params['amount'] = player.outstanding_property_offer['price']
            params['description'] = 'sell property'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(code)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        else:
            logger.debug("Not sure what happened! Something broke!")
            logger.error("Exception")
            raise Exception

        logger.debug('Transaction successful. Nulling outstanding property offers data structures and returning successful action code')
        player.is_property_offer_outstanding = False
        player.outstanding_property_offer['from_player'] = None
        player.outstanding_property_offer['asset'] = None
        player.outstanding_property_offer['price'] = flag_config_dict['failure_code']
        return flag_config_dict['successful_action']


def skip_turn():
    """
    Use this action when you want to skip the turn i.e. you want to move on without taking any action at all in either
    pre-roll or out-of-turn phases
    :return: 2
    """
    logger.debug('player is skipping turn')
    return flag_config_dict['skip_turn'] # uses special code, since we need it in gameplay


def concluded_actions():
    """
    Use this to conclude a post-roll phase, or to signal that you are done acting in a pre-roll or out-of-turn phase
    if your first action was not skip_turn.
    :return: successful action code
    """
    logger.debug('player has concluded actions')
    return flag_config_dict['successful_action'] # does nothing; code is always a success


def mortgage_property(player, asset, current_gameboard):
    """
    Action for player to mortgage asset.
    :param player: Player instance. The player wants to mortgage asset
    :param asset:  Purchaseable Location instance (railroad, utility or real estate).
    :return: successful action code if the mortgage has gone through, failure code otherwise.
    """
    if asset.owned_by != player:
        logger.debug(player.player_name+' is trying to mortgage property that is not theirs. Returning failure code')
        return flag_config_dict['failure_code']
    elif asset.is_mortgaged is True or asset in player.mortgaged_assets: # the or is unnecessary but serves as a check
        logger.debug(asset.name+' is already mortgaged to begin with...Returning failure code')
        return flag_config_dict['failure_code']
    elif asset.loc_class == 'real_estate' and (asset.num_houses > 0 or asset.num_hotels > 0):
        logger.debug(asset.name+' has improvements. Remove improvements before attempting mortgage. Returning failure code')
        return flag_config_dict['failure_code']
    else:
        if current_gameboard['bank'].total_cash_with_bank >= asset.mortgage:   # i.e. bank has enough money to the player mortgage
            logger.debug("Setting asset to mortgage status and adding to player's mortgaged assets")
            asset.is_mortgaged = True
            player.mortgaged_assets.add(asset)
            code = player.receive_cash(asset.mortgage, current_gameboard, bank_flag=True)
            # add to game history
            if code == flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(player.receive_cash)
                params = dict()
                params['self'] = player
                params['amount'] = asset.mortgage
                params['description'] = 'mortgage property'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                logger.debug("Property has been mortgaged and player has received cash. Returning successful action code")
                return flag_config_dict['successful_action'] # property has been successfully mortgaged

            else:
                logger.debug("Not sure what happened! Something broke although bank had sufficient funds !")
                logger.error("Exception")
                raise Exception

        else:
            logger.debug('Bank didnot have sufficient funds to pay player. Hence could not mortgage player\'s property.')
            return flag_config_dict['failure_code']


def improve_property(player, asset, current_gameboard, add_house=True, add_hotel=False):
    """
    Function for improving asset belonging to player by adding house or hotel.
    Another thing to remember is that once you add a hotel, it stands as its own unit. If you decide to sell, you'll
    have to sell the entire hotel or not at all.
    :param player: Player instance. The player who is attempting to improve an asset by building houses or hotels.
    :param asset: RealEstateLocation instance.
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :param add_house: A Boolean. True if you want to add a house to asset.
    :param add_hotel: A Boolean. True if you want to add a hotel to asset.
    :return: successful action code if player has successfully managed to improve property or failure code otherwise.
    """
    if asset.owned_by != player or asset.is_mortgaged:
        # these are the usual conditions that we verify before allowing any improvement to proceed
        logger.debug(player.player_name+' does not own this property, or it is mortgaged. Returning failure code')
        return flag_config_dict['failure_code']
    elif asset.loc_class != 'real_estate':
        logger.debug(asset.name+' is not real estate and cannot be improved. Returning failure code')
        return flag_config_dict['failure_code']
    elif asset.color not in player.full_color_sets_possessed:
        # these are the usual conditions that we verify before allowing any improvement to proceed
        logger.debug(player.player_name+' does not own all properties of this color, hence it cannot be improved. Returning failure code')
        return flag_config_dict['failure_code']
    elif player.current_cash <= asset.price_per_house:
        logger.debug(player.player_name+ ' cannot afford this improvement. Returning failure code')
        return flag_config_dict['failure_code']

    if add_hotel: # this is the simpler case
        logger.debug('Looking to improve '+asset.name+' by adding a hotel.')
        if asset.num_hotels == current_gameboard['bank'].hotel_limit:
            logger.debug('There is already ' + str(current_gameboard['bank'].hotel_limit) + ' hotel(s) here. You cannot exceed this limit. Returning failure code')
            return flag_config_dict['failure_code']
        elif asset.num_hotels == 0 and asset.num_houses != current_gameboard['bank'].house_limit_before_hotel:
            logger.debug('You need to have ' + str(current_gameboard['bank'].house_limit_before_hotel)
                         + ' houses before you can build a hotel...Returning failure code')
            return flag_config_dict['failure_code']
        flag = True
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if asset.num_hotels == 0 and not (same_colored_asset.num_houses == current_gameboard['bank'].house_limit_before_hotel
                    or same_colored_asset.num_hotels == 1): # as long as all other houses
                # of that color have either max limit of houses before hotel can be built or a hotel, we can build a hotel on this asset. (Uniform improvement rule)
                flag = False
                break
            elif same_colored_asset.num_hotels < asset.num_hotels:
                flag = False
                break
        if flag:
            if current_gameboard['bank'].improvement_possible(player, asset, current_gameboard, add_house=False, add_hotel=True):
                logger.debug('Improving asset and updating num_total_hotels and num_total_houses. Currently property has ' + str(asset.num_hotels))
                player.num_total_hotels += 1
                player.num_total_houses -= asset.num_houses
                logger.debug(player.player_name+' now has num_total_hotels '+str(player.num_total_hotels)+' and num_total_houses '+str(player.num_total_houses))
                logger.debug('Charging player for improvements.')
                player.charge_player(asset.price_per_house, current_gameboard, bank_flag=True)
                current_gameboard['bank'].total_hotels -= 1
                current_gameboard['bank'].total_houses += asset.num_houses
                logger.debug('Bank now has ' + str(current_gameboard['bank'].total_houses) + ' houses and ' + str(current_gameboard['bank'].total_hotels) + ' hotels left.')
                # add to game history
                current_gameboard['history']['function'].append(player.charge_player)
                params = dict()
                params['self'] = player
                params['amount'] = asset.price_per_house
                params['description'] = 'improvements'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                logger.debug('Updating houses and hotels on the asset')
                asset.num_houses = 0
                asset.num_hotels += 1
                logger.debug('Player has successfully improved property. Returning successful action code')
                return flag_config_dict['successful_action']

            else:
                logger.debug('Bank has no hotels left for purchase. Kindly wait till someone returns a hotel to the bank.')
                return flag_config_dict['failure_code']

        else:
            logger.debug('All same-colored properties must be uniformly improved first before you can build a hotel on this property. Returning failure code')
            return flag_config_dict['failure_code']

    elif add_house:
        logger.debug('Looking to improve '+asset.name+' by adding a house. Currently property has ' + str(asset.num_houses))
        if asset.num_hotels > 0 or asset.num_houses == current_gameboard['bank'].house_limit_before_hotel:
            logger.debug('There is already a hotel here or you have built the max number of houses that you can on a property. '
                         'You are not permitted another house. Returning failure code')
            return flag_config_dict['failure_code']
        flag = True
        current_asset_num_houses = asset.num_houses
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if same_colored_asset.num_houses < current_asset_num_houses or same_colored_asset.num_hotels > 0:
                flag = False
                break
        if flag:
            if current_gameboard['bank'].improvement_possible(player, asset, current_gameboard, add_house=True, add_hotel=False):
                logger.debug('Improving asset and updating num_total_houses.')
                player.num_total_houses += 1
                logger.debug(player.player_name+ ' now has num_total_hotels '+ str(
                    player.num_total_hotels)+ ' and num_total_houses '+ str(player.num_total_houses))
                logger.debug('Charging player for improvements.')
                player.charge_player(asset.price_per_house, current_gameboard, bank_flag=True)
                current_gameboard['bank'].total_houses -= 1
                logger.debug('Bank now has ' + str(current_gameboard['bank'].total_houses) + ' houses and ' + str(current_gameboard['bank'].total_hotels) + ' hotels left.')
                # add to game history
                current_gameboard['history']['function'].append(player.charge_player)
                params = dict()
                params['self'] = player
                params['amount'] = asset.price_per_house
                params['description'] = 'improvements'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                logger.debug('Updating houses and hotels on the asset')
                asset.num_houses += 1
                logger.debug('Player has successfully improved property. Returning successful action code')
                return flag_config_dict['successful_action']

            else:
                logger.debug('Bank has no houses left for purchase. Kindly wait till someone returns a house to the bank.')
                return flag_config_dict['failure_code']

        else:
            logger.debug('All same-colored properties must be uniformly improved first before you can build a house on this property. Returning failure code')
            return flag_config_dict['failure_code']

    else:
        #ideally should never reach here, but if it does, then return failure code.
        logger.debug("Didnot succeed in improving house/hotel. Returning failure code.")
        return flag_config_dict['failure_code']


def use_get_out_of_jail_card(player, current_gameboard):
    """
    Function for player to use a get_out_of_jail_free card.
    :param player: Player instance. Player who is trying to use get_out_of_jail_card. We give first preference to the
    card that is drawn from the chance pack, assuming the player has both cards.
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: successful action code if the player has successfully used get out of jail card, or failure code otherwise.
    """
    import copy
    if not player.currently_in_jail:
        logger.debug('Player is not currently in jail and cannot use the card. Returning failure code')
        return flag_config_dict['failure_code']  # simple check. note that player will still have the card(s)

    if player.has_get_out_of_jail_chance_card:  # we give first preference to chance, then community chest
        logger.debug('Player has get_out_of_jail_chance card. Removing card and setting player jail status to False')
        player.has_get_out_of_jail_chance_card = False
        player.currently_in_jail = False
        logger.debug('Adding the card back again to the chance pack.')
        current_gameboard['chance_cards'].add(
            copy.deepcopy(current_gameboard['chance_card_objects']['get_out_of_jail_free']))
        logger.debug('Returning successful action code')
        return flag_config_dict['successful_action']
    elif player.has_get_out_of_jail_community_chest_card:
        logger.debug('Player has get_out_of_jail_community_chest card. Removing card and setting player jail status to False')
        player.has_get_out_of_jail_community_chest_card = False
        player.currently_in_jail = False
        logger.debug('Adding the card back again to the community chest pack.')
        current_gameboard['community_chest_cards'].add(
            copy.deepcopy(current_gameboard['community_chest_card_objects']['get_out_of_jail_free']))
        logger.debug('Returning successful action code')
        return flag_config_dict['successful_action']
    else:
        logger.debug('Player does not possess a get_out_of_jail free card! Returning failure code')
        return flag_config_dict['failure_code']


def pay_jail_fine(player, current_gameboard):
    """
    If you don't have enough cash, you'll stay in jail. Otherwise, the fine will be charged and you will be out of jail.
    :param player: Player instance.
    :return: successful action code if the fine payment succeeds, otherwise failure code
    """
    if player.current_cash >= current_gameboard['bank'].jail_fine and player.currently_in_jail:
        player.charge_player(current_gameboard['bank'].jail_fine, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(player.charge_player)
        params = dict()
        params['self'] = player
        params['amount'] = current_gameboard['bank'].jail_fine
        params['description'] = 'jail fine'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        logger.debug('Player has been charged the fine. Setting currently_in_status to False and returning successful action code')
        player.currently_in_jail = False
        return flag_config_dict['successful_action']
    else:
        logger.debug("Either you are not in jail, or you don't have the cash for the fine. Returning failure code")
        return flag_config_dict['failure_code']


def roll_die(die_objects, choice, current_gameboard):
    """
    The function takes a vector of Dice objects and for each object, samples a value. It returns a list of sampled die values.
    :param die_objects: A vector of Dice objects.
    :param choice: The numpy choice function.
    :return: the numbers that get rolled on the dice as a list.
    """
    logger.debug('rolling die...')
    output_vector = list()
    for d in die_objects:
        if d.die_state_distribution == 'uniform':
            output_vector.append(choice(a=d.die_state))
        elif d.die_state_distribution == 'biased':
            output_vector.append(Dice.biased_die_roll(d.die_state, choice))
        else:
            logger.error("Exception")
            raise Exception

    return output_vector


def buy_property(player, asset, current_gameboard):
    """
    Action for player to buy asset from bank. Player must also have enough cash for the asset. Note that if the asset
    does not belong to the bank, the only way currently for player to buy it is if the owner offers to sell it
    and the player accepts the offer.
    :param player: Player instance. The player wants to buy asset
    :param asset: Purchaseable Location instance (railroad, utility or real estate). The asset must currently be owned by the bank
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: successful action code if player has succeeded in buying the property, failure code if either the player has failed OR if the property ended
    up going to auction (in the latter case, the player may still succeed in obtaining the asset!)
    """
    if asset.owned_by != current_gameboard['bank']:
        logger.debug(asset.name+' is not owned by Bank! Resetting option_to_buy for player and returning code failure code')
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return flag_config_dict['failure_code']

    if player.current_cash < asset.price:
        # property has to go up for auction.
        index_current_player = current_gameboard['players'].index(player)  # in players, find the index of the current player
        starting_player_index = (index_current_player + 1) % len(current_gameboard['players'])  # the next player's index. this player will start the auction
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        logger.debug(asset.name+ ' is going up for auction since '+ player.player_name+ ' does not have enough cash to purchase this property. Conducting auction and returning failure code')
        Bank.auction(starting_player_index, current_gameboard, asset)
        # add to game history
        current_gameboard['history']['function'].append(Bank.auction)
        params = dict()
        params['self'] = current_gameboard['bank']
        params['starting_player_index'] = starting_player_index
        params['current_gameboard'] = current_gameboard
        params['asset'] = asset
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return flag_config_dict['failure_code'] # this is a failure code even though you may still succeed in buying the property at auction
    else:
        logger.debug('Charging '+player.player_name+ ' amount '+str(asset.price)+' for asset '+asset.name)
        player.charge_player(asset.price, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(player.charge_player)
        params = dict()
        params['self'] = player
        params['amount'] = asset.price
        params['description'] = 'buy property'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        asset.update_asset_owner(player, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(asset.update_asset_owner)
        params = dict()
        params['self'] = asset
        params['player'] = player
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        logger.debug(asset.name+ ' ownership has been updated! Resetting option_to_buy for player and returning code successful action code')
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return flag_config_dict['successful_action']


def make_trade_offer(from_player, offer, to_player, current_gameboard=None):
    """
    Action for one player to make a trade offer to another player to trade cash or properties or both. Note that
    the trade is processed only if to_player invokes accept_trade_offer when it is their turn next.
    :param from_player: Player instance. The player who is offering to make the trade offer.
    :param offer: a dictionary with the trade requirements  - property_set_offered, property_set_wanted, cash_offered, cash_wanted
    :param to_player: Player instance. The player to whom the offer is being made.
    :return: successful action code if the player succeeds in making the offer (doesn't mean the other player has to accept), otherwise failure code
    make_trade_offer becomes unsuccessful if:
    - the player to whom the trade offer is being made already has an existing trade offer or
    - if negative cash amounts are involved in the offer or
    - if ownership of the properties are incorrect or
    - if the properties involved in the trade are improved.
    - if the properties involved in the trade are mortgaged.
    """
    if to_player.status == 'lost':
        logger.debug("Trade offer is being made to a player who has lost the game already! Returning failure code.")
        return flag_config_dict['failure_code']

    if to_player.is_trade_offer_outstanding:
        logger.debug(to_player.player_name+' already has a trade offer. You must wait. Returning failure code')
        return flag_config_dict['failure_code']

    elif offer['cash_offered']<0 or offer['cash_wanted']<0:
        logger.debug('Cash offered or cash wanted amounts cannot be negative. Only positive amounts allowed. Returning failure code')
        return flag_config_dict['failure_code']

    else:
        logger.debug('Instantiating data structures outstanding_trade_offer and setting is_trade_offer_outstanding to True to enable trade offer to '+to_player.player_name)
        offer_prop_set = set()
        if len(offer['property_set_offered'])==0:
            logger.debug(from_player.player_name + ' has no properties to offer to ' + to_player.player_name)
        else:
            for item in offer['property_set_offered']:
                if item.owned_by != from_player:
                    logger.debug(from_player.player_name+' player does not own ' + item.name +' . Hence cannot make an offer on this property. Returning failure code.')
                    return flag_config_dict['failure_code']
                elif item.loc_class == 'real_estate' and (item.num_houses > 0 or item.num_hotels > 0):
                    logger.debug(item.name+' has improvements. Clear them before making an offer! Returning failure code.')
                    return flag_config_dict['failure_code']
                elif (item.loc_class == 'real_estate' or item.loc_class == 'railroad' or item.loc_class == 'utility') and item.is_mortgaged:
                    logger.debug(item.name+' is mortgaged. Cannot make an offer on mortgaged properties! Returning failure code.')
                    return flag_config_dict['failure_code']
                else:
                    offer_prop_set.add(item)
            logger.debug(from_player.player_name + ' wants to offer properties to ' + to_player.player_name + ' for cash = ' + str(offer['cash_wanted']))
        to_player.outstanding_trade_offer['property_set_offered'] = offer_prop_set

        want_prop_set = set()
        if len(offer['property_set_wanted'])==0:
            logger.debug(from_player.player_name + ' wants no properties from ' + to_player.player_name)
        else:
            for item in offer['property_set_wanted']:
                if item.owned_by != to_player:
                    logger.debug(to_player.player_name+' player does not own ' + item.name +'. Invalid property requested. Returning failure code.')
                    return flag_config_dict['failure_code']
                elif item.loc_class == 'real_estate' and (item.num_houses > 0 or item.num_hotels > 0):
                    logger.debug(item.name+' has improvements. Can request for unimproved properties only. Returning failure code.')
                    return flag_config_dict['failure_code']
                elif (item.loc_class == 'real_estate' or item.loc_class == 'railroad' or item.loc_class == 'utility') and item.is_mortgaged:
                    logger.debug(item.name+' is mortgaged. Cannot request mortgaged properties from other players! Returning failure code.')
                    return flag_config_dict['failure_code']
                else:
                    want_prop_set.add(item)
            logger.debug(from_player.player_name + ' wants properties from ' + to_player.player_name + ' by offering cash = ' + str(offer['cash_offered']))
        to_player.outstanding_trade_offer['property_set_wanted'] = want_prop_set

        to_player.outstanding_trade_offer['cash_offered'] = offer['cash_offered']
        to_player.outstanding_trade_offer['cash_wanted'] = offer['cash_wanted']
        to_player.outstanding_trade_offer['from_player'] = from_player
        to_player.is_trade_offer_outstanding = True
        logger.debug('Offer has been made.')
        return flag_config_dict['successful_action'] # offer has been made


def accept_trade_offer(player, current_gameboard):
    """
    Action for player to decide whether they should accept an outstanding trade offer.
    :param player: Player instance. player must decide whether to accept an outstanding trade offer. If the offer is accepted,
    we will begin property and cash transfers.
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: successful action code if the property offer is accepted and property is successfully transferred, otherwise failure code.
    accept_trade_offer becomes unsuccessful if:
    - player has no outstanding_trade_offer
    - if player does not have enough cash required for the transaction
    - if ownership of properties are incorrect
    - if the properties involved in the trade are improved.
    - if the properties involved in the trade are mortgaged.
    """
    if player.outstanding_trade_offer['from_player'].status == 'lost':
        logger.debug("I have an outstanding trade offer that was made to me by a player that has lost the game! Cannot process trade offer. Returning failure code.")
        return flag_config_dict['failure_code']

    if not player.is_trade_offer_outstanding:
        logger.debug(player.player_name+' does not have outstanding trade offers to accept. Returning failure code')
        return flag_config_dict['failure_code']

    else:
        flag_cash_wanted = 0
        flag_cash_offered = 1
        flag_properties_offered = 1
        flag_properties_wanted = 1
        if player.outstanding_trade_offer['cash_wanted']<player.current_cash:
            flag_cash_wanted = 1
        for item in player.outstanding_trade_offer['property_set_wanted']:
            if item.owned_by != player:
                flag_properties_wanted = 0
                logger.debug(player.player_name+ ' doesnot own ' + item.name + '. Cannot accept sell trade offer.')
                break
            elif item.loc_class == 'real_estate' and (item.num_houses > 0 or item.num_hotels > 0):
                logger.debug(item.name+' has improvements. Cannot accept sell trade offer. Returning failure code.')
                flag_properties_wanted = 0
                break
            elif (item.loc_class == 'real_estate' or item.loc_class == 'railroad' or item.loc_class == 'utility') and item.is_mortgaged:
                logger.debug(item.name+' is mortgaged. Cannot accept sell trade offer! Returning failure code.')
                flag_properties_wanted = 0
                break
        for item in player.outstanding_trade_offer['property_set_offered']:
            if item.owned_by != player.outstanding_trade_offer['from_player']:
                flag_properties_offered = 0
                logger.debug(player.outstanding_trade_offer['from_player'].player_name+ ' doesnot own ' + item.name + '. Cannot accept sell trade offer.')
                break
            elif item.loc_class == 'real_estate' and (item.num_houses > 0 or item.num_hotels > 0):
                logger.debug(item.name+' has improvements. Cannot accept sell trade offer. Returning failure code.')
                flag_properties_offered = 0
                break
            elif (item.loc_class == 'real_estate' or item.loc_class == 'railroad' or item.loc_class == 'utility') and item.is_mortgaged:
                logger.debug(item.name+' is mortgaged. Cannot accept sell trade offer! Returning failure code.')
                flag_properties_offered = 0
                break
        if flag_cash_offered and flag_cash_wanted and flag_properties_offered and flag_properties_wanted:
            logger.debug('Initiating trade offer transfer...')
            for item in player.outstanding_trade_offer['property_set_offered']:
                func_asset = item
                func = func_asset.transfer_property_between_players
                func(player.outstanding_trade_offer['from_player'], player, current_gameboard)
                # add to game history
                current_gameboard['history']['function'].append(func)
                params = dict()
                params['self'] = func_asset
                params['from_player'] = player.outstanding_trade_offer['from_player']
                params['to_player'] = player
                params['current_gameboard'] = current_gameboard
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            for item in player.outstanding_trade_offer['property_set_wanted']:
                func_asset = item
                func = func_asset.transfer_property_between_players
                func(player, player.outstanding_trade_offer['from_player'], current_gameboard)
                # add to game history
                current_gameboard['history']['function'].append(func)
                params = dict()
                params['self'] = func_asset
                params['from_player'] = player
                params['to_player'] = player.outstanding_trade_offer['from_player']
                params['current_gameboard'] = current_gameboard
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            player.charge_player(player.outstanding_trade_offer['cash_wanted'], current_gameboard, bank_flag=False)
            current_gameboard['history']['function'].append(player.charge_player)
            params = dict()
            params['self'] = player
            params['amount'] = player.outstanding_trade_offer['cash_wanted']
            params['description'] = 'trade'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            code = player.outstanding_trade_offer['from_player'].receive_cash(player.outstanding_trade_offer['cash_wanted'], current_gameboard, bank_flag=False)
            if code == flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(player.outstanding_trade_offer['from_player'].receive_cash)
                params = dict()
                params['self'] = player.outstanding_trade_offer['from_player']
                params['amount'] = player.outstanding_trade_offer['cash_wanted']
                params['description'] = 'trade'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            code = player.receive_cash(player.outstanding_trade_offer['cash_offered'], current_gameboard, bank_flag=False)
            if code == flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(player.receive_cash)
                params = dict()
                params['self'] = player
                params['amount'] = player.outstanding_trade_offer['cash_offered']
                params['description'] = 'trade'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            player.outstanding_trade_offer['from_player'].charge_player(player.outstanding_trade_offer['cash_offered'], current_gameboard, bank_flag=False)
            current_gameboard['history']['function'].append(player.outstanding_trade_offer['from_player'].charge_player)
            params = dict()
            params['self'] = player.outstanding_trade_offer['from_player']
            params['amount'] = player.outstanding_trade_offer['cash_offered']
            params['description'] = 'trade'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            logger.debug('Transaction successful. Nulling outstanding trade offers data structures and returning successful action code')
            player.is_trade_offer_outstanding = False
            player.outstanding_trade_offer['from_player'] = None
            player.outstanding_trade_offer['property_set_offered'] = set()
            player.outstanding_trade_offer['property_set_wanted'] = set()
            player.outstanding_trade_offer['cash_wanted'] = 0
            player.outstanding_trade_offer['cash_offered'] = 0
            return flag_config_dict['successful_action']

        else:
            logger.debug('Transaction unsuccessful. Trade offer could not be accepted. Nulling outstanding trade offers data structures and returning failure code')
            player.is_trade_offer_outstanding = False
            player.outstanding_trade_offer['from_player'] = None
            player.outstanding_trade_offer['property_set_offered'] = set()
            player.outstanding_trade_offer['property_set_wanted'] = set()
            player.outstanding_trade_offer['cash_wanted'] = 0
            player.outstanding_trade_offer['cash_offered'] = 0
            return flag_config_dict['failure_code']


def pre_roll_arbitrary_action(from_player=None, to_player=None, action_params_dict=None, current_gameboard=None):
    """
    1. init (default --> placed in intialize_game_elements.py -->init_arbitrary_action())
    2. action choice func def
    3. add action into compute allowable actions
    4. agent calls the action with schema printing
    ### move to_player to action_params_dict dictionary
    """
    if action_params_dict is not None and 'location' in action_params_dict:
        if isinstance(action_params_dict['location'], Location):
            print("Hi, I am on location: " + action_params_dict['location'].name)



def out_of_turn_arbitrary_action(from_player=None, to_player=None, action_params_dict=None, current_gameboard=None):
    pass


def post_roll_arbitrary_action(from_player=None, to_player=None, action_params_dict=None, current_gameboard=None):
    """
    Example:
        from_player='Player_4'
        param['action_params_dict'] = {location: 'Connecticut Avenue', 'installment_interest': 0.15,
                                        'down_payment': 10, 'num_rounds': 3}
        the _populate_param_dict func in player.py will automatically find the corresponding location instance of str 'Connecticut Avenue',
        and replace the location name to the instance
        action_params_dict = {'location': <monopoly_simulator.location.RealEstateLocation object at 0x7fa2dcf076d8>,
                            'installment_interest': 0.15, 'down_payment': 10, 'num_rounds': 3}
        We'll first check location name has been transferred to location instance, make sure the location is a real estate
        or railroad, also Player_4 is physically in the location position, and the location is owned bank. We then need to
        make sure the down_payment is lower than location's price, else the installments will be negative.

        Before paying the down payment, the last thing is to make sure this mortgage purchase hasn't been conducted by Player_4.

        The player will then be charged the down_payment, we will obtain a log shows 'Player_4 paid fee for mortgage to
                                                                                    purchase property down payment: 10,
                                                                                    the full price of the asset is: 120.0'
        120 is the full price of 'Connecticut Avenue'.

        The ownership of Connecticut Avenue will be updated, Player_4 becomes the owner of Connecticut Avenue but the property
        is in the 'is_mortgaged' status until Player_4 finished the 3-round installments.

        The 'is_mortgaged' status cannot be freed by common free_mortgage func, if the player is trying to free it by free_mortgage,
        we will have the log like 'This action choice cannot be invoked. Returning failure code.'

        After paying down payment, when Player_4 passes go, 42.166666 will be charged (120(full price) - 10(down_payment))
                                                                                        / 3 (num_rounds) * (1 + 0.15 (installment_interest))
        This charge action will be invoked 3 (num_rounds) rounds unless the game ended early, Player_4 did not have chance to pass go.

        If Player_4 successfully paying off the loan after 3 rounds (passes go three times), Connecticut Avenue will be
         removed from Player_4's mortgaged_assets.

    """
    if 'mortgage_buy_property' in current_gameboard:
        if 'mortgage_buy_property_installments' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['mortgage_buy_property_installments'] = dict()
        if isinstance(action_params_dict['location'], Location):
            if action_params_dict['location'].loc_class == 'real_estate' or action_params_dict['location'].loc_class == 'railroad':
                asset = action_params_dict['location']
                # check player on property
                if current_gameboard['location_sequence'][from_player.current_position] != asset:
                    logger.debug(
                        from_player.player_name + ' is not physically on ' + asset.name + ' position, Resetting option_to_buy for player and returning code failure code')
                    from_player.reset_option_to_buy()
                    # add to game history
                    current_gameboard['history']['function'].append(from_player.reset_option_to_buy)
                    params = dict()
                    params['self'] = from_player
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(None)
                    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
                    return flag_config_dict['failure_code']
                # check property belongs to bank
                if asset.owned_by != current_gameboard['bank']:
                    logger.debug(
                        asset.name + ' is not owned by Bank! Resetting option_to_buy for player and returning code failure code')
                    from_player.reset_option_to_buy()
                    # add to game history
                    current_gameboard['history']['function'].append(from_player.reset_option_to_buy)
                    params = dict()
                    params['self'] = from_player
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(None)
                    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                    return flag_config_dict['failure_code']

                # make sure down payment is lower than asset price
                if current_gameboard['mortgage_buy_property']['down_payment'] >= asset.price:
                    logger.debug("Parameter down payment is higher than asset price. Returning failure code")
                    return flag_config_dict['failure_code']
                logger.debug(
                    from_player.player_name + " is trying to mortgage purchase " + asset.name)
                # check whether the action has been conducted
                if asset.name in from_player.agent._agent_memory[
                    'mortgage_buy_property_installments']:
                    logger.debug(asset.name + " mortgage to buy property has been conducted.")
                    return flag_config_dict['failure_code']
                # update mortgage progress (modify down payment and installment interest)
                from_player.agent._agent_memory['mortgage_buy_property_installments'][asset.name] = dict()
                ori_mortgage_percentage = current_gameboard['bank'].mortgage_percentage
                current_gameboard['bank'].mortgage_percentage = current_gameboard['mortgage_buy_property'][
                    'installment_interest']
                ori_mortgage_price = action_params_dict[
                    'location'].mortgage  # modify purchase-mortgage percentage and down-payment
                asset.mortgage = asset.price - current_gameboard['mortgage_buy_property']['down_payment']
                ###
                # charge player and add log to game history
                from_player.charge_player(current_gameboard['mortgage_buy_property']['down_payment'], current_gameboard,
                                          bank_flag=True)
                logger.debug(
                    from_player.player_name + ' paid fee for mortgage to purchase property down payment: ' + str(
                        current_gameboard['mortgage_buy_property'][
                            'down_payment']) + ', the full price of the asset is: ' + str(
                        asset.price))
                current_gameboard['history']['function'].append(from_player.charge_player)
                params = dict()
                params['self'] = from_player
                params['amount'] = current_gameboard['mortgage_buy_property']['down_payment']
                params['description'] = 'mortgage to purchase property down-payment'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
                # update asset owner and add log to game history
                asset.update_asset_owner(from_player, current_gameboard)
                current_gameboard['history']['function'].append(asset.update_asset_owner)
                params = dict()
                params['self'] = asset
                params['player'] = from_player
                params['current_gameboard'] = current_gameboard
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
                logger.debug(
                    asset.name + ' ownership has been updated! Resetting option_to_buy for player and returning code successful action code')
                from_player.reset_option_to_buy()
                current_gameboard['history']['function'].append(from_player.reset_option_to_buy)
                params = dict()
                params['self'] = from_player
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
                # set asset to mortgage status
                if asset.owned_by != from_player:
                    logger.debug(
                        from_player.player_name + ' is trying to mortgage property that is not theirs. Returning failure code')
                    return flag_config_dict['failure_code']
                elif asset.is_mortgaged is True or asset in from_player.mortgaged_assets:  # the or is unnecessary but serves as a check
                    logger.debug(asset.name + ' is already mortgaged to begin with...Returning failure code')
                    return flag_config_dict['failure_code']
                elif asset.loc_class == 'real_estate' and (asset.num_houses > 0 or asset.num_hotels > 0):
                    logger.debug(
                        asset.name + ' has improvements. Remove improvements before attempting mortgage. Returning failure code')
                    return flag_config_dict['failure_code']
                else:
                    logger.debug("Setting asset to mortgage status and adding to player's mortgaged assets")
                    asset.is_mortgaged = True
                    from_player.mortgaged_assets.add(asset)
                    logger.debug(
                        "Property has been mortgaged and player has received cash. Returning successful action code")
                from_player.agent._agent_memory['mortgage_buy_property_installments'][asset.name]['amount_left'] \
                    = asset.calculate_mortgage_owed(asset, current_gameboard)
                from_player.agent._agent_memory['mortgage_buy_property_installments'][asset.name]['num_rounds_left'] \
                    = current_gameboard['mortgage_buy_property']['num_rounds']
                from_player.agent._agent_memory['mortgage_buy_property_installments'][asset.name]['amount_needed_per_round'] \
                    = from_player.agent._agent_memory['mortgage_buy_property_installments'][asset.name]['amount_left'] / \
                      from_player.agent._agent_memory['mortgage_buy_property_installments'][asset.name]['num_rounds_left']
                from_player.agent._agent_memory['mortgage_buy_property_installments'][asset.name]['asset'] = asset

                logger.debug(from_player.player_name + " will be paying mortgage on " + action_params_dict[
                    'location'].name + " in to buy property.")
                # restore mortgage perc for common mortgage and asset's mortgage
                current_gameboard['bank'].mortgage_percentage = ori_mortgage_percentage
                asset.mortgage = ori_mortgage_price

            else:

                logger.debug("Cannot mortgage to buy this property since its not real_estate/railroad.")
                return flag_config_dict['failure_code']
                ###

            # if 'auxiliary_check_for_go' not in current_gameboard:
            #     current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__],
            #                                                           'charge_mortgage_fee_util')
            # action_choices.free_mortgage = getattr(sys.modules[__name__], 'reassign_free_mortgage')
            return flag_config_dict['successful_action']
        else:
            logger.debug("Cannot find the corresponding location instance for the input location name.")
            return flag_config_dict['failure_code']
    else:
        logger.debug("something wrong with novelty injection...")
        raise Exception


def make_arbitrary_interaction(from_player, to_player, interaction_params_dict, current_gameboard):
    """
    Example interaction_params_dict = {'location': 'Pacific Avenue', 'to_location': New York Avenue}
    from_player = Player_2, to_player = Player_3

    The location is an asset owned by from_player (who sends the offer), and to_location is an asset owned by to_player
    (who receives the offer).

    The make_arbitrary_interaction could be called in out_of_turn move and we do not limit the position of offer sender 
    and receiver when the trade happens (i.e., the sender do not need to at 'location' or 'to_location' to send offer,
    and the receiver do not need to at 'location' or 'to_location' to receive offer.)
    
    After the receiver (Player_3 in the example) accepted the offer, each time Player_3 lands on 'Pacific Avenue' or
    Player_2 lands on 'New York Avenue', the rent fee needed to pay will be 0.

    If the receiver reject the offer, the rents don't change.
    :param from_player: 
    :param to_player: 
    :param interaction_params_dict: 
    :param current_gameboard: 
    :return: 
    """
    # set default interaction id
    if 'default_interaction_id' not in current_gameboard:
        current_gameboard['default_interaction_id'] = 0

    # avoid interacting player lost
    if to_player.status == 'lost':
        logger.debug("Free rent offer is being made to a player who has lost the game already! Returning failure code.")
        return flag_config_dict['failure_code']
    logger.debug(f"{from_player.player_name} is trying to send offer to {to_player.player_name}.")
    
    # avoid conduct same interaction contract twice
    if 'free_rent' in to_player.agent._agent_memory and 'free_rent' in from_player.agent._agent_memory:
        for temp_id, item in from_player.agent._agent_memory['free_rent'].items():
            if item['location'] == interaction_params_dict['location'] and \
                    item['to_location'] == interaction_params_dict['to_location'] and \
                    item['to_player'] == to_player:
                logger.debug(f'A same contract exists between {from_player.player_name} and {to_player.player_name}')
                return flag_config_dict['failure_code']
            
    # avoid the sender and receiver are the same player
    if from_player == to_player:
        logger.debug(f'{from_player.player_name} Cannot make interaction offer to itself')
        return action_choices.flag_config_dict['failure_code']
    
    # avoid using other player's or bank's property to make interaction
    if interaction_params_dict['to_location'].owned_by != to_player or \
            interaction_params_dict['location'].owned_by != from_player:
        logger.debug(
            f"{from_player.player_name} did not own {interaction_params_dict['location'].name} to make offer, or"
            f" interaction offer send to wrong player who did not own {interaction_params_dict['to_location'].name}")
        return action_choices.flag_config_dict['failure_code']

    logger.debug(
        f"{from_player.player_name} ask for free rent to {to_player.player_name} on peoperty {interaction_params_dict['to_location'].name}."
        f" If {to_player.player_name} accepts, {to_player.player_name} will also do not need to pay rent on {from_player.player_name}'s property {interaction_params_dict['location'].name}.")
    
    if 'free_rent_interaction' in current_gameboard:  # interaction schema
        if 'free_rent' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['free_rent'] = dict()
        if 'free_rent' not in to_player.agent._agent_memory:
            to_player.agent._agent_memory['free_rent'] = dict()

        # only real_estate could be used in free-rent action
        if interaction_params_dict['location'].loc_class == 'real_estate':
            # from_player has two location info and who is the receiver
            interaction_id = current_gameboard['default_interaction_id']

            from_player.agent._agent_memory['free_rent'][interaction_id] = dict()
            from_player.agent._agent_memory['free_rent'][interaction_id]['location'] = interaction_params_dict[
                'location']
            from_player.agent._agent_memory['free_rent'][interaction_id]['to_location'] = interaction_params_dict[
                'to_location']
            from_player.agent._agent_memory['free_rent'][interaction_id]['to_player'] = to_player

            interaction_params_dict['from_player'] = from_player
            to_player.interaction_dict[interaction_id] = interaction_params_dict

            # increase interaction id for next potential interaction id created by agent
            current_gameboard['default_interaction_id'] += 1
            logger.debug(f'{from_player.player_name} send request to {to_player.player_name} for freeing rent.')

        else:
            logger.debug('Cannot free rent on this location since its not real_estate')
            return action_choices.flag_config_dict['failure_code']

        return flag_config_dict['successful_action']
    else:
        logger.debug('something wrong with novelty injection...')
        raise Exception


def accept_arbitrary_interaction(from_player, to_player, interaction_id, decision, current_gameboard):
    """

    :param player:
    :param interaction_id: Each interaction will associated with a unique id
    :param decision: boolean, true/false --> accept/reject interaction offer
    :param current_gameboard:
    :return:
    """
    if interaction_id not in to_player.interaction_dict:
        logger.debug("Incorrect interaction id")
        return flag_config_dict['failure_code']

    if from_player == to_player:
        logger.debug(f'{to_player} cannot accept/reject offer from itself')
        return flag_config_dict['failure_code']

    if decision:  # if accept the offer

        logger.debug(
            f"{to_player.player_name} accept the offer from {from_player.player_name}. When {to_player.player_name}"
            f" passes {from_player.agent._agent_memory['free_rent'][interaction_id]['location'].name} or "
            f"{from_player.player_name} passes {from_player.agent._agent_memory['free_rent'][interaction_id]['to_location'].name},"
            f" they don't need to pay rent.")
        # to_player has two location info and who is the sender
        to_player.agent._agent_memory['free_rent'][interaction_id] = dict()
        to_player.agent._agent_memory['free_rent'][interaction_id]['from_player'] = from_player
        to_player.agent._agent_memory['free_rent'][interaction_id]['location'] = \
            from_player.agent._agent_memory['free_rent'][interaction_id]['location']
        to_player.agent._agent_memory['free_rent'][interaction_id]['to_location'] = \
            from_player.agent._agent_memory['free_rent'][interaction_id]['to_location']

    if not decision:  # if to_player reject this offer, from_player delete corresponding offer from its memory
        logger.debug(
            f"The offer from {from_player.player_name} to {to_player.player_name} is refused by {to_player.player_name}.")
        del from_player.agent._agent_memory['free_rent'][interaction_id]
        # del to_player.agent._agent_memory['free_rent'][interaction_id]
        # return failure_code

    # if reach here, either accept or reject, remove interaction_id from to_player's interaction_dict
    del to_player.interaction_dict[interaction_id]
    return flag_config_dict['successful_action']


def print_schema(current_gameboard, schema_type=None):
    """
    When an aribitrary action/interaction is available in the simulator, schema that describes the parameters for the action/intercation
    function call will be present in the schema. The agent just has to call the "print_schema" function with the type.
    :param current_gameboard:
    :param schema_type: pre_roll_arbitrary_action, post_roll_arbitrary_action, out_of_turn_arbitrary_action
    :return:
    """
    if schema_type is None:
        logger.debug("Schema type not provided. Returning failure code.")
        return flag_config_dict['failure_code']

    schema = schema_type + "_schema"
    if schema not in current_gameboard:
        # print('schema in not in gameboard')
        logger.debug("Schema of requested type not available...")
        return flag_config_dict['failure_code']
    current_gameboard["schema"] = current_gameboard[schema]
    # print('schema:', current_gameboard["schema"])
    logger.debug("Requested schema info has been made available.")
    return flag_config_dict['successful_action']


def print_pre_roll_arbitrary_action_schema():
    # check location is a real location:
    # if not return -1
    return {'location': 'Location'}
    # dict


def print_post_roll_arbitrary_action_schema():
    return {'location': 'Location', 'num_rounds': 'Rounds', 'installment_interest': 'Perc_of_amount',
            'down_payment': 'Amount'}


def print_out_of_turn_arbitrary_action_schema():
    pass


def print_interaction_arbitrary_action_schema():
    return {'from_player': 'Player1', 'to_player': 'Player2', 'rounds': 'Rounds', 'perc_of_amount': 'Percentage of Amount'}

