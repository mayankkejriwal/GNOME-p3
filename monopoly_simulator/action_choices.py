import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

file_handler = logging.FileHandler('gameplay_logs.log', mode='a')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def free_mortgage(player, asset, current_gameboard):
    """
    Action for freeing player's mortgage on asset.
    :param player: A Player instance.
    :param asset:  A Location instance that is purchaseable (real estate, railroad or utility). If the asset is not
    purchaseable an Exception will automatically be raised.
    :return: 1 if the player has succeeded in freeing the mortgage on asset, otherwise -1
    """
    logger.debug(player.player_name+' is attempting to free up mortgage on asset '+asset.name)
    if asset.owned_by != player:
        logger.debug(player.player_name+' is trying to free up mortgage on property that is not theirs. Returning -1')
        return -1
    elif asset.is_mortgaged is False or asset not in player.mortgaged_assets:  # the or is unnecessary but serves as a check
        logger.debug(asset.name+'  is not mortgaged to begin with. Returning -1')
        return -1
    elif player.current_cash <= asset.calculate_mortgage_owed(asset, current_gameboard):
        logger.debug(player.player_name+ ' does not have cash to free mortgage on asset '+str(asset.name)+'. Returning -1')
        return -1
    else:
        player.charge_player(asset.calculate_mortgage_owed(asset, current_gameboard))
        logger.debug(player.player_name+"Player has paid down mortgage with interest. Setting status of asset to unmortgaged, and removing asset from player's mortgaged set")
        asset.is_mortgaged = False
        player.mortgaged_assets.remove(asset)
        logger.debug('Mortgage has successfully been freed. Returning 1')
        return 1


def make_sell_property_offer(from_player, asset, to_player, price):
    """
    Action for one player to make an offer to another player to see an asset they possess at an offering price. Note that
    the property is only sold and exchanges hands if to_player invokes accept_sell_property_offer when it is their turn next
    :param from_player: Player instance. The player who is offering to sell.
    :param asset: purchaseable Location instance. The asset on which the offer is being made.
    :param to_player: Player instance. The player to whom the offer is being made.
    :param price: An integer. The price at which from_player is offering to sell asset to to_player
    :return: 1 if the player succeeds in making the offer (doesn't mean the other player has to accept), otherwise -1
    """

    if to_player.is_property_offer_outstanding:
        logger.debug(to_player.player_name+' already has a property offer. You must wait. Returning -1')
        return -1
    elif asset.owned_by != from_player:
        logger.debug(from_player.player_name+'player does not own this property and cannot make an offer. Returning -1')
        return -1
    elif asset.loc_class == 'real_estate' and (asset.num_houses > 0 or asset.num_hotels > 0):
        logger.debug(asset.name+' has improvements. Clear them before making an offer! Returning -1') # note that this entails a risk since you
        # could clear the improvements, and still not get an offer accepted. Decide at your own peril!
        return -1
    else:
        logger.debug('Instantiating data structures outstanding_property_offer and setting is_property_offer_outstanding to True to enable property offer to '+to_player.player_name)
        to_player.outstanding_property_offer['asset'] = asset
        to_player.outstanding_property_offer['from_player'] = from_player
        to_player.outstanding_property_offer['price'] = price
        to_player.is_property_offer_outstanding = True
        logger.debug('Offer has been made.')
        return 1 # offer has been made


def sell_property(player, asset, current_gameboard):
    """
    Action to sell asset to bank. Note that while we allow you to sell mortgaged properties, the bank will deduct what
    it is due before paying you if the property is mortgaged.
    :param player: Player instance. Player who is attempting to sell the property
    :param asset: purchaseable Location instance. The asset to be sold to the bank.
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: 1 if the sale is successful, -1 otherwise.
    """

    if asset.owned_by != player:
        logger.debug(player.player_name+' does not own this property and cannot sell it. Returning -1')
        return -1

    elif asset.loc_class == 'real_estate' and (asset.num_houses > 0 or asset.num_hotels > 0) :
        logger.debug(asset.name+' has improvements. Clear them before trying to sell! Returning -1')
        return -1

    else:
        logger.debug('Transferring property to bank')
        cash_due = asset.transfer_property_to_bank(player, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(asset.transfer_property_to_bank)
        params = dict()
        params['self'] = asset
        params['player'] = player
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(cash_due)

        logger.debug('Transfer successful. Paying player what they are due for the property and returning 1...')
        player.receive_cash(cash_due)
        # add to game history
        current_gameboard['history']['function'].append(player.receive_cash)
        params = dict()
        params['self'] = player
        params['amount'] = cash_due
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        return 1 # property has been successfully sold


def sell_house_hotel(player, asset, current_gameboard, sell_house=True, sell_hotel=False):
    """
    Action for player to see either house or hotel on asset that they own. Note that player can only sell houses or hotels to the bank.
    :param player: Player instance.
    :param asset: RealEstateLocation instance.
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :param sell_house: A boolean. True if player wants to sell a house on asset.
    :param sell_hotel: A boolean. True if player wants to sell a hotel on asset.
    :return: 1 if sale goes through, otherwise -1
    """

    if asset.owned_by != player:
        logger.debug(player.player_name+' does not own this property and cannot make an offer. Returning -1')
        return -1
    elif asset.loc_class != 'real_estate':
        logger.debug(asset.name+' is not real estate. Returning -1')
        return -1
    elif asset.num_hotels == 0 and sell_hotel:
        logger.debug('There are no hotels to sell. Returning -1')
        return -1
    elif asset.num_houses == 0 and sell_house:
        logger.debug('There are no houses to sell. Returning -1')
        return -1

    if sell_hotel: # this is the simpler case
        logger.debug('Looking to sell hotel on '+asset.name)
        flag = True
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if not (same_colored_asset.num_hotels == 1 or (same_colored_asset.num_hotels == 0 and
                                    same_colored_asset.num_houses == 0)) : # if there are no hotels on other properties,
                # there must not be houses either, otherwise  the uniform improvement rule gets broken. The not on the
                # outside enforces this rule.
                flag = False
                break
        if flag:
            logger.debug('Selling hotel and updating num_total_hotels and num_total_houses.')
            player.num_total_hotels -= 1
            logger.debug(player.player_name+' now has num_total_hotels '+str(player.num_total_hotels)+' and num_total_houses '+str(player.num_total_houses))
            logger.debug('Paying player for sale.')
            player.receive_cash((asset.price_per_house*4)/2) # player only gets half the initial cost back. Recall that you can sell the entire hotel or not at all.
            current_gameboard['bank'].total_hotels += 1   #incrementing the bank's total_hotels number since a hotel has been returned.
            # add to game history
            current_gameboard['history']['function'].append(player.receive_cash)
            params = dict()
            params['self'] = player
            params['amount'] = (asset.price_per_house*4)/2
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)

            logger.debug('Updating houses and hotels on the asset')
            asset.num_houses = 0 # this should already be 0 but just in case
            asset.num_hotels = 0
            logger.debug('Player has successfully sold hotel. Returning 1')
            return 1

        else:
            logger.debug('All same-colored properties must stay uniformly improved for you to sell a hotel on this property. ' \
                  'You may need to build hotels on other properties of the same color before attempting to sell this one. Returning -1')
            return -1

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
            logger.debug('Selling house and updating num_total_houses.')
            player.num_total_houses -= 1
            logger.debug(player.player_name+ ' now has num_total_hotels '+ str(
                player.num_total_hotels)+ ' and num_total_houses '+ str(player.num_total_houses))
            logger.debug('Paying player for sale.')
            player.receive_cash(asset.price_per_house/2)
            current_gameboard['bank'].total_houses += 1   #incrementing the bank's total_houses number since a house has been returned.
            # add to game history
            current_gameboard['history']['function'].append(player.receive_cash)
            params = dict()
            params['self'] = player
            params['amount'] = asset.price_per_house/2
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)

            logger.debug('Updating houses and hotels on the asset')
            asset.num_houses -= 1
            logger.debug('Player has successfully sold house. Returning 1')
            return 1

        else:
            logger.debug('All same-colored properties must stay uniformly improved for you to sell a house on this property. ' \
                  'You may need to build houses on other properties of the same color before attempting to sell this one. Returning -1')
            return -1


def accept_sell_property_offer(player, current_gameboard):
    """
    Action for player to decide whether they should accept an outstanding property offer.
    :param player: Player instance. player must decide whether to accept an outstanding property offer. If the offer is accepted,
    we will begin property transfer.
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: 1 if the property offer is accepted and property is successfully transferred, otherwise -1.
    """
    if not player.is_property_offer_outstanding:
        logger.debug(player.player_name+' does not have outstanding property offers to accept. Returning -1')
        return -1
    elif player.current_cash <= player.outstanding_property_offer['price']:
        logger.debug(player.player_name+' does not have the cash necessary to accept. Nulling outstanding property offers data structures and returning -1')
        player.is_property_offer_outstanding = False
        player.outstanding_property_offer['from_player'] = None
        player.outstanding_property_offer['asset'] = None
        player.outstanding_property_offer['price'] = -1
        return -1
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

        logger.debug('Initiating cash transfer from one player to another')
        player.charge_player(player.outstanding_property_offer['price'])
        # add to game history
        current_gameboard['history']['function'].append(player.charge_player)
        params = dict()
        params['self'] = player
        params['amount'] = player.outstanding_property_offer['price']
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        player.outstanding_property_offer['from_player'].receive_cash(player.outstanding_property_offer['price'])
        # add to game history
        current_gameboard['history']['function'].append(player.outstanding_property_offer['from_player'].receive_cash)
        params = dict()
        params['self'] = player.outstanding_property_offer['from_player']
        params['amount'] = player.outstanding_property_offer['price']
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        logger.debug('Transaction successful. Nulling outstanding property offers data structures and returning 1')
        player.is_property_offer_outstanding = False
        player.outstanding_property_offer['from_player'] = None
        player.outstanding_property_offer['asset'] = None
        player.outstanding_property_offer['price'] = -1
        return 1


def skip_turn():
    """
    Use this action when you want to skip the turn i.e. you want to move on without taking any action at all in either
    pre-roll or out-of-turn phases
    :return: 2
    """
    logger.debug('player is skipping turn')
    return 2 # uses special code, since we need it in gameplay


def concluded_actions():
    """
    Use this to conclude a post-roll phase, or to signal that you are done acting in a pre-roll or out-of-turn phase
    if your first action was not skip_turn.
    :return: 1
    """
    logger.debug('player has concluded actions')
    return 1 # does nothing; code is always a success


def mortgage_property(player, asset, current_gameboard):
    """
    Action for player to mortgage asset.
    :param player: Player instance. The player wants to mortgage asset
    :param asset:  Purchaseable Location instance (railroad, utility or real estate).
    :return: 1 if the mortgage has gone through, -1 otherwise.
    """
    if asset.owned_by != player:
        logger.debug(player.player_name+' is trying to mortgage property that is not theirs. Returning -1')
        return -1
    elif asset.is_mortgaged is True or asset in player.mortgaged_assets: # the or is unnecessary but serves as a check
        logger.debug(asset.name+' is already mortgaged to begin with...Returning -1')
        return -1
    elif asset.loc_class == 'real_estate' and (asset.num_houses > 0 or asset.num_hotels > 0):
        logger.debug(asset.name+' has improvements. Remove improvements before attempting mortgage. Returning -1')
        return -1
    else:
        logger.debug("Setting asset to mortgage status and adding to player's mortgaged assets")
        asset.is_mortgaged = True
        player.mortgaged_assets.add(asset)
        player.receive_cash(asset.mortgage)
        # add to game history
        current_gameboard['history']['function'].append(player.receive_cash)
        params = dict()
        params['self'] = player
        params['amount'] = asset.mortgage
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        logger.debug("Property has been mortgaged and player has received cash. Returning 1")
        return 1 # property has been successfully mortgaged


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
    :return: 1 if player has successfully managed to improve property or -1 otherwise.
    """
    if asset.owned_by != player or asset.is_mortgaged:
        # these are the usual conditions that we verify before allowing any improvement to proceed
        logger.debug(player.player_name+' does not own this property, or it is mortgaged. Returning -1')
        return -1
    elif asset.loc_class != 'real_estate':
        logger.debug(asset.name+' is not real estate and cannot be improved. Returning -1')
        return -1
    elif (asset.color not in player.full_color_sets_possessed):

        # these are the usual conditions that we verify before allowing any improvement to proceed
        logger.debug(player.player_name+' does not own all properties of this color, hence it cannot be improved. Returning -1')
        return -1
    elif player.current_cash <= asset.price_per_house:
        logger.debug(player.player_name+ ' cannot afford this improvement. Returning -1')
        return -1

    if add_hotel: # this is the simpler case
        logger.debug('Looking to improve '+asset.name+' by adding a hotel.')
        if asset.num_hotels == 1:
            logger.debug('There is already a hotel here. You are only permitted one. Returning -1')
            return -1
        elif asset.num_houses != 4:
            logger.debug('You need to have four houses before you can build a hotel...Returning -1')
            return -1
        flag = True
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if not (same_colored_asset.num_houses == 4 or same_colored_asset.num_hotels == 1): # as long as all other houses
                # of that color have either 4 houses or a hotel, we can build a hotel on this asset.
                flag = False
                break
        if flag:
            if current_gameboard['bank'].total_hotels > 0:
                logger.debug('Improving asset and updating num_total_hotels and num_total_houses.')
                player.num_total_hotels += 1
                player.num_total_houses -= asset.num_houses
                logger.debug(player.player_name+' now has num_total_hotels '+str(player.num_total_hotels)+' and num_total_houses '+str(player.num_total_houses))
                logger.debug('Charging player for improvements.')
                player.charge_player(asset.price_per_house)
                current_gameboard['bank'].total_hotels -= 1
                current_gameboard['bank'].total_houses += asset.num_houses
                logger.debug('Bank now has ' + str(current_gameboard['bank'].total_houses) + ' houses and ' + str(current_gameboard['bank'].total_hotels) + ' hotels left.')
                # add to game history
                current_gameboard['history']['function'].append(player.charge_player)
                params = dict()
                params['self'] = player
                params['amount'] = asset.price_per_house
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)

                logger.debug('Updating houses and hotels on the asset')
                asset.num_houses = 0
                asset.num_hotels = 1
                logger.debug('Player has successfully improved property. Returning 1')
                return 1

            else:
                logger.debug('Bank has no hotels left for purchase. Kindly wait till someone returns a hotel to the bank.')
                return -1

        else:
            logger.debug('All same-colored properties must be informly improved first before you can build a hotel on this property. Returning -1')
            return -1

    elif add_house:
        logger.debug('Looking to improve '+asset.name+' by adding a house.')
        if asset.num_hotels == 1 or asset.num_houses == 4:
            logger.debug('There is already a hotel or 4 houses here. You are not permitted another house. Returning -1')
            return -1
        flag = True
        current_asset_num_houses = asset.num_houses
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if same_colored_asset.num_houses < current_asset_num_houses or same_colored_asset.num_hotels == 1:
                flag = False
                break
        if flag:
            if current_gameboard['bank'].total_houses > 0:
                logger.debug('Improving asset and updating num_total_houses.')
                player.num_total_houses += 1
                logger.debug(player.player_name+ ' now has num_total_hotels '+ str(
                    player.num_total_hotels)+ ' and num_total_houses '+ str(player.num_total_houses))
                logger.debug('Charging player for improvements.')
                player.charge_player(asset.price_per_house)
                current_gameboard['bank'].total_houses -= 1
                logger.debug('Bank now has ' + str(current_gameboard['bank'].total_houses) + ' houses and ' + str(current_gameboard['bank'].total_hotels) + ' hotels left.')
                # add to game history
                current_gameboard['history']['function'].append(player.charge_player)
                params = dict()
                params['self'] = player
                params['amount'] = asset.price_per_house
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)

                logger.debug('Updating houses and hotels on the asset')
                asset.num_houses += 1
                logger.debug('Player has successfully improved property. Returning 1')
                return 1

            else:
                logger.debug('Bank has no houses left for purchase. Kindly wait till someone returns a house to the bank.')
                return -1

        else:
            logger.debug('All same-colored properties must be informly improved first before you can build a hotel on this property. Returning -1')
            return -1


def use_get_out_of_jail_card(player, current_gameboard):
    """
    Function for player to use a get_out_of_jail_free card.
    :param player: Player instance. Player who is trying to use get_out_of_jail_card. We give first preference to the
    card that is drawn from the chance pack, assuming the player has both cards.
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: 1 if the player has successfully used get out of jail card, or -1 otherwise.
    """
    import copy
    if not player.currently_in_jail:
        logger.debug('Player is not currently in jail and cannot use the card. Returning -1')
        return -1  # simple check. note that player will still have the card(s)

    if player.has_get_out_of_jail_chance_card:  # we give first preference to chance, then community chest
        logger.debug('Player has get_out_of_jail_chance card. Removing card and setting player jail status to False')
        player.has_get_out_of_jail_chance_card = False
        player.currently_in_jail = False
        logger.debug('Adding the card back again to the chance pack.')
        current_gameboard['chance_cards'].add(
            copy.deepcopy(current_gameboard['chance_card_objects']['get_out_of_jail_free']))
        logger.debug('Returning 1')
        return 1
    elif player.has_get_out_of_jail_community_chest_card:
        logger.debug('Player has get_out_of_jail_community_chest card. Removing card and setting player jail status to False')
        player.has_get_out_of_jail_community_chest_card = False
        player.currently_in_jail = False
        logger.debug('Adding the card back again to the community chest pack.')
        current_gameboard['community_chest_cards'].add(
            copy.deepcopy(current_gameboard['community_chest_card_objects']['get_out_of_jail_free']))
        logger.debug('Returning 1')
        return 1
    else:
        logger.debug('Player does not possess a get_out_of_jail free card! Returning -1')
        return -1


def pay_jail_fine(player, current_gameboard):
    """
    If you don't have enough cash, you'll stay in jail. Otherwise, the fine will be charged and you will be out of jail.
    :param player: Player instance.
    :return: 1 if the fine payment succeeds, otherwise -1
    """
    if player.current_cash >= 50 and player.currently_in_jail:
        player.charge_player(50)
        # add to game history
        current_gameboard['history']['function'].append(player.charge_player)
        params = dict()
        params['self'] = player
        params['amount'] = 50
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        logger.debug('Player has been charged the fine. Setting currently_in_status to False and returning 1')
        player.currently_in_jail = False
        return 1
    else:
        logger.debug("Either you are not in jail, or you don't have the cash for the fine. Returning -1")
        return -1


def roll_die(die_objects, choice):
    """
    The function takes a vector of Dice objects and for each object, samples a value. It returns a list of sampled die values.
    :param die_objects: A vector of Dice objects.
    :param choice: The numpy choice function.
    :return:
    """
    logger.debug('rolling die...')
    output_vector = list()
    for d in die_objects:
        if d.die_state_distribution == 'uniform':
            output_vector.append(choice(a=d.die_state))
        elif d.die_state_distribution == 'biased':
            output_vector.append(_biased_die_roll_1(d.die_state, choice))
        else:
            logger.error("Exception")

    return output_vector


def buy_property(player, asset, current_gameboard):
    """
    Action for player to buy asset from bank. Player must also have enough cash for the asset. Note that if the asset
    does not belong to the bank, the only way currently for player to buy it is if the owner offers to sell it
    and the player accepts the offer.
    :param player: Player instance. The player wants to buy asset
    :param asset: Purchaseable Location instance (railroad, utility or real estate). The asset must currently be owned by the bank
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: 1 if player has succeeded in buying the property, -1 if either the player has failed OR if the property ended
    up going to auction (in the latter case, the player may still succeed in obtaining the asset!)
    """
    if asset.owned_by != current_gameboard['bank']:
        logger.debug(asset.name+' is not owned by Bank! Resetting option_to_buy for player and returning code -1')
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        return -1

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

        logger.debug(asset.name+ ' is going up for auction since '+ player.player_name+ ' does not have enough cash to purchase this property. Conducting auction and returning -1')
        current_gameboard['bank'].auction(starting_player_index, current_gameboard, asset)
        # add to game history
        current_gameboard['history']['function'].append(current_gameboard['bank'].auction)
        params = dict()
        params['self'] = current_gameboard['bank']
        params['starting_player_index'] = starting_player_index
        params['current_gameboard'] = current_gameboard
        params['asset'] = asset
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        return -1 # this is a -1 even though you may still succeed in buying the property at auction
    else:
        logger.debug('Charging '+player.player_name+ ' amount '+str(asset.price)+' for asset '+asset.name)
        player.charge_player(asset.price)
        # add to game history
        current_gameboard['history']['function'].append(player.charge_player)
        params = dict()
        params['self'] = player
        params['amount'] = asset.price
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        asset.update_asset_owner(player, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(asset.update_asset_owner)
        params = dict()
        params['self'] = asset
        params['player'] = player
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        logger.debug(asset.name+ ' ownership has been updated! Resetting option_to_buy for player and returning code 1')
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        return 1

def _biased_die_roll_1(die_state, choice):
    p = list()
    die_total = sum(die_state)
    logger.debug ("die_tot"+str(die_total))
    logger.debug (die_state)
    for i in die_state:
        p.append(i*1.0/die_total)
    return choice(a=die_state, p=p)



