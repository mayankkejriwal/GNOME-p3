import numpy as np
from monopoly_simulator.card_utility_actions import _has_player_passed_go, move_player_after_die_roll
from monopoly_simulator.player import Player
from monopoly_simulator.agent import Agent
from monopoly_simulator.bank import Bank
from monopoly_simulator import background_agent_v3_1
from monopoly_simulator.location import RealEstateLocation, TaxLocation
from monopoly_simulator.flag_config import flag_config_dict
from monopoly_simulator import diagnostics
from monopoly_simulator import action_choices
import random
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
    params['description'] = 'Player charged in contingency function.'
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)


def alternate_contingency_function_SR_1(player, card, current_gameboard):
    """
    This function has the exact signature as calculate_street_repair_cost.

    Note that this function is being provided as an example. There may be other alternate contingency functions that will
    be written in this file with the exact same syntax but with different logic or values. This function may itself
    undergo changes (but the syntax and function it substitutes will not change).
    :return:
    """
    # print("inside new contingency SR")
    logger.debug('executing calculate_street_repair_cost for '+ player.player_name)
    cost_per_house = 4500
    cost_per_hotel = 6500
    cost = player.num_total_houses * cost_per_house + player.num_total_hotels * cost_per_hotel
    player.charge_player(cost, current_gameboard, bank_flag=True)
    # add to game history
    current_gameboard['history']['function'].append(player.charge_player)
    params = dict()
    params['self'] = player
    params['amount'] = cost
    params['description'] = 'Player charged in contingency function.'
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)


def alternate_contingency_function_GR_1(player, card, current_gameboard):
    """
    This function has the exact signature as calculate_street_repair_cost.

    Note that this function is being provided as an example. There may be other alternate contingency functions that will
    be written in this file with the exact same syntax but with different logic or values. This function may itself
    undergo changes (but the syntax and function it substitutes will not change).
    :return:
    """
    # print("inside new contingency GR")
    logger.debug('executing calculate_general_repair_cost for ' + player.player_name)
    cost_per_house = 5500
    cost_per_hotel = 5000
    cost = player.num_total_houses * cost_per_house + player.num_total_hotels * cost_per_hotel
    player.charge_player(cost, current_gameboard, bank_flag=True)
    # add to game history
    current_gameboard['history']['function'].append(player.charge_player)
    params = dict()
    params['self'] = player
    params['amount'] = cost
    params['description'] = 'Player charged in contingency function.'
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)


def alternate_auction(starting_player_index, current_gameboard, asset):
    """
    This function will be called when a player lands on a purchaseable property (real estate, railroad or utility)
    but decides not to make the purchase.
    :param starting_player_index:  An integer. The index of the player in current_gameboard['players'] who will be starting the auction
    :param current_gameboard: A dict. Specifies the global game board data structure
    :param asset: A purchaseable instance of Location (i.e. RealEstateLocation, UtilityLocation or RailroadLocation)
    :return: None
    """
    print("inside new auction")
    logger.debug('Entering auctioning for asset '+asset.name)

    current_bid = 0
    players_out_of_auction = set()
    winning_player = None
    bidding_player_index = None

    # Since the starting player may be out of the game, we first check if we should update the starting player
    for p in current_gameboard['players']:
        if p.status == 'lost':
            players_out_of_auction.add(p)
        else:
            logger.debug(p.player_name+' is an auction participant.')

    count = 0
    while count < len(current_gameboard['players']):
        if current_gameboard['players'][starting_player_index] in players_out_of_auction:
            count += 1
            starting_player_index = (starting_player_index+1)%len(current_gameboard['players'])
        else:
            bidding_player_index = starting_player_index
            break

    if bidding_player_index is None: # no one left to auction. This is a failsafe, the code should never get here.
        logger.debug('No one is left in the game that can participate in the auction! Why are we here?')
        return
    else:
        logger.debug(current_gameboard['players'][bidding_player_index].player_name+' will place the first bid')

    while len(players_out_of_auction) < len(current_gameboard['players']): # we iterate and bid till just one player remains
        bidding_player = current_gameboard['players'][bidding_player_index]
        if bidding_player in players_out_of_auction:
            bidding_player_index = (bidding_player_index+1)%len(current_gameboard['players']) # next player
            continue
        proposed_bid = bidding_player.agent.make_bid(bidding_player, current_gameboard,
                            asset, current_bid)
        # add to game history
        current_gameboard['history']['function'].append(bidding_player.agent.make_bid)
        params = dict()
        params['player'] = bidding_player
        params['current_gameboard'] = current_gameboard
        params['asset'] = asset
        params['current_bid'] = current_bid
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(proposed_bid)

        logger.debug(bidding_player.player_name+' proposed bid '+str(proposed_bid))

        if proposed_bid == 0:
            players_out_of_auction.add(bidding_player)
            logger.debug(bidding_player.player_name+' is out of the auction.')
            bidding_player_index = (bidding_player_index + 1) % len(current_gameboard['players'])
            continue
        elif proposed_bid <= current_bid: # the <= serves as a forcing function to ensure the proposed bid must be non-zero
            players_out_of_auction.add(bidding_player)
            logger.debug(bidding_player.player_name+ ' is out of the auction.')
            bidding_player_index = (bidding_player_index + 1) % len(current_gameboard['players'])
            continue

        current_bid = proposed_bid
        logger.debug('The current highest bid is '+str(current_bid)+ ' and is held with '+bidding_player.player_name)
        winning_player = bidding_player
        bidding_player_index = (bidding_player_index + 1) % len(current_gameboard['players'])

    if winning_player:
        winning_player.charge_player(current_bid, current_gameboard, bank_flag=True) # if it got here then current_bid is non-zero.
        # add to game history
        current_gameboard['history']['function'].append(winning_player.charge_player)
        params = dict()
        params['self'] = winning_player
        params['amount'] = current_bid
        params['description'] = 'auction'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        if 'auction_transaction_tax' in current_gameboard and current_gameboard['auction_transaction_tax'] > 0:
            # novelty_code_injection
            winning_player.charge_player(current_gameboard['auction_transaction_tax'], current_gameboard, bank_flag=True)
            # add to game history
            current_gameboard['history']['function'].append(winning_player.charge_player)
            params = dict()
            params['self'] = winning_player
            params['amount'] = current_gameboard['auction_transaction_tax']
            params['description'] = 'auction tax'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)

        asset.update_asset_owner(winning_player, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(asset.update_asset_owner)
        params = dict()
        params['self'] = asset
        params['player'] = winning_player
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
    else:
        logger.debug('Auction did not succeed in a sale.')
    return


def alternate_improvement_possible(self, player, asset, current_gameboard, add_house=True, add_hotel=False):
    # print("inside new improvement possible")

    # novelty_code_injection
    if 'forbidden_improvement_color' in current_gameboard and asset.color in current_gameboard['forbidden_improvement_color']:
        logger.debug('You are trying to improve a property color forbidden under local law. Returning False')
        return False

    if add_hotel and add_house:
        logger.debug("Cant build both a house and a hotel on a property at once!! Raising Exception.")
        raise Exception
    if add_hotel:
        if self.total_hotels > 0:
            return True
    elif add_house:
        if self.total_houses > 0:
            return True


def utility_railroad_taxation(player, new_pos, current_gameboard):
    # print("inside new tax func")

    if 'utility_tax' not in current_gameboard or 'railroad_tax' not in current_gameboard:
        logger.debug("Tax amounts not defined. Raising Exception!")
        raise Exception

    if player.num_utilities_possessed > 0:
        player.charge_player(current_gameboard['utility_tax'], current_gameboard, bank_flag=True)
        logger.debug("Player charged tax on owned utilities while passing Go!")
        current_gameboard['history']['function'].append(player.charge_player)
        params = dict()
        params['self'] = player
        params['amount'] = current_gameboard['utility_tax']
        params['description'] = 'utility tax'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

    if player.num_railroads_possessed > 0:
        player.charge_player(current_gameboard['railroad_tax'], current_gameboard, bank_flag=True)
        logger.debug("Player charged tax on owned railroads while passing Go!")
        current_gameboard['history']['function'].append(player.charge_player)
        params = dict()
        params['self'] = player
        params['amount'] = current_gameboard['railroad_tax']
        params['description'] = 'railroad tax'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)


def net_worth_taxation(player, new_pos, current_gameboard):
    # print("inside wealth tax func")
    if 'wealth_tax' in current_gameboard: # novelty_code_injection
        networth_p1ayer = 0
        networth_p1ayer += player.current_cash
        if player.assets:
            for prop in player.assets:
                if prop.loc_class == 'real_estate':
                    networth_p1ayer += prop.price
                    networth_p1ayer += prop.num_houses * prop.price_per_house
                    networth_p1ayer += prop.num_hotels * prop.price_per_house * 5
                elif prop.loc_class == 'railroad':
                    networth_p1ayer += prop.price
                elif prop.loc_class == 'utility':
                    networth_p1ayer += prop.price
        tax_charged = networth_p1ayer*current_gameboard['wealth_tax']
        player.charge_player(tax_charged, current_gameboard, bank_flag=True)
        logger.debug(player.player_name + ' is being charged a wealth tax '+str(tax_charged)+' for properties owned.')
        current_gameboard['history']['function'].append(player.charge_player)
        params = dict()
        params['self'] = player
        params['amount'] = tax_charged
        params['description'] = 'tax on properties'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)


def random_player_movement(player, rel_move, current_gameboard, check_for_go=True):
    # print("inside random die roll movement")
    if 'die_sig' in current_gameboard and current_gameboard['die_sig'] == 1: # the second condition is unnecessary for now
        dec_num = np.random.rand()
        if dec_num > 0.5: # we won't honor the dice anymore
            rel_move = int(np.random.rand()*len(current_gameboard['location_sequence']))

    logger.debug('executing move_player_after_die_roll for '+player.player_name+' by '+str(rel_move)+' relative steps forward.')
    num_locations = len(current_gameboard['location_sequence'])
    go_position = current_gameboard['go_position']
    go_increment = current_gameboard['go_increment']

    new_position = (player.current_position+rel_move) % num_locations

    if check_for_go:
        if _has_player_passed_go(player.current_position, new_position, go_position):
            if 'auxiliary_check_for_go' in current_gameboard:
                current_gameboard['auxiliary_check_for_go'](player, None, current_gameboard)
            logger.debug(player.player_name+' passes Go.')
            code = player.receive_cash(go_increment, current_gameboard, bank_flag=True)
            # add to game history
            if code == 1:
                current_gameboard['history']['function'].append(player.receive_cash)
                params = dict()
                params['self'] = player
                params['amount'] = go_increment
                params['description'] = 'go increment'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
            else:
                logger.debug('Current cash balance with the bank = '+ str(current_gameboard['bank'].total_cash_with_bank))
                logger.debug("Player supposed to receive go increment, but bank has no sufficient funds, hence unable to pay player." +
                             "Player will have to pass GO position without receiving go increment!")

    player.update_player_position(new_position, current_gameboard)  # update this only after checking for go
    # add to game history
    current_gameboard['history']['function'].append(player.update_player_position)
    params = dict()
    params['self'] = player
    params['new_position'] = new_position
    params['current_gameboard'] = current_gameboard
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)


def decrease_go_increment(player, new_pos, current_gameboard):
    # print("inside decrease go inc func")
    if 'contingent_go' in current_gameboard and current_gameboard['contingent_go'] is True:
        if player.num_total_hotels > 0 or player.num_utilities_possessed > 0 or player.num_railroads_possessed > 0 or len(
                player.mortgaged_assets) > 0:
            player.charge_player(current_gameboard['go_increment'], current_gameboard, bank_flag=True)
            logger.debug("Bank deducted go increment to compensate for the amount that will be received by player.")
            current_gameboard['history']['function'].append(player.charge_player)
            params = dict()
            params['self'] = player
            params['amount'] = current_gameboard['go_increment']
            params['description'] = 'negative go incrmement'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)


def inflation_increment(player, new_pos, current_gameboard):
    # print("inside inflation increment")
    if 'inflation_increment' in current_gameboard and current_gameboard['inflation_increment'] > 0:
        color_count = dict()
        for color, assets in current_gameboard['color_assets'].items():
            if color not in color_count:
                color_count[color] = 0
            for asset in assets:
                if asset.owned_by != current_gameboard['bank']:
                    color_count[color] += 1

        for color, assets in current_gameboard['color_assets'].items():
            if color_count[color] > 0:
                for asset in assets:
                    if asset.owned_by == current_gameboard['bank'] and asset.price < 1500:
                        asset.price += (current_gameboard['inflation_increment']*color_count[color])
                        logger.debug('Bank is inflating price of '+asset.name+' because of demand for its color. New price of property is '+str(asset.price))


def backward_movement(player, rel_move, current_gameboard, check_for_go=True):
    # print("inside back move")
    if 'backward' in current_gameboard and current_gameboard['backward'] is True:
        logger.debug('executing move_player_after_die_roll for ' + player.player_name + ' by ' + str(
            rel_move) + ' relative steps backward.')
    else:
        logger.debug('executing move_player_after_die_roll for '+player.player_name+' by '+str(rel_move)+' relative steps forward.')

    num_locations = len(current_gameboard['location_sequence'])
    go_position = current_gameboard['go_position']
    go_increment = current_gameboard['go_increment']

    if 'backward' in current_gameboard and current_gameboard['backward'] is True:
        new_position = (player.current_position + (num_locations-rel_move)) % num_locations
    else:
        new_position = (player.current_position+rel_move) % num_locations

    if check_for_go:
        if _has_player_passed_go(player.current_position, new_position, go_position):
            if 'auxiliary_check_for_go' in current_gameboard:
                current_gameboard['auxiliary_check_for_go'](player, None, current_gameboard)
            logger.debug(player.player_name+' passes Go.')
            code = player.receive_cash(go_increment, current_gameboard, bank_flag=True)
            # add to game history
            if code == 1:
                current_gameboard['history']['function'].append(player.receive_cash)
                params = dict()
                params['self'] = player
                params['amount'] = go_increment
                params['description'] = 'go increment'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
            else:
                logger.debug('Current cash balance with the bank = '+ str(current_gameboard['bank'].total_cash_with_bank))
                logger.debug("Player supposed to receive go increment, but bank has no sufficient funds, hence unable to pay player." +
                             "Player will have to pass GO position without receiving go increment!")

    player.update_player_position(new_position, current_gameboard)  # update this only after checking for go
    # add to game history
    current_gameboard['history']['function'].append(player.update_player_position)
    params = dict()
    params['self'] = player
    params['new_position'] = new_position
    params['current_gameboard'] = current_gameboard
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)


def multiply_die_roll(player, rel_move, current_gameboard, check_for_go=True):
    # print("inside multiple die roll")
    if 'mult_signal' in current_gameboard and current_gameboard['mult_signal'] is True and 'die_objects' in current_gameboard['history']['param'][-1]:
        rel_move = np.prod(current_gameboard['history']['return'][-1])

    logger.debug('executing move_player_after_die_roll for '+player.player_name+' by '+str(rel_move)+' relative steps forward.')
    num_locations = len(current_gameboard['location_sequence'])
    go_position = current_gameboard['go_position']
    go_increment = current_gameboard['go_increment']

    new_position = (player.current_position+rel_move) % num_locations

    if check_for_go:
        if _has_player_passed_go(player.current_position, new_position, go_position):
            if 'auxiliary_check_for_go' in current_gameboard:
                current_gameboard['auxiliary_check_for_go'](player, None, current_gameboard)
            logger.debug(player.player_name+' passes Go.')
            code = player.receive_cash(go_increment, current_gameboard, bank_flag=True)
            # add to game history
            if code == 1:
                current_gameboard['history']['function'].append(player.receive_cash)
                params = dict()
                params['self'] = player
                params['amount'] = go_increment
                params['description'] = 'go increment'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
            else:
                logger.debug('Current cash balance with the bank = '+ str(current_gameboard['bank'].total_cash_with_bank))
                logger.debug("Player supposed to receive go increment, but bank has no sufficient funds, hence unable to pay player." +
                             "Player will have to pass GO position without receiving go increment!")

    player.update_player_position(new_position, current_gameboard)  # update this only after checking for go
    # add to game history
    current_gameboard['history']['function'].append(player.update_player_position)
    params = dict()
    params['self'] = player
    params['new_position'] = new_position
    params['current_gameboard'] = current_gameboard
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)


# def alternate_calculate_and_pay_rent_dues(self, current_gameboard):
#     print("inside new calc rent")
#
#     current_loc = current_gameboard['location_sequence'][self.current_position]
#     logger.debug('calculating and paying rent dues for '+ self.player_name+ ' who is in property '+current_loc.name+' which is owned by '+current_loc.owned_by.player_name)
#     if 'rent_flag' in current_gameboard:
#         rent = RealEstateLocation.calculate_rent(current_loc, current_gameboard)/current_gameboard['rent_flag']
#     else:
#         rent = RealEstateLocation.calculate_rent(current_loc, current_gameboard)
#     # add to game history
#     current_gameboard['history']['function'].append(RealEstateLocation.calculate_rent)
#     params = dict()
#     params['self'] = current_loc
#     current_gameboard['history']['param'].append(params)
#     current_gameboard['history']['return'].append(rent)
#
#     recipient = current_loc.owned_by
#     code = recipient.receive_cash(rent, current_gameboard, bank_flag=False)
#     # add to game history
#     if code == 1:
#         current_gameboard['history']['function'].append(recipient.receive_cash)
#         params = dict()
#         params['self'] = recipient
#         params['amount'] = rent
#         params['description'] = 'rent'
#         current_gameboard['history']['param'].append(params)
#         current_gameboard['history']['return'].append(None)
#     else:
#         logger.debug("Not sure what happened! Something broke!")
#         logger.error("Exception")
#         raise Exception
#
#     self.charge_player(rent, current_gameboard, bank_flag=False)
#     # add to game history
#     current_gameboard['history']['function'].append(self.charge_player)
#     params = dict()
#     params['self'] = self
#     params['amount'] = rent
#     params['description'] = 'rent'
#     current_gameboard['history']['param'].append(params)
#     current_gameboard['history']['return'].append(None)


def alternate_rent_dues(asset, current_gameboard):
    logger.debug('calculating rent for '+asset.name)
    ans = asset.rent # unimproved-non-monopolized rent (the default)
    if asset.num_hotels == 1:
        logger.debug('property has a hotel. Updating rent.')
        ans = asset.rent_hotel
    elif asset.num_houses > 0: # later we can replace these with reflections
        logger.debug('property has '+str(asset.num_houses)+' houses. Updating rent.')
        ans = asset._house_rent_dict[asset.num_houses] # if for some reason you have more than 4 houses, you'll get a key error
    elif asset.color in asset.owned_by.full_color_sets_possessed:
        ans = asset.rent*current_gameboard['bank'].monopolized_property_rent_factor # charge twice the rent on unimproved monopolized properties.
        logger.debug('property has color '+ asset.color+ ' which is monopolized by '+asset.owned_by.player_name+'. Updating rent.')
    logger.debug('rent is calculated to be '+str(ans))
    if 'rent_flag' in current_gameboard:
        return ans/current_gameboard['rent_flag']
    else:
        return ans


def alternate_railroad_dues(asset, current_gameboard):
    logger.debug('calculating railroad dues for '+asset.name)
    if asset.owned_by.num_railroads_possessed > 4 or asset.owned_by.num_railroads_possessed < 0:
        logger.debug('Error! num railroads possessed by '+ asset.owned_by.player_name+ ' is '+ \
            str(asset.owned_by.num_railroads_possessed)+', which is impossible')

        logger.error("Exception")
        raise Exception
    dues = asset._railroad_dues[asset.owned_by.num_railroads_possessed]

    logger.debug('railroad dues are '+str(dues))
    if 'rent_flag' in current_gameboard:
        return dues/current_gameboard['rent_flag']
    else:
        return dues


def alternate_utility_dues(asset, current_gameboard, die_total):
    logger.debug('calculating utility dues for '+ asset.name)
    if asset.owned_by.num_utilities_possessed > 2 or asset.owned_by.num_utilities_possessed < 0:
            logger.debug('Error! num utilities possessed by '+asset.owned_by.player_name+' is '+ \
                str(asset.owned_by.num_utilities_possessed)+ ', which is impossible')

            logger.error("Exception")
            raise Exception

    dues = die_total*asset._die_multiples[asset.owned_by.num_utilities_possessed]
    logger.debug('utility dues are '+ str(dues))
    if 'rent_flag' in current_gameboard:
        return dues/current_gameboard['rent_flag']
    else:
        return dues


def reassign_failure_code(current_gameboard):
    print("inside new fail code")
    if 'failure_code' in current_gameboard:
        flag_config_dict['failure_code'] = current_gameboard['failure_code']


def property_random_distribution_among_players(current_gameboard):
    print("inside random distribution")
    players = ['player_1','player_2','player_3','player_4']
    player_dict = dict()
    for p in current_gameboard['players']:
        player_dict[p.player_name] = p
    count = 0
    for l in current_gameboard['location_sequence']:
        if l.loc_class == 'real_estate':
            p = player_dict[players[count]]
            l.owned_by = p
            p.assets.add(l)

        if count == 3:
            count = 0
        else:
            count += 1

    for color, assets in current_gameboard['color_assets'].items():
        for p in player_dict.values():
            if len(assets.difference(p.assets)) == 0:
                p.full_color_sets_possessed.add(color)


def mess_player_info(player, current_gameboard, allowable_actions, code):
    player_args = dict()
    player_args['status'] = 'waiting_for_move'
    player_args['current_position'] = current_gameboard['go_position']
    player_args['has_get_out_of_jail_chance_card'] = False
    player_args['has_get_out_of_jail_community_chest_card'] = False
    player_args['current_cash'] = 1500
    player_args['num_railroads_possessed'] = 0
    player_args['num_utilities_possessed'] = 0
    player_args['full_color_sets_possessed'] = set()
    player_args['assets'] = set()
    player_args['currently_in_jail'] = False
    player_args['agent'] = Agent(**background_agent_v3_1.decision_agent_methods)

    players_list = list()

    current_gameboard['reverse_player_mapping_dict'] = current_gameboard['players']

    for pl in current_gameboard['players']:
        if pl != player:
            player_args['player_name'] = pl.player_name
            dummy_player = Player(**player_args)
            players_list.append(dummy_player)
        else:
            players_list.append(player)

    current_gameboard['players'] = players_list


def assign_player_info_back(player, current_gameboard, allowable_actions, code):
    current_gameboard['players'] = current_gameboard['reverse_player_mapping_dict']


def update_asset_owner(self, player, current_gameboard):
    print("inside new func")
    """
    If the asset is non-purchaseable, we will raise an exception. A more elegant way (we'll make this change
    in a close future edition) is to have a PurchaseableLocation class sitting between the purchaseable sub-classes
    like real estate and Location, and to add update_asset_owner as a method of PurchaseableLocation.

    Note that we remove the asset from the previous owner's portfolio if it is not owned by the bank.
    :param player: Player instance. The player who now owns this asset (self)
    :param current_gameboard: A dict. The global gameboard data structure
    :return: None
    """
    logger.debug('attempting to update asset '+ self.name+ ' to reflect new owner: '+ player.player_name)
    if self.loc_class == 'real_estate' or self.loc_class == 'railroad' or self.loc_class == 'utility':
        if self.owned_by == player:
            logger.debug(player.player_name+' already owns this asset! Raising exception...')
            logger.error("Exception")
            raise Exception
        elif type(self.owned_by) != Bank: # not owned by this player or by the bank.
            logger.debug('Asset is owned by '+self.owned_by.player_name+'. Attempting to remove...')
            self.owned_by.remove_asset(self)
            # add to game history
            current_gameboard['history']['function'].append(self.owned_by.remove_asset)
            params = dict()
            params['self'] = self.owned_by
            params['asset'] = self
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)

            self.owned_by = current_gameboard['bank'] # this is temporary, but we want to enforce safe behavior

        self.owned_by = player
        player.add_asset(self, current_gameboard) # if the property is mortgaged, this will get reflected in the new owner's portfolio
        # add to game history
        current_gameboard['history']['function'].append(player.add_asset)
        params = dict()
        params['self'] = player
        params['asset'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        logger.debug('Asset ownership update succeeded.')
    else:
        logger.debug('Asset ',self.name+' is non-purchaseable!')
        logger.error("Exception")
        raise Exception


def pay_jail_visitation_fee(player, new_position, current_gameboard):
    if "jail_visit_fee" not in current_gameboard:
        logger.debug("jail_visit_fee cannot be found in the gameboard, check why?")
        raise Exception

    jail_loc = None
    for p in current_gameboard['location_sequence']:
        if p.name == 'In Jail/Just Visiting':
            jail_loc = p
            break

    jail_visit_flag = False

    jail_position = jail_loc.start_position
    if new_position == jail_position: # we've landed on go
        jail_visit_flag = True

    elif new_position == player.current_position:  # we've gone all round the board
        jail_visit_flag = True

    elif player.current_position < new_position:
        if new_position >= jail_position > player.current_position:
            jail_visit_flag = True

    elif player.current_position > new_position:
        if jail_position > player.current_position or jail_position <= new_position:
            jail_visit_flag = True

    if jail_visit_flag:
        logger.debug(player.player_name + " charged jail visitation fee!")
        player.charge_player(current_gameboard['jail_visit_fee'], current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(player.charge_player)
        params = dict()
        params['self'] = player
        params['amount'] = current_gameboard['jail_visit_fee']
        params['description'] = 'jail visit fee'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)


def charge_compound_interest_on_cash(player, new_position, current_gameboard):
    if "cash_interest_perc" in current_gameboard:
        compound_interest = current_gameboard['cash_interest_perc'] * player.current_cash   # if player has no money or negative cash bal, then compund interest not charged
        if compound_interest > 0:
            logger.debug(player.player_name + " charged compound interest on cash upon passing go!")
            player.charge_player(compound_interest, current_gameboard, bank_flag=True)

            # add to game history
            current_gameboard['history']['function'].append(player.charge_player)
            params = dict()
            params['self'] = player
            params['amount'] = compound_interest
            params['description'] = 'compound_interest on player cash'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)

    else:
        logger.debug("cash_interest_perc cannot be found in the gameboard, check why?")
        raise Exception


def charge_player_when_passing_tax_loc(player, new_position, current_gameboard):
    tax_locations = list()
    for l in current_gameboard['location_sequence']:
        if l.loc_class == 'tax':
            tax_locations.append(l)

    for p in tax_locations:
        tax_flag = False

        tax_position_start = p.start_position

        if new_position == tax_position_start: # we've landed on tax location, no tax deduction
            tax_flag = False                                                        # since process_move_consequence will take of it

        elif new_position == player.current_position:  # we've gone all round the board
            tax_flag = True

        elif player.current_position < new_position:
            if new_position > tax_position_start > player.current_position:
                tax_flag = True

        elif player.current_position > new_position:
            if tax_position_start > player.current_position or tax_position_start < new_position:
                tax_flag = True

        if tax_flag:
            logger.debug(player.player_name + " charged tax when passing tax location.")
            tax_due = TaxLocation.calculate_tax(p, player, current_gameboard)
            player.charge_player(tax_due, current_gameboard, bank_flag=True)
            # add to game history
            current_gameboard['history']['function'].append(player.charge_player)
            params = dict()
            params['self'] = player
            params['amount'] = tax_due
            params['description'] = 'tax'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)


def move_all_players_after_dieroll(player, rel_move, current_gameboard, check_for_go):
    """
    Only the player who rolled the dice gets the go increment, other players are just moved around
    :param player:
    :param rel_move:
    :param current_gameboard:
    :param check_for_go:
    :return:
    """
    # print("inside move all players after die roll")
    logger.debug('executing move_player_after_die_roll for ' + player.player_name + ' by ' + str(rel_move) + ' relative steps forward.')
    num_locations = len(current_gameboard['location_sequence'])
    go_position = current_gameboard['go_position']
    go_increment = current_gameboard['go_increment']

    new_position = (player.current_position+rel_move) % num_locations

    if 'auxiliary_check' in current_gameboard:
        current_gameboard['auxiliary_check'](player, new_position, current_gameboard)

    if check_for_go:
        if _has_player_passed_go(player.current_position, new_position, go_position):
            if 'auxiliary_check_for_go' in current_gameboard:
                current_gameboard['auxiliary_check_for_go'](player, new_position, current_gameboard)
            logger.debug(player.player_name+' passes Go.')
            code = player.receive_cash(go_increment, current_gameboard, bank_flag=True)
            # add to game history
            if code == 1:
                current_gameboard['history']['function'].append(player.receive_cash)
                params = dict()
                params['self'] = player
                params['amount'] = go_increment
                params['description'] = 'go increment'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
            else:
                logger.debug('Current cash balance with the bank = '+ str(current_gameboard['bank'].total_cash_with_bank))
                logger.debug("Player supposed to receive go increment, but bank has no sufficient funds, hence unable to pay player." +
                             "Player will have to pass GO position without receiving go increment!")

    player.update_player_position(new_position, current_gameboard)  # update this only after checking for go
    # add to game history
    current_gameboard['history']['function'].append(player.update_player_position)
    params = dict()
    params['self'] = player
    params['new_position'] = new_position
    params['current_gameboard'] = current_gameboard
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)

    logger.debug("Updating positions of other players.")
    for p in current_gameboard['players']:
        if p != player and p.status != 'lost':
            logger.debug("Updating positions of " + p.player_name)
            p_new_position = (p.current_position+rel_move) % num_locations
            p.update_player_position(p_new_position, current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(p.update_player_position)
            params = dict()
            params['self'] = p
            params['new_position'] = p_new_position
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)


def alternate_check_for_game_termination(current_gameboard, tot_time=70):
    if "die_roll_limit" in current_gameboard:
        if len(current_gameboard['die_sequence'][0]) >= current_gameboard['die_roll_limit']:
            logger.debug("Game reached/exceeded max die roll limit of " + str(len(current_gameboard['die_sequence'][0])) + " ...Terminating game.")
            return True
    elif "time_limit" in current_gameboard:
        if tot_time >= current_gameboard['time_limit']:
            logger.debug("Game reached/exceeded max time limit of " + str(current_gameboard['time_limit']) + " seconds...Terminating game.")
            return True
    else:
        logger.debug("Game termination condition for novelty not specified..")
        raise Exception


def auxiliary_go_tax_on_color_ownership(player, new_position, current_gameboard):
    logger.debug("Deducting color tax upon passing GO for " + player.player_name)
    colors_possessed = set()
    for p in player.assets:
        colors_possessed.add(p.color)
    if None in colors_possessed:
        colors_possessed.remove(None)

    tax_due = 0
    for c in colors_possessed:
        tax_due += current_gameboard['color_tax_dict'][c]

    player.charge_player(tax_due, current_gameboard, bank_flag=True)
    # add to game history
    current_gameboard['history']['function'].append(player.charge_player)
    params = dict()
    params['self'] = player
    params['amount'] = tax_due
    params['description'] = 'color tax'
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)


def avenue_rule_change(player, current_gameboard, allowable_actions, code):
    if player._option_to_buy and "Avenue" in current_gameboard['location_sequence'][player.current_position].name:
        if player.current_cash < current_gameboard['avenue_purchase_cash_limit']:
            logger.debug("Insufficient cash balance to buy an avenue!")
            player._option_to_buy = False    # to prevent location from going into auction if player is unable to buy it
            if 'buy_property' in allowable_actions:
                allowable_actions.remove('buy_property')


def charge_compound_interest_on_mortgage(player, new_position, current_gameboard):
    compound_interest = 0
    if "mortgage_interest_perc" in current_gameboard:
        for m in player.mortgaged_assets:
            compound_interest += current_gameboard['mortgage_interest_perc'] * m.mortgage

        if compound_interest > 0:
            logger.debug(player.player_name + " charged compound interest on mortgage upon passing go!")
            player.charge_player(compound_interest, current_gameboard, bank_flag=True)
            # add to game history
            current_gameboard['history']['function'].append(player.charge_player)
            params = dict()
            params['self'] = player
            params['amount'] = compound_interest
            params['description'] = 'compound interest on player mortgage(s)'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)

    else:
        logger.debug("mortgage_interest_perc cannot be found in the gameboard, check why?")
        raise Exception


def calculate_mortgage_owed_dynamic(mortgaged_property, current_gameboard=None):
    if not mortgaged_property.is_mortgaged:
        logger.error("Exception")
        raise Exception
    else:
        if current_gameboard['bank'].total_mortgage_rule is False:
            player = mortgaged_property.owned_by
            # mortgage_percentage made a function of the number of player's mortgaged assets
            mortgage_perc = (1 + len(player.mortgaged_assets)*current_gameboard['mortgage_dynamic_perc']) * current_gameboard['bank'].mortgage_percentage
                            # 1 + len added so that mortgage_perc doesnot become 0 for first mortgage
                            # if num mortgaged asset = 0, then player not affected by the mortgage_dynamic_perc for the 1st mortgage
            mortgage_owed = (1.0+mortgage_perc) * mortgaged_property.mortgage
            logger.debug("Mortgage owed dynamically adjusted based on number of properties the player has mortgaged.")
            return mortgage_owed
        else:
            # to avoid passing in a player object, I am going to use the owner of the mortgaged_property as the player whose
            # total debt outstanding we have to compute the mortgage against.
            player = mortgaged_property.owned_by
            total = 0
            for a in player.mortgaged_assets:
                total += ((1.0+current_gameboard['bank'].mortgage_percentage)*a.mortgage)
            return total


def calculate_rent_dynamic(player, new_position, current_gameboard):
    logger.debug("Rents increasing!!")
    for l in current_gameboard['location_sequence']:
        if hasattr(l, 'owned_by') and not isinstance(l.owned_by, Bank):
            if l.loc_class == 'railroad':
                for i in [1, 2, 3, 4]:
                    l._railroad_dues[i] *= (1+current_gameboard['rent_dynamic_perc']*0.5)  #without factoring it by 0.5, the value increases to a very high value
            elif l.loc_class == 'utility':
                for i in [1, 2]:
                    l._die_multiples[i] *= (1+current_gameboard['rent_dynamic_perc']*0.5)
            elif l.loc_class == 'real_estate':
                l.rent_1_house *= (1+current_gameboard['rent_dynamic_perc']*0.2)
                l.rent_2_houses *= (1+current_gameboard['rent_dynamic_perc']*0.2)
                l.rent_3_houses *= (1+current_gameboard['rent_dynamic_perc']*0.2)
                l.rent_4_houses *= (1+current_gameboard['rent_dynamic_perc']*0.2)
                l.rent_hotel *= (1+current_gameboard['rent_dynamic_perc']*0.2)
                l.rent *= (1+current_gameboard['rent_dynamic_perc'])
                for i in [1, 2, 3, 4]:
                    l._house_rent_dict[i] *= (1+current_gameboard['rent_dynamic_perc'])


def fork_at_free_parking_func(current_player, rel_move, current_gameboard, check_for_go):
    logger.debug("Forking at free parking!")
    if rel_move % 2 == 0:
        move_player_after_die_roll(current_player, rel_move, current_gameboard, check_for_go)
    else:
        move_player_after_die_roll(current_player, 0, current_gameboard, check_for_go=False)   # player does not move


def ownership_based_tax_func(location, player, current_gameboard):
    """
    When a player lands on a tax location upon die roll, other players are also charged tax.
    Tax for all players are a function of the number properties that they own on that wing of the board (ie the wing on which
    that tax location is).
    This serves the purpose of reducing wealth inequality amongst players.
    Thus a player may own a max of 6 props on a wing(ie own all props on a wing) or none.
    If none, then no tax is charged even if the player is the player who rolled the dice and ended up on the tax location.
    :param location:
    :param player:
    :param current_gameboard:
    :return:
    """
    logger.debug("Remaining players will be now be charged tax!!")
    players_property_dict = dict()
    players_property_dict['player_1'] = list()
    players_property_dict['player_2'] = list()
    players_property_dict['player_3'] = list()
    players_property_dict['player_4'] = list()

    wing_1 = ['Mediterranean Avenue', 'Baltic Avenue', 'Reading Railroad', 'Oriental Avenue', 'Vermont Avenue', 'Connecticut Avenue']
    wing_4 = ['Pacific Avenue', 'North Carolina Avenue', 'Pennsylvania Avenue', 'Short Line', 'Park Place', 'Boardwalk']

    if location.name == 'Income Tax':
        for p in current_gameboard['players']:
            if p.status != 'lost':
                for prop in p.assets:
                    if prop.name in wing_1:
                        players_property_dict[p.player_name].append(prop)
    elif location.name == 'Luxury Tax':
        for p in current_gameboard['players']:
            if p.status != 'lost':
                for prop in p.assets:
                    if prop.name in wing_4:
                        players_property_dict[p.player_name].append(prop)

    for p in current_gameboard['players']:
        if p != player and p.status != 'lost':
            tax_due = (len(players_property_dict[p.player_name]) * current_gameboard['tax_perc']) * location.amount_due
            p.charge_player(tax_due, current_gameboard, bank_flag=True)
            logger.debug(p.player_name + " charged tax based on number of properties that it owns to reduce wealth inequality!")
            # add to game history
            current_gameboard['history']['function'].append(p.charge_player)
            params = dict()
            params['self'] = p
            params['amount'] = tax_due
            params['description'] = 'tax'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)

    # for player who rolled the dice, player gets charged upon return to process_move_consequences, else will be charged twice
    return (len(players_property_dict[player.player_name]) * current_gameboard['tax_perc']) * location.amount_due


def tax_reduces_wealth_inequality_func(location, player, current_gameboard):
    """
    When a player lands on a tax location upon die roll, other players are also charged tax.
    Tax for all players are a function of the number properties that they own on that wing of the board (ie the wing on which
    that tax location is).
    This serves the purpose of reducing wealth inequality amongst players.
    Thus a player may own a max of 6 props on a wing(ie own all props on a wing) or none.
    If none, then no tax is charged even if the player is the player who rolled the dice and ended up on the tax location.
    :param location:
    :param player:
    :param current_gameboard:
    :return:
    """
    logger.debug("All players will be now charged tax according to net worth!!")
    for p in current_gameboard['players']:
        if p != player and p.status != 'lost':
            networth_player = 0
            networth_player += p.current_cash
            if p.assets:
                for prop in p.assets:
                    if prop.loc_class == 'real_estate':
                        networth_player += prop.price
                        networth_player += prop.num_houses*prop.price_per_house
                        networth_player += prop.num_hotels*prop.price_per_house*(current_gameboard['bank'].house_limit_before_hotel + 1)
                    elif prop.loc_class == 'railroad':
                        networth_player += prop.price
                    elif prop.loc_class == 'utility':
                        networth_player += prop.price

            tax_due = networth_player * current_gameboard['tax_perc']
            p.charge_player(tax_due, current_gameboard, bank_flag=True)
            logger.debug(p.player_name + " charged tax based on number of properties that it owns to reduce wealth inequality!")
            # add to game history
            current_gameboard['history']['function'].append(p.charge_player)
            params = dict()
            params['self'] = p
            params['amount'] = tax_due
            params['description'] = 'tax'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)

    networth_player = 0
    networth_player += player.current_cash
    if player.assets:
        for prop in player.assets:
            if prop.loc_class == 'real_estate':
                networth_player += prop.price
                networth_player += prop.num_houses*prop.price_per_house
                networth_player += prop.num_hotels*prop.price_per_house*(current_gameboard['bank'].house_limit_before_hotel + 1)
            elif prop.loc_class == 'railroad':
                networth_player += prop.price
            elif prop.loc_class == 'utility':
                networth_player += prop.price
    # for player who rolled the dice, player gets charged upon return to process_move_consequences, else will be charged twice
    return networth_player * current_gameboard['tax_perc']


def set_send_to_jail_limited(player, current_gameboard):
    """
    This function used in combination with alternate_compute_allowable_post_roll_actions and
    alternate_handle_negative_cash_balance
    :param player:
    :param current_gameboard:
    :return:
    """
    if current_gameboard['jail_times'][player.player_name] > 0:
        current_gameboard['jail_times'][player.player_name] -= 1
        logger.debug("Since player ended up in jail, reducing player jail count for " + player.player_name + ' to ' +
                     str(current_gameboard['jail_times'][player.player_name]))
        player.currently_in_jail = True
    else:
        current_gameboard['jail_limit_player'][player.player_name] = True
        logger.debug(player.player_name + " will have to exit game since player got away without paying jail fine too many times.")
        player.current_cash = -10    # cash made negative so that player will call handle_negative_cash_balance and return -1 and go bankrupt (workaround)

    for p in current_gameboard['players']:
        logger.debug("Status inside "+p.player_name + " " + p.status)


def alternate_pay_jail_fine(player, current_gameboard):
    """
    If you don't have enough cash, you'll stay in jail. Otherwise, the fine will be charged and you will be out of jail.
    If you pay jail fine first time around, the jail limit will not be affected.
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

        current_gameboard['jail_times'][player.player_name] += 1
        logger.debug("Since player agreed to pay jail fine, increasing player jail count for " + player.player_name + " to " +
                     str(current_gameboard['jail_times'][player.player_name]))

        logger.debug('Player has been charged the fine. Setting currently_in_status to False and returning successful action code')
        player.currently_in_jail = False
        return flag_config_dict['successful_action']
    else:
        logger.debug("Either you are not in jail, or you don't have the cash for the fine. Returning failure code")
        return flag_config_dict['failure_code']


def alternate_compute_allowable_post_roll_actions(self, current_gameboard):
    allowable_actions = set()
    if current_gameboard['jail_limit_player'][self.player_name]:
        logger.debug('computing allowable post-roll actions for '+ self.player_name)
        logger.debug('Since player has exceeded jail entry limit, player forced to conclude actions!')
        allowable_actions.add("concluded_actions")
    else:
        logger.debug('computing allowable post-roll actions for '+ self.player_name)
        allowable_actions.add("concluded_actions")

        if self.num_total_hotels > 0 or self.num_total_houses > 0:
            allowable_actions.add("sell_house_hotel")

        if len(self.assets) > 0:
            allowable_actions.add("sell_property")
            if len(self.mortgaged_assets) < len(self.assets):
                allowable_actions.add("mortgage_property")

        if self._option_to_buy is True:
            allowable_actions.add("buy_property")

    return allowable_actions


def alternate_handle_negative_cash_balance(self, current_gameboard):
    """
    This function is called if the player ends up with a negative cash balance. This function prompts the agent's handle_negative_cash_balance()
    function to keep taking moves until the player has a positive cash balance. We have set a limit defined by "successful_tries" so that
    the game does not go on for a very long time trying to save the player. The agent can only take "successful_tries" number of successful actions
    to save its player. Beyond this limit, if the player still has a negative cash balance, the agent cannot do anything more to save the player and
    the function is forced to return.
    A limit is also set on the number of unsuccessful actions that the agent can take defined by "unsuccessful_tries".
    Beyond this limit, if the player still has a negative cash balance, the function is forced to return with a failure code.
    This also ensures that the game doesnot go on for too long trying to execute unsuccessful actions.

    :param current_gameboard: The global gameboard data structure
    :return: 3 return cases:
    - successful action code if the players cash balance > 0
    - successful action code if the player tried its best to save the player by executing actions within the "successful_tries" counter limits
    and is finally forced to return as the counter ran out.
    - failure code if the player decides to quit without even trying and itself returns a failure code.
    - failure code if the player tried to save player by taking unsuccessful actions consecutively till the "unsuccessful_tries" counter runs out.
    """
    if current_gameboard['jail_limit_player'][self.player_name]:
        logger.debug(self.player_name + " forced to leave game as jail exit times without paying jail fine exceeded limits!")
        return action_choices.flag_config_dict['failure_code']

    logger.debug("We are trying to relieve " + self.player_name + " from negative cash balance.")
    code = 0
    unsuccessful_tries = 3
    successful_tries = 10

    if self.current_cash > 0:
        logger.debug(self.player_name + " didnot have negative cash balance, don't know why this function was called!! Raising exception..")
        raise Exception

    while successful_tries > 0:
        action_to_execute, parameters = self.agent.handle_negative_cash_balance(self, current_gameboard)
        t = (action_to_execute, parameters)
        # add to game history
        current_gameboard['history']['function'].append(self.agent.handle_negative_cash_balance)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        if isinstance(code, int):
            code = [code]
        params['code'] = code
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(t)

        if action_to_execute is None:
            return parameters    # done handling negative cash balance, parameters will be an int (successful action code or failure code
                                    # depending on whether the agent successfully relieved the player from negative cash bal or if it decided to quit.)
        else:
            if action_to_execute == "make_trade_offer":
                code = action_choices.flag_config_dict['failure_code']
                logger.debug("Cannot make a trade offer while handling negative cash balance!!!")
            else:
                action_to_execute_temp = Player._resolve_function_names_to_pointers(action_to_execute, self, current_gameboard)
                parameters_temp = Player._populate_param_dict(parameters, self, current_gameboard)
                code = self._execute_action(action_to_execute_temp, parameters_temp, current_gameboard)
                logger.debug('Received code '+ str(code)+ '. Continuing iteration...')

            successful_tries -= 1
            if code == action_choices.flag_config_dict['failure_code']:
                successful_tries += 1
                unsuccessful_tries -= 1
                logger.debug(self.player_name + ' has executed an unsuccessful handle negative cash balance action.')
            if unsuccessful_tries == 0:
                if self.current_cash > 0:    # should never enter this 'if loop' since action was unsuccessful, but just in case....
                    return action_choices.flag_config_dict['successful_action']
                logger.debug(self.player_name + " has exceeded unsuccessful action limits to handle negative cash balance. Returning failure code.")
                return action_choices.flag_config_dict['failure_code']

    # reaches here only after 10 successful tries and the player still has negative cash balance.
    # Returns successful action code since the agent atleast tried to save the player but couldn't. Remaining checks on whether cash bal is > 0 or not
    # is again checked for in gameplay.py
    return action_choices.flag_config_dict['successful_action']


def alternate_update_asset_owner(self, player, current_gameboard):
    logger.debug('attempting to update asset '+ self.name+ ' to reflect new owner: '+ player.player_name)
    if self.loc_class == 'real_estate' or self.loc_class == 'railroad' or self.loc_class == 'utility':
        if self.owned_by == player:
            logger.debug(player.player_name+' already owns this asset! Raising exception...')
            logger.error("Exception")
            raise Exception
        elif type(self.owned_by) != Bank: # not owned by this player or by the bank.
            logger.debug('Asset is owned by '+self.owned_by.player_name+'. Attempting to remove...')
            self.owned_by.remove_asset(self)
            # add to game history
            current_gameboard['history']['function'].append(self.owned_by.remove_asset)
            params = dict()
            params['self'] = self.owned_by
            params['asset'] = self
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)

            self.owned_by = current_gameboard['bank'] # this is temporary, but we want to enforce safe behavior

        self.owned_by = player
        player.add_asset(self, current_gameboard) # if the property is mortgaged, this will get reflected in the new owner's portfolio
        # add to game history
        current_gameboard['history']['function'].append(player.add_asset)
        params = dict()
        params['self'] = player
        params['asset'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        logger.debug('Asset ownership update succeeded.')

        if self.loc_class == 'real_estate':
            asset_list = list(player.assets)
            logger.debug(player.player_name + " will lose all railroads and utilities (if it owns any) since it has decided to buy real estate!")
            for prop in asset_list:
                if prop.loc_class == 'railroad' or prop.loc_class == 'utility':
                    cash_due = prop.transfer_property_to_bank(player, current_gameboard)
                    # since player wont receive the cash_due in this novelty, even if the bank has no money to pay the player
                    # and returns a failure code, the asset transfer still happens explicity here.
                    # if the bank has cash, the transfer happens inside the transfer_property_to_bank() function
                    if cash_due == flag_config_dict['failure_code']:
                        player.remove_asset(self)
                        if prop.is_mortgaged:
                            prop.is_mortgaged = False
                        # add to game history
                        current_gameboard['history']['function'].append(player.remove_asset)
                        params = dict()
                        params['self'] = player
                        params['asset'] = prop
                        current_gameboard['history']['param'].append(params)
                        current_gameboard['history']['return'].append(None)
                        prop.owned_by = current_gameboard['bank']
                    logger.debug("Player lost " + prop.name + " to the bank.")
                    # add to game history
                    current_gameboard['history']['function'].append(prop.transfer_property_to_bank)
                    params = dict()
                    params['self'] = prop
                    params['player'] = player
                    params['current_gameboard'] = current_gameboard
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(cash_due)

        elif self.loc_class == 'railroad' or self.loc_class == 'utility':
            asset_list = list(player.assets)
            logger.debug(player.player_name + " will lose all real estate properties (if it owns any) and improvements since it has decided to buy "
                                              "railroad/utility!")
            for prop in asset_list:
                if prop.loc_class == 'real_estate':
                    num_houses = prop.num_houses
                    num_hotel = prop.num_hotels
                    prop.num_houses = 0
                    prop.num_hotels = 0
                    player.num_total_houses -= num_houses
                    player.num_total_hotels -= num_hotel
                    current_gameboard['bank'].total_houses += num_houses
                    current_gameboard['bank'].total_hotels += num_hotel
                    cash_due = prop.transfer_property_to_bank(player, current_gameboard)
                    # since player wont receive the cash_due in this novelty, even if the bank has no money to pay the player
                    # and returns a failure code, the asset transfer still happens explicity here.
                    # if the bank has cash, the transfer happens inside the transfer_property_to_bank() function
                    if cash_due == flag_config_dict['failure_code']:
                        player.remove_asset(self)
                        if prop.is_mortgaged:
                            prop.is_mortgaged = False
                        # add to game history
                        current_gameboard['history']['function'].append(player.remove_asset)
                        params = dict()
                        params['self'] = player
                        params['asset'] = prop
                        current_gameboard['history']['param'].append(params)
                        current_gameboard['history']['return'].append(None)
                        prop.owned_by = current_gameboard['bank']

                    logger.debug("Player lost " + prop.name + " to the bank.")
                    # add to game history
                    current_gameboard['history']['function'].append(prop.transfer_property_to_bank)
                    params = dict()
                    params['self'] = prop
                    params['player'] = player
                    params['current_gameboard'] = current_gameboard
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(cash_due)

    else:
        logger.debug('Asset '+ self.name +' is non-purchaseable!')
        logger.error("Exception")
        raise Exception


def alternate_calculate_railroad_dues(asset, current_gameboard):
    logger.debug('calculating railroad dues for '+asset.name)
    if asset.owned_by.num_railroads_possessed > 4 or asset.owned_by.num_railroads_possessed < 0:
        logger.debug('Error! num railroads possessed by '+ asset.owned_by.player_name+ ' is '+ \
            str(asset.owned_by.num_railroads_possessed)+', which is impossible')

        logger.error("Exception")
        raise Exception

    if asset.name == 'Reading Railroad' or asset.name == 'Short Line':
        logger.debug("Calculating updated dues for new class of railroads!")
        dues = 500
    else:
        dues = asset._railroad_dues[asset.owned_by.num_railroads_possessed]

    logger.debug('railroad dues are '+str(dues))
    return dues


def hide_player_color_sets_before(self, current_gameboard, allowable_actions, code):
    current_gameboard['players_actual_color_sets'] = dict()
    if self.player_name == 'player_4':
        current_gameboard['players_actual_color_sets'][self.player_name] = self.full_color_sets_possessed
        self.full_color_sets_possessed = set()


def hide_player_color_sets_after(self, current_gameboard, allowable_actions, code):
    if self.player_name == 'player_4':
        self.full_color_sets_possessed = current_gameboard['players_actual_color_sets'][self.player_name]
        current_gameboard['players_actual_color_sets'] = dict()


def hide_player_assets_before(self, current_gameboard, allowable_actions, code):
    current_gameboard['player_actual_assets'] = dict()
    if self.player_name == 'player_4':
        for p in current_gameboard['players']:     # for TA2 player, we hide details of other player assets
            if p.player_name != 'player_1':
                current_gameboard['player_actual_assets'][p.player_name] = p.assets
                p.assets = set()


def hide_player_assets_after(self, current_gameboard, allowable_actions, code):
    if self.player_name == 'player_4':
        for p in current_gameboard['players']:     # for TA2 player, we hide details of other player assets
            if p.player_name != 'player_1':
                p.assets = current_gameboard['player_actual_assets'][p.player_name]
    current_gameboard['player_actual_assets'] = dict()


def incorrect_property_colors_before(self, current_gameboard, allowable_actions, code):
    color_list = ['Blue', 'SkyBlue', 'Brown', 'Orange', 'Orchid', 'Red', 'Green', 'Yellow']
    current_gameboard['color_asset_map'] = dict()
    if self.player_name == 'player_4':
        current_gameboard['color_asset_map'][self.player_name] = dict()
        for p in self.assets:
            if p.loc_class == 'real_estate':
                current_gameboard['color_asset_map'][self.player_name][p.name] = p.color
                p.color = np.random.choice(color_list)


def incorrect_property_colors_after(self, current_gameboard, allowable_actions, code):
    if self.player_name == 'player_4':
        for p in self.assets:
            if p.loc_class == 'real_estate':
                p.color = current_gameboard['color_asset_map'][self.player_name][p.name]
    current_gameboard['color_asset_map'] = dict()


def assign_dummy_players_before(self, current_gameboard, allowable_actions, code):
    if self.player_name == 'player_1':
        logger.debug("Assigning dummy player!")
        player_args = dict()
        player_args['status'] = 'waiting_for_move'
        player_args['current_position'] = current_gameboard['go_position']
        player_args['has_get_out_of_jail_chance_card'] = False
        player_args['has_get_out_of_jail_community_chest_card'] = False
        player_args['current_cash'] = 1500
        player_args['num_railroads_possessed'] = 0
        player_args['num_utilities_possessed'] = 0
        player_args['full_color_sets_possessed'] = set()
        player_args['assets'] = set()
        player_args['currently_in_jail'] = False
        player_args['agent'] = Agent(**background_agent_v3_1.decision_agent_methods)

        current_gameboard['reverse_player_mapping_dict'] = list()
        for p in current_gameboard['players']:
            current_gameboard['reverse_player_mapping_dict'].append(p)

        players_list = list()

        for pl in current_gameboard['players']:
            if pl != self:
                player_args['player_name'] = pl.player_name
                dummy_player = Player(**player_args)
                players_list.append(dummy_player)
            else:
                players_list.append(self)

        current_gameboard['players'] = players_list


def assign_dummy_players_after(self, current_gameboard, allowable_actions, code):
    if self.player_name == 'player_1':
        logger.debug("Reverting dummy player!")
        reverse_map_list = list()
        for p in current_gameboard['reverse_player_mapping_dict']:
            reverse_map_list.append(p)
        current_gameboard['players'] = reverse_map_list
        current_gameboard['reverse_player_mapping_dict'] = list()


def uncolor_properties_before(self, current_gameboard, allowable_actions, code):
    # print("inside uncolor properties before")
    new_color_list = ['Wwhite', 'Black']
    color_list = ['Blue', 'SkyBlue', 'Brown', 'Orange', 'Orchid', 'Red', 'Green', 'Yellow']
    current_gameboard['color_asset_map'] = dict()
    if self.player_name == 'player_4':
        logger.debug("Assigning black and white colors")
        current_gameboard['color_asset_map'][self.player_name] = dict()
        for p in current_gameboard['location_sequence']:
            if p.loc_class == 'real_estate':
                current_gameboard['color_asset_map'][p.name] = p.color
                p.color = np.random.choice(new_color_list)

        color_assets = dict()
        for o in current_gameboard['location_sequence']:
            if o.color is None:
                continue
            else:
                if o.color not in color_assets:
                    color_assets[o.color] = set()
                color_assets[o.color].add(o)
        current_gameboard['color_assets'] = color_assets

        current_gameboard['old_full_color_sets'] = dict()
        for p in current_gameboard['players']:
            current_gameboard['old_full_color_sets'][p.player_name] = p.full_color_sets_possessed
            new_full_color_sets = set()
            if p.assets:
                for prop in p.assets:
                    if prop.loc_class == 'real_estate':
                        new_full_color_sets.add(prop.color)
            p.full_color_sets_possessed = new_full_color_sets


def uncolor_properties_after(self, current_gameboard, allowable_actions, code):
    # print("inside uncolor properties after")
    if self.player_name == 'player_4':
        logger.debug("Reverting black and white colors")
        for p in current_gameboard['location_sequence']:
            if p.loc_class == 'real_estate':
                p.color = current_gameboard['color_asset_map'][p.name]
        current_gameboard['color_asset_map'] = dict()

        color_assets = dict()
        for o in current_gameboard['location_sequence']:
            if o.color is None:
                continue
            else:
                if o.color not in color_assets:
                    color_assets[o.color] = set()
                color_assets[o.color].add(o)

        current_gameboard['color_assets'] = color_assets

        for p in current_gameboard['players']:
            p.full_color_sets_possessed = current_gameboard['old_full_color_sets'][p.player_name]
        current_gameboard['old_full_color_sets'] = dict()


def property_name_change_before(self, current_gameboard, allowable_actions, code):
    if self.player_name == 'player_4':
        old_new_name_mapping= dict()
        new_name = "Property_"
        new_property_name_list = list()
        for i in range(22):
            prop_name = new_name + str(i)
            new_property_name_list.append(prop_name)

        for p in current_gameboard['location_sequence']:
            if p.loc_class == 'real_estate':
                new_prop_name = new_property_name_list.pop(0)
                old_new_name_mapping[new_prop_name] = p.name        # mapping between new and old prop name
                p.name = new_prop_name

        current_gameboard['property_names_dict'] = old_new_name_mapping


def property_name_change_after(self, current_gameboard, allowable_actions, code):
    if self.player_name == 'player_4':
        for p in current_gameboard['location_sequence']:
            if p.loc_class == 'real_estate':
                old_name = current_gameboard['property_names_dict'][p.name]
                p.name = old_name


def populate_param_dict_mod(param_dict, player, current_gameboard):
    if player.player_name != 'player_4':
        if not param_dict:   # check if param_dict is an empty dictionary --> skip turn and conclude_actions
            return param_dict

        if 'player' in param_dict:
            param_dict['player'] = player
        if 'current_gameboard' in param_dict:
            param_dict['current_gameboard'] = current_gameboard
        if 'asset' in param_dict:
            for loc in current_gameboard['location_sequence']:
                if loc.name == param_dict['asset']:
                    param_dict['asset'] = loc

        # following keys are mostly relevant to trading
        if 'from_player' in param_dict:
            for p in current_gameboard['players']:
                if p.player_name == param_dict['from_player']:
                    param_dict['from_player'] = p
        if 'to_player' in param_dict:
            for p in current_gameboard['players']:
                if p.player_name == param_dict['to_player']:
                    param_dict['to_player'] = p
        if 'offer' in param_dict:
            property_set_offered = param_dict['offer']['property_set_offered']   # set of property names (not list and does not involve pointers)
            property_set_wanted = param_dict['offer']['property_set_wanted']    # set of property names (not list and does not involve pointers)
            # iterate through these sets of strings and replace with property pointers

            flag_replacement_offer = False
            flag_replacement_wanted = False

            property_set_offered_ptr = set()
            for prop in property_set_offered:
                for loc in current_gameboard['location_sequence']:
                    if isinstance(prop, str) and loc.name == prop:
                        flag_replacement_offer = True
                        property_set_offered_ptr.add(loc)
                        break

            property_set_wanted_ptr = set()
            for prop in property_set_wanted:
                for loc in current_gameboard['location_sequence']:
                    if isinstance(prop, str) and loc.name == prop:
                        flag_replacement_wanted = True
                        property_set_wanted_ptr.add(loc)
                        break

            if flag_replacement_offer:
                param_dict['offer']['property_set_offered'] = property_set_offered_ptr
            if flag_replacement_wanted:
                param_dict['offer']['property_set_wanted'] = property_set_wanted_ptr
        return param_dict

    elif player.player_name == 'player_4':
        if not param_dict:   # check if param_dict is an empty dictionary --> skip turn and conclude_actions
            return param_dict

        if 'player' in param_dict:
            param_dict['player'] = player
        if 'current_gameboard' in param_dict:
            param_dict['current_gameboard'] = current_gameboard
        if 'asset' in param_dict:
            if param_dict['asset'] in current_gameboard['property_names_dict']:
                asset_name_converted = current_gameboard['property_names_dict'][param_dict['asset']]
            else:
                asset_name_converted = param_dict['asset']
            for loc in current_gameboard['location_sequence']:
                if loc.name == asset_name_converted:
                    param_dict['asset'] = loc

        # following keys are mostly relevant to trading
        if 'from_player' in param_dict:
            for p in current_gameboard['players']:
                if p.player_name == param_dict['from_player']:
                    param_dict['from_player'] = p
        if 'to_player' in param_dict:
            for p in current_gameboard['players']:
                if p.player_name == param_dict['to_player']:
                    param_dict['to_player'] = p
        if 'offer' in param_dict:
            property_set_offered = param_dict['offer']['property_set_offered']   # set of property names (not list and does not involve pointers)
            property_set_wanted = param_dict['offer']['property_set_wanted']    # set of property names (not list and does not involve pointers)
            # iterate through these sets of strings and replace with property pointers

            flag_replacement_offer = False
            flag_replacement_wanted = False

            property_set_offered_ptr = set()
            for prop in property_set_offered:
                for loc in current_gameboard['location_sequence']:
                    if isinstance(prop, str) and prop in current_gameboard['property_names_dict'] and loc.name == current_gameboard['property_names_dict'][prop]:
                        flag_replacement_offer = True
                        property_set_offered_ptr.add(loc)
                        break
                    elif isinstance(prop, str) and loc.name == prop:
                        flag_replacement_offer = True
                        property_set_offered_ptr.add(loc)
                        break

            property_set_wanted_ptr = set()
            for prop in property_set_wanted:
                for loc in current_gameboard['location_sequence']:
                    if isinstance(prop, str) and prop in current_gameboard['property_names_dict'] and loc.name == current_gameboard['property_names_dict'][prop]:
                        flag_replacement_wanted = True
                        property_set_wanted_ptr.add(loc)
                        break
                    elif isinstance(prop, str) and loc.name == prop:
                        flag_replacement_wanted = True
                        property_set_wanted_ptr.add(loc)
                        break

            if flag_replacement_offer:
                param_dict['offer']['property_set_offered'] = property_set_offered_ptr
            if flag_replacement_wanted:
                param_dict['offer']['property_set_wanted'] = property_set_wanted_ptr
        return param_dict


def calculate_new_rent_due_to_hotel_limit_novelty(asset, current_gameboard):
    logger.debug('calculating rent for '+asset.name)
    ans = asset.rent # unimproved-non-monopolized rent (the default)
    if asset.num_hotels > 0:
        logger.debug('property has ' + str(asset.num_hotels) + ' hotel(s). Updating rent.')
        ans = asset.rent_hotel*asset.num_hotels
    elif asset.num_houses > 0: # later we can replace these with reflections
        logger.debug('property has '+str(asset.num_houses)+' houses. Updating rent.')
        ans = asset._house_rent_dict[asset.num_houses] # if for some reason you have more than 4 houses, you'll get a key error
    elif asset.color in asset.owned_by.full_color_sets_possessed:
        ans = asset.rent*current_gameboard['bank'].monopolized_property_rent_factor # charge twice the rent on unimproved monopolized properties.
        logger.debug('property has color '+ asset.color+ ' which is monopolized by '+asset.owned_by.player_name+'. Updating rent.')
    logger.debug('rent is calculated to be '+str(ans))
    return ans


def calculate_new_rent_luxury_hotel(asset, current_gameboard):
    # regular hotel charged normal rent, luxury hotel charged twice the rent of normal hotel
    logger.debug('calculating rent for '+asset.name)
    ans = asset.rent # unimproved-non-monopolized rent (the default)
    if asset.num_hotels > 0:
        logger.debug('property has 1 regular hotel and ' + str(asset.num_hotels - 1) + ' luxury hotel(s). Updating rent.')
        price_per_luxury_hotel = 2*asset.rent_hotel
        ans = asset.rent_hotel + price_per_luxury_hotel*(asset.num_hotels-1)
    elif asset.num_houses > 0: # later we can replace these with reflections
        logger.debug('property has '+str(asset.num_houses)+' houses. Updating rent.')
        ans = asset._house_rent_dict[asset.num_houses] # if for some reason you have more than 4 houses, you'll get a key error
    elif asset.color in asset.owned_by.full_color_sets_possessed:
        ans = asset.rent*current_gameboard['bank'].monopolized_property_rent_factor # charge twice the rent on unimproved monopolized properties.
        logger.debug('property has color '+ asset.color+ ' which is monopolized by '+asset.owned_by.player_name+'. Updating rent.')
    logger.debug('rent is calculated to be '+str(ans))
    return ans
