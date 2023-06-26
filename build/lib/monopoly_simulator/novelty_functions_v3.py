import numpy as np
from monopoly_simulator.card_utility_actions import _has_player_passed_go, move_player_after_die_roll, _move_player__check_for_go
from monopoly_simulator.player import Player
from monopoly_simulator.dice import Dice
from monopoly_simulator.agent import Agent
from monopoly_simulator.bank import Bank
from monopoly_simulator import background_agent_v3_1
from monopoly_simulator.location import RealEstateLocation, TaxLocation, UtilityLocation, RailroadLocation
from monopoly_simulator.flag_config import flag_config_dict
from monopoly_simulator import diagnostics
from monopoly_simulator import action_choices
import random
import sys
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
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


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
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


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
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


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
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        asset.update_asset_owner(winning_player, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(asset.update_asset_owner)
        params = dict()
        params['self'] = asset
        params['player'] = winning_player
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
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
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


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
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


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
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
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
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


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
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


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
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
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
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


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
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
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
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


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
#     current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
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
#         current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
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
#     current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


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
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


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
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


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
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
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
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


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
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


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
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
                        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
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
                    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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
                        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
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
                    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

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



#-------------------------------------------Phase 2 Novelties---------------------------------------------

#----------------------------------------------Actions----------------------------------------------------


def transfer_GOO_jail_card(from_player, to_player, action_params_dict=None, current_gameboard=None):
    """
    This function checks if the player has a GOO jail card (either from chance or community chest) when called.
    If it does, then the card is transfered from the from_player to the to_player.
    """
    print("inside GOO func")
    if to_player.status == 'lost':
        logger.debug(to_player.player_name + " has lost the game. Can't transfer GOO jail card.")
        return action_choices.flag_config_dict['failure_code']

    if from_player.has_get_out_of_jail_chance_card or from_player.has_get_out_of_jail_community_chest_card:
        if from_player.has_get_out_of_jail_chance_card:
            if from_player.has_get_out_of_jail_chance_card:
                from_player.has_get_out_of_jail_chance_card = False
            to_player.has_get_out_of_jail_chance_card = True
            logger.debug("GOO jail chance card: " + from_player.player_name + " to " + to_player.player_name)

        elif from_player.has_get_out_of_jail_community_chest_card:
            from_player.has_get_out_of_jail_community_chest_card = False
            to_player.has_get_out_of_jail_community_chest_card = True
            logger.debug("GOO jail cc card: " + from_player.player_name + " to " + to_player.player_name)

        return action_choices.flag_config_dict['successful_action']
    else:
        logger.debug(from_player.player_name + " has no GOO card")
        return action_choices.flag_config_dict['failure_code']


def lawsuit_prevents_improvements(from_player, to_player, action_params_dict, current_gameboard):
    """
    from_player can file a lawsuit against to_player for a certain number of rounds during which from_player pays an amount to the bank
    and the to_player is not allowed improvements.
    Note: from_player and to_player can only have one lawsuit active at a time.
    :param from_player:
    :param to_player:
    :param action_params_dict:
    :param current_gameboard:
    :return:
    """
    logger.debug(from_player.player_name + " filed a lawsuit against " + to_player.player_name)
    if 'lawsuit_dict' in current_gameboard:
        if 'from_player_num_rounds' in from_player.agent._agent_memory:
            logger.debug(from_player.player_name + " has already filed a lawsuit. Wait for lawsuit to close before filing another one!")
            return action_choices.flag_config_dict['failure_code']
        if 'against_player_num_rounds' in from_player.agent._agent_memory:
            logger.debug(to_player.player_name + " already has a lawsuit filed against it. Wait for its lawsuit to close before filing another one!")
            return action_choices.flag_config_dict['failure_code']
        print(current_gameboard['lawsuit_dict']['from_player_num_rounds'])
        from_player.agent._agent_memory['from_player_num_rounds'] = current_gameboard['lawsuit_dict']['from_player_num_rounds']
        to_player.agent._agent_memory['against_player_num_rounds'] = current_gameboard['lawsuit_dict']['against_player_num_rounds']
        current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], "_lawsuit_prevents_improvements_from_player")
        action_choices.improve_property = getattr(sys.modules[__name__], "_lawsuit_prevents_improvements_against_player")
        logger.debug(from_player.player_name + " filed a lawsuit against " + to_player.player_name)
        return action_choices.flag_config_dict['successful_action']
    else:
        logger.debug("Lawsuit dict not present in gameboard! Something is wrong with novelty injection...")
        return action_choices.flag_config_dict['failure_code']


def _lawsuit_prevents_improvements_from_player(player, new_pos, current_gameboard):
    # if 'lawsuit_dict' in current_gameboard and current_gameboard['lawsuit_dict']['from_player'] == player:
    if 'lawsuit_dict' in current_gameboard and 'from_player_num_rounds' in player.agent._agent_memory:
        if player.agent._agent_memory['from_player_num_rounds'] > 0:
            logger.debug("Lawsuit fee deducted for " + player.player_name)
            player.charge_player(current_gameboard['lawsuit_dict']['amount'], current_gameboard, True)
            current_gameboard['history']['function'].append(player.charge_player)
            params = dict()
            params['self'] = player
            params['amount'] = current_gameboard['lawsuit_dict']['amount']
            params['description'] = 'lawsuit fee'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            logger.debug(player.player_name + " passed GO, lawsuit now active for " +
                     str(player.agent._agent_memory['from_player_num_rounds']) + " round(s).")
            player.agent._agent_memory['from_player_num_rounds'] -= 1

    # elif 'lawsuit_dict' in current_gameboard and current_gameboard['lawsuit_dict']['against_player'] == player:
    elif 'lawsuit_dict' in current_gameboard and 'against_player_num_rounds' in player.agent._agent_memory:
        logger.debug(player.player_name + " passed GO, lawsuit now active for " +
                     str(player.agent._agent_memory['against_player_num_rounds']) + " round(s).")
        player.agent._agent_memory['against_player_num_rounds'] -= 1

    if 'from_player_num_rounds' in player.agent._agent_memory and player.agent._agent_memory['from_player_num_rounds'] == 0:
        del player.agent._agent_memory['from_player_num_rounds']
    if 'against_player_num_rounds' in player.agent._agent_memory and player.agent._agent_memory['against_player_num_rounds'] == 0:
        del player.agent._agent_memory['against_player_num_rounds']


def _lawsuit_prevents_improvements_against_player(player, asset, current_gameboard, add_house=True, add_hotel=False):
    """
    The following block of code prevents property improvement by the player against whom lawsuit is currently filed for
    a certain number of rounds defined by "current_gameboard['lawsuit_dict']['against_player_num_rounds']".
    """
    #------------------------novelty--------------------------------
    if 'lawsuit_dict' in current_gameboard and 'against_player_num_rounds' in player.agent._agent_memory:
        if player.agent._agent_memory['against_player_num_rounds'] > 0:
            logger.debug(player.player_name + " Cannot improve since lawsuit is filed against it.")
            return
    #--------------------------------------------------------

    if asset.owned_by != player or asset.is_mortgaged:
        # these are the usual conditions that we verify before allowing any improvement to proceed
        logger.debug(player.player_name+' does not own this property, or it is mortgaged. Returning failure code')
        return action_choices.flag_config_dict['failure_code']
    elif asset.loc_class != 'real_estate':
        logger.debug(asset.name+' is not real estate and cannot be improved. Returning failure code')
        return action_choices.flag_config_dict['failure_code']
    elif asset.color not in player.full_color_sets_possessed:
        # these are the usual conditions that we verify before allowing any improvement to proceed
        logger.debug(player.player_name+' does not own all properties of this color, hence it cannot be improved. Returning failure code')
        return action_choices.flag_config_dict['failure_code']
    elif player.current_cash <= asset.price_per_house:
        logger.debug(player.player_name+ ' cannot afford this improvement. Returning failure code')
        return action_choices.flag_config_dict['failure_code']

    if add_hotel: # this is the simpler case
        logger.debug('Looking to improve '+asset.name+' by adding a hotel.')
        if asset.num_hotels == current_gameboard['bank'].hotel_limit:
            logger.debug('There is already ' + str(current_gameboard['bank'].hotel_limit) + ' hotel(s) here. You cannot exceed this limit. Returning failure code')
            return action_choices.flag_config_dict['failure_code']
        elif asset.num_hotels == 0 and asset.num_houses != current_gameboard['bank'].house_limit_before_hotel:
            logger.debug('You need to have ' + str(current_gameboard['bank'].house_limit_before_hotel)
                         + ' houses before you can build a hotel...Returning failure code')
            return action_choices.flag_config_dict['failure_code']
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
                return action_choices.flag_config_dict['successful_action']

            else:
                logger.debug('Bank has no hotels left for purchase. Kindly wait till someone returns a hotel to the bank.')
                return action_choices.flag_config_dict['failure_code']

        else:
            logger.debug('All same-colored properties must be uniformly improved first before you can build a hotel on this property. Returning failure code')
            return action_choices.flag_config_dict['failure_code']

    elif add_house:
        logger.debug('Looking to improve '+asset.name+' by adding a house. Currently property has ' + str(asset.num_houses))
        if asset.num_hotels > 0 or asset.num_houses == current_gameboard['bank'].house_limit_before_hotel:
            logger.debug('There is already a hotel here or you have built the max number of houses that you can on a property. '
                         'You are not permitted another house. Returning failure code')
            return action_choices.flag_config_dict['failure_code']
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
                return action_choices.flag_config_dict['successful_action']

            else:
                logger.debug('Bank has no houses left for purchase. Kindly wait till someone returns a house to the bank.')
                return action_choices.flag_config_dict['failure_code']

        else:
            logger.debug('All same-colored properties must be uniformly improved first before you can build a house on this property. Returning failure code')
            return action_choices.flag_config_dict['failure_code']

    else:
        #ideally should never reach here, but if it does, then return failure code.
        logger.debug("Didnot succeed in improving house/hotel. Returning failure code.")
        return action_choices.flag_config_dict['failure_code']


def monopoly_based_income_tax(from_player, to_player, action_params_dict, current_gameboard):
    """
    If player owns monopolies, then the tax becomes a function of the number of monopolies owned, else returns regular tax location amount due.
    :param location:
    :param player:
    :param current_gameboard:
    :return:
    """
    if 'tax_perc' in current_gameboard:
        # current_gameboard['from_player'] = from_player
        from_player.agent._agent_memory['alt_income_tax'] = True
        TaxLocation.calculate_tax = getattr(sys.modules[__name__], "_calculate_income_tax_util")
        return action_choices.flag_config_dict['successful_action']
    else:
        logger.debug("something wrong with novelty injection...")
        return action_choices.flag_config_dict['failure_code']


def _calculate_income_tax_util(location, player, current_gameboard):
    # if location.name == 'Income Tax' and current_gameboard['from_player'] == player:
    if location.name == 'Income Tax' and 'alt_income_tax' in player.agent._agent_memory:
        if len(player.full_color_sets_possessed) > 0:
            num_monopolies = len(player.full_color_sets_possessed)
            logger.debug("Tax calculated based on number of monopolies.")
            return location.amount_due*(1 + num_monopolies*current_gameboard['tax_perc'])
    return location.amount_due


def illegal_use_of_GOO_jail_card(from_player, to_player, action_params_dict, current_gameboard):
    if to_player.currently_in_jail and (from_player.has_get_out_of_jail_chance_card or from_player.has_get_out_of_jail_community_chest_card):
        _use_get_out_of_jail_card_util(from_player, to_player, current_gameboard)
        return action_choices.flag_config_dict['successful_action']
    elif not to_player.currently_in_jail:
        logger.debug(to_player.player_name + " currently not in jail, returning failure code...")
        return action_choices.flag_config_dict['failure_code']
    else:
        logger.debug(from_player.player_name + " does not have GOO jail free card")
        return action_choices.flag_config_dict['failure_code']


def _use_get_out_of_jail_card_util(from_player, to_player, current_gameboard):
    """
    from_player uses its GOO jail free card on behalf of to_player and forcefully gets it out of jail.
    """
    import copy

    if from_player.has_get_out_of_jail_chance_card:  # we give first preference to chance, then community chest
        logger.debug(from_player.player_name + " used GOO jail free chance card on behalf of " + to_player.player_name)
        from_player.has_get_out_of_jail_chance_card = False
        to_player.currently_in_jail = False
        logger.debug('Adding the card back again to the chance pack.')
        current_gameboard['chance_cards'].add(
            copy.deepcopy(current_gameboard['chance_card_objects']['get_out_of_jail_free']))
    elif from_player.has_get_out_of_jail_community_chest_card:
        logger.debug(from_player.player_name + " used GOO jail free cc card on behalf of " + to_player.player_name)
        from_player.has_get_out_of_jail_community_chest_card = False
        to_player.currently_in_jail = False
        logger.debug('Adding the card back again to the community chest pack.')
        current_gameboard['community_chest_cards'].add(
            copy.deepcopy(current_gameboard['community_chest_card_objects']['get_out_of_jail_free']))


def installment_based_free_mortgage(from_player, to_player, action_params_dict, current_gameboard):
    '''
    If the player decides to mortgage property in installments, then the installments will be paid in the auxiliary_before_pre_roll_check action.
    The details are saved in the player's respective agent memory to keep track on how much has been paid off in the installments.
    Note, if the player has chosen this arbitrary action choice, then the regular free_mortgage() function in action_choices will return failure
    code saying it cannot be invoked to free a mortgage on a property that is being freed in installments. Hence action_choices.free_mortgage()
    function is also lifted
    :param from_player:
    :param to_player:
    :param action_params_dict:
    :param current_gameboard:
    :return:
    '''
    if 'installment_fee' in current_gameboard:
        if 'mortgage_installments' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['mortgage_installments'] = dict()
        if action_params_dict['location'].loc_class == 'real_estate' or action_params_dict['location'].loc_class == 'railroad' or action_params_dict['location'].loc_class == 'utility':
            if not action_params_dict['location'].is_mortgaged:
                logger.debug(action_params_dict['location'].name + " is not mortgaged! Invalid action choice.")
                return action_choices.flag_config_dict['failure_code']
            if action_params_dict['location'].name in from_player.agent._agent_memory['mortgage_installments']:
                logger.debug(action_params_dict['location'].name + " mortgage is already being paid off in installments.")
                return action_choices.flag_config_dict['failure_code']

            from_player.agent._agent_memory['mortgage_installments'][action_params_dict['location'].name] = dict()
            from_player.agent._agent_memory['mortgage_installments'][action_params_dict['location'].name]['amount_left'] = action_params_dict['location'].calculate_mortgage_owed(action_params_dict['location'], current_gameboard)
            from_player.agent._agent_memory['mortgage_installments'][action_params_dict['location'].name]['num_rounds_left'] = current_gameboard['num_rounds']

            logger.debug(from_player.player_name + " will be paying mortgage on " + action_params_dict['location'].name + " in installments.")
            from_player.charge_player(current_gameboard['installment_fee'], current_gameboard, bank_flag=True)
            logger.debug(from_player.player_name + ' paid fee for mortgage installment payment: ' + str(current_gameboard['installment_fee']))
            current_gameboard['history']['function'].append(from_player.charge_player)
            params = dict()
            params['self'] = from_player
            params['amount'] = current_gameboard['installment_fee']
            params['description'] = 'mortgage installment fee'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        else:
            logger.debug("Cannot free mortgage on this location since its not real_estate/utility/railroad.")
            return action_choices.flag_config_dict['failure_code']

        if 'auxiliary_check_for_go' not in current_gameboard:
            current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], "_installment_free_mortgage_util")
        return action_choices.flag_config_dict['successful_action']
    else:
        logger.debug("something wrong with novelty injection...")
        raise Exception


def _installment_free_mortgage_util(player, position, current_gameboard):
    if 'mortgage_installments' in player.agent._agent_memory:
        import copy
        items = copy.deepcopy(player.agent._agent_memory['mortgage_installments'])
        for k, item in items.items():
            amount_due = float(item['amount_left']/item['num_rounds_left'])
            charge_player_amt = amount_due + current_gameboard['installment_fee']
            player.agent._agent_memory['mortgage_installments'][k]['num_rounds_left'] -= 1
            player.agent._agent_memory['mortgage_installments'][k]['amount_left'] -= amount_due

            player.charge_player(charge_player_amt, current_gameboard, bank_flag=True)
            logger.debug(player.player_name + ' paid mortgage installment of ' + str(charge_player_amt))
            current_gameboard['history']['function'].append(player.charge_player)
            params = dict()
            params['self'] = player
            params['amount'] = charge_player_amt
            params['description'] = 'improvements'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            if player.agent._agent_memory['mortgage_installments'][k]['num_rounds_left'] == 0: # completed mortgage installments on this property
                del player.agent._agent_memory['mortgage_installments'][k]


def reassign_free_mortgage(player, asset, current_gameboard):
    # --------------------novelty---------------------------------------
    if 'mortgage_installments' in player.agent._agent_memory and asset.name in player.agent._agent_memory['mortgage_installments']:
        logger.debug(player.player_name + " has opted to pay mortgage in installments. This action choice cannot be invoked. Returning failure code.")
        return flag_config_dict['failure_code']
    #-------------------------------------------------------------------
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
        player.charge_player(asset.calculate_mortgage_owed(asset, current_gameboard), current_gameboard, bank_flag=True)
        logger.debug(player.player_name+"Player has paid down mortgage with interest. Setting status of asset to unmortgaged, and removing asset from player's mortgaged set")
        asset.is_mortgaged = False
        player.mortgaged_assets.remove(asset)
        logger.debug('Mortgage has successfully been freed. Returning successful action code')
        return flag_config_dict['successful_action']


def changing_real_estate_colors(from_player, to_player, action_params_dict, current_gameboard):
    """

    :param from_player: player that wants to change the color of its real estate location
    :param to_player:
    :param action_params_dict: 'location' key in this dictionary holds the location which needs to a color change. 'color' key denotes
    the color to which the location color has to be changed to.
    :param current_gameboard:
    :return:
    """
    if 'real_estate_change_colors' in current_gameboard:
        if current_gameboard['real_estate_change_colors'][from_player.player_name] > 0:
            if action_params_dict['location'].loc_class != 'real_estate' or action_params_dict['color'] not in current_gameboard['color_assets']:
                logger.debug("Something wrong with novelty params. Returning failure code")
                return action_choices.flag_config_dict['failure_code']
            elif action_params_dict['location'].num_houses > 0 or action_params_dict['location'].num_hotels > 0:
                logger.debug("Cannot change color of an improved property. Returning failure code")
                return action_choices.flag_config_dict['failure_code']
            else:
                old_color = action_params_dict['location'].color
                action_params_dict['location'].color = action_params_dict['color']       # color of location in location objects automatically changes due to reference
                current_gameboard['color_assets'][old_color].remove(action_params_dict['location'])
                current_gameboard['color_assets'][action_params_dict['location'].color].add(action_params_dict['location'])
                current_gameboard['real_estate_change_colors'][from_player.player_name] -= 1
                logger.debug(from_player.player_name + " changed the color of " + action_params_dict['location'].name + " to " + action_params_dict['color'])
                return action_choices.flag_config_dict['successful_action']
        else:
            logger.debug(from_player.player_name + " has used up all chances to change the color of a location. Can't process this action choice.")
            return action_choices.flag_config_dict['failure_code']
    else:
        logger.debug("Something is wrong with novelty injection routine....Raising Exception.")
        raise Exception


def stay_in_jail_choice(from_player, to_player, action_params_dict, current_gameboard):
    """
    player can decide to stay in jail either when it lands in jail by the card or "go to jail" location, and even if it is just visiting.
    In order to get out of jail after it has made the voluntary decision to stay in jail, the arbitrary action has to be called again with
    the action_params_dict['stay_in_jail'] param set to false
    :param from_player:
    :param to_player:
    :param action_params_dict:
    :param current_gameboard:
    :return:
    """
    if current_gameboard['location_sequence'][from_player.current_position].name == "In Jail/Just Visiting" and action_params_dict['stay_in_jail']:
        if not from_player.currently_in_jail:           # just visiting jail, but in post roll player decides to stay in jail
            from_player.currently_in_jail = True
        from_player.agent._agent_memory['stay_in_jail_flag'] = True
        logger.debug(from_player.player_name + " choses to voluntarily stay in jail by paying the bank a % of the rent accrued.")
        return action_choices.flag_config_dict['successful_action']

    elif current_gameboard['location_sequence'][from_player.current_position].name == "In Jail/Just Visiting" and not action_params_dict['stay_in_jail']:
        from_player.agent._agent_memory['stay_in_jail_flag'] = False
        logger.debug(from_player.player_name + " choses to leave voluntary jail confinement")
        return action_choices.flag_config_dict['successful_action']

    elif current_gameboard['location_sequence'][from_player.current_position].name != "In Jail/Just Visiting":
        logger.debug(from_player.player_name + " not in In Jail/Just Visiting position, cannot execute this action.")
        return action_choices.flag_config_dict['failure_code']


def alternate_set_currently_in_jail_to_false(player, current_gameboard):
    if 'stay_in_jail' in player.agent._agent_memory and current_gameboard['stay_in_jail']==True:
        player.currently_in_jail = True
    else:
        player.currently_in_jail = False


def alternate_rent_payment(self, current_gameboard):
    """
    if recipient of rent has 'stay_in_jail_flag' flag set to true in its agent._agent_memory, then it owes the bank a percentage
    of rent accrued while it makes an action choice to voluntarily stay in jail.
    :param self:
    :param current_gameboard:
    :return:
    """
    current_loc = current_gameboard['location_sequence'][self.current_position]
    logger.debug('calculating and paying rent dues for '+ self.player_name+ ' who is in property '+current_loc.name+' which is owned by '+current_loc.owned_by.player_name)
    rent = RealEstateLocation.calculate_rent(current_loc, current_gameboard)
    # add to game history
    current_gameboard['history']['function'].append(RealEstateLocation.calculate_rent)
    params = dict()
    params['asset'] = current_loc
    params['current_gameboard'] = current_gameboard
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(rent)
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

    recipient = current_loc.owned_by
    code = recipient.receive_cash(rent, current_gameboard, bank_flag=False)
    # add to game history
    if code == action_choices.flag_config_dict['successful_action']:
        current_gameboard['history']['function'].append(recipient.receive_cash)
        params = dict()
        params['self'] = recipient
        params['amount'] = rent
        params['description'] = 'rent'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
    else:
        logger.debug("Not sure what happened! Something broke!")
        logger.error("Exception")
        raise Exception


    #-----------------------------novelty-----------------------------
    if 'stay_in_jail_flag' in recipient.agent._agent_memory and recipient.agent._agent_memory['stay_in_jail_flag']:
        if 'jail_tax_perc' not in current_gameboard:
            logger.debug("Something went wrong with novelty injection...")
            raise Exception
        stay_in_jail_fee = rent*current_gameboard['jail_tax_perc']
        recipient.charge_player(stay_in_jail_fee, current_gameboard, bank_flag=True)    # pay the bank an amount for staying in jail by choice
        logger.debug(recipient.player_name + " paid the bank a % of rent for voluntarily staying in jail.")
        # add to game history
        current_gameboard['history']['function'].append(self.charge_player)
        params = dict()
        params['self'] = recipient
        params['amount'] = stay_in_jail_fee
        params['description'] = 'stay in jail fee'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
    #----------------------------------------------------------------

    self.charge_player(rent, current_gameboard, bank_flag=False)
    # add to game history
    current_gameboard['history']['function'].append(self.charge_player)
    params = dict()
    params['self'] = self
    params['amount'] = rent
    params['description'] = 'rent'
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


def add_dummy_locs_on_monopolized_color_group(from_player, to_player, action_params_dict, current_gameboard):
    # Note: dummy location will not be added to player's portfolio to avoid trading, improvements, etc
    # solely for the purpose of collecting rent which will be calculated only if the player has a monopoly over that color group,
    # else will return 0.
    if 'dummy_locs' in current_gameboard:
        if current_gameboard['dummy_locs'][from_player.player_name] > 0:

            location_name = "dummy_loc_" + from_player.player_name + "_" + str(current_gameboard['dummy_locs'][from_player.player_name])
            new_location = RealEstateLocation("real_estate", location_name, action_params_dict['start_pos'], action_params_dict['start_pos']+1, action_params_dict['color'], 0, 0, 0,
                                              0, 0, 0, 0, 0, 0, from_player, 0, 0)

            current_gameboard['railroad_positions'] = list()
            current_gameboard['utility_positions'] = list()

            # now let's repair the other fields
            new_location_sequence = list()
            forbidden_loc_names = set()

            for loc in current_gameboard['location_sequence']:
                if loc.name in forbidden_loc_names :
                    new_location_sequence.append(loc)
                    continue
                new_start_position = len(new_location_sequence) # the new start position is the current length of the new sequence
                if new_start_position == new_location.start_position:
                    new_end_position = new_start_position + (new_location.end_position - new_location.start_position)
                    new_location_sequence.append(new_location)
                    forbidden_loc_names.add(new_location.name)
                else:
                    new_end_position = new_start_position + (loc.end_position - loc.start_position) # the new end position is the new start position + difference'
                    for i in range(loc.start_position, loc.end_position):
                        new_location_sequence.append(loc)
                        if loc.loc_class == 'railroad':
                            current_gameboard['railroad_positions'].append(len(new_location_sequence)-1) # we cannot directly use the start and end position, since the whole board is changing through 'stretching'
                        elif loc.loc_class == 'utility':
                            current_gameboard['utility_positions'].append(len(new_location_sequence)-1)

                        if loc.name == 'In Jail/Just Visiting':
                            current_gameboard['jail_position'] = len(new_location_sequence)-1

                        if loc.name == 'Go':
                            current_gameboard['go_position'] = len(new_location_sequence)-1

                    loc.start_position = new_start_position
                    loc.end_position = new_end_position
                    forbidden_loc_names.add(loc.name)
            current_gameboard['location_sequence'] = new_location_sequence
            logger.debug(from_player.player_name + " has added a dummy location of color " + action_params_dict['color'])

            from_player.charge_player(current_gameboard['cost'], current_gameboard, bank_flag=True)
            logger.debug(from_player.player_name + ' paid dummy location cost of ' + str(current_gameboard['cost']))
            current_gameboard['history']['function'].append(from_player.charge_player)
            params = dict()
            params['self'] = from_player
            params['amount'] = current_gameboard['cost']
            params['description'] = 'dummy location cost'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            current_gameboard['dummy_locs'][from_player.player_name] -= 1
            return action_choices.flag_config_dict['successful_action']
        else:
            logger.debug(from_player.player_name + " has crossed the linit for dummy locations. Cannot set up more!")
            return action_choices.flag_config_dict['failure_code']
    else:
        logger.debug("Something is wrong with novelty injection routine....Raising Exception.")
        raise Exception


def _calc_max_rent_in_color_group(asset, current_gameboard):
    ans = float(0)
    if asset.owned_by.assets:
        for a in asset.owned_by.assets:
            if a != asset and a.color == asset.color:
                if a.num_hotels == 1:
                    ans = max(ans, a.rent_hotel)
                elif a.num_houses > 0: # later we can replace these with reflections
                    ans = max(ans, a._house_rent_dict[a.num_houses]) # if for some reason you have more than 4 houses, you'll get a key error
                elif a.color in a.owned_by.full_color_sets_possessed:
                    ans = max(ans, a.rent*current_gameboard['bank'].monopolized_property_rent_factor) # charge twice the rent on unimproved monopolized properties.

        logger.debug('rent is calculated to be '+str(ans))
        return ans
    else:
        logger.debug('Player have no any asset, rent is calculated to be 0.')
        return(0)


def alternate_calculate_rent_based_on_dummy_location(asset, current_gameboard):
    if asset.name.startswith("dummy_loc_"):
        ans = _calc_max_rent_in_color_group(asset, current_gameboard)
        logger.debug(asset.name + " is a dummy location. Rent is max rent over properties owned by the player in that color provided the color group is monopolized."
                                  "Else the rent will be 0.")
        return ans
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
    return ans


def dice_insurance_reroll(from_player, to_player, action_params_dict, current_gameboard):
    """
    When the from_player decides to call this function, a flag gets activated in the _agent_memory. If this flag is true, then that
    means the player has insured its NEXT dice roll and will be allowed to roll a second time if it wishes to.
    :param from_player:
    :param to_player:
    :param action_params_dict:
    :param current_gameboard:
    :return:
    """
    if 'dice_insurance' in current_gameboard:
        from_player.agent._agent_memory['dice_insured'] = True
        from_player.agent._agent_memory['choice_list'] = action_params_dict['choice_list']
        from_player.charge_player(current_gameboard['dice_insurance'], current_gameboard, bank_flag=True)
        logger.debug(from_player.player_name + " paid the bank " + str(current_gameboard['dice_insurance']) + " to insure die roll.")
        # add to game history
        current_gameboard['history']['function'].append(from_player.charge_player)
        params = dict()
        params['self'] = from_player
        params['amount'] = current_gameboard['dice_insurance']
        params['description'] = 'dice roll insurance'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return action_choices.flag_config_dict['successful_action']

    else:
        logger.debug("Something is wrong with novelty injection routine....Raising Exception.")
        raise Exception


def insured_die_roll(die_objects, choice, current_gameboard):
    """
    The function takes a vector of Dice objects and for each object, samples a value. It returns a list of sampled die values.
    Note: for this novelty, since the player handle is not available in this function directly, we look at player status and
    check which player has "current_move" status. This means, this player is currently rolling the dice and will be able to re-roll
    if the dice was insured in its oot move for the given re-roll choice list (available in the agent memory).
    :param die_objects: A vector of Dice objects.
    :param choice: The numpy choice function.
    :return: the numbers that get rolled on the dice as a list.
    """
    logger.debug('rolling die...')

    #-------------------------novelty-----------------------
    reroll_flag = False
    current_move_player = None
    for p in current_gameboard['players']:
        if p.status == 'current_move':
            current_move_player = p
            if 'dice_insured' in p.agent._agent_memory:
                logger.debug(p.player_name + " has insured dice for this turn, will be allowed to re-roll based on re-roll conditions.")
                reroll_flag = True
    #-------------------------------------------------------

    reroll_count = 0
    max_reroll_number = 3
    output_vector = list()
    for d in die_objects:
        if d.die_state_distribution == 'uniform':
            output_vector.append(choice(a=d.die_state))
            # -------------------------novelty-----------------------
            # Note: additional die roll is just appended to existing output_vector, so that the sum will reflect the reroll
            if reroll_flag:
                while( current_gameboard['location_sequence'][sum(output_vector)].name in \
                        current_move_player.agent._agent_memory['choice_list'] and (reroll_count < max_reroll_number)):
                    logger.debug(current_move_player.player_name + " rerolling dice since dice is insured")
                    output_vector.pop()
                    output_vector.append(choice(a=d.die_state))
                    reroll_count += 1
                if reroll_count == max_reroll_number:
                    logger.debug(current_move_player.player_name + " cannot reroll dice because reroll_count is reached the max_reroll_number")
            # -------------------------------------------------------
        elif d.die_state_distribution == 'biased':
            output_vector.append(Dice.biased_die_roll(d.die_state, choice))
            # -------------------------novelty-----------------------
            if reroll_flag:
                if current_gameboard['location_sequence'][sum(output_vector)].name in \
                        current_move_player.agent._agent_memory['choice_list']:
                    logger.debug(current_move_player.player_name + " rerolling dice since dice is insured")
                    output_vector.append(Dice.biased_die_roll(d.die_state, choice))
            # -------------------------------------------------------
        else:
            logger.error("Exception")
            raise Exception
    """
    output_vector = list()
    for d in die_objects:
        if d.die_state_distribution == 'uniform':
            output_vector.append(choice(a=d.die_state))
            #-------------------------novelty-----------------------
            # Note: additional die roll is just appended to existing output_vector, so that the sum will reflect the reroll
            if reroll_flag:
                if current_gameboard['location_sequence'][sum(output_vector)].name in current_move_player.agent._agent_memory['choice_list']:
                    logger.debug(current_move_player.player_name + " rerolling dice since dice is insured")
                    output_vector.append(choice(a=d.die_state))
            #-------------------------------------------------------
        elif d.die_state_distribution == 'biased':
            output_vector.append(Dice.biased_die_roll(d.die_state, choice))
            #-------------------------novelty-----------------------
            if reroll_flag:
                if current_gameboard['location_sequence'][sum(output_vector)].name in current_move_player.agent._agent_memory['choice_list']:
                    logger.debug(current_move_player.player_name + " rerolling dice since dice is insured")
                    output_vector.append(Dice.biased_die_roll(d.die_state, choice))
            #-------------------------------------------------------
        else:
            logger.error("Exception")
            raise Exception

    """
    #-------------------------novelty-----------------------
    # dice insurance only valid for one post-roll move. Have to reinsure each time.
    if 'dice_insured' in current_move_player.agent._agent_memory:
        del current_move_player.agent._agent_memory['dice_insured']
    if 'choice_list' in current_move_player.agent._agent_memory:
        del current_move_player.agent._agent_memory['choice_list']
    #---------------------------------------------------------

    return output_vector


def pay_bank_save_money(from_player, to_player, action_params_dict, current_gameboard):
    """
    if the 'save_money_by_paying_bank' flag is true already, then it gets deactivated (by removing from agent memory) and the bank pays
    the player a percentage of what was paid by the player to the bank to make this action choice, else gets activated.
    :param from_player:
    :param to_player:
    :param action_params_dict:
    :param current_gameboard:
    :return:
    """
    if current_gameboard['location_sequence'][from_player.current_position].loc_class != 'real_estate' and \
        current_gameboard['location_sequence'][from_player.current_position].loc_class != 'railroad' and \
        current_gameboard['location_sequence'][from_player.current_position].loc_class != 'utility':
        logger.debug('Location needs to be a real estate/railroad/utility location to execute this action choice.')
        return action_choices.flag_config_dict['failure_code']

    if current_gameboard['location_sequence'][from_player.current_position].owned_by == from_player:
        property_name = current_gameboard['location_sequence'][from_player.current_position].name
        if 'save_money_by_paying_bank' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['save_money_by_paying_bank'] = dict()

        if 'save_money_by_paying_bank' in from_player.agent._agent_memory and property_name in from_player.agent._agent_memory['save_money_by_paying_bank']\
                and from_player.agent._agent_memory['save_money_by_paying_bank'][property_name]:
            del from_player.agent._agent_memory['save_money_by_paying_bank'][property_name]
            return_amt = current_gameboard['save_amt']*current_gameboard['return_perc']
            from_player.receive_cash(return_amt, current_gameboard, bank_flag=True)
            logger.debug("Bank paid " + from_player.player_name + " " + str(return_amt) + " for deactivating action choice - 'pay bank and save money on rents' on " +
                         property_name)
            # add to game history
            current_gameboard['history']['function'].append(from_player.receive_cash)
            params = dict()
            params['self'] = from_player
            params['amount'] = return_amt
            params['description'] = 'return save amount on rents'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        else:
            from_player.agent._agent_memory['save_money_by_paying_bank'][property_name] = True
            from_player.charge_player(current_gameboard['save_amt'], current_gameboard, bank_flag=True)
            logger.debug(from_player.player_name + " paid the bank "+ str(current_gameboard['save_amt']) + " for activating action choice - 'pay bank and save money on rents' on "+
                         property_name)
            # add to game history
            current_gameboard['history']['function'].append(from_player.charge_player)
            params = dict()
            params['self'] = from_player
            params['amount'] = current_gameboard['save_amt']
            params['description'] = 'save amount on rents'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return action_choices.flag_config_dict['successful_action']
    else:
        logger.debug(from_player.player_name + " does not own this location. Cannot execute this action.")
        return action_choices.flag_config_dict['failure_code']


def alternate_pay_rent(self, current_gameboard):
    current_loc = current_gameboard['location_sequence'][self.current_position]
    logger.debug('calculating and paying rent dues for '+ self.player_name+ ' who is in property '+current_loc.name+' which is owned by '+current_loc.owned_by.player_name)
    rent = RealEstateLocation.calculate_rent(current_loc, current_gameboard)
    # add to game history
    current_gameboard['history']['function'].append(RealEstateLocation.calculate_rent)
    params = dict()
    params['asset'] = current_loc
    params['current_gameboard'] = current_gameboard
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(rent)
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

    recipient = current_loc.owned_by
    #-----------------------------novelty------------------------------------------
    save_amt = 0
    current_loc_name = current_loc.name
    if 'save_amt' not in current_gameboard or 'save_perc' not in current_gameboard:
        logger.debug("Something wrong with novelty injection.")
        raise Exception
    if 'save_money_by_paying_bank' in recipient.agent._agent_memory and current_loc_name in recipient.agent._agent_memory['save_money_by_paying_bank'] \
            and recipient.agent._agent_memory['save_money_by_paying_bank'][current_loc_name]:
        save_amt = current_gameboard['save_amt']*current_gameboard['save_perc']
        logger.debug('calculated save amount due to arbitrary action choice to be ' + str(save_amt))
    #------------------------------------------------------------------------------
    code = recipient.receive_cash(rent+save_amt, current_gameboard, bank_flag=False)
    # add to game history
    if code == action_choices.flag_config_dict['successful_action']:
        current_gameboard['history']['function'].append(recipient.receive_cash)
        params = dict()
        params['self'] = recipient
        params['amount'] = rent+save_amt
        params['description'] = 'rent'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
    else:
        logger.debug("Not sure what happened! Something broke!")
        logger.error("Exception")
        raise Exception

    self.charge_player(rent+save_amt, current_gameboard, bank_flag=False)
    # add to game history
    current_gameboard['history']['function'].append(self.charge_player)
    params = dict()
    params['self'] = self
    params['amount'] = rent+save_amt
    params['description'] = 'rent'
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


def connect_properties(from_player, to_player, action_params_dict, current_gameboard):
    """
    if player is currently on a location owned by it when invoking this action choice then, it can directly tunnel to the location destination
    specified in the arbitrary action choice action_params_dict.
    Note: even if agent decides to tunnel the player to same location as it is on currently, the action will be executed and player will be charged
    although technically the player has not moved. Its the agents responsibility to tunnel to different location and not waste the action choice chance.
    :param from_player:
    :param to_player:
    :param action_params_dict:
    :param current_gameboard:
    :return:process_move_consequences_rent_agreement
    """
    if current_gameboard['location_sequence'][from_player.current_position].loc_class != 'real_estate' and \
        current_gameboard['location_sequence'][from_player.current_position].loc_class != 'railroad' and \
        current_gameboard['location_sequence'][from_player.current_position].loc_class != 'utility':
        logger.debug('Location needs to be a real estate/railroad/utility location to execute this action choice.')
        return action_choices.flag_config_dict['failure_code']

    if 'tunneling_fee' in current_gameboard:
        if current_gameboard['location_sequence'][from_player.current_position].owned_by == from_player and action_params_dict['location'] in from_player.assets:
            _move_player__check_for_go(from_player, action_params_dict['location'].start_position, current_gameboard)

            # add by Peter: -----------------------
            # RailroadLocation and UtilityLocation have no rent
            # change: if no rent, then rent = 0
            try:
                dues = action_params_dict['location'].rent + current_gameboard['tunneling_fee']
            except:
                dues = current_gameboard['tunneling_fee']
            # -----------------------
            #dues = action_params_dict['location'].rent + current_gameboard['tunneling_fee']
            from_player.charge_player(dues, current_gameboard, bank_flag=True)
            logger.debug(from_player.player_name + " has tunneled to " + action_params_dict['location'].name + " and paid dues for the same.")
            # add to game history
            current_gameboard['history']['function'].append(from_player.charge_player)
            params = dict()
            params['self'] = from_player
            params['amount'] = dues
            params['description'] = 'tunneling dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            return action_choices.flag_config_dict['successful_action']
        else:
            logger.debug("Either current location not owned by the player or " + action_params_dict['location'].name + " not in player assets. Cannot tunnel to that destination.")
            return action_choices.flag_config_dict['failure_code']
    else:
        logger.debug("Something is wrong with novelty injection routine....Raising Exception.")
        raise Exception


def rent_and_tax_exemptions(from_player, to_player, action_params_dict, current_gameboard):
    if 'turns' in from_player.agent._agent_memory and from_player.agent._agent_memory['turns'] > 0:
        logger.debug(from_player.player_name + " has already requested for this action, wait until the turns are over to make this action choice again.")
        return action_choices.flag_config_dict['failure_code']
    else:
        from_player.agent._agent_memory['turns'] = current_gameboard['turns']
        logger.debug(from_player.player_name + " has invoked rent and tax exemption arbitrary action.")
        if 'auxiliary_check_for_go' not in current_gameboard:
            current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], "_decrement_rent_and_tax_exemptions_turns")
        return action_choices.flag_config_dict['successful_action']


def _decrement_rent_and_tax_exemptions_turns(player, new_position, current_gameboard):
    if 'turns' in player.agent._agent_memory and player.agent._agent_memory['turns'] > 0:
        logger.debug(player.player_name + " passed Go, decrementing turns for rent and tax exemption.")
        player.agent._agent_memory['turns'] -= 1
        if player.agent._agent_memory['turns'] == 0:
            del player.agent._agent_memory['turns']


def alt_func_Realestate(asset, current_gameboard):
    asset_owner = asset.owned_by
    if 'turns' in asset_owner.agent._agent_memory and asset_owner.agent._agent_memory['turns'] > 0:
        logger.debug(asset_owner.player_name + " seeking tax exemption by not charging rent. Thus rent = 0.")
        return 0
    else:
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
        return ans


def alt_func_Railroad(asset, current_gameboard):
    asset_owner = asset.owned_by
    if 'turns' in asset_owner.agent._agent_memory and asset_owner.agent._agent_memory['turns'] > 0:
        logger.debug(asset_owner.player_name + " seeking tax exemption by not charging railroad dues. Thus dues = 0.")
        return 0
    else:
        logger.debug('calculating railroad dues for '+asset.name)
        if asset.owned_by.num_railroads_possessed > 4 or asset.owned_by.num_railroads_possessed < 0:
            logger.debug('Error! num railroads possessed by '+ asset.owned_by.player_name+ ' is '+ \
                str(asset.owned_by.num_railroads_possessed)+', which is impossible')

            logger.error("Exception")
            raise Exception
        dues = asset._railroad_dues[asset.owned_by.num_railroads_possessed]

        logger.debug('railroad dues are '+str(dues))
        return dues


def alt_func_Utility(asset, current_gameboard, die_total):
    asset_owner = asset.owned_by
    if 'turns' in asset_owner.agent._agent_memory and asset_owner.agent._agent_memory['turns'] > 0:
        logger.debug(asset_owner.player_name + " seeking tax exemption by not charging utility dues. Thus dues = 0.")
        return 0
    else:
        logger.debug('calculating utility dues for '+ asset.name)
        if asset.owned_by.num_utilities_possessed > 2 or asset.owned_by.num_utilities_possessed < 0:
                logger.debug('Error! num utilities possessed by '+asset.owned_by.player_name+' is '+ \
                    str(asset.owned_by.num_utilities_possessed)+ ', which is impossible')

                logger.error("Exception")
                raise Exception

        dues = die_total*asset._die_multiples[asset.owned_by.num_utilities_possessed]
        logger.debug('utility dues are '+ str(dues))
        return dues


def alternate_func_IncomeTax(location, player, current_gameboard):
    if location.name == 'Income Tax' and 'turns' in player.agent._agent_memory and player.agent._agent_memory['turns'] > 0:
        logger.debug(player.player_name + " will not be charged income tax since it is not charging rent on its properties.")
        return 0
    return location.amount_due


def auction_holding(from_player, to_player, action_params_dict, current_gameboard):
    """
    only auction on one property can be held off by paying the amount for x number of turns. If someone else lands on it meanwhile and decides to
    buy it, then the player loses its right to hold off the auction.
    :param from_player:
    :param to_player:
    :param action_params_dict:
    :param current_gameboard:
    :return:
    """

    # add by Peter -----------------------
    if action_params_dict['location'].loc_class != 'real_estate' and \
        action_params_dict['location'].loc_class != 'railroad' and \
        action_params_dict['location'].loc_class != 'utility':
        logger.debug('Location needs to be a real estate/railroad/utility location to execute this action choice.')
        return action_choices.flag_config_dict['failure_code']
    # -----------------------


    if 'auction_hold' not in from_player.agent._agent_memory or from_player.agent._agent_memory['auction_hold']['turns'] <= 0:
        from_player.agent._agent_memory['auction_hold'] = dict()
        from_player.agent._agent_memory['auction_hold']['turns'] = current_gameboard['turns']
        from_player.agent._agent_memory['auction_hold']['auction_location'] = action_params_dict['location']
        logger.debug(from_player.player_name + " has placed an auction hold on " + action_params_dict['location'].name)
        if 'auxiliary_check_for_go' not in current_gameboard:
            current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], "_aux_go_auction_hold")
        return action_choices.flag_config_dict['successful_action']
    else:
        logger.debug(from_player.player_name + " already has a held of an auction. Wait for this to clear up before putting up another auction hold.")
        return action_choices.flag_config_dict['failure_code']


def _aux_go_auction_hold(player, new_position, current_gameboard):
    if 'auction_hold' in player.agent._agent_memory and player.agent._agent_memory['auction_hold']['turns'] > 0:
        if player.agent._agent_memory['auction_hold']['auction_location'].owned_by == current_gameboard['bank']:
            dues = current_gameboard['auction_hold_amt']
            player.charge_player(dues, current_gameboard, bank_flag=True)
            logger.debug(player.player_name + " has paid auction hold fee.")
            # add to game history
            current_gameboard['history']['function'].append(player.charge_player)
            params = dict()
            params['self'] = player
            params['amount'] = dues
            params['description'] = 'auction hold dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            player.agent._agent_memory['auction_hold']['turns'] -= 1
            # since _own_or_auction is reassigned to the new function, the new function will now be called where player can decide if it wants to buy the property/auction
            player._own_or_auction(current_gameboard, current_gameboard['location_sequence'][player.agent._agent_memory['auction_hold']['auction_location'].start_position])

            # if the player held off the auction for "turns" number of times or finally decided to auction the property, then auction_hold is invalidated
            if player.agent._agent_memory['auction_hold']['turns'] == 0 or player.agent._agent_memory['auction_hold']['auction_location'].owned_by != current_gameboard['bank']:
                del player.agent._agent_memory['auction_hold']


def alt_own_or_auction(self, current_gameboard, asset):
    logger.debug('Executing _own_or_auction for '+self.player_name)

    dec = self.agent.make_buy_property_decision(self, current_gameboard, asset) # your agent has to make a decision here
    # add to game history
    current_gameboard['history']['function'].append(self.agent.make_buy_property_decision)
    params = dict()
    params['asset'] = asset
    params['player'] = self
    params['current_gameboard'] = current_gameboard
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(dec)
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

    logger.debug(self.player_name+' decides to purchase? '+str(dec))
    if dec is True:
        asset.update_asset_owner(self, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(asset.update_asset_owner)
        params = dict()
        params['self'] = asset
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return
    else:
        #--------------------novelty-----------------------------------------
        if 'auction_hold' in self.agent._agent_memory and self.agent._agent_memory['auction_hold']['auction_location'] == asset \
                and self.agent._agent_memory['auction_hold']['turns'] > 0:
            logger.debug("Auction being held of since player has agreed to pay auction hold fee.")
            return
        #--------------------------------------------------------------------
        logger.debug('Since '+self.player_name+' decided not to purchase, we are invoking auction proceedings for asset '+asset.name)
        index_current_player = current_gameboard['players'].index(self)  # in players, find the index of the current player
        starting_player_index = (index_current_player + 1) % len(current_gameboard['players'])  # the next player's index. this player will start the auction
        # the auction function will automatically check whether the player is still active or not etc. We don't need to
        # worry about conducting a valid auction in this function.
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
        return


def max_house_player_charges_tax(from_player, to_player, action_params_dict, current_gameboard):
    """
    :param from_player:
    :param to_player:
    :param action_params_dict:
    :param current_gameboard:
    :return:
    """
    player_num_houses = from_player.num_total_houses
    player_with_max_houses = from_player
    for p in current_gameboard['players']:
        if p != from_player and p.status != 'lost' and p.num_total_houses > player_num_houses:
            player_num_houses = p.num_total_houses
            player_with_max_houses = p

    if from_player != player_with_max_houses:
        logger.debug(from_player.player_name + " does not have the max number of houses. Cannot execute action choice. Returning failure code.")
        if 'max_house_taxation' in from_player.agent._agent_memory:
            logger.debug("rRemoving max_house_taxation key for player as it does not own max num of houses. ")
            del from_player.agent._agent_memory['max_house_taxation']
        return action_choices.flag_config_dict['failure_code']
    elif 'max_house_taxation' in from_player.agent._agent_memory:
        logger.debug(from_player.player_name + " already is charging taxes on other player improvements.")
        return action_choices.flag_config_dict['successful_action']
    else:
        from_player.agent._agent_memory['max_house_taxation'] = True
        logger.debug("Set max house taxation flag")
        if 'auxiliary_check_for_go' not in current_gameboard:       #player will be charged a tax perc of wealth when passing go if max_house_taxaxtion flag is True
            current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], "_charge_tax_since_player_charges_max_house_tax")
        logger.debug(from_player.player_name + " can now charge taxes on other player property improvements.")
        return action_choices.flag_config_dict['successful_action']


def _charge_tax_since_player_charges_max_house_tax(player, pos, current_gameboard):
    if 'max_house_taxation' in player.agent._agent_memory:
        _charge_net_worth_tax(player, current_gameboard)


def _charge_net_worth_tax(player, current_gameboard):
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
    tax_charged = networth_p1ayer*current_gameboard['tax_perc']
    player.charge_player(tax_charged, current_gameboard, bank_flag=True)
    logger.debug(player.player_name + ' is being charged a wealth tax '+str(tax_charged)+' for properties owned.')
    current_gameboard['history']['function'].append(player.charge_player)
    params = dict()
    params['self'] = player
    params['amount'] = tax_charged
    params['description'] = 'wealth tax'
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

def alternate_improve_property(player, asset, current_gameboard, add_house=True, add_hotel=False):
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

                #-------------------------------novelty--------------------------
                for p in current_gameboard['players']:
                    if 'max_house_taxaxtion' in p.agent._agent_memory:
                        if p == player:
                            logger.debug("This player himself has the max number of houses. No taxes")
                        else:
                            dues_tax = asset.price_per_house*current_gameboard['max_house_tax']
                            player.charge_player(dues_tax, current_gameboard, bank_flag=False)
                            logger.debug(player.player_name + " has paid tax on improvement to player with highest num of houses.")
                            # add to game history
                            current_gameboard['history']['function'].append(player.charge_player)
                            params = dict()
                            params['self'] = player
                            params['amount'] = dues_tax
                            params['description'] = 'improvements tax'
                            current_gameboard['history']['param'].append(params)
                            current_gameboard['history']['return'].append(None)
                            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                            p.receive_cash(dues_tax, current_gameboard, bank_flag=False)
                            logger.debug(p.player_name + " has receieved tax on improvement from player since it has highest num of houses.")
                            # add to game history
                            current_gameboard['history']['function'].append(p.receive_cash)
                            params = dict()
                            params['self'] = p
                            params['amount'] = dues_tax
                            params['description'] = 'improvements tax'
                            current_gameboard['history']['param'].append(params)
                            current_gameboard['history']['return'].append(None)
                            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                            # also recalculate which player now has max num of houses, if the new player has max num,
                            # then del max_house_taxaxtion key from agent_memory of old player
                            if player.num_total_houses > p.num_total_houses:
                                logger.debug(player.player_name + " has more num of houses than " + p.player_name + " and so max_house_taxaxtion key deleted for " +
                                             p.player_name)
                                del p.agent._agent_memory['max_house_taxaxtion']
                #--------------------------------------------------------------------------------------------
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

def reverse_improve_property(player, asset, current_gameboard, add_house=True, add_hotel=False):
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

    if add_hotel:
        logger.debug('Looking to improve '+asset.name+' by adding a hotel.')
        # ----------------------novelty----------------------------
        if asset.num_houses > 0 or asset.num_hotels == current_gameboard['bank'].hotel_limit:
            logger.debug('There is already a house here or you have built the max number of hotels that you can on a property. '
                         'You are not permitted another house. Returning failure code')
            return flag_config_dict['failure_code']
        flag = True
        current_asset_num_hotels = asset.num_hotels
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if same_colored_asset.num_hotels < current_asset_num_hotels or same_colored_asset.num_houses > 0:
                flag = False
                break
        # ----------------------------------------------------------
        if flag:
            if current_gameboard['bank'].improvement_possible(player, asset, current_gameboard, add_house=False, add_hotel=True):
                logger.debug('Improving asset and updating num_total_hotels and num_total_houses. Currently property has ' + str(asset.num_hotels))
                player.num_total_hotels += 1
                # ----------------------novelty----------------------------
                #player.num_total_houses -= asset.num_houses
                # ----------------------------------------------------------
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
                # ----------------------novelty----------------------------
                # asset.num_houses = 0
                # ----------------------------------------------------------
                asset.num_hotels += 1
                logger.debug('Player has successfully improved property. Returning successful action code')
                return flag_config_dict['successful_action']

            else:
                logger.debug('Bank has no hotels left for purchase. Kindly wait till someone returns a hotel to the bank.')
                return flag_config_dict['failure_code']

        else:
            logger.debug('All same-colored properties must be uniformly improved first before you can build a hotel on this property. Returning failure code')
            logger.debug(player.player_name + ' now has num_total_hotels ' + str(
                player.num_total_hotels) + ' and num_total_houses ' + str(player.num_total_houses))
            return flag_config_dict['failure_code']

    elif add_house:
        logger.debug('Looking to improve '+asset.name+' by adding a house. Currently property has ' + str(asset.num_houses))
        # ----------------------novelty-----------------------------
        if asset.num_houses == current_gameboard['bank'].house_limit_before_hotel:
            logger.debug('There is already ' + str(current_gameboard['bank'].house_limit_before_hotel) + ' houses(s) here. You cannot exceed this limit. Returning failure code')
            return flag_config_dict['failure_code']
        elif asset.num_houses == 0 and asset.num_hotels != current_gameboard['bank'].hotel_limit:
            logger.debug('You need to have ' + str(current_gameboard['bank'].hotel_limit)
                         + ' hotels before you can build a house...Returning failure code')
            return flag_config_dict['failure_code']
        flag = True
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if asset.num_houses == 0 and not (same_colored_asset.num_hotels == current_gameboard['bank'].hotel_limit
                    or same_colored_asset.num_houses == current_gameboard['bank'].house_limit_before_hotel): # as long as all other hotels
                # of that color have either max limit of hotels before house can be built or a house, we can build a house on this asset. (Uniform improvement rule)
                flag = False
                break
            elif same_colored_asset.num_houses < asset.num_houses:
                flag = False
                break
        # ----------------------------------------------------------
        if flag:
            if current_gameboard['bank'].improvement_possible(player, asset, current_gameboard, add_house=True, add_hotel=False):
                logger.debug('Improving asset and updating num_total_houses.')
                player.num_total_houses += 1
                # ----------------------novelty----------------------------
                if asset.num_houses == 0:
                    player.num_total_hotels -= 1
                #print(player.num_total_hotels)
                #print(player.num_total_houses)
                #print('=')
                # ----------------------------------------------------------
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
                # ----------------------novelty----------------------------
                asset.num_hotels = 0
                # ----------------------------------------------------------
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


def exchange_properties(from_player, to_player, action_params_dict, current_gameboard):
    if to_player.status == 'lost':
        logger.debug("Exchange action made with a player that has lost the game. Returning failure code.")
        return flag_config_dict['failure_code']

    from_player_assets = set()
    from_player_amt = float(0)

    if len(from_player.assets) > 0:
        for loc in from_player.assets:
            from_player_assets.add(loc.name)

    to_player_assets = set()
    to_player_amt = float(0)

    if len(to_player.assets) > 0:
        for loc in to_player.assets:
            to_player_assets.add(loc.name)

    for p in current_gameboard['location_sequence']:
        if p.name in from_player_assets:
            logger.debug(p.name + " is owned by " + p.owned_by.player_name + ". Transferring property to " + to_player.player_name)
            p.update_asset_owner(to_player, current_gameboard)
            from_player_amt += p.price
            from_player_assets.remove(p.name)
        elif p.name in to_player_assets:
            logger.debug(p.name + " is owned by " + p.owned_by.player_name + ". Transferring property to " + from_player.player_name)
            p.update_asset_owner(from_player, current_gameboard)
            to_player_amt += p.price
            to_player_assets.remove(p.name)

    if len(from_player_assets) > 0 or len(to_player_assets) > 0:
        logger.debug("Something wrong with exchanging properties.")
        raise Exception

    else:
        logger.debug(from_player.player_name + " is charged a transfer fee that has to  paid to the bank.")
        from_player.charge_player(current_gameboard['transfer_fee'], current_gameboard, bank_flag=True)
        logger.debug(from_player.player_name + " has paid property transfer fee to the bank.")
        # add to game history
        current_gameboard['history']['function'].append(from_player.charge_player)
        params = dict()
        params['self'] = from_player
        params['amount'] = current_gameboard['transfer_fee']
        params['description'] = 'property transfer fee'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        if from_player_amt > to_player_amt:
            dues = from_player_amt - to_player_amt
            to_player.charge_player(dues, current_gameboard, bank_flag=False)
            logger.debug(to_player.player_name + " has paid property exchange amount to " + from_player.player_name + " since it got properties of more value than it"
                                                                                                                      " already had.")
            # add to game history
            current_gameboard['history']['function'].append(to_player.charge_player)
            params = dict()
            params['self'] = to_player
            params['amount'] = dues
            params['description'] = 'property transfer fee'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            from_player.receive_cash(dues, current_gameboard, bank_flag=False)
            logger.debug(from_player.player_name + " has receieved property exchange amount from " + to_player.player_name + " as it offered properties of higher value.")
            # add to game history
            current_gameboard['history']['function'].append(from_player.receive_cash)
            params = dict()
            params['self'] = from_player
            params['amount'] = dues
            params['description'] = 'improvements tax'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        elif from_player_amt < to_player_amt:
            dues = to_player_amt - from_player_amt
            from_player.charge_player(dues, current_gameboard, bank_flag=False)
            logger.debug(from_player.player_name + " has paid property exchange amount to " + to_player.player_name + " since it got properties of more value than it"
                                                                                                                      " already had.")
            # add to game history
            current_gameboard['history']['function'].append(from_player.charge_player)
            params = dict()
            params['self'] = from_player
            params['amount'] = dues
            params['description'] = 'property transfer fee'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            to_player.receive_cash(dues, current_gameboard, bank_flag=False)
            logger.debug(to_player.player_name + " has receieved property exchange amount from " + from_player.player_name + " as it offered properties of higher value.")
            # add to game history
            current_gameboard['history']['function'].append(to_player.receive_cash)
            params = dict()
            params['self'] = to_player
            params['amount'] = dues
            params['description'] = 'improvements tax'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        else:
            logger.debug("Both players has properties of equal net value, no cash exchange involved for property exchange.")

        logger.debug("Properties have been exchanged between " + from_player.player_name + " and " + to_player.player_name)
        return flag_config_dict['successful_action']


# --------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------Relations----------------------------------------------------------------------------


def _set_to_sorted_list_func(set_cards):
    cc_card_dict = dict()
    while len(set_cards) != 0:
        popped_card = set_cards.pop()
        try:
            cc_card_dict[str(popped_card.name)].append(popped_card)
        except:
            cc_card_dict[str(popped_card.name)] = [popped_card]
    list_cards = []

    for sorted_key in sorted(cc_card_dict):   #sorts dictionary based on dict keys
        for j in range(len(cc_card_dict[sorted_key])):
            list_cards.append(cc_card_dict[sorted_key][j])
    return list_cards


def pick_card_from_community_chest_temp(player, current_gameboard):
    """
    Pick the card  from the community chest pack and execute the action
    Note: get_out_of_jail_free card is treated a little differently, since we must remove it from the card pack.
    :param player: an instance of Player. This is the player that will be picking the card.
    :param current_gameboard: A dict. The global gameboard data structure
    :return: None
    """
    logger.debug(player.player_name+' is picking card from community chest.')
    card_rand = np.random.RandomState(current_gameboard['card_seed'])
    set_cc_cards_copy = current_gameboard['community_chest_cards'].copy()
    list_community_chest_cards = _set_to_sorted_list_func(set_cc_cards_copy)
    card = card_rand.choice(list_community_chest_cards)
    current_gameboard['picked_community_chest_cards'].append(current_gameboard['community_chest_card_objects'][card.name])
    # card = card_rand.choice(list(current_gameboard['community_chest_cards']))
    current_gameboard['card_seed'] += 1
    logger.debug(player.player_name+' picked card '+card.name)
    if card.name == 'get_out_of_jail_free':
        logger.debug('removing get_out_of_jail card from community chest pack')
        current_gameboard['community_chest_cards'].remove(card)
        card.action(player, card, current_gameboard, pack='community_chest')

        current_gameboard['history']['function'].append(card.action)
        params = dict()
        params['player'] = player
        params['card'] = card
        params['current_gameboard'] = current_gameboard
        params['pack'] = 'community_chest'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
    else:    # apply the card action to all players
        #---------------------------novelty---------------------------------------------------
        logger.debug("This action is now applied to all players")
        for p in current_gameboard['players']:
            if p.status != 'lost':
                card.action(p, card, current_gameboard) # all card actions except get out of jail free must take this signature
                # add to game history
                current_gameboard['history']['function'].append(card.action)
                params = dict()
                params['player'] = p
                params['card'] = card
                params['current_gameboard'] = current_gameboard
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])



def pick_card_from_chance_temp(player, current_gameboard):
    """
    Pick the card  from the chance pack and execute the action
    Note: get_out_of_jail_free card is treated a little differently, since we must remove it from the card pack.
    :param player: an instance of Player. This is the player that will be picking the card.
    :param current_gameboard: A dict. The global gameboard data structure
    :return: None
    """
    logger.debug(player.player_name+ ' is picking card from chance.')
    card_rand = np.random.RandomState(current_gameboard['card_seed'])
    set_chance_cards_copy = current_gameboard['chance_cards'].copy()
    list_chance_cards = _set_to_sorted_list_func(set_chance_cards_copy)
    card = card_rand.choice(list_chance_cards)
    current_gameboard['picked_chance_cards'].append(current_gameboard['chance_card_objects'][card.name])
    # card = card_rand.choice(list(current_gameboard['chance_cards']))
    current_gameboard['card_seed'] += 1
    logger.debug(player.player_name+ ' picked card '+ card.name)
    if card.name == 'get_out_of_jail_free':
        logger.debug('removing get_out_of_jail card from chance pack')
        current_gameboard['chance_cards'].remove(card)
        card.action(player, card, current_gameboard, pack='chance')
        current_gameboard['history']['function'].append(card.action)
        params = dict()
        params['player'] = player
        params['card'] = card
        params['current_gameboard'] = current_gameboard
        params['pack'] = 'chance'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
    else:    # apply the card action to all players
        #---------------------------novelty---------------------------------------------------
        logger.debug("This action is now applied to all players")
        for p in current_gameboard['players']:
            if p.status != 'lost':
                card.action(p, card, current_gameboard) # all card actions except get out of jail free must take this signature
                # add to game history
                current_gameboard['history']['function'].append(card.action)
                params = dict()
                params['player'] = p
                params['card'] = card
                params['current_gameboard'] = current_gameboard
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


def process_move_consequences_temp(self, current_gameboard):
    current_location = current_gameboard['location_sequence'][self.current_position] # get the Location object corresponding to player's current position
    if current_location.loc_class == 'do_nothing': # we now look at each location class case by case
        logger.debug(self.player_name+' is on a do_nothing location, namely '+current_location.name+'. Nothing to process. Returning...')
        return
    elif current_location.loc_class == 'real_estate':
        logger.debug(self.player_name+ ' is on a real estate location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+' is owned by Bank. Setting _option_to_buy to true for '+self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+current_location.owned_by.player_name+' and is not mortgaged. Proceeding to calculate and pay rent.')
            self.calculate_and_pay_rent_dues(current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(self.calculate_and_pay_rent_dues)
            params = dict()
            params['self'] = self
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            return
    elif current_location.loc_class == 'tax':
        logger.debug(self.player_name+ ' is on a tax location, namely '+ current_location.name+ '. Deducting tax...')
        tax_due = TaxLocation.calculate_tax(current_location, self, current_gameboard)
        self.charge_player(tax_due, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(self.charge_player)
        params = dict()
        params['self'] = self
        params['amount'] = tax_due
        params['description'] = 'tax'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return
    elif current_location.loc_class == 'railroad':
        logger.debug(self.player_name+ ' is on a railroad location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = RailroadLocation.calculate_railroad_dues(current_location, current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(RailroadLocation.calculate_railroad_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            recipient = current_location.owned_by
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of railroads'] = recipient.num_railroads_possessed
                params['description'] = 'railroad dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of railroads'] = recipient.num_railroads_possessed
            params['description'] = 'railroad dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    #----------------------novelty--------------------------------------------------------------------------
    elif current_location.loc_class == 'utility':
        logger.debug(self.player_name+ ' is on a utility location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name + ' is owned by ' + current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = UtilityLocation.calculate_utility_dues(current_location, current_gameboard, current_gameboard['current_die_total'])
            # add to game history
            current_gameboard['history']['function'].append(UtilityLocation.calculate_utility_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            params['die_total'] = current_gameboard['current_die_total']
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            #-----------novelty------------------------------
            # the owner of property will pay rent to the player that lands on his utility
            recipient = self
            player_that_gets_charged = current_location.owned_by    # utility owner gets charged the rent

            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                logger.debug(self.player_name + " received cash upon landing on utility.")
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of utilities'] = player_that_gets_charged.num_utilities_possessed
                params['description'] = 'utility dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            player_that_gets_charged.charge_player(dues, current_gameboard, bank_flag=False)
            logger.debug(player_that_gets_charged.player_name + " paid rent when " + self.player_name + " landed on this property.")
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = player_that_gets_charged
            params['amount'] = dues
            params['number of utilities'] = player_that_gets_charged.num_utilities_possessed
            params['description'] = 'utility dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return
    elif current_location.loc_class == 'action':
        logger.debug(self.player_name+ ' is on an action location, namely '+ current_location.name+ '. Performing action...')
        current_location.perform_action(self, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(current_location.perform_action)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return
    else:
        logger.error(self.player_name+' is on an unidentified location type. Raising exception.')
        logger.error("Exception")
        raise Exception


def alternate_tax_calc_based_on_property_ownership(location, player, current_gameboard):
    """
    Tax is calculated based on property ownership. Player pays as tax the highest rent (possibly with improvement)
    over all properties that it owns. If player has no properties, then it does not pay taxes.
    (Applicable for both tax locations)
    :param location:
    :param player:
    :param current_gameboard:
    :return:
    """
    if len(player.assets) == 0:
        return 0

    else:
        max_rent = 0.0
        for a in player.assets:
            if a.loc_class == 'real_estate':
                if a.num_hotels > 0:
                    max_rent = max(max_rent, a.rent_hotel)
                elif a.num_houses > 0:
                    max_rent = max(max_rent, a._house_rent_dict[a.num_houses])
                elif a.color in player.full_color_sets_possessed:
                    max_rent = max(max_rent, a.rent*current_gameboard['bank'].monopolized_property_rent_factor)
                else:
                    max_rent = max(max_rent, a.rent)
            elif a.loc_class == 'railroad':
                max_rent = max(max_rent, a._railroad_dues[a.owned_by.num_railroads_possessed])
            elif a.loc_class == 'utility':
                if player.num_utilities_possessed == 1:
                    max_rent = max(max_rent, 4*12)  # max die total can be 6+6
                elif player.num_utilities_possessed == 2:
                    max_rent = max(max_rent, 10*12)  # max die total can be 6+6
        logger.debug("Max rent that can collected by player is " + str(max_rent))
        return max_rent


def alternate_rent_calc_based_on_max_rent(asset, current_gameboard):
    """
    Real estate property rent of a monopolized color group will be equal to max rent in that color group
    :param asset:
    :param current_gameboard:
    :return:
    """
    logger.debug('calculating rent for '+asset.name)
    max_rent = float(asset.rent) # unimproved-non-monopolized rent (the default)
    asset_owned_by = asset.owned_by
    if asset.color in asset_owned_by.full_color_sets_possessed:
        for a in asset_owned_by.assets:
            if a.color == asset.color:      # also takes care of the current asset when a == asset
                if a.num_hotels > 0:
                    max_rent = max(max_rent, a.rent_hotel)
                elif a.num_houses > 0:
                    max_rent = max(max_rent, a._house_rent_dict[a.num_houses])
                else:
                    max_rent = max(max_rent, a.rent*current_gameboard['bank'].monopolized_property_rent_factor)
    logger.debug('Max rent is calculated to be ' + str(max_rent))
    return max_rent


def alternate_improve_property(player, asset, current_gameboard, add_house=True, add_hotel=False):
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

        #---------------------novelty------------------------------
        elif asset.num_hotels == 0 and asset.num_houses != 0:
            logger.debug('Houses are being set up, cannot setup hotel after houses...Returning failure code')
            return flag_config_dict['failure_code']
        flag = True
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if asset.num_hotels == 0 and not (same_colored_asset.num_houses == 0 or same_colored_asset.num_hotels == 1): # as long as all other houses
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
                player.charge_player(asset.price_per_house*5, current_gameboard, bank_flag=True)
                current_gameboard['bank'].total_hotels -= 1
                current_gameboard['bank'].total_houses += asset.num_houses
                logger.debug('Bank now has ' + str(current_gameboard['bank'].total_houses) + ' houses and ' + str(current_gameboard['bank'].total_hotels) + ' hotels left.')
                # add to game history
                current_gameboard['history']['function'].append(player.charge_player)
                params = dict()
                params['self'] = player
                params['amount'] = asset.price_per_house*5
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
        if asset.num_hotels == 0 or asset.num_houses == current_gameboard['bank'].house_limit_before_hotel:
            logger.debug('Hotels(s) have to be built before houses or you have built the max number of houses that you can on a property. '
                         'You are not permitted another house. Returning failure code')
            return flag_config_dict['failure_code']
        flag = True
        current_asset_num_houses = asset.num_houses

        #-------------------novelty---------------------------
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if same_colored_asset.num_hotels == 0 and same_colored_asset.num_houses < current_asset_num_houses:
                flag = False
                break
            if same_colored_asset.num_hotels == 1 and current_asset_num_houses > 1:
                flag = False
                break
        if flag:
            if current_gameboard['bank'].improvement_possible(player, asset, current_gameboard, add_house=True, add_hotel=False):
                logger.debug('Improving asset and updating num_total_houses.')
                player.num_total_houses += 1
                player.num_total_hotels -= asset.num_hotels
                logger.debug(player.player_name+ ' now has num_total_hotels '+ str(
                    player.num_total_hotels)+ ' and num_total_houses '+ str(player.num_total_houses))
                logger.debug('Charging player for improvements.')
                player.charge_player(asset.price_per_house, current_gameboard, bank_flag=True)
                current_gameboard['bank'].total_houses -= 1
                current_gameboard['bank'].total_hotels += asset.num_hotels
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
                asset.num_hotels = 0
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


def alternate_move_player_on_landing_GO(self, new_position, current_gameboard):
    logger.debug('Player is currently in position '+current_gameboard['location_sequence'][self.current_position].name)

    if new_position == current_gameboard['go_position']:
        first_monopolized_color_group_after_go = None
        monopoly_color_order = ["Brown", "SkyBlue", "Orchid", "Orange", "Red", "Yellow", "Green", "Blue"]

        for c in monopoly_color_order:
            for p in current_gameboard['players']:
                if p.status != 'lost' and c in p.full_color_sets_possessed:
                    first_monopolized_color_group_after_go = c
                    break
            if first_monopolized_color_group_after_go is not None:
                break
        if first_monopolized_color_group_after_go is not None:
            for l in current_gameboard['location_sequence']:
                if l.color == first_monopolized_color_group_after_go:
                    new_position = l.start_position
                    logger.debug("Now " + self.player_name + " landed on GO, so moving it to the nearest monopolized color group after GO: " +
                                 first_monopolized_color_group_after_go)
                    break
        else:
            logger.debug(self.player_name + " remains on GO, as there are no monopolized color groups on this board!")
        # if no colors are monopolized, then the player remains on Go.

    logger.debug("Player is moving to location " + current_gameboard['location_sequence'][new_position].name)
    self.current_position = new_position


def alternate_pay_utility_rent(self, current_gameboard):
    current_location = current_gameboard['location_sequence'][self.current_position] # get the Location object corresponding to player's current position
    if current_location.loc_class == 'do_nothing': # we now look at each location class case by case
        logger.debug(self.player_name+' is on a do_nothing location, namely '+current_location.name+'. Nothing to process. Returning...')
        return
    elif current_location.loc_class == 'real_estate':
        logger.debug(self.player_name+ ' is on a real estate location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+' is owned by Bank. Setting _option_to_buy to true for '+self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+current_location.owned_by.player_name+' and is not mortgaged. Proceeding to calculate and pay rent.')
            self.calculate_and_pay_rent_dues(current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(self.calculate_and_pay_rent_dues)
            params = dict()
            params['self'] = self
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    elif current_location.loc_class == 'tax':
        logger.debug(self.player_name+ ' is on a tax location, namely '+ current_location.name+ '. Deducting tax...')
        tax_due = TaxLocation.calculate_tax(current_location, self, current_gameboard)
        self.charge_player(tax_due, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(self.charge_player)
        params = dict()
        params['self'] = self
        params['amount'] = tax_due
        params['description'] = 'tax'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return

    elif current_location.loc_class == 'railroad':
        logger.debug(self.player_name+ ' is on a railroad location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = RailroadLocation.calculate_railroad_dues(current_location, current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(RailroadLocation.calculate_railroad_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            recipient = current_location.owned_by
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of railroads'] = recipient.num_railroads_possessed
                params['description'] = 'railroad dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of railroads'] = recipient.num_railroads_possessed
            params['description'] = 'railroad dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    elif current_location.loc_class == 'utility':
        logger.debug(self.player_name+ ' is on a utility location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = UtilityLocation.calculate_utility_dues(current_location, current_gameboard, current_gameboard['current_die_total'])
            # add to game history
            current_gameboard['history']['function'].append(UtilityLocation.calculate_utility_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            params['die_total'] = current_gameboard['current_die_total']
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            """
            utility owner will not get the rent, instead utility rent will go to the bank
            """
            recipient = current_location.owned_by
            # code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # # add to game history
            # if code == action_choices.flag_config_dict['successful_action']:
            #     current_gameboard['history']['function'].append(recipient.receive_cash)
            #     params = dict()
            #     params['self'] = recipient
            #     params['amount'] = dues
            #     params['number of utilities'] = recipient.num_utilities_possessed
            #     params['description'] = 'utility dues'
            #     current_gameboard['history']['param'].append(params)
            #     current_gameboard['history']['return'].append(code)
            #     current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            # else:
            #     logger.debug("Not sure what happened! Something broke!")
            #     logger.error("Exception")
            #     raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=True) # bank_flag made true so that the player that lands on the prop pays rent to bank
            logger.debug(self.player_name + " pays utility rent to bank instead of the owner, owner will get income tax exemption!")
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of utilities'] = recipient.num_utilities_possessed
            params['description'] = 'utility dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return
    elif current_location.loc_class == 'action':
        logger.debug(self.player_name+ ' is on an action location, namely '+ current_location.name+ '. Performing action...')
        current_location.perform_action(self, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(current_location.perform_action)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return
    else:
        logger.error(self.player_name+' is on an unidentified location type. Raising exception.')
        logger.error("Exception")
        raise Exception


def alternate_income_tax_payment(location, player, current_gameboard):
    if location.name == 'Income Tax' and player.num_utilities_possessed > 0:
        logger.debug(player.player_name + " owns utilities and the utility rents are paid to the bank, thus can write off income taxes!")
        return 0
    else:
        return location.amount_due


def alternate_luxury_tax_calc(location, player, current_gameboard):
    if location.name == 'Luxury Tax':
        logger.debug("Calculating luxury tax based on highest price property in each color groups owned by player.........")
        luxury_tax = float(0)
        color_map = dict()
        for a in player.assets:
            if a.color is None:    # ignore non-realestate locs
                continue
            if a.color not in color_map:
                color_map[a.color] = dict()
            color_map[a.color][a] = a.price

        for key, val in color_map.items():
            color_map[key] = {k: v for k, v in sorted(color_map[key].items(), key=lambda item: item[1])}
            highest_price_prop = list(color_map[key].keys())[-1]
            logger.debug("Color group: " + key + " Most valuable prop: " + highest_price_prop.name + " " + str(highest_price_prop.price))
            luxury_tax += highest_price_prop.price

        return luxury_tax

    else:
        return location.amount_due


def alternate_player_movement(self, current_gameboard):
    current_location = current_gameboard['location_sequence'][self.current_position] # get the Location object corresponding to player's current position

    #-------------------------novelty------------------------------
    # play all players that are currently on that location an amt = 2*go_inc as tresspassing fee
    for p in current_gameboard['players']:
        if p != self and p.current_position == self.current_position:
            logger.debug(p.player_name + " already is on " + current_location.name)
            dues = 2*current_gameboard['go_increment']
            logger.debug(self.player_name + " paying " + p.player_name + " tresspassing fee of " + str(dues))
            recipient = p
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of utilities'] = recipient.num_utilities_possessed
                params['description'] = 'tresspassing fee'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of utilities'] = recipient.num_utilities_possessed
            params['description'] = 'tresspassing fee'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

    if current_location.loc_class == 'do_nothing': # we now look at each location class case by case
        logger.debug(self.player_name+' is on a do_nothing location, namely '+current_location.name+'. Nothing to process. Returning...')
        return
    elif current_location.loc_class == 'real_estate':
        logger.debug(self.player_name+ ' is on a real estate location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+' is owned by Bank. Setting _option_to_buy to true for '+self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+current_location.owned_by.player_name+' and is not mortgaged. Proceeding to calculate and pay rent.')
            self.calculate_and_pay_rent_dues(current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(self.calculate_and_pay_rent_dues)
            params = dict()
            params['self'] = self
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return
    elif current_location.loc_class == 'tax':
        logger.debug(self.player_name+ ' is on a tax location, namely '+ current_location.name+ '. Deducting tax...')
        tax_due = TaxLocation.calculate_tax(current_location, self, current_gameboard)
        self.charge_player(tax_due, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(self.charge_player)
        params = dict()
        params['self'] = self
        params['amount'] = tax_due
        params['description'] = 'tax'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return
    elif current_location.loc_class == 'railroad':
        logger.debug(self.player_name+ ' is on a railroad location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = RailroadLocation.calculate_railroad_dues(current_location, current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(RailroadLocation.calculate_railroad_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            recipient = current_location.owned_by
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of railroads'] = recipient.num_railroads_possessed
                params['description'] = 'railroad dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of railroads'] = recipient.num_railroads_possessed
            params['description'] = 'railroad dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    elif current_location.loc_class == 'utility':
        logger.debug(self.player_name+ ' is on a utility location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = UtilityLocation.calculate_utility_dues(current_location, current_gameboard, current_gameboard['current_die_total'])
            # add to game history
            current_gameboard['history']['function'].append(UtilityLocation.calculate_utility_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            params['die_total'] = current_gameboard['current_die_total']
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            recipient = current_location.owned_by
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of utilities'] = recipient.num_utilities_possessed
                params['description'] = 'utility dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of utilities'] = recipient.num_utilities_possessed
            params['description'] = 'utility dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    elif current_location.loc_class == 'action':
        logger.debug(self.player_name+ ' is on an action location, namely '+ current_location.name+ '. Performing action...')
        current_location.perform_action(self, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(current_location.perform_action)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return
    else:
        logger.error(self.player_name+' is on an unidentified location type. Raising exception.')
        logger.error("Exception")
        raise Exception


def alternate_free_parking_func(self, current_gameboard):
    current_location = current_gameboard['location_sequence'][self.current_position] # get the Location object corresponding to player's current position

    if current_location.loc_class == 'do_nothing': # we now look at each location class case by case

        #---------------------novelty------------------------------------
        # if the player lands on free parking, pay the bank parking dues = go_inc amt

        if current_location.name == 'Free Parking':
            logger.debug(self.player_name+ ' is on Free parking location, paying the bank free parking due = ' + str(current_gameboard['go_increment']))
            dues = current_gameboard['go_increment']
            self.charge_player(dues, current_gameboard, bank_flag=True)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['description'] = 'free parking dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return
        #----------------------------------------------------------------------------

        logger.debug(self.player_name+' is on a do_nothing location, namely '+current_location.name+'. Nothing to process. Returning...')
        return

    elif current_location.loc_class == 'real_estate':
        logger.debug(self.player_name+ ' is on a real estate location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+' is owned by Bank. Setting _option_to_buy to true for '+self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+current_location.owned_by.player_name+' and is not mortgaged. Proceeding to calculate and pay rent.')
            self.calculate_and_pay_rent_dues(current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(self.calculate_and_pay_rent_dues)
            params = dict()
            params['self'] = self
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    elif current_location.loc_class == 'tax':
        logger.debug(self.player_name+ ' is on a tax location, namely '+ current_location.name+ '. Deducting tax...')
        tax_due = TaxLocation.calculate_tax(current_location, self, current_gameboard)
        self.charge_player(tax_due, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(self.charge_player)
        params = dict()
        params['self'] = self
        params['amount'] = tax_due
        params['description'] = 'tax'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return

    elif current_location.loc_class == 'railroad':
        logger.debug(self.player_name+ ' is on a railroad location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = RailroadLocation.calculate_railroad_dues(current_location, current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(RailroadLocation.calculate_railroad_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            recipient = current_location.owned_by
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of railroads'] = recipient.num_railroads_possessed
                params['description'] = 'railroad dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of railroads'] = recipient.num_railroads_possessed
            params['description'] = 'railroad dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    elif current_location.loc_class == 'utility':
        logger.debug(self.player_name+ ' is on a utility location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = UtilityLocation.calculate_utility_dues(current_location, current_gameboard, current_gameboard['current_die_total'])
            # add to game history
            current_gameboard['history']['function'].append(UtilityLocation.calculate_utility_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            params['die_total'] = current_gameboard['current_die_total']
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            recipient = current_location.owned_by
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of utilities'] = recipient.num_utilities_possessed
                params['description'] = 'utility dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of utilities'] = recipient.num_utilities_possessed
            params['description'] = 'utility dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    elif current_location.loc_class == 'action':
        logger.debug(self.player_name+ ' is on an action location, namely '+ current_location.name+ '. Performing action...')
        current_location.perform_action(self, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(current_location.perform_action)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return

    else:
        logger.error(self.player_name+' is on an unidentified location type. Raising exception.')
        logger.error("Exception")
        raise Exception


def alternate_railroads_functionality(self, current_gameboard):
    current_location = current_gameboard['location_sequence'][self.current_position] # get the Location object corresponding to player's current position
    if current_location.loc_class == 'do_nothing': # we now look at each location class case by case
        logger.debug(self.player_name+' is on a do_nothing location, namely '+current_location.name+'. Nothing to process. Returning...')
        return
    elif current_location.loc_class == 'real_estate':
        logger.debug(self.player_name+ ' is on a real estate location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+' is owned by Bank. Setting _option_to_buy to true for '+self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+current_location.owned_by.player_name+' and is not mortgaged. Proceeding to calculate and pay rent.')
            self.calculate_and_pay_rent_dues(current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(self.calculate_and_pay_rent_dues)
            params = dict()
            params['self'] = self
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    elif current_location.loc_class == 'tax':
        logger.debug(self.player_name+ ' is on a tax location, namely '+ current_location.name+ '. Deducting tax...')
        tax_due = TaxLocation.calculate_tax(current_location, self, current_gameboard)
        self.charge_player(tax_due, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(self.charge_player)
        params = dict()
        params['self'] = self
        params['amount'] = tax_due
        params['description'] = 'tax'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return

    elif current_location.loc_class == 'railroad':
        logger.debug(self.player_name+ ' is on a railroad location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not have to pay rent.')

            #----------------------novelty--------------------------------
            i = self.current_position+1
            while i < len(current_gameboard['location_sequence']):
                if current_gameboard['location_sequence'][i].loc_class == 'railroad':
                    if i > self.current_position:
                        rel_locs = i - self.current_position - 7
                    else:
                        rel_locs = (40 + i) - self.current_position - 7
                    logger.debug("Since " + self.player_name + " landed on railroad, moving the player 7 locations behind next railroad.")
                    current_gameboard['move_player_after_die_roll'](self, rel_locs, current_gameboard, True)   # player will get go_inc if it passes GO
                    current_gameboard['history']['function'].append(current_gameboard['move_player_after_die_roll'])
                    params = dict()
                    params['player'] = self
                    params['rel_move'] = rel_locs
                    params['current_gameboard'] = current_gameboard
                    params['check_for_go'] = True
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(None)
                    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                    self.process_move_consequences(current_gameboard)
                    # add to game history
                    current_gameboard['history']['function'].append(self.process_move_consequences)
                    params = dict()
                    params['self'] = self
                    params['current_gameboard'] = current_gameboard
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(None)
                    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
                    break
                i = (i+1) % len(current_gameboard['location_sequence'])
            #-------------------------------------------------------------
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = RailroadLocation.calculate_railroad_dues(current_location, current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(RailroadLocation.calculate_railroad_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            recipient = current_location.owned_by
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of railroads'] = recipient.num_railroads_possessed
                params['description'] = 'railroad dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of railroads'] = recipient.num_railroads_possessed
            params['description'] = 'railroad dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            #----------------------novelty--------------------------------
            i = self.current_position+1
            while i < len(current_gameboard['location_sequence']):
                if current_gameboard['location_sequence'][i].loc_class == 'railroad':
                    if i > self.current_position:
                        rel_locs = i - self.current_position - 7
                    else:
                        rel_locs = (40 + i) - self.current_position - 7
                    logger.debug("Since " + self.player_name + " landed on railroad, moving the player 7 locations behind next railroad.")
                    current_gameboard['move_player_after_die_roll'](self, rel_locs, current_gameboard, True)   # player will get go_inc if it passes GO
                    current_gameboard['history']['function'].append(current_gameboard['move_player_after_die_roll'])
                    params = dict()
                    params['player'] = self
                    params['rel_move'] = rel_locs
                    params['current_gameboard'] = current_gameboard
                    params['check_for_go'] = True
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(None)
                    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                    self.process_move_consequences(current_gameboard)
                    # add to game history
                    current_gameboard['history']['function'].append(self.process_move_consequences)
                    params = dict()
                    params['self'] = self
                    params['current_gameboard'] = current_gameboard
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(None)
                    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
                    break
                i = (i+1) % len(current_gameboard['location_sequence'])
            #-------------------------------------------------------------

            return
    elif current_location.loc_class == 'utility':
        logger.debug(self.player_name+ ' is on a utility location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = UtilityLocation.calculate_utility_dues(current_location, current_gameboard, current_gameboard['current_die_total'])
            # add to game history
            current_gameboard['history']['function'].append(UtilityLocation.calculate_utility_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            params['die_total'] = current_gameboard['current_die_total']
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            recipient = current_location.owned_by
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of utilities'] = recipient.num_utilities_possessed
                params['description'] = 'utility dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of utilities'] = recipient.num_utilities_possessed
            params['description'] = 'utility dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    elif current_location.loc_class == 'action':
        logger.debug(self.player_name+ ' is on an action location, namely '+ current_location.name+ '. Performing action...')
        current_location.perform_action(self, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(current_location.perform_action)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return
    else:
        logger.error(self.player_name+' is on an unidentified location type. Raising exception.')
        logger.error("Exception")
        raise Exception


def alternate_jail_location_func(self, current_gameboard):
    current_location = current_gameboard['location_sequence'][self.current_position] # get the Location object corresponding to player's current position
    if current_location.loc_class == 'do_nothing': # we now look at each location class case by case
        #---------------------novelty-----------------------------------------
        # if players owns GOO jail card when passing Jail location (not by Go to jail location), it has to pay GOO jail card tax to the bank
        if current_location.name == 'In Jail/Just Visiting':
            if self.has_get_out_of_jail_chance_card or self.has_get_out_of_jail_community_chest_card:
                logger.debug("Charging player GOO card tax since the player owns this card and has not used it.")
                GOO_card_tax = current_gameboard['go_increment']
                self.charge_player(GOO_card_tax, current_gameboard, bank_flag=True)
                # add to game history
                current_gameboard['history']['function'].append(self.charge_player)
                params = dict()
                params['self'] = self
                params['amount'] = GOO_card_tax
                params['description'] = 'GOO jail card tax'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
                return
        #-----------------------------------------------------------------------

        logger.debug(self.player_name+' is on a do_nothing location, namely '+current_location.name+'. Nothing to process. Returning...')
        return
    elif current_location.loc_class == 'real_estate':
        logger.debug(self.player_name+ ' is on a real estate location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+' is owned by Bank. Setting _option_to_buy to true for '+self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+current_location.owned_by.player_name+' and is not mortgaged. Proceeding to calculate and pay rent.')
            self.calculate_and_pay_rent_dues(current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(self.calculate_and_pay_rent_dues)
            params = dict()
            params['self'] = self
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return
    elif current_location.loc_class == 'tax':
        logger.debug(self.player_name+ ' is on a tax location, namely '+ current_location.name+ '. Deducting tax...')
        tax_due = TaxLocation.calculate_tax(current_location, self, current_gameboard)
        self.charge_player(tax_due, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(self.charge_player)
        params = dict()
        params['self'] = self
        params['amount'] = tax_due
        params['description'] = 'tax'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return

    elif current_location.loc_class == 'railroad':
        logger.debug(self.player_name+ ' is on a railroad location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = RailroadLocation.calculate_railroad_dues(current_location, current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(RailroadLocation.calculate_railroad_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            recipient = current_location.owned_by
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of railroads'] = recipient.num_railroads_possessed
                params['description'] = 'railroad dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of railroads'] = recipient.num_railroads_possessed
            params['description'] = 'railroad dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    elif current_location.loc_class == 'utility':
        logger.debug(self.player_name+ ' is on a utility location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = UtilityLocation.calculate_utility_dues(current_location, current_gameboard, current_gameboard['current_die_total'])
            # add to game history
            current_gameboard['history']['function'].append(UtilityLocation.calculate_utility_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            params['die_total'] = current_gameboard['current_die_total']
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            recipient = current_location.owned_by
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of utilities'] = recipient.num_utilities_possessed
                params['description'] = 'utility dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of utilities'] = recipient.num_utilities_possessed
            params['description'] = 'utility dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    elif current_location.loc_class == 'action':
        logger.debug(self.player_name+ ' is on an action location, namely '+ current_location.name+ '. Performing action...')
        current_location.perform_action(self, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(current_location.perform_action)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return

    else:
        logger.error(self.player_name+' is on an unidentified location type. Raising exception.')
        logger.error("Exception")
        raise Exception


def last_loc_monopoly_tax(self, current_gameboard):
    last_loc_dict = {'Brown': 'Baltic Avenue', 'SkyBlue': 'Connecticut Avenue', 'Orchid': 'Virginia Avenue', 'Orange': 'New York Avenue',
                     'Red':'Illinois Avenue', 'Yellow': 'Marvin Gardens', 'Green': 'Pennsylvania Avenue', 'Blue': 'Boardwalk'}

    current_location = current_gameboard['location_sequence'][self.current_position] # get the Location object corresponding to player's current position
    if current_location.loc_class == 'do_nothing': # we now look at each location class case by case
        logger.debug(self.player_name+' is on a do_nothing location, namely '+current_location.name+'. Nothing to process. Returning...')
        return
    elif current_location.loc_class == 'real_estate':
        logger.debug(self.player_name+ ' is on a real estate location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+' is owned by Bank. Setting _option_to_buy to true for '+self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            #---------------------------------novelty--------------------------------
            # last loc in monopolized color group will be taxable, owner of the loc has to pay bank a tax each time it lands on it
            if current_location.color in self.full_color_sets_possessed:    # monopolized color group
                if current_location.name == last_loc_dict[current_location.color]:
                    logger.debug(current_location.color + " is monopolized by player, charging monopolized color group tax.")
                    tax_val = current_gameboard['go_increment']
                    self.charge_player(tax_val, current_gameboard, bank_flag=True)
                    # add to game history
                    current_gameboard['history']['function'].append(self.charge_player)
                    params = dict()
                    params['self'] = self
                    params['amount'] = tax_val
                    params['description'] = 'monopolized color group tax'
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(None)
                    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
                    return
            #-----------------------------------------------------------------------

            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+current_location.owned_by.player_name+' and is not mortgaged. Proceeding to calculate and pay rent.')
            self.calculate_and_pay_rent_dues(current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(self.calculate_and_pay_rent_dues)
            params = dict()
            params['self'] = self
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    elif current_location.loc_class == 'tax':
        logger.debug(self.player_name+ ' is on a tax location, namely '+ current_location.name+ '. Deducting tax...')
        tax_due = TaxLocation.calculate_tax(current_location, self, current_gameboard)
        self.charge_player(tax_due, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(self.charge_player)
        params = dict()
        params['self'] = self
        params['amount'] = tax_due
        params['description'] = 'tax'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return

    elif current_location.loc_class == 'railroad':
        logger.debug(self.player_name+ ' is on a railroad location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = RailroadLocation.calculate_railroad_dues(current_location, current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(RailroadLocation.calculate_railroad_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            recipient = current_location.owned_by
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of railroads'] = recipient.num_railroads_possessed
                params['description'] = 'railroad dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of railroads'] = recipient.num_railroads_possessed
            params['description'] = 'railroad dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    elif current_location.loc_class == 'utility':
        logger.debug(self.player_name+ ' is on a utility location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = UtilityLocation.calculate_utility_dues(current_location, current_gameboard, current_gameboard['current_die_total'])
            # add to game history
            current_gameboard['history']['function'].append(UtilityLocation.calculate_utility_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            params['die_total'] = current_gameboard['current_die_total']
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            recipient = current_location.owned_by
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of utilities'] = recipient.num_utilities_possessed
                params['description'] = 'utility dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of utilities'] = recipient.num_utilities_possessed
            params['description'] = 'utility dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            return

    elif current_location.loc_class == 'action':
        logger.debug(self.player_name+ ' is on an action location, namely '+ current_location.name+ '. Performing action...')
        current_location.perform_action(self, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(current_location.perform_action)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        return

    else:
        logger.error(self.player_name+' is on an unidentified location type. Raising exception.')
        logger.error("Exception")
        raise Exception


def alternate_buy_property_with_neighbour_tax(player, asset, current_gameboard):
    """
    If a player buys a property, it will also have to pay taxes to the players that own properties to the left and
    right of this property. If the real estate properties to the immediate left and right of this property is unowned or owned by this
    player itself, then no tax will be levied on those properties.
    :param player:
    :param asset:
    :param current_gameboard:
    :return:
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

        logger.debug(asset.name+ ' ownership has been updated! Resetting option_to_buy for player')
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        logger.debug("Player also has to pay neighbour tax to the owners of properties to the immediate left and right of " + asset.name)
        left_prop = current_gameboard['location_sequence'][-1]
        right_prop = current_gameboard['location_sequence'][3]
        if asset.start_position == 1:
            left_prop = current_gameboard['location_sequence'][-1]
            right_prop = current_gameboard['location_sequence'][3]
        elif asset.start_position == 39:
            left_prop = current_gameboard['location_sequence'][1]
            right_prop = current_gameboard['location_sequence'][37]
        else:
            for j in range(asset.start_position-1, -1, -1):
                if current_gameboard['location_sequence'][j].loc_class == 'real_estate':
                    left_prop = current_gameboard['location_sequence'][j]
                    break
            for j in range(asset.start_position+1, 40):
                if current_gameboard['location_sequence'][j].loc_class == 'real_estate':
                    right_prop = current_gameboard['location_sequence'][j]
                    break
        if left_prop.owned_by != current_gameboard['bank']:
            if left_prop.owned_by == player:
                logger.debug("Property to the left is " + left_prop.name + " and is owned by this player itself. No neighbour tax.")
            else:
                logger.debug("Property to the left is " + left_prop.name + " and is owned by " + left_prop.owned_by.player_name)
        elif left_prop.owned_by == current_gameboard['bank']:
            logger.debug("Property to the left is " + left_prop.name + " and is owned by the bank. No neighbour tax.")
        if left_prop.owned_by != current_gameboard['bank'] and left_prop.owned_by != player:
            dues = float(left_prop.price/5)   # tax amt
            recipient = left_prop.owned_by
            logger.debug("Paying neighbour tax = " + str(dues))
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['description'] = 'neighbour tax'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            player.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(player.charge_player)
            params = dict()
            params['self'] = player
            params['amount'] = dues
            params['description'] = 'neighbour tax'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        if right_prop.owned_by != current_gameboard['bank']:
            if right_prop.owned_by == player:
                logger.debug("Property to the left is " + right_prop.name + " and is owned by this player itself. No neighbour tax.")
            else:
                logger.debug("Property to the left is " + right_prop.name + " and is owned by " + right_prop.owned_by.player_name)
        elif right_prop.owned_by == current_gameboard['bank']:
            logger.debug("Property to the left is " + right_prop.name + " and is owned by the bank. No neighbour tax")

        if right_prop.owned_by != current_gameboard['bank'] and right_prop.owned_by != player:
            dues = float(right_prop.price/5)   # tax amt
            recipient = right_prop.owned_by
            logger.debug("Paying neighbour tax = " + str(dues))
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['description'] = 'neighbour tax'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            player.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(player.charge_player)
            params = dict()
            params['self'] = player
            params['amount'] = dues
            params['description'] = 'neighbour tax'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return flag_config_dict['successful_action']


def chat_assignment(from_player=None, to_player=None, action_params_dict=None, current_gameboard=None):
    print("inside chat assign")
    print(action_params_dict['message'])


#---------------------------------------------Interactions----------------------------------------------------------------------------

# Interaction 5
def make_borrow_money_offer(from_player, to_player, interaction_params_dict, current_gameboard):
    if to_player.status == 'lost':
        logger.debug("Borrow offer is being made to a player who has lost the game already! Returning failure code.")
        return flag_config_dict['failure_code']

    if interaction_params_dict['amount'] < 0:
        logger.debug("Cannot borrow negative amounts of money")
        return flag_config_dict['failure_code']
    elif 'borrow_offers' in from_player.agent._agent_memory and current_gameboard['interaction_id'] in from_player.agent._agent_memory['borrow_offers'] or \
            current_gameboard['interaction_id'] in to_player.interaction_dict:
        logger.debug("Current interaction id already exists, something wrong with novelty injection.")
        return flag_config_dict['failure_code']
    else:
        logger.debug(from_player.player_name + " making borrow money offer to " + to_player.player_name + ". Populating interaction dictionary.")
        interaction_id = current_gameboard['interaction_id']
        if 'borrow_offers' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['borrow_offers'] = dict()
        from_player.agent._agent_memory['borrow_offers'][interaction_id] = dict()
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['accepted'] = False
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['to_player'] = to_player
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['amount'] = interaction_params_dict['amount']
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['interest_rate'] = interaction_params_dict['interest_rate']
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['num_rounds'] = interaction_params_dict['num_rounds']

        to_player.interaction_dict[interaction_id] = dict()
        to_player.interaction_dict[interaction_id]['from_player'] = from_player
        to_player.interaction_dict[interaction_id]['amount'] = interaction_params_dict['amount']
        to_player.interaction_dict[interaction_id]['interest_rate'] = interaction_params_dict['interest_rate']
        to_player.interaction_dict[interaction_id]['num_rounds'] = interaction_params_dict['num_rounds']

        current_gameboard['interaction_id'] += 1
        logger.debug('Borrow offer has been made.')
        return flag_config_dict['successful_action']


def accept_borrow_money_offer(from_player, to_player, interaction_id, decision, current_gameboard):
    if interaction_id not in to_player.interaction_dict:
        logger.debug("Something wrong with novelty injection...")
        raise Exception
    elif 'borrow_offers' in from_player.agent._agent_memory and interaction_id not in from_player.agent._agent_memory['borrow_offers']:
        logger.debug("Interaction id does not exist! Returning failure code.")
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['failure_code']

    else:
        if not decision:
            logger.debug(to_player.player_name + " rejected borrow money offer from " + from_player.player_name)
            del from_player.agent._agent_memory['borrow_offers'][interaction_id]
            del to_player.interaction_dict[interaction_id]
            return flag_config_dict['successful_action']
        else:
            from_player.agent._agent_memory['borrow_offers'][interaction_id]['accepted'] = True
            logger.debug(to_player.player_name + " accepted borrow money offer from " + from_player.player_name)
            amt = to_player.interaction_dict[interaction_id]['amount']

            to_player.charge_player(amt, current_gameboard, bank_flag=False)
            logger.debug(to_player.player_name + " has paid " + from_player.player_name + " an amount of " + str(amt))
            # add to game history
            current_gameboard['history']['function'].append(to_player.charge_player)
            params = dict()
            params['self'] = to_player
            params['amount'] = amt
            params['description'] = 'borrowed money'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            from_player.receive_cash(amt, current_gameboard, bank_flag=False)
            logger.debug(from_player.player_name + " has received " + str(amt))
            # add to game history
            current_gameboard['history']['function'].append(from_player.receive_cash)
            params = dict()
            params['self'] = from_player
            params['amount'] = amt
            params['description'] = 'borrow money'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            del to_player.interaction_dict[interaction_id]
            return flag_config_dict['successful_action']


def pay_interest_on_borrowed_money(player, pos, current_gameboard):
    if 'borrow_offers' in player.agent._agent_memory and len(player.agent._agent_memory['borrow_offers']) > 0:
        import copy
        offers_dict = copy.deepcopy(player.agent._agent_memory['borrow_offers'])
        for id, offer in offers_dict.items():
            if offer['accepted']:       # then pay interest to to_player along with amount due
                amount_due = offer['amount']/offer['num_rounds']
                amount_payable = float(amount_due*(1+offer['interest_rate']))
                recipient = offer['to_player']

                player.charge_player(amount_payable, current_gameboard, bank_flag=False)
                logger.debug(player.player_name + " has paid " + recipient.player_name + " an amount of " + str(amount_payable) + " towards borrowed money payments")
                # add to game history
                current_gameboard['history']['function'].append(player.charge_player)
                params = dict()
                params['self'] = player
                params['amount'] = amount_payable
                params['description'] = 'return borrowed money with interest'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                recipient.receive_cash(amount_payable, current_gameboard, bank_flag=False)
                logger.debug(recipient.player_name + " has received " + str(amount_payable))
                # add to game history
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = amount_payable
                params['description'] = 'return borrowed money with interest'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                player.agent._agent_memory['borrow_offers'][id]['num_rounds'] -= 1
                player.agent._agent_memory['borrow_offers'][id]['amount'] -= amount_due

                if player.agent._agent_memory['borrow_offers'][id]['num_rounds'] == 0:
                    logger.debug(player.player_name + " finished paying off " + recipient.player_name + " borrowed money with interest.")
                    del player.agent._agent_memory['borrow_offers'][id]

# Interaction 12
def pay_interest_on_borrowed_money_with_inflation(player, pos, current_gameboard):
    inflation_rate = 0.05
    if 'borrow_offers' in player.agent._agent_memory and len(player.agent._agent_memory['borrow_offers']) > 0:
        import copy
        offers_dict = copy.deepcopy(player.agent._agent_memory['borrow_offers'])
        for id, offer in offers_dict.items():
            if offer['accepted']:       # then pay interest to to_player along with amount due

                offer['amount'] *= (1 - inflation_rate)
                amount_due = offer['amount']/offer['num_rounds']
                amount_payable = float(amount_due*(1+offer['interest_rate']))
                recipient = offer['to_player']


                player.charge_player(amount_payable, current_gameboard, bank_flag=False)
                logger.debug(player.player_name + " has paid " + recipient.player_name + " an amount of " + str(amount_payable) + " towards borrowed money payments")
                # add to game history
                current_gameboard['history']['function'].append(player.charge_player)
                params = dict()
                params['self'] = player
                params['amount'] = amount_payable
                params['description'] = 'return borrowed money with interest'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                recipient.receive_cash(amount_payable, current_gameboard, bank_flag=False)
                logger.debug(recipient.player_name + " has received " + str(amount_payable))
                # add to game history
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = amount_payable
                params['description'] = 'return borrowed money with interest'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


                player.agent._agent_memory['borrow_offers'][id]['num_rounds'] -= 1
                player.agent._agent_memory['borrow_offers'][id]['amount'] *= (1 - inflation_rate)
                player.agent._agent_memory['borrow_offers'][id]['amount'] -= amount_due


                if player.agent._agent_memory['borrow_offers'][id]['num_rounds'] == 0:
                    logger.debug(player.player_name + " finished paying off " + recipient.player_name + " borrowed money with interest.")
                    del player.agent._agent_memory['borrow_offers'][id]

# Interaction 13
def make_borrow_money_offer_with_restrict1(from_player, to_player, interaction_params_dict, current_gameboard):
    if to_player.status == 'lost':
        logger.debug("Borrow offer is being made to a player who has lost the game already! Returning failure code.")
        return flag_config_dict['failure_code']

    if interaction_params_dict['interest_rate'] >= 0.35 or interaction_params_dict['num_rounds'] <= 5:
        logger.debug("The given parameters are not followed the restrictions. Returning failure code.")
        return flag_config_dict['failure_code']

    if interaction_params_dict['amount'] < 0:
        logger.debug("Cannot borrow negative amounts of money")
        return flag_config_dict['failure_code']
    elif 'borrow_offers' in from_player.agent._agent_memory and current_gameboard['interaction_id'] in from_player.agent._agent_memory['borrow_offers'] or \
            current_gameboard['interaction_id'] in to_player.interaction_dict:
        logger.debug("Current interaction id already exists, something wrong with novelty injection.")
        return flag_config_dict['failure_code']
    else:
        logger.debug(from_player.player_name + " making borrow money offer to " + to_player.player_name + ". Populating interaction dictionary.")
        interaction_id = current_gameboard['interaction_id']
        if 'borrow_offers' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['borrow_offers'] = dict()
        from_player.agent._agent_memory['borrow_offers'][interaction_id] = dict()
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['accepted'] = False
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['to_player'] = to_player
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['amount'] = interaction_params_dict['amount']
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['interest_rate'] = interaction_params_dict['interest_rate']
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['num_rounds'] = interaction_params_dict['num_rounds']

        to_player.interaction_dict[interaction_id] = dict()
        to_player.interaction_dict[interaction_id]['from_player'] = from_player
        to_player.interaction_dict[interaction_id]['amount'] = interaction_params_dict['amount']
        to_player.interaction_dict[interaction_id]['interest_rate'] = interaction_params_dict['interest_rate']
        to_player.interaction_dict[interaction_id]['num_rounds'] = interaction_params_dict['num_rounds']

        current_gameboard['interaction_id'] += 1
        logger.debug('Borrow offer has been made.')
        return flag_config_dict['successful_action']

# Interaction 14
def make_borrow_money_offer_with_restrict2(from_player, to_player, interaction_params_dict, current_gameboard):
    if to_player.status == 'lost':
        logger.debug("Borrow offer is being made to a player who has lost the game already! Returning failure code.")
        return flag_config_dict['failure_code']

    if interaction_params_dict['interest_rate'] <= 0.15 or interaction_params_dict['num_rounds'] >= 10 or interaction_params_dict['amount'] >= 500:
        logger.debug("The given parameters are not followed the restrictions. Returning failure code.")
        return flag_config_dict['failure_code']

    if interaction_params_dict['amount'] < 0:
        logger.debug("Cannot borrow negative amounts of money")
        return flag_config_dict['failure_code']
    elif 'borrow_offers' in from_player.agent._agent_memory and current_gameboard['interaction_id'] in from_player.agent._agent_memory['borrow_offers'] or \
            current_gameboard['interaction_id'] in to_player.interaction_dict:
        logger.debug("Current interaction id already exists, something wrong with novelty injection.")
        return flag_config_dict['failure_code']
    else:
        logger.debug(from_player.player_name + " making borrow money offer to " + to_player.player_name + ". Populating interaction dictionary.")
        interaction_id = current_gameboard['interaction_id']
        if 'borrow_offers' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['borrow_offers'] = dict()
        from_player.agent._agent_memory['borrow_offers'][interaction_id] = dict()
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['accepted'] = False
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['to_player'] = to_player
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['amount'] = interaction_params_dict['amount']
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['interest_rate'] = interaction_params_dict['interest_rate']
        from_player.agent._agent_memory['borrow_offers'][interaction_id]['num_rounds'] = interaction_params_dict['num_rounds']

        to_player.interaction_dict[interaction_id] = dict()
        to_player.interaction_dict[interaction_id]['from_player'] = from_player
        to_player.interaction_dict[interaction_id]['amount'] = interaction_params_dict['amount']
        to_player.interaction_dict[interaction_id]['interest_rate'] = interaction_params_dict['interest_rate']
        to_player.interaction_dict[interaction_id]['num_rounds'] = interaction_params_dict['num_rounds']

        current_gameboard['interaction_id'] += 1
        logger.debug('Borrow offer has been made.')
        return flag_config_dict['successful_action']

# Interaction 6
def make_trade_goo_card_offer(from_player, to_player, interaction_params_dict, current_gameboard):
    if to_player.status == 'lost':
        logger.debug("Trade offer is being made to a player who has lost the game already! Returning failure code.")
        return flag_config_dict['failure_code']
    elif not from_player.has_get_out_of_jail_chance_card and not from_player.has_get_out_of_jail_community_chest_card:
        logger.debug(from_player.player_name + " does not have GOO jail card, cannot make this interaction offer.")
        return flag_config_dict['failure_code']
    else:
        interaction_id = current_gameboard['interaction_id']
        if 'made_offers' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['made_offers'] = dict()
        else:
            # check for same outstanding offers, cannot make same offer twice when outstanding
            for id, v in to_player.interaction_dict.items():
                if from_player.has_get_out_of_jail_chance_card and v['from_player'] == from_player and v['chance_card']:
                    logger.debug(from_player.player_name + " has already made a trade GOO chance card offer to " + to_player.player_name + ". Returning failure code")
                    return flag_config_dict['failure_code']
                elif from_player.has_get_out_of_jail_community_chest_card and v['from_player'] == from_player and v['cc_card']:
                    logger.debug(from_player.player_name + " has already made a trade GOO cc card offer to " + to_player.player_name + ". Returning failure code")
                    return flag_config_dict['failure_code']

        from_player.agent._agent_memory['made_offers'][interaction_id] = dict()
        from_player.agent._agent_memory['made_offers'][interaction_id]['to_player'] = to_player

        to_player.interaction_dict[interaction_id] = dict()
        to_player.interaction_dict[interaction_id]['from_player'] = from_player
        to_player.interaction_dict[interaction_id]['amount'] = interaction_params_dict['amount']
        if from_player.has_get_out_of_jail_chance_card:
            to_player.interaction_dict[interaction_id]['chance_card'] = True
            to_player.interaction_dict[interaction_id]['cc_card'] = False
        else:
            to_player.interaction_dict[interaction_id]['chance_card'] = False
            to_player.interaction_dict[interaction_id]['cc_card'] = True

        current_gameboard['interaction_id'] += 1
        logger.debug(from_player.player_name + " has made a GOO card trade offer")
        return flag_config_dict['successful_action']


def accept_trade_goo_card_offer(from_player, to_player, interaction_id, decision, current_gameboard):
    """
    accept offer will not go through if the player already has a cc/chance card and the offer involves the same card
    :param from_player:
    :param to_player:
    :param interaction_id:
    :param decision:
    :param current_gameboard:
    :return:
    """
    if interaction_id not in to_player.interaction_dict:
        logger.debug("Something wrong with novelty injection...")
        raise Exception
    elif 'made_offers' in from_player.agent._agent_memory and interaction_id not in from_player.agent._agent_memory['made_offers']:
        logger.debug("Interaction id does not exist! Returning failure code.")
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['failure_code']

    else:
        if not decision:
            logger.debug(to_player.player_name + " rejected GOO card trade offer from " + from_player.player_name)
            del from_player.agent._agent_memory['made_offers'][interaction_id]
            del to_player.interaction_dict[interaction_id]
            return flag_config_dict['successful_action']
        else:
            if to_player.has_get_out_of_jail_community_chest_card and to_player.interaction_dict[interaction_id]['cc_card']:
                logger.debug(to_player.player_name + " already has cc card, cannot accept offer.")
                del from_player.agent._agent_memory['made_offers'][interaction_id]
                del to_player.interaction_dict[interaction_id]
                return flag_config_dict['failure_code']
            elif to_player.has_get_out_of_jail_chance_card and to_player.interaction_dict[interaction_id]['chance_card']:
                logger.debug(to_player.player_name + " already has chance card, cannot accept offer.")
                del from_player.agent._agent_memory['made_offers'][interaction_id]
                del to_player.interaction_dict[interaction_id]
                return flag_config_dict['failure_code']

            logger.debug(to_player.player_name + " accepted GOO card trade offer from " + from_player.player_name)
            amt = to_player.interaction_dict[interaction_id]['amount']

            to_player.charge_player(amt, current_gameboard, bank_flag=False)
            logger.debug(to_player.player_name + " has paid " + from_player.player_name + " an amount of " + str(amt))
            # add to game history
            current_gameboard['history']['function'].append(to_player.charge_player)
            params = dict()
            params['self'] = to_player
            params['amount'] = amt
            if to_player.interaction_dict[interaction_id]['chance_card']:
                params['description'] = 'trade GOO chance card'
            else:
                params['description'] = 'trade GOO cc card'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            from_player.receive_cash(amt, current_gameboard, bank_flag=False)
            logger.debug(from_player.player_name + " has received " + str(amt))
            # add to game history
            current_gameboard['history']['function'].append(from_player.receive_cash)
            params = dict()
            params['self'] = from_player
            params['amount'] = amt
            if to_player.interaction_dict[interaction_id]['chance_card']:
                params['description'] = 'trade GOO chance card'
            else:
                params['description'] = 'trade GOO cc card'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            if to_player.interaction_dict[interaction_id]['chance_card']:
                from_player.has_get_out_of_jail_chance_card = False
                to_player.has_get_out_of_jail_chance_card = True

            elif to_player.interaction_dict[interaction_id]['cc_card']:
                from_player.has_get_out_of_jail_community_chest_card = False
                to_player.has_get_out_of_jail_community_chest_card = True

            if to_player.interaction_dict[interaction_id]['chance_card']:
                logger.debug("Successfully transfered GOO jail chance card from " + from_player.player_name + " to " + to_player.player_name)
            else:
                logger.debug("Successfully transfered GOO jail cc card from " + from_player.player_name + " to " + to_player.player_name)

            del to_player.interaction_dict[interaction_id]
            del from_player.agent._agent_memory['made_offers'][interaction_id]
            return flag_config_dict['successful_action']

# Interaction 7
def make_trade_house_hotel_offer(from_player, to_player, interaction_params_dict, current_gameboard):
    """
    # Peter add: turning location and to_location into object--------------
    print(type(interaction_params_dict['location']))
    print(type(interaction_params_dict['to_location']))
    location_str = interaction_params_dict['_location']
    to_location_str = interaction_params_dict['to_location']

    try:
        logger.debug("Turning location string in to object")
        interaction_params_dict['location'] = current_gameboard['location_objects'][location_str]
        interaction_params_dict['to_location'] = current_gameboard['location_objects'][to_location_str]
    except:
        logger.debug("Location is not existed. Please check the location name!")
        return flag_config_dict['failure_code']
    # --------------
    """
    logger.debug("Trying to trade improvement from " + interaction_params_dict['location'].name + " to " + interaction_params_dict['to_location'].name)
    if to_player.status == 'lost':
        logger.debug("Trade offer is being made to a player who has lost the game already! Returning failure code.")
        return flag_config_dict['failure_code']
    elif from_player.num_total_houses == 0 and interaction_params_dict['house']:
        logger.debug(from_player.player_name + " has no houses but is making a trade house offer! Returning failure code.")
        return flag_config_dict['failure_code']
    elif from_player.num_total_hotels == 0 and interaction_params_dict['hotel']:
        logger.debug(from_player.player_name + " has no hotels but is making a trade hotel offer! Returning failure code.")
        return flag_config_dict['failure_code']
    else:
        if interaction_params_dict['location'] not in from_player.assets:
            logger.debug(from_player.player_name + " does not own " + interaction_params_dict['location'].name + "! Returning failure code.")
            return flag_config_dict['failure_code']
        elif interaction_params_dict['location'].loc_class != 'real_estate':
            logger.debug(interaction_params_dict['location'].name + " is not a real estate. Returning failure code.")
            return flag_config_dict['failure_code']
        elif interaction_params_dict['house'] and interaction_params_dict['location'].num_houses == 0:
            logger.debug(from_player.player_name + " does not own houses on " + interaction_params_dict['location'].name + "! Returning failure code.")
            return flag_config_dict['failure_code']
        elif interaction_params_dict['hotel'] and interaction_params_dict['location'].num_hotels == 0:
            logger.debug(from_player.player_name + " does not own houses on " + interaction_params_dict['location'].name + "! Returning failure code.")
            return flag_config_dict['failure_code']
        elif interaction_params_dict['to_location'].loc_class != 'real_estate':
            logger.debug(interaction_params_dict['to_location'].name + " is not a real estate. Returning failure code.")
            return flag_config_dict['failure_code']
        elif interaction_params_dict['to_location'].is_mortgaged:
            logger.debug(interaction_params_dict['to_location'].name + " is mortgaged, cannot set up improvements here. Returning failure code.")
            return flag_config_dict['failure_code']
        else:
            interaction_id = current_gameboard['interaction_id']
            if 'made_offers' not in from_player.agent._agent_memory:
                from_player.agent._agent_memory['made_offers'] = dict()
            else:
                # check for same outstanding offers, cannot make same offer twice when outstanding
                for id, v in to_player.interaction_dict.items():
                    if v['from_player'] == from_player and v['location'] == interaction_params_dict['location'] and v['house'] == interaction_params_dict['house']:
                        logger.debug(from_player.player_name + " has already made the same offer to " + to_player.player_name + " and is still outstanding. Returning failure code")
                        return flag_config_dict['failure_code']

            from_player.agent._agent_memory['made_offers'][interaction_id] = dict()
            from_player.agent._agent_memory['made_offers'][interaction_id]['to_player'] = to_player

            to_player.interaction_dict[interaction_id] = dict()
            to_player.interaction_dict[interaction_id]['from_player'] = from_player
            to_player.interaction_dict[interaction_id]['location'] = interaction_params_dict['location']
            to_player.interaction_dict[interaction_id]['house'] = interaction_params_dict['house']
            to_player.interaction_dict[interaction_id]['hotel'] = interaction_params_dict['hotel']
            to_player.interaction_dict[interaction_id]['to_location'] = interaction_params_dict['to_location']
            to_player.interaction_dict[interaction_id]['amount'] = interaction_params_dict['amount']

            current_gameboard['interaction_id'] += 1
            logger.debug(from_player.player_name + " has made a trade house/hotel offer")
            return flag_config_dict['successful_action']


def accept_trade_house_hotel_offer(from_player, to_player, interaction_id, decision, current_gameboard):
    """
    # added by Peter
    if to_player.interaction_dict['location'] not in from_player.assets or to_player.interaction_dict['to_location'] not in to_player.assets:
        logger.debug("")
        return flag_config_dict['failure_code']
    #
    """
    if interaction_id not in to_player.interaction_dict:
        logger.debug("Something wrong with novelty injection...")
        raise Exception

    elif not decision:
        logger.debug(to_player.player_name + " rejected trade house/hotel offer from " + from_player.player_name)
        del from_player.agent._agent_memory['made_offers'][interaction_id]
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['successful_action']

    elif 'made_offers' in from_player.agent._agent_memory and interaction_id not in from_player.agent._agent_memory['made_offers']:
        logger.debug("Interaction id does not exist! Returning failure code.")
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['failure_code']

    # Peter added, the from_player may sell the property to the bank before the to_player accept the offer
    elif isinstance(to_player.interaction_dict[interaction_id]['location'].owned_by, Bank):
        logger.debug(to_player.interaction_dict[interaction_id]['location'].name + "is owned by the bank. Returning failure code.")
        del from_player.agent._agent_memory['made_offers'][interaction_id]
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['failure_code']
    # -----------------------------


    elif to_player.interaction_dict[interaction_id]['location'].owned_by.player_name != to_player.interaction_dict[interaction_id]['from_player'].player_name:
        logger.debug("Location not owned by the player in params. Returning failure code.")
        del from_player.agent._agent_memory['made_offers'][interaction_id]
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['failure_code']

    elif to_player.interaction_dict[interaction_id]['location'].loc_class != "real_estate":
        logger.debug(to_player.interaction_dict[interaction_id]['location'].name + " not of type real estate. Returning failure code.")
        del from_player.agent._agent_memory['made_offers'][interaction_id]
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['failure_code']

    elif to_player.interaction_dict[interaction_id]['to_location'].loc_class != "real_estate":
        logger.debug(to_player.interaction_dict[interaction_id]['to_location'].name + " not of type real estate. Returning failure code.")
        del from_player.agent._agent_memory['made_offers'][interaction_id]
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['failure_code']

    elif to_player.interaction_dict[interaction_id]['to_location'].is_mortgaged:
        logger.debug(to_player.interaction_dict[interaction_id]['to_location'].name + " is mortgaged. Returning failure code.")
        del from_player.agent._agent_memory['made_offers'][interaction_id]
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['failure_code']

    elif to_player.interaction_dict[interaction_id]['location'].color not in from_player.full_color_sets_possessed:
        logger.debug(to_player.interaction_dict[interaction_id]['location'].name + " not of monopolized color group. Returning failure code.")
        del from_player.agent._agent_memory['made_offers'][interaction_id]
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['failure_code']

    # Peter added: I think this determination should be set in agent decision, not here
    #elif to_player.interaction_dict[interaction_id]['to_loca$tion'].color not in to_player.full_color_sets_possessed:
    #    logger.debug(to_player.interaction_dict[interaction_id]['to_location'].name + " not of monopolized color group. Returning failure code.")
    #    del from_player.agent._agent_memory['made_offers'][interaction_id]
    #    del to_player.interaction_dict[interaction_id]
    #    return flag_config_dict['failure_code']


    elif to_player.interaction_dict[interaction_id]['location'].num_hotels == 0 and to_player.interaction_dict[interaction_id]['location'].num_houses == 0:
        logger.debug("No houses and hotels to trade on this property.")
        del from_player.agent._agent_memory['made_offers'][interaction_id]
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['failure_code']

    else:
        if to_player.interaction_dict[interaction_id]['hotel']: # this is the simpler case
            from_prop = to_player.interaction_dict[interaction_id]['location']
            logger.debug('Looking to trade hotel on '+ from_prop.name)
            for same_colored_asset in current_gameboard['color_assets'][from_prop.color]:
                if same_colored_asset == from_prop:
                    continue
                if from_prop.num_hotels == 1 and not (same_colored_asset.num_hotels == 1 or (same_colored_asset.num_hotels == 0 and
                                        same_colored_asset.num_houses == 0)) :
                    logger.debug('All same-colored properties must stay uniformly improved. Returning failure code')
                    del from_player.agent._agent_memory['made_offers'][interaction_id]
                    del to_player.interaction_dict[interaction_id]
                    return flag_config_dict['failure_code']
                elif from_prop.num_hotels < same_colored_asset.num_hotels:    # need to follow uniform improvement rule
                    logger.debug('All same-colored properties must stay uniformly improved. Returning failure code')
                    del from_player.agent._agent_memory['made_offers'][interaction_id]
                    del to_player.interaction_dict[interaction_id]
                    return flag_config_dict['failure_code']

            to_prop = to_player.interaction_dict[interaction_id]['to_location']
            logger.debug('Looking to place hotel on '+ to_prop.name)
            if to_prop.num_hotels == current_gameboard['bank'].hotel_limit:
                logger.debug('There is already ' + str(current_gameboard['bank'].hotel_limit) + ' hotel(s) here. Cannot exceed this limit. Returning failure code')
                del from_player.agent._agent_memory['made_offers'][interaction_id]
                del to_player.interaction_dict[interaction_id]
                return flag_config_dict['failure_code']
            elif to_prop.num_hotels == 0 and to_prop.num_houses != current_gameboard['bank'].house_limit_before_hotel:
                logger.debug('Need to have ' + str(current_gameboard['bank'].house_limit_before_hotel)
                             + ' houses before you can build a hotel...Returning failure code')
                del from_player.agent._agent_memory['made_offers'][interaction_id]
                del to_player.interaction_dict[interaction_id]
                return flag_config_dict['failure_code']

            for same_colored_asset in current_gameboard['color_assets'][to_prop.color]:
                if same_colored_asset == to_prop:
                    continue
                if to_prop.num_hotels == 0 and not (same_colored_asset.num_houses == current_gameboard['bank'].house_limit_before_hotel
                        or same_colored_asset.num_hotels == 1): # as long as all other houses
                    # of that color have either max limit of houses before hotel can be built or a hotel, we can build a hotel on this asset. (Uniform improvement rule)
                    logger.debug('All same-colored properties must be uniformly improved. Returning failure code')
                    del from_player.agent._agent_memory['made_offers'][interaction_id]
                    del to_player.interaction_dict[interaction_id]
                    return flag_config_dict['failure_code']
                elif same_colored_asset.num_hotels < to_prop.num_hotels:
                    logger.debug('All same-colored properties must be uniformly improved. Returning failure code')
                    del from_player.agent._agent_memory['made_offers'][interaction_id]
                    del to_player.interaction_dict[interaction_id]
                    return flag_config_dict['failure_code']

            logger.debug(to_player.player_name + " accepting trade hotel offer from " + from_player.player_name)
            code = from_player.receive_cash(to_player.interaction_dict[interaction_id]['amount'], current_gameboard, bank_flag=False)
            from_player.num_total_hotels -= 1
            logger.debug(from_player.player_name+' now has num_total_hotels '+str(from_player.num_total_hotels)+' and num_total_houses '+str(from_player.num_total_houses))
            # add to game history
            current_gameboard['history']['function'].append(from_player.receive_cash)
            params = dict()
            params['self'] = from_player
            params['amount'] = to_player.interaction_dict[interaction_id]['amount']
            params['description'] = 'trade hotel'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(code)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            logger.debug('Updating houses and hotels on the asset')
            from_prop.num_houses = 0 # this should already be 0 but just in case
            from_prop.num_hotels -= 1

            to_player.charge_player(to_player.interaction_dict[interaction_id]['amount'], current_gameboard, bank_flag=False)
            to_player.num_total_hotels += 1
            to_player.num_total_houses -= to_prop.num_houses
            current_gameboard['bank'].total_houses += to_prop.num_houses
            logger.debug(to_player.player_name+' now has num_total_hotels '+str(to_player.num_total_hotels)+' and num_total_houses '+str(to_player.num_total_houses))
            # add to game history
            current_gameboard['history']['function'].append(to_player.charge_player)
            params = dict()
            params['self'] = to_player
            params['amount'] = to_player.interaction_dict[interaction_id]['amount']
            params['description'] = 'trade hotel'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            logger.debug('Updating houses and hotels on the asset')
            to_prop.num_houses = 0
            to_prop.num_hotels += 1

            logger.debug('Transferred hotel from ' + from_player.player_name + " to " + to_player.player_name)
            del from_player.agent._agent_memory['made_offers'][interaction_id]
            del to_player.interaction_dict[interaction_id]
            return flag_config_dict['successful_action']

        elif to_player.interaction_dict[interaction_id]['house']:
            from_prop = to_player.interaction_dict[interaction_id]['location']
            logger.debug('Looking to trade house on '+ from_prop.name)
            current_asset_num_houses = from_prop.num_houses
            for same_colored_asset in current_gameboard['color_assets'][from_prop.color]:
                if same_colored_asset == from_prop:
                    continue
                if same_colored_asset.num_houses > current_asset_num_houses or same_colored_asset.num_hotels == 1:
                    logger.debug('All same-colored properties must stay uniformly improved. Returning failure code')
                    return flag_config_dict['failure_code']

            to_prop = to_player.interaction_dict[interaction_id]['to_location']
            logger.debug('Looking to place house on '+ to_prop.name)
            if to_prop.num_hotels > 0 or to_prop.num_houses == current_gameboard['bank'].house_limit_before_hotel:
                logger.debug('There is already a hotel here or you have built the max number of houses that you can on a property. '
                             'Not permitted another house. Returning failure code')
                return flag_config_dict['failure_code']

            current_asset_num_houses = to_prop.num_houses
            for same_colored_asset in current_gameboard['color_assets'][to_prop.color]:
                if same_colored_asset == to_prop:
                    continue
                if same_colored_asset.num_houses < current_asset_num_houses or same_colored_asset.num_hotels > 0:
                    print(same_colored_asset.name, same_colored_asset.num_houses, current_asset_num_houses, to_prop.num_hotels, same_colored_asset.num_hotels)
                    logger.debug('All same-colored properties must stay uniformly improved. Returning failure code 1')
                    return flag_config_dict['failure_code']

            logger.debug(to_player.player_name + " accepting trade house offer from " + from_player.player_name)
            code = from_player.receive_cash(to_player.interaction_dict[interaction_id]['amount'], current_gameboard, bank_flag=False)
            from_player.num_total_houses -= 1
            logger.debug(from_player.player_name+' now has num_total_hotels '+str(from_player.num_total_hotels)+' and num_total_houses '+str(from_player.num_total_houses))
            # add to game history
            current_gameboard['history']['function'].append(from_player.receive_cash)
            params = dict()
            params['self'] = from_player
            params['amount'] = to_player.interaction_dict[interaction_id]['amount']
            params['description'] = 'trade house'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(code)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            logger.debug('Updating houses and hotels on the asset')
            from_prop.num_houses -= 1

            to_player.charge_player(to_player.interaction_dict[interaction_id]['amount'], current_gameboard, bank_flag=False)
            to_player.num_total_houses += 1
            logger.debug(to_player.player_name + ' now has num_total_hotels '+str(to_player.num_total_hotels) + ' and num_total_houses '+str(to_player.num_total_houses))
            # add to game history
            current_gameboard['history']['function'].append(to_player.charge_player)
            params = dict()
            params['self'] = to_player
            params['amount'] = to_player.interaction_dict[interaction_id]['amount']
            params['description'] = 'trade house'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            logger.debug('Updating houses and hotels on the asset')
            to_prop.num_houses += 1

            ####### Peter debug
            logger.debug((to_player.interaction_dict[interaction_id]['location'].name) + " trade into " + (to_player.interaction_dict[interaction_id]['to_location'].name))
            #######
            logger.debug('Transferred house/hotels from ' + from_player.player_name + " to " + to_player.player_name)
            del from_player.agent._agent_memory['made_offers'][interaction_id]
            del to_player.interaction_dict[interaction_id]
            return flag_config_dict['successful_action']

# Interaction 8
def make_futures_contract(from_player, to_player, interaction_params_dict, current_gameboard):
    """
    from_player makes a contract to to_player for a certain agreed upon amount for transfer of property to to_player when from_player purchases it.
    :param from_player:
    :param to_player:
    :param interaction_params_dict:
    :param current_gameboard:
    :return:
    """
    if to_player.status == 'lost':
        logger.debug("Futures contract is being made to a player who has lost the game already! Returning failure code.")
        return flag_config_dict['failure_code']
    elif interaction_params_dict['location'].loc_class != 'real_estate':
        logger.debug(interaction_params_dict['location'].name + " is not a real estate. Returning failure code.")
        return flag_config_dict['failure_code']
    else:
        interaction_id = current_gameboard['interaction_id']
        if 'made_offers' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['made_offers'] = dict()
        else:
            # check for same outstanding offers, cannot make same offer twice when outstanding
            for id, v in to_player.interaction_dict.items():
                if v['from_player'] == from_player and v['location'] == interaction_params_dict['location']:
                    logger.debug(from_player.player_name + " has already made the same offer to " + to_player.player_name + " and is still outstanding. Returning failure code")
                    return flag_config_dict['failure_code']

            for it, v in from_player.agent._agent_memory['made_offers'].items():
                if v['to_player'] == to_player and v['location'] == interaction_params_dict['location']:
                    logger.debug(from_player.player_name + " has already made the same offer to " + to_player.player_name + " and is still outstanding. Returning failure code")
                    return flag_config_dict['failure_code']

        from_player.agent._agent_memory['made_offers'][interaction_id] = dict()
        from_player.agent._agent_memory['made_offers'][interaction_id]['to_player'] = to_player
        from_player.agent._agent_memory['made_offers'][interaction_id]['accepted'] = False
        from_player.agent._agent_memory['made_offers'][interaction_id]['location'] = interaction_params_dict['location']
        from_player.agent._agent_memory['made_offers'][interaction_id]['contract_price'] = interaction_params_dict['contract_price']
        from_player.agent._agent_memory['made_offers'][interaction_id]['amount'] = interaction_params_dict['amount']

        to_player.interaction_dict[interaction_id] = dict()
        to_player.interaction_dict[interaction_id]['from_player'] = from_player
        to_player.interaction_dict[interaction_id]['location'] = interaction_params_dict['location']
        to_player.interaction_dict[interaction_id]['contract_price'] = interaction_params_dict['contract_price']
        to_player.interaction_dict[interaction_id]['amount'] = interaction_params_dict['amount']

        current_gameboard['interaction_id'] += 1
        logger.debug(from_player.player_name + " has made a futures contract offer on " + interaction_params_dict['location'].name + " to " + to_player.player_name)
        return flag_config_dict['successful_action']


def accept_futures_contract(from_player, to_player, interaction_id, decision, current_gameboard):
    if interaction_id not in to_player.interaction_dict:
        logger.debug("Something wrong with novelty injection...")
        raise Exception

    elif not decision:
        logger.debug(to_player.player_name + " rejected futures contract offer from " + from_player.player_name)
        del from_player.agent._agent_memory['made_offers'][interaction_id]
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['successful_action']

    elif 'made_offers' in from_player.agent._agent_memory and interaction_id not in from_player.agent._agent_memory['made_offers']:
        logger.debug("Interaction id does not exist! Returning failure code.")
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['failure_code']

    elif to_player.interaction_dict[interaction_id]['location'].loc_class != "real_estate":
        logger.debug(to_player.interaction_dict[interaction_id]['location'].name + " not of type real estate. Returning failure code.")
        del from_player.agent._agent_memory['made_offers'][interaction_id]
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['failure_code']

    else:
        from_player.agent._agent_memory['made_offers'][interaction_id]['accepted'] = True
        logger.debug(to_player.player_name + " has accepted a futures contract offer on " +
                     from_player.agent._agent_memory['made_offers'][interaction_id]['location'].name + " from " + from_player.player_name +
                     " for a contract price of " + str(from_player.agent._agent_memory['made_offers'][interaction_id]['contract_price']))

        code = to_player.receive_cash(to_player.interaction_dict[interaction_id]['contract_price'], current_gameboard, bank_flag=False)
        # add to game history
        current_gameboard['history']['function'].append(to_player.receive_cash)
        params = dict()
        params['self'] = to_player
        params['amount'] = to_player.interaction_dict[interaction_id]['contract_price']
        params['description'] = 'futures contract'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(code)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        from_player.charge_player(to_player.interaction_dict[interaction_id]['contract_price'], current_gameboard, bank_flag=False)
        # add to game history
        current_gameboard['history']['function'].append(from_player.charge_player)
        params = dict()
        params['self'] = from_player
        params['amount'] = to_player.interaction_dict[interaction_id]['contract_price']
        params['description'] = 'futures contract'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        logger.debug(from_player.player_name + " paid contract price to " + to_player.player_name)
        del to_player.interaction_dict[interaction_id]
        return flag_config_dict['successful_action']


def transfer_property_on_futures_contract(player, position, current_gameboard):
    if 'made_offers' in player.agent._agent_memory:
        import copy
        offers = copy.deepcopy(player.agent._agent_memory['made_offers'])
        for id, offer in offers.items():
            if offer['accepted']:
                logger.debug("Trying to transfer " + offer['location'].name + " to " + player.player_name + " as part of approved futures contract since player is passing GO.")
                if offer['location'].owned_by != offer['to_player']:
                    logger.debug(offer['location'].name + " not owned by player in futures contract. Returning failure code.")
                    # print("1", offer['location'].owned_by.player_name)
                    return flag_config_dict['failure_code']

                if offer['location'].is_mortgaged:
                    logger.debug(offer['location'].name + " is mortgaged. Forcefully freeing mortgage for property transfer since futures contract was made.")
                    #offer['to_player'].charge_player(offer['location'].calculate_mortgage_owed(offer['location'], current_gameboard), current_gameboard, bank_flag=True)
                    offer['to_player'].charge_player(
                        offer['location'].calculate_mortgage_owed(offer['location'], current_gameboard),
                        current_gameboard, bank_flag=True)
                    logger.debug(offer['to_player'].player_name+" has paid down mortgage with interest. Setting status of asset to unmortgaged, and removing asset from player's mortgaged set")
                    offer['location'].is_mortgaged = False
                    offer['to_player'].mortgaged_assets.remove(offer['location'])
                    logger.debug('Mortgage has successfully been freed.')

                elif offer['location'].num_houses > 0 or offer['location'].num_hotels:
                    logger.debug(offer['location'].name + " has improvements. Forcefully removing improvements for property transfer since futures contract was made.")
                    # remove improvements from all same color group properties since player wont have monopoly
                    _remove_all_improvements(offer['to_player'], offer['location'], current_gameboard)

                logger.debug("Transferring property from " + offer['to_player'].player_name + " to " + player.player_name)
                to_player = offer['to_player']
                code = to_player.receive_cash(offer['amount'], current_gameboard, bank_flag=False)
                # add to game history
                current_gameboard['history']['function'].append(to_player.receive_cash)
                params = dict()
                params['self'] = to_player
                params['amount'] = offer['amount']
                params['description'] = 'property price in futures contract'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                player.charge_player(offer['amount'], current_gameboard, bank_flag=False)
                # add to game history
                current_gameboard['history']['function'].append(player.charge_player)
                params = dict()
                params['self'] = player
                params['amount'] = offer['amount']
                params['description'] = 'property price in futures contract'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                logger.debug(player.player_name + " finished paying " + to_player.player_name + " price of property as stated in futures contract.")

                offer['location'].transfer_property_between_players(to_player, player, current_gameboard)
                del player.agent._agent_memory['made_offers'][id]


def _remove_all_improvements(player, location, current_gameboard):
    # doubt, should the bank pay the player or not cause its force remove?
    # taken care of in transfer_property_between_players -> update_asset_owned -> remove asset
    logger.debug('Attempting to remove asset ' + location.name + ' from ownership of ' + player.player_name)
    if location not in player.assets:
        logger.error('Error! Player does not own asset!')
        logger.error("Exception")
        raise Exception

    logger.debug('total no. of assets now owned by player: ' + str(len(player.assets)))

    if type(location) == RealEstateLocation:
        if location.color in player.full_color_sets_possessed:
            player.full_color_sets_possessed.remove(location.color)

        if location.num_houses > 0:
            player.num_total_houses -= location.num_houses
            logger.debug('Remove houses for future contract.')
            logger.debug('Decrementing ' + player.player_name + "'s num_total_houses count by " + str(location.num_houses) +
                         ". Total houses now owned by player now is " + str(player.num_total_houses))
        elif location.num_hotels > 0:
            player.num_total_hotels -= location.num_hotels
            logger.debug('Remove hotels for future contract.')
            logger.debug('Decrementing ' + player.player_name + "'s num_total_hotels count by " + str(location.num_hotels) +
                         ". Total hotels now owned by player now is " + str(player.num_total_hotels))
    else:
        logger.error('The property to be removed from the portfolio is not real estate. How did it get here?')
        logger.error("Exception")
        raise Exception

    if location.is_mortgaged:  # the asset is still mortgaged after we remove it from the player's portfolio. The next player must free it up.
        logger.debug('asset ' + location.name + " is mortgaged. Removing from player's mortgaged assets.")
        player.mortgaged_assets.remove(location)
        logger.debug('Total number of mortgaged assets owned by player is ' + str(len(player.mortgaged_assets)))


# hongyu interaction below
# Interaction 1
def make_trade_offer_within_incoming_group(from_player, offer, to_player, current_gameboard):
    # modify add current_gameboard into make_trade_offer() function in action_choices file
    """
    Action for one player to make a trade offer to another player to trade cash or properties or both. Note that
    the trade is processed only if to_player invokes accept_trade_offer when it is their turn next.

    a specific version of make trade offer func for interaction novelty, which player could only make trade offer
    with others if and only if from_player and to_player are in the same incoming group
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

    - if players are not in the same incoming group
    """
    if to_player.status == 'lost':
        logger.debug("Trade offer is being made to a player who has lost the game already! Returning failure code.")
        return flag_config_dict['failure_code']

    net_worth_list = dict()
    for player in current_gameboard['players']:
        if player.status != 'lost':
            net_worth_list[player.player_name] = _compute_net_worth_of_the_agent(player, current_gameboard)

    avg_net_worth = None
    if len(net_worth_list) > 2:
        avg_net_worth = sum(net_worth_list.values()) / len(net_worth_list)
    # print(avg_net_worth, net_worth_list)
    # if there are more than two players in the game board, then there is an incoming group for players
    if avg_net_worth and \
            ((net_worth_list[from_player.player_name] <= avg_net_worth < net_worth_list[to_player.player_name]) or
             (net_worth_list[to_player.player_name] <= avg_net_worth < net_worth_list[from_player.player_name])):
        # print(f'{from_player.player_name} and {to_player.player_name} are not in the same incoming group')
        logger.debug(f'{from_player.player_name} and {to_player.player_name} are not in the same incoming group')
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
        logger.debug('trade_within_incoming_group injected')
        return flag_config_dict['successful_action'] # offer has been made


def _compute_net_worth_of_the_agent(player, current_gameboard):
    """
    compute net worth of a provided player
    :param player:
    :param current_gameboard:
    :return: net worth
    """
    networth = player.current_cash
    if player.assets:
        for prop in player.assets:
            if prop.loc_class == 'real_estate':
                networth += prop.price
                networth += prop.num_houses*prop.price_per_house
                networth += prop.num_hotels*prop.price_per_house*(current_gameboard['bank'].house_limit_before_hotel + 1)
            elif prop.loc_class == 'railroad':
                networth += prop.price
            elif prop.loc_class == 'utility':
                networth += prop.price
    logger.debug(f'{player.player_name} has net worth {networth}')
    return networth


# Interaction 2
def ask_for_installment(from_player, to_player, interaction_params_dict, current_gameboard):
    """
    from_player assign a new interaction id to to_player interaction_dict so that to_player would be able to
    decide whether reject/accept the action
    :param from_player:
    :param to_player:
    :param interaction_params_dict:
    :param current_gameboard:
    :return:
    """
    if interaction_params_dict['location'].loc_class != 'real_estate' and \
            interaction_params_dict['location'].loc_class != 'railroad' and \
            interaction_params_dict['location'].loc_class != 'utility':
        logger.debug('Location needs to be a real estate/railroad/utility location to execute this action choice.')
        return action_choices.flag_config_dict['failure_code']

    if 'rent_installment' in from_player.agent._agent_memory:
        for temp_id, item in from_player.agent._agent_memory['rent_installment'].items():
            if item['location'] == interaction_params_dict['location'] and item['to_player'] == to_player:
                logger.debug(f'{from_player.player_name} has same contract with {to_player.player_name}')
                return action_choices.flag_config_dict['failure_code']

    if from_player == to_player:
        logger.debug(f'{from_player.player_name} Cannot make interaction offer to itself')
        return action_choices.flag_config_dict['failure_code']
    if len(current_gameboard['interaction_schema'].keys() & interaction_params_dict.keys()) != len(current_gameboard['interaction_schema']):
        logger.debug(f'did not send it proper interaction schema')
        return action_choices.flag_config_dict['failure_code']
    if interaction_params_dict['location'].owned_by != to_player:
        logger.debug(f"interaction offer send to wrong player who did not own {interaction_params_dict['location'].name}")
        return action_choices.flag_config_dict['failure_code']



    logger.debug(f'{from_player.player_name} ask for installment to {to_player.player_name} with param {interaction_params_dict}')
    # print(f'{from_player.player_name} ask for installment to {to_player.player_name} with param {interaction_params_dict}')
    if 'interaction_schema' in current_gameboard:
        # inject rent_installment key into agent memory for further usage
        if 'rent_installment' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['rent_installment'] = dict()
        if 'rent_installment' not in to_player.agent._agent_memory:
            to_player.agent._agent_memory['rent_installment'] = dict()

        # only real_estate/railroad/utitlity could be paid with installment
        if interaction_params_dict['location'].loc_class == 'real_estate' or \
                interaction_params_dict['location'].loc_class == 'railroad' or \
                interaction_params_dict['location'].loc_class == 'utility':

            # interaction offer schema check
            if interaction_params_dict['num_rounds_left'] < 0:
                return action_choices.flag_config_dict['failure_code']
            if interaction_params_dict['initial_charge_amount'] < 0:
                return action_choices.flag_config_dict['failure_code']

            # from_player decide installment fee and etc
            interaction_id = current_gameboard['default_interaction_id']

            from_player.agent._agent_memory['rent_installment'][interaction_id] = dict()
            from_player.agent._agent_memory['rent_installment'][interaction_id]['num_rounds_left'] = interaction_params_dict['num_rounds_left']
            from_player.agent._agent_memory['rent_installment'][interaction_id]['installment_fee'] = interaction_params_dict['installment_fee']
            from_player.agent._agent_memory['rent_installment'][interaction_id]['initial_charge_amount'] = interaction_params_dict['initial_charge_amount']
            from_player.agent._agent_memory['rent_installment'][interaction_id]['location'] = interaction_params_dict['location']
            from_player.agent._agent_memory['rent_installment'][interaction_id]['to_player'] = to_player

            # print interaction schema --> {key: expected value (data type) grounding later}

            interaction_params_dict['from_player'] = from_player
            to_player.interaction_dict[interaction_id] = interaction_params_dict

            # increase interaction id for next potential interaction id created by agent
            current_gameboard['default_interaction_id'] += 1
            logger.debug(f'{from_player.player_name} send request to {to_player.player_name} for installment rent payment')

        else:
            logger.debug('Cannot pay rent with installment on this location since its not real_estate/utility/railroad')
            return action_choices.flag_config_dict['failure_code']

        if 'auxiliary_check_for_go' not in current_gameboard:
            current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], "_ask_for_installment_helper")
        logger.debug(str(from_player.player_name) + " send request to " + str(to_player.player_name) + " for installment rent payment")
        return action_choices.flag_config_dict['successful_action']
    else:
        logger.debug('something wrong with novelty injection...')
        raise Exception


def _ask_for_installment_helper(player, position, current_gameboard):
    """
    the function used for charge from_player and transfer that amount to to_player since they have both agree on
    some contract for installment
    :param player: from_player object
    :param position: property where from_player need to pay the rent
    :param current_gameboard:
    :return:
    """
    if 'rent_installment' in player.agent._agent_memory:
        potential_delete_item = set()
        for interaction_id, item in player.agent._agent_memory['rent_installment'].items():
            # print(interaction_id, item)
            # detect if the new position is still belong to to_player
            if 'to_player' in item and item['location'].owned_by != item['to_player']:
                potential_delete_item.add(interaction_id)
                del item['to_player'].agent._agent_memory['rent_installment'][interaction_id]

            elif 'amount_left' in item and 'to_player' in item:  # player land on this property previously so 'amount_left' key appear
                amount_due = float(item['amount_left']/item['num_rounds_left'])
                charge_player_amt = amount_due + item['installment_fee']  # total charge amount
                to_player = player.agent._agent_memory['rent_installment'][interaction_id]['to_player']  # to_player object
                # print(f'{player.player_name} reduce amount left {amount_due} and number of rounds by 1')
                logger.debug(f'{player.player_name} reduce amount left {amount_due} and number of rounds by 1')

                if charge_player_amt < 0:
                    charge_player_amt = 0

                print(f'{player.player_name} is going to pay {charge_player_amt} to {to_player.player_name} at {item["location"].name}')


                # modify agent memory
                player.agent._agent_memory['rent_installment'][interaction_id]['num_rounds_left'] -= 1
                player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] -= amount_due


                # here need to charge from_player and transfer rent to to_player
                player.charge_player(charge_player_amt, current_gameboard, bank_flag=False)
                logger.debug(f'{player.player_name} paid rent of {charge_player_amt} to {to_player.player_name}')
                current_gameboard['history']['function'].append(player.charge_player)
                params = dict()
                params['self'] = player
                params['amount'] = charge_player_amt
                params['description'] = 'pay rent installment'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                # to_player gets the amount paid from from_player
                to_player.receive_cash(charge_player_amt, current_gameboard, bank_flag=False)
                logger.debug(f'{to_player.player_name} gets rent from {player.player_name} for {position}')
                current_gameboard['history']['function'].append(to_player.receive_cash)
                params = dict()
                params['self'] = to_player
                params['amount'] = charge_player_amt
                params['description'] = 'receive installment rent'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                # from_player completes the contract
                if player.agent._agent_memory['rent_installment'][interaction_id]['num_rounds_left'] == 0:
                    potential_delete_item.add(interaction_id)
                    del to_player.agent._agent_memory['rent_installment'][interaction_id]

            elif 'to_player' in item:  # only need to update number of rounds left since player never land on this property
                # print(f'{player.player_name} reduce number of rounds by 1')
                logger.debug(f'{player.player_name} reduce number of rounds by 1')
                to_player = player.agent._agent_memory['rent_installment'][interaction_id]['to_player']
                player.agent._agent_memory['rent_installment'][interaction_id]['num_rounds_left'] -= 1
                if player.agent._agent_memory['rent_installment'][interaction_id]['num_rounds_left'] == 0:
                    potential_delete_item.add(interaction_id)
                    del to_player.agent._agent_memory['rent_installment'][interaction_id]

        # if finish, remove contract from memories of both from_player and to_player
        for del_id in potential_delete_item:
            del player.agent._agent_memory['rent_installment'][del_id]
    else:
        logger.debug(f'{player.player_name} does not have any interaction offer signed yet')


def move_player_after_die_roll_check_rent_installment(player, rel_move, current_gameboard, check_for_go=True):
    """process_move_consequences_rent_installment
     This is a utility function used in gameplay, rather than card draw.
     The goal of the function is to move the player by rel_move steps forward from the player's current position.
     if check_for_go is disabled, we will not check for go and the player's cash will not be incremented as it would be
     if we did check and the player passed go.
     It's important to note that if we are 'visiting' in jail, this function will not set the player.currently_in_jail field to True, since it shouldn't.

     For installment, we should check if current player has assigned the contract with other on the new position
     if ture, then we should add amount to pay into the memory which would be charged after passing go
     if false, then the process would be same as before
    :param player: Player instance. This is the player to move.
    :param rel_move: An integer. The number of steps by which to move the player forward.
    :param current_gameboard: A dict. The global gameboard data structure.
    :param check_for_go: A boolean. If True, as set by default, then we will check for go and increment player cash by
    go_increment if we land on go or pass it.
    :return:  None
    """
    logger.debug('executing move_player_after_die_roll for '+player.player_name+' by '+str(rel_move)+' relative steps forward.')
    num_locations = len(current_gameboard['location_sequence'])
    go_position = current_gameboard['go_position']
    go_increment = current_gameboard['go_increment']

    new_position = (player.current_position+rel_move) % num_locations

    if 'auxiliary_check' in current_gameboard:
        current_gameboard['auxiliary_check'](player, new_position, current_gameboard)

    curr_property = current_gameboard['location_sequence'][new_position]
    if (curr_property.loc_class == 'real_estate' or curr_property.loc_class == 'railroad' or curr_property.loc_class == 'utility') \
            and 'rent_installment' in player.agent._agent_memory and not isinstance(curr_property.owned_by, Bank):
        for interaction_id, item in player.agent._agent_memory['rent_installment'].items():
            if 'to_player' in item and interaction_id not in item['to_player'].agent._agent_memory['rent_installment']:
                continue
            if 'location' in item and item['location'].name == curr_property.name:  # find a contract with this property
                # amount already being charged
                charged_amount = item['initial_charge_amount']

                # first time land on this location
                if 'amount_left' not in item:
                    if curr_property.loc_class == 'real_estate':
                        amount_left = RealEstateLocation.calculate_rent(curr_property, current_gameboard)
                        player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] = amount_left - charged_amount
                    elif curr_property.loc_class == 'railroad':
                        amount_left = RailroadLocation.calculate_railroad_dues(curr_property, current_gameboard)
                        player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] = amount_left - charged_amount
                    elif curr_property.loc_class == 'utility':
                        amount_left = UtilityLocation.calculate_utility_dues(curr_property, current_gameboard, current_gameboard['current_die_total'])
                        player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] = amount_left - charged_amount
                    else:
                        logger.debug('interaction offer could only include real_estate, railraod, and utility, something weng wrong')
                        raise Exception
                else:  # more than one time land on this location
                    if curr_property.loc_class == 'real_estate':
                        amount_left = RealEstateLocation.calculate_rent(curr_property, current_gameboard)
                        player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] += amount_left - charged_amount
                    elif curr_property.loc_class == 'railroad':
                        amount_left = RailroadLocation.calculate_railroad_dues(curr_property, current_gameboard)
                        player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] += amount_left - charged_amount
                    elif curr_property.loc_class == 'utility':
                        amount_left = UtilityLocation.calculate_utility_dues(curr_property, current_gameboard, current_gameboard['current_die_total'])
                        player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] += amount_left - charged_amount
                    else:
                        logger.debug('interaction offer could only include real_estate, railraod, and utility, something weng wrong')
                        raise Exception
                logger.debug(f'{player.player_name} adding proper amount into the interaction offer')
                break  # only one offer could be in this location

    if check_for_go:
        if _has_player_passed_go(player.current_position, new_position, go_position):
            if 'auxiliary_check_for_go' in current_gameboard:
                current_gameboard['auxiliary_check_for_go'](player, new_position, current_gameboard)
            logger.debug(player.player_name+' passes Go.')
            code = player.receive_cash(go_increment, current_gameboard, bank_flag=True)
            # add to game history
            if code == flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(player.receive_cash)
                params = dict()
                params['self'] = player
                params['amount'] = go_increment
                params['description'] = 'go increment'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
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
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


def process_move_consequences_rent_installment(self, current_gameboard):
    """
    Given the current position of the player (e.g., after the dice has rolled and the player has been moved), what
    are the consequences of being on that location? This function provides the main logic, in particular, whether
    the player has the right to purchase a property or has to pay rent on that property etc.

    If the current_location in the contract offer, there is not need to charge player
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: None
    """
    current_location = current_gameboard['location_sequence'][self.current_position] # get the Location object corresponding to player's current position

    # check if location in contract or not
    # if within one of the contracts, then the amount should be reduced when passing go
    # if not, charge properly
    if 'rent_installment' in self.agent._agent_memory:
        for interaction_id, item in self.agent._agent_memory['rent_installment'].items():
            if 'location' in item and item['location'].name == current_location.name:
                # print(f'{self.player_name} has contract with property {current_location.name}')
                logger.debug(f'{self.player_name} has contract with property {current_location.name}')
                return

    if current_location.loc_class == 'do_nothing': # we now look at each location class case by case
        logger.debug(self.player_name+' is on a do_nothing location, namely '+current_location.name+'. Nothing to process. Returning...')
        return
    elif current_location.loc_class == 'real_estate':
        logger.debug(self.player_name+ ' is on a real estate location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+' is owned by Bank. Setting _option_to_buy to true for '+self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+current_location.owned_by.player_name+' and is not mortgaged. Proceeding to calculate and pay rent.')
            self.calculate_and_pay_rent_dues(current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(self.calculate_and_pay_rent_dues)
            params = dict()
            params['self'] = self
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            return
    elif current_location.loc_class == 'tax':
        logger.debug(self.player_name+ ' is on a tax location, namely '+ current_location.name+ '. Deducting tax...')
        tax_due = TaxLocation.calculate_tax(current_location, self, current_gameboard)
        self.charge_player(tax_due, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(self.charge_player)
        params = dict()
        params['self'] = self
        params['amount'] = tax_due
        params['description'] = 'tax'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return
    elif current_location.loc_class == 'railroad':
        logger.debug(self.player_name+ ' is on a railroad location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = RailroadLocation.calculate_railroad_dues(current_location, current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(RailroadLocation.calculate_railroad_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            recipient = current_location.owned_by
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of railroads'] = recipient.num_railroads_possessed
                params['description'] = 'railroad dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of railroads'] = recipient.num_railroads_possessed
            params['description'] = 'railroad dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            return
    elif current_location.loc_class == 'utility':
        logger.debug(self.player_name+ ' is on a utility location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            dues = UtilityLocation.calculate_utility_dues(current_location, current_gameboard, current_gameboard['current_die_total'])
            # add to game history
            current_gameboard['history']['function'].append(UtilityLocation.calculate_utility_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            params['die_total'] = current_gameboard['current_die_total']
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            recipient = current_location.owned_by
            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of utilities'] = recipient.num_utilities_possessed
                params['description'] = 'utility dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of utilities'] = recipient.num_utilities_possessed
            params['description'] = 'utility dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            return
    elif current_location.loc_class == 'action':
        logger.debug(self.player_name+ ' is on an action location, namely '+ current_location.name+ '. Performing action...')
        current_location.perform_action(self, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(current_location.perform_action)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return
    else:
        logger.error(self.player_name+' is on an unidentified location type. Raising exception.')
        logger.error("Exception")
        raise Exception


def accept_ask_for_installment(from_player, to_player, interaction_id, decision, current_gameboard):
    """
    this function would be run whether to_player decide to accept/reject the offer. If decision is true then we are
    going to trigger some function. If not, we are just going to delete that from to_player's interaction dict
    :param from_player: offer from this player
    :param to_player: player making decisions
    :param interaction_id: current interaction id
    :param decision: True/False
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
        #logger.debug(interaction_id)
        logger.debug(f'{to_player.player_name} accept the offer from {from_player.player_name}')
        # to_player do not need to record offer info, only the interaction_id and corresponding from_player
        to_player.agent._agent_memory['rent_installment'][interaction_id] = dict()
        to_player.agent._agent_memory['rent_installment'][interaction_id]['from_player'] = from_player



        # charge from_player the initial installment fee
        initial_amount = from_player.agent._agent_memory['rent_installment'][interaction_id]['initial_charge_amount']
        logger.debug(f'{from_player.player_name} is charged with amount {initial_amount}')
        from_player.charge_player(initial_amount, current_gameboard, bank_flag=False)
        # add to game history
        current_gameboard['history']['function'].append(from_player.charge_player)
        params = dict()
        params['self'] = from_player
        params['amount'] = initial_amount
        params['description'] = 'from_player installment rent initial charge fee'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        code = to_player.receive_cash(initial_amount, current_gameboard, bank_flag=False)
        # add to game history
        if code == action_choices.flag_config_dict['successful_action']:
            logger.debug(f'{to_player.player_name} is receiving amount {initial_amount}')
            current_gameboard['history']['function'].append(to_player.receive_cash)
            params = dict()
            params['self'] = to_player
            params['amount'] = initial_amount
            params['description'] = 'to_player receive initial rent fee'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(code)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        else:
            logger.debug("Not sure what happened! Something broke!")
            logger.error("Exception")
            raise Exception

    if not decision:  # if to_player reject this offer, from_player delete corresponding offer from its memory
        logger.debug(str(to_player.player_name) + " reject installment rent payment from " + str(from_player.player_name))
        del from_player.agent._agent_memory['rent_installment'][interaction_id]

    # if reach here, either accept or reject, remove interaction_id from to_player's interaction_dict
    del to_player.interaction_dict[interaction_id]
    logger.debug(str(to_player.player_name) + " accept installment rent payment from " + str(from_player.player_name))
    return flag_config_dict['successful_action']




# Interaction 9

def ask_for_installment_forever(from_player, to_player, interaction_params_dict, current_gameboard):
    """
    from_player assign a new interaction id to to_player interaction_dict so that to_player would be able to
    decide whether reject/accept the action
    :param from_player:
    :param to_player:
    :param interaction_params_dict:
    :param current_gameboard:
    :return:
    """
    if interaction_params_dict['location'].loc_class != 'real_estate' and \
            interaction_params_dict['location'].loc_class != 'railroad' and \
            interaction_params_dict['location'].loc_class != 'utility':
        logger.debug('Location needs to be a real estate/railroad/utility location to execute this action choice.')
        return action_choices.flag_config_dict['failure_code']

    if 'rent_installment' in to_player.agent._agent_memory:
        for temp_id, item in from_player.agent._agent_memory['rent_installment'].items():
            if item['location'] == interaction_params_dict['location'] and item['to_player'] == to_player:
                logger.debug(f'{from_player.player_name} has same contract with {to_player.player_name}')
                return action_choices.flag_config_dict['failure_code']

    if from_player == to_player:
        logger.debug(f'{from_player.player_name} Cannot make interaction offer to itself')
        return action_choices.flag_config_dict['failure_code']
    if len(current_gameboard['interaction_schema'].keys() & interaction_params_dict.keys()) != len(current_gameboard['interaction_schema']):
        logger.debug(f'did not send it proper interaction schema')
        return action_choices.flag_config_dict['failure_code']
    if interaction_params_dict['location'].owned_by != to_player:
        logger.debug(f"interaction offer send to wrong player who did not own {interaction_params_dict['location'].name}")
        return action_choices.flag_config_dict['failure_code']



    logger.debug(f'{from_player.player_name} ask for installment to {to_player.player_name} with param {interaction_params_dict}')
    # print(f'{from_player.player_name} ask for installment to {to_player.player_name} with param {interaction_params_dict}')
    if 'interaction_schema' in current_gameboard:
        # inject rent_installment key into agent memory for further usage
        if 'rent_installment' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['rent_installment'] = dict()
        if 'rent_installment' not in to_player.agent._agent_memory:
            to_player.agent._agent_memory['rent_installment'] = dict()

        # only real_estate/railroad/utitlity could be paid with installment
        if interaction_params_dict['location'].loc_class == 'real_estate' or \
                interaction_params_dict['location'].loc_class == 'railroad' or \
                interaction_params_dict['location'].loc_class == 'utility':

            # interaction offer schema check
            if interaction_params_dict['installment_fee'] < 0:
                return action_choices.flag_config_dict['failure_code']
            if interaction_params_dict['initial_charge_amount'] < 0:
                return action_choices.flag_config_dict['failure_code']

            # from_player decide installment fee and etc
            interaction_id = current_gameboard['default_interaction_id']

            from_player.agent._agent_memory['rent_installment'][interaction_id] = dict()
            from_player.agent._agent_memory['rent_installment'][interaction_id]['installment_fee'] = interaction_params_dict['installment_fee']
            from_player.agent._agent_memory['rent_installment'][interaction_id]['initial_charge_amount'] = interaction_params_dict['initial_charge_amount']
            from_player.agent._agent_memory['rent_installment'][interaction_id]['location'] = interaction_params_dict['location']
            from_player.agent._agent_memory['rent_installment'][interaction_id]['to_player'] = to_player

            # print interaction schema --> {key: expected value (data type) grounding later}

            interaction_params_dict['from_player'] = from_player
            to_player.interaction_dict[interaction_id] = interaction_params_dict

            # increase interaction id for next potential interaction id created by agent
            current_gameboard['default_interaction_id'] += 1
            logger.debug(f'{from_player.player_name} send request to {to_player.player_name} for installment rent payment forever')

        else:
            logger.debug('Cannot pay rent with installment on this location since its not real_estate/utility/railroad')
            return action_choices.flag_config_dict['failure_code']

        if 'auxiliary_check_for_go' not in current_gameboard:
            current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], "_ask_for_installment_forever_helper")
        logger.debug(str(from_player.player_name) + " send request to " + str(to_player.player_name) + " for installment rent payment")
        return action_choices.flag_config_dict['successful_action']
    else:
        logger.debug('something wrong with novelty injection...')
        raise Exception

def _ask_for_installment_forever_helper(player, position, current_gameboard):
    """
    the function used for charge from_player and transfer that amount to to_player since they have both agree on
    some contract for installment
    :param player: from_player object
    :param position: property where from_player need to pay the rent
    :param current_gameboard:
    :return:
    """
    if 'rent_installment' in player.agent._agent_memory:
        potential_delete_item = set()
        for interaction_id, item in player.agent._agent_memory['rent_installment'].items():
            # detect if the new position is still belong to to_player
            if 'to_player' in item and item['location'].owned_by != item['to_player']:
                potential_delete_item.add(interaction_id)
                del item['to_player'].agent._agent_memory['rent_installment'][interaction_id]

            elif 'amount_left' in item and 'to_player' in item:  # player land on this property previously so 'amount_left' key appear
                #amount_due = float(item['amount_left']/item['num_rounds_left'])
                charge_player_amt = item['installment_fee']
                to_player = player.agent._agent_memory['rent_installment'][interaction_id]['to_player']  # to_player object
                # print(f'{player.player_name} reduce amount left {amount_due} and number of rounds by 1')
                #logger.debug(f'{player.player_name} reduce amount left {amount_due} and number of rounds by 1')


                print(f'{player.player_name} is going to pay {charge_player_amt} to {to_player.player_name} at {item["location"].name}')

                # modify agent memory
                #player.agent._agent_memory['rent_installment'][interaction_id]['num_rounds_left'] -= 1
                #player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] -= amount_due


                # here need to charge from_player and transfer rent to to_player
                player.charge_player(charge_player_amt, current_gameboard, bank_flag=False)
                logger.debug(f'{player.player_name} paid rent of {charge_player_amt} to {to_player.player_name}')
                current_gameboard['history']['function'].append(player.charge_player)
                params = dict()
                params['self'] = player
                params['amount'] = charge_player_amt
                params['description'] = 'pay rent installment'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                # to_player gets the amount paid from from_player
                to_player.receive_cash(charge_player_amt, current_gameboard, bank_flag=False)
                logger.debug(f'{to_player.player_name} gets rent from {player.player_name} for {position}')
                current_gameboard['history']['function'].append(to_player.receive_cash)
                params = dict()
                params['self'] = to_player
                params['amount'] = charge_player_amt
                params['description'] = 'receive installment rent'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                # from_player completes the contract
                #if player.agent._agent_memory['rent_installment'][interaction_id]['num_rounds_left'] == 0:
                #    potential_delete_item.add(interaction_id)
                #    del to_player.agent._agent_memory['rent_installment'][interaction_id]
            """
            elif 'to_player' in item:  # only need to update number of rounds left since player never land on this property
                # print(f'{player.player_name} reduce number of rounds by 1')
                logger.debug(f'{player.player_name} reduce number of rounds by 1')
                to_player = player.agent._agent_memory['rent_installment'][interaction_id]['to_player']
                if player.agent._agent_memory['rent_installment'][interaction_id]['num_rounds_left'] == 0:
                    potential_delete_item.add(interaction_id)
                    del to_player.agent._agent_memory['rent_installment'][interaction_id]
            """
        # if finish, remove contract from memories of both from_player and to_player
        for del_id in potential_delete_item:
            del player.agent._agent_memory['rent_installment'][del_id]
    else:
        logger.debug(f'{player.player_name} does not have any interaction offer signed yet')

# Interaction 10
def ask_for_global_rent_installment(from_player, to_player, interaction_params_dict, current_gameboard):
    """
    from_player assign a new interaction id to to_player interaction_dict so that to_player would be able to
    decide whether reject/accept the action
    :param from_player:
    :param to_player:
    :param interaction_params_dict:
    :param current_gameboard:
    :return:
    """

    if 'rent_installment' in to_player.agent._agent_memory:
        for temp_id, item in from_player.agent._agent_memory['rent_installment'].items():
            if item['to_player'] == to_player:
                logger.debug(f'{from_player.player_name} has same contract with {to_player.player_name}')
                return action_choices.flag_config_dict['failure_code']

    if from_player == to_player:
        logger.debug(f'{from_player.player_name} Cannot make interaction offer to itself')
        return action_choices.flag_config_dict['failure_code']
    if len(current_gameboard['interaction_schema'].keys() & interaction_params_dict.keys()) != len(current_gameboard['interaction_schema']):
        logger.debug(f'did not send it proper interaction schema')
        return action_choices.flag_config_dict['failure_code']



    logger.debug(f'{from_player.player_name} ask for installment to {to_player.player_name} with param {interaction_params_dict}')
    # print(f'{from_player.player_name} ask for installment to {to_player.player_name} with param {interaction_params_dict}')
    if 'interaction_schema' in current_gameboard:
        # inject rent_installment key into agent memory for further usage
        if 'rent_installment' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['rent_installment'] = dict()
        if 'rent_installment' not in to_player.agent._agent_memory:
            to_player.agent._agent_memory['rent_installment'] = dict()

        # only real_estate/railroad/utitlity could be paid with installment
        if True:

            # interaction offer schema check
            if interaction_params_dict['principal_fraction'] < 0:
                return action_choices.flag_config_dict['failure_code']
            if interaction_params_dict['interest_rate'] < 0:
                return action_choices.flag_config_dict['failure_code']
            if interaction_params_dict['initial_charge_amount'] < 0:
                return action_choices.flag_config_dict['failure_code']

            # from_player decide installment fee and etc
            interaction_id = current_gameboard['default_interaction_id']

            from_player.agent._agent_memory['rent_installment'][interaction_id] = dict()
            from_player.agent._agent_memory['rent_installment'][interaction_id]['principal_fraction'] = interaction_params_dict['principal_fraction']
            from_player.agent._agent_memory['rent_installment'][interaction_id]['interest_rate'] = interaction_params_dict['interest_rate']
            from_player.agent._agent_memory['rent_installment'][interaction_id]['initial_charge_amount'] = interaction_params_dict['initial_charge_amount']
            from_player.agent._agent_memory['rent_installment'][interaction_id]['to_player'] = to_player

            # print interaction schema --> {key: expected value (data type) grounding later}

            interaction_params_dict['from_player'] = from_player
            to_player.interaction_dict[interaction_id] = interaction_params_dict

            # increase interaction id for next potential interaction id created by agent
            current_gameboard['default_interaction_id'] += 1
            logger.debug(f'{from_player.player_name} send request to {to_player.player_name} for installment global rent payment')

        else:
            logger.debug('Cannot pay rent with installment on this location since its not real_estate/utility/railroad')
            return action_choices.flag_config_dict['failure_code']

        if 'auxiliary_check_for_go' not in current_gameboard:
            current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], "_ask_for_global_installment_helper")
        logger.debug(str(from_player.player_name) + " send request to " + str(to_player.player_name) + " for installment global rent payment")
        return action_choices.flag_config_dict['successful_action']
    else:
        logger.debug('something wrong with novelty injection...')
        raise Exception


def _ask_for_global_installment_helper(player, position, current_gameboard):
    """
    the function used for charge from_player and transfer that amount to to_player since they have both agree on
    some contract for installment
    :param player: from_player object
    :param position: property where from_player need to pay the rent
    :param current_gameboard:
    :return:
    """
    if 'rent_installment' in player.agent._agent_memory:
        potential_delete_item = set()
        for interaction_id, item in player.agent._agent_memory['rent_installment'].items():
            # print(interaction_id, item)
            # detect if the new position is still belong to to_player
            """
            if 'to_player' in item and item['location'].owned_by != item['to_player']:
                potential_delete_item.add(interaction_id)
                del item['to_player'].agent._agent_memory['rent_installment'][interaction_id]
            """
            if 'amount_left' in item and 'to_player' in item:  # player land on this property previously so 'amount_left' key appear

                amount_due = float(item['amount_left']*item['principal_fraction'])
                charge_player_amt = amount_due * (1 + item['interest_rate']) # total charge amount
                to_player = player.agent._agent_memory['rent_installment'][interaction_id]['to_player']  # to_player object
                # print(f'{player.player_name} reduce amount left {amount_due} and number of rounds by 1')
                logger.debug(f'{player.player_name} reduce amount left {amount_due}')

                if charge_player_amt < 0:
                    charge_player_amt = 0

                print(f'{player.player_name} is going to pay {charge_player_amt} to {to_player.player_name}')

                # modify agent memory
                player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] *= (1 - item['principal_fraction'])


                # here need to charge from_player and transfer rent to to_player
                player.charge_player(charge_player_amt, current_gameboard, bank_flag=False)
                logger.debug(f'{player.player_name} paid rent of {charge_player_amt} to {to_player.player_name}')
                current_gameboard['history']['function'].append(player.charge_player)
                params = dict()
                params['self'] = player
                params['amount'] = charge_player_amt
                params['description'] = 'pay rent installment'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                # to_player gets the amount paid from from_player
                to_player.receive_cash(charge_player_amt, current_gameboard, bank_flag=False)
                logger.debug(f'{to_player.player_name} gets rent from {player.player_name} for {position}')
                current_gameboard['history']['function'].append(to_player.receive_cash)
                params = dict()
                params['self'] = to_player
                params['amount'] = charge_player_amt
                params['description'] = 'receive installment rent'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])



        # if finish, remove contract from memories of both from_player and to_player
        for del_id in potential_delete_item:
            del player.agent._agent_memory['rent_installment'][del_id]
    else:
        logger.debug(f'{player.player_name} does not have any interaction offer signed yet')

def move_player_after_die_roll_check_global_rent_installment(player, rel_move, current_gameboard, check_for_go=True):
    """
     This is a utility function used in gameplay, rather than card draw.
     The goal of the function is to move the player by rel_move steps forward from the player's current position.
     if check_for_go is disabled, we will not check for go and the player's cash will not be incremented as it would be
     if we did check and the player passed go.
     It's important to note that if we are 'visiting' in jail, this function will not set the player.currently_in_jail field to True, since it shouldn't.

     For installment, we should check if current player has assigned the contract with other on the new position
     if ture, then we should add amount to pay into the memory which would be charged after passing go
     if false, then the process would be same as before
    :param player: Player instance. This is the player to move.
    :param rel_move: An integer. The number of steps by which to move the player forward.
    :param current_gameboard: A dict. The global gameboard data structure.
    :param check_for_go: A boolean. If True, as set by default, then we will check for go and increment player cash by
    go_increment if we land on go or pass it.
    :return:  None
    """
    logger.debug('executing move_player_after_die_roll for '+player.player_name+' by '+str(rel_move)+' relative steps forward.')
    num_locations = len(current_gameboard['location_sequence'])
    go_position = current_gameboard['go_position']
    go_increment = current_gameboard['go_increment']

    new_position = (player.current_position+rel_move) % num_locations

    if 'auxiliary_check' in current_gameboard:
        current_gameboard['auxiliary_check'](player, new_position, current_gameboard)

    curr_property = current_gameboard['location_sequence'][new_position]
    if (curr_property.loc_class == 'real_estate' or curr_property.loc_class == 'railroad' or curr_property.loc_class == 'utility') \
            and 'rent_installment' in player.agent._agent_memory and not isinstance(curr_property.owned_by, Bank):
        for interaction_id, item in player.agent._agent_memory['rent_installment'].items():
            if 'to_player' not in item:
                continue
            if 'to_player' in item and interaction_id not in item['to_player'].agent._agent_memory['rent_installment']:
                continue

            if item['to_player'].assets and curr_property in item['to_player'].assets:
                #if curr_property is in to_player's assets
                # amount already being charged
                charged_amount = item['initial_charge_amount']

                # first time land on this location
                if 'amount_left' not in item:
                    if curr_property.loc_class == 'real_estate':
                        amount_left = RealEstateLocation.calculate_rent(curr_property, current_gameboard)
                        player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] = amount_left - charged_amount
                    elif curr_property.loc_class == 'railroad':
                        amount_left = RailroadLocation.calculate_railroad_dues(curr_property, current_gameboard)
                        player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] = amount_left - charged_amount
                    elif curr_property.loc_class == 'utility':
                        amount_left = UtilityLocation.calculate_utility_dues(curr_property, current_gameboard, current_gameboard['current_die_total'])
                        player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] = amount_left - charged_amount
                    else:
                        logger.debug('interaction offer could only include real_estate, railraod, and utility, something weng wrong')
                        raise Exception
                else:  # more than one time land on this location
                    if curr_property.loc_class == 'real_estate':
                        amount_left = RealEstateLocation.calculate_rent(curr_property, current_gameboard)
                        player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] += amount_left - charged_amount
                    elif curr_property.loc_class == 'railroad':
                        amount_left = RailroadLocation.calculate_railroad_dues(curr_property, current_gameboard)
                        player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] += amount_left - charged_amount
                    elif curr_property.loc_class == 'utility':
                        amount_left = UtilityLocation.calculate_utility_dues(curr_property, current_gameboard, current_gameboard['current_die_total'])
                        player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] += amount_left - charged_amount
                    else:
                        logger.debug('interaction offer could only include real_estate, railraod, and utility, something weng wrong')
                        raise Exception
                logger.debug((player.player_name) + " having global rent: " + str(
                    player.agent._agent_memory['rent_installment'][interaction_id]['amount_left']))
                logger.debug(f'{player.player_name} adding proper amount into the interaction offer')
                break  # only one offer could be in this location

    if check_for_go:
        if _has_player_passed_go(player.current_position, new_position, go_position):
            if 'auxiliary_check_for_go' in current_gameboard:
                current_gameboard['auxiliary_check_for_go'](player, new_position, current_gameboard)
            logger.debug(player.player_name+' passes Go.')
            code = player.receive_cash(go_increment, current_gameboard, bank_flag=True)
            # add to game history
            if code == flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(player.receive_cash)
                params = dict()
                params['self'] = player
                params['amount'] = go_increment
                params['description'] = 'go increment'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
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
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

# Interaction 15
def ask_for_installment_with_restriction1(from_player, to_player, interaction_params_dict, current_gameboard):
    """
    from_player assign a new interaction id to to_player interaction_dict so that to_player would be able to
    decide whether reject/accept the action
    :param from_player:
    :param to_player:
    :param interaction_params_dict:
    :param current_gameboard:
    :return:
    """
    # check the restriction condition



    if interaction_params_dict['installment_fee_percentage'] <= 0.05 or interaction_params_dict['num_rounds_left'] >= 10:
        logger.debug("The given parameters are not followed the restrictions. Returning failure code.")
        return flag_config_dict['failure_code']
    #

    if interaction_params_dict['location'].loc_class != 'real_estate' and \
            interaction_params_dict['location'].loc_class != 'railroad' and \
            interaction_params_dict['location'].loc_class != 'utility':
        logger.debug('Location needs to be a real estate/railroad/utility location to execute this action choice.')
        return action_choices.flag_config_dict['failure_code']

    if 'rent_installment' in from_player.agent._agent_memory:
        for temp_id, item in from_player.agent._agent_memory['rent_installment'].items():
            if item['location'] == interaction_params_dict['location'] and item['to_player'] == to_player:
                logger.debug(f'{from_player.player_name} has same contract with {to_player.player_name}')
                return action_choices.flag_config_dict['failure_code']

    if from_player == to_player:
        logger.debug(f'{from_player.player_name} Cannot make interaction offer to itself')
        return action_choices.flag_config_dict['failure_code']
    if len(current_gameboard['interaction_schema'].keys() & interaction_params_dict.keys()) != len(current_gameboard['interaction_schema']):
        logger.debug(f'did not send it proper interaction schema')
        return action_choices.flag_config_dict['failure_code']
    if interaction_params_dict['location'].owned_by != to_player:
        logger.debug(f"interaction offer send to wrong player who did not own {interaction_params_dict['location'].name}")
        return action_choices.flag_config_dict['failure_code']



    logger.debug(f'{from_player.player_name} ask for installment to {to_player.player_name} with param {interaction_params_dict}')
    # print(f'{from_player.player_name} ask for installment to {to_player.player_name} with param {interaction_params_dict}')
    if 'interaction_schema' in current_gameboard:
        # inject rent_installment key into agent memory for further usage
        if 'rent_installment' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['rent_installment'] = dict()
        if 'rent_installment' not in to_player.agent._agent_memory:
            to_player.agent._agent_memory['rent_installment'] = dict()

        # only real_estate/railroad/utitlity could be paid with installment
        if interaction_params_dict['location'].loc_class == 'real_estate' or \
                interaction_params_dict['location'].loc_class == 'railroad' or \
                interaction_params_dict['location'].loc_class == 'utility':

            # interaction offer schema check
            if interaction_params_dict['num_rounds_left'] < 0:
                return action_choices.flag_config_dict['failure_code']
            if interaction_params_dict['initial_charge_amount'] < 0:
                return action_choices.flag_config_dict['failure_code']

            # from_player decide installment fee and etc
            interaction_id = current_gameboard['default_interaction_id']

            from_player.agent._agent_memory['rent_installment'][interaction_id] = dict()
            from_player.agent._agent_memory['rent_installment'][interaction_id]['num_rounds_left'] = interaction_params_dict['num_rounds_left']
            from_player.agent._agent_memory['rent_installment'][interaction_id]['installment_fee_percentage'] = interaction_params_dict['installment_fee_percentage']
            from_player.agent._agent_memory['rent_installment'][interaction_id]['initial_charge_amount'] = interaction_params_dict['initial_charge_amount']
            from_player.agent._agent_memory['rent_installment'][interaction_id]['location'] = interaction_params_dict['location']
            from_player.agent._agent_memory['rent_installment'][interaction_id]['to_player'] = to_player

            # print interaction schema --> {key: expected value (data type) grounding later}

            interaction_params_dict['from_player'] = from_player
            to_player.interaction_dict[interaction_id] = interaction_params_dict

            # increase interaction id for next potential interaction id created by agent
            current_gameboard['default_interaction_id'] += 1
            logger.debug(f'{from_player.player_name} send request to {to_player.player_name} for installment rent payment')

        else:
            logger.debug('Cannot pay rent with installment on this location since its not real_estate/utility/railroad')
            return action_choices.flag_config_dict['failure_code']

        if 'auxiliary_check_for_go' not in current_gameboard:
            current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], "_ask_for_installment_helper_restriction1")
        logger.debug(str(from_player.player_name) + " send request to " + str(to_player.player_name) + " for installment rent payment")
        return action_choices.flag_config_dict['successful_action']
    else:
        logger.debug('something wrong with novelty injection...')
        raise Exception

def _ask_for_installment_helper_restriction1(player, position, current_gameboard):
    """
    the function used for charge from_player and transfer that amount to to_player since they have both agree on
    some contract for installment
    :param player: from_player object
    :param position: property where from_player need to pay the rent
    :param current_gameboard:
    :return:
    """
    if 'rent_installment' in player.agent._agent_memory:
        potential_delete_item = set()
        for interaction_id, item in player.agent._agent_memory['rent_installment'].items():
            # print(interaction_id, item)
            # detect if the new position is still belong to to_player
            if 'to_player' in item and item['location'].owned_by != item['to_player']:
                potential_delete_item.add(interaction_id)
                del item['to_player'].agent._agent_memory['rent_installment'][interaction_id]

            elif 'amount_left' in item and 'to_player' in item:  # player land on this property previously so 'amount_left' key appear
                amount_due = float(item['amount_left']/item['num_rounds_left'])
                charge_player_amt = amount_due * (1 + item['installment_fee_percentage'])
                to_player = player.agent._agent_memory['rent_installment'][interaction_id]['to_player']  # to_player object
                # print(f'{player.player_name} reduce amount left {amount_due} and number of rounds by 1')
                logger.debug(f'{player.player_name} reduce amount left {amount_due} and number of rounds by 1')

                if charge_player_amt < 0:
                    charge_player_amt = 0

                print(f'{player.player_name} is going to pay {charge_player_amt} to {to_player.player_name} at {item["location"].name}')


                # modify agent memory
                player.agent._agent_memory['rent_installment'][interaction_id]['num_rounds_left'] -= 1
                player.agent._agent_memory['rent_installment'][interaction_id]['amount_left'] -= amount_due


                # here need to charge from_player and transfer rent to to_player
                player.charge_player(charge_player_amt, current_gameboard, bank_flag=False)
                logger.debug(f'{player.player_name} paid rent of {charge_player_amt} to {to_player.player_name}')
                current_gameboard['history']['function'].append(player.charge_player)
                params = dict()
                params['self'] = player
                params['amount'] = charge_player_amt
                params['description'] = 'pay rent installment'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                # to_player gets the amount paid from from_player
                to_player.receive_cash(charge_player_amt, current_gameboard, bank_flag=False)
                logger.debug(f'{to_player.player_name} gets rent from {player.player_name} for {position}')
                current_gameboard['history']['function'].append(to_player.receive_cash)
                params = dict()
                params['self'] = to_player
                params['amount'] = charge_player_amt
                params['description'] = 'receive installment rent'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                # from_player completes the contract
                if player.agent._agent_memory['rent_installment'][interaction_id]['num_rounds_left'] == 0:
                    potential_delete_item.add(interaction_id)
                    del to_player.agent._agent_memory['rent_installment'][interaction_id]

            elif 'to_player' in item:  # only need to update number of rounds left since player never land on this property
                # print(f'{player.player_name} reduce number of rounds by 1')
                logger.debug(f'{player.player_name} reduce number of rounds by 1')
                to_player = player.agent._agent_memory['rent_installment'][interaction_id]['to_player']
                player.agent._agent_memory['rent_installment'][interaction_id]['num_rounds_left'] -= 1
                if player.agent._agent_memory['rent_installment'][interaction_id]['num_rounds_left'] == 0:
                    potential_delete_item.add(interaction_id)
                    del to_player.agent._agent_memory['rent_installment'][interaction_id]

        # if finish, remove contract from memories of both from_player and to_player
        for del_id in potential_delete_item:
            del player.agent._agent_memory['rent_installment'][del_id]
    else:
        logger.debug(f'{player.player_name} does not have any interaction offer signed yet')


# Interaction 3
def ask_for_rent_agreement(from_player, to_player, interaction_params_dict, current_gameboard):
    """
    from_player send rent agreement request to to_player, then to_player should decide whether to accept/reject this
    offer. Rent agreement including:
        1.fraction between 0 and 1. Lower the fraction is, less rent need to be charged
    between from_player and to_player. E.x. fraction = 0 mean no rent need to be paid and fraction = 1 pay rent with
    original amount.
        2. number of rounds left, which is how long the agreement is valid during the game playing. Once from_player
    pass go, then reduce 1
    :param from_player:
    :param to_player:
    :param interaction_params_dict: player decide interaction parameters from interaction schema provided in game board
    :param current_gameboard:
    :return:
    """
    if from_player == to_player:
        logger.debug('cannot make interaction offer itself')
        return flag_config_dict['failure_code']

    player2net_worth = dict()
    for player in current_gameboard['players']:
        if player.status != 'lost':
            player2net_worth[player.player_name] = _compute_net_worth_of_the_agent(player, current_gameboard)

    # add by Peter ------
    if from_player.player_name not in player2net_worth:
        logger.debug((from_player.player_name) + "is lost already")
        return action_choices.flag_config_dict['failure_code']
    if to_player.player_name not in player2net_worth:
        logger.debug((to_player.player_name) + "is lost already")
        return action_choices.flag_config_dict['failure_code']
    # ------

    avg_net_worth = None
    if len(player2net_worth) > 2:
        avg_net_worth = sum(player2net_worth.values()) / len(player2net_worth)

    # if two players are not in the same incoming group, failure
    if avg_net_worth and \
            ((player2net_worth[from_player.player_name] <= avg_net_worth < player2net_worth[to_player.player_name]) or
             (player2net_worth[from_player.player_name] > avg_net_worth >= player2net_worth[to_player.player_name])):
        logger.debug(f"{from_player.player_name} and {to_player.player_name} are not in the same incoming group")
        return action_choices.flag_config_dict['failure_code']

    # if two player already signed some contract, failure
    if 'rent_agreement' in from_player.agent._agent_memory:  # check from_player
        for temp_id, item in from_player.agent._agent_memory['rent_agreement'].items():
            if 'from_player' in item and item['from_player'].player_name == to_player.player_name:
                logger.debug(f'{from_player.player_name} already signed contract with {to_player.player_name}')
                return action_choices.flag_config_dict['failure_code']
            if 'to_player' in item and item['to_player'].player_name == to_player.player_name:
                logger.debug(f'{from_player.player_name} already signed contract with {to_player.player_name}')
                return action_choices.flag_config_dict['failure_code']

    if 'rent_agreement' in to_player.agent._agent_memory:  # check to_player
        for temp_id, item in to_player.agent._agent_memory['rent_agreement'].items():
            if 'from_player' in item and item['from_player'].player_name == from_player.player_name:
                logger.debug(f'{to_player.player_name} already signed contract with {from_player.player_name}')
                return action_choices.flag_config_dict['failure_code']
            if 'to_player' in item and item['to_player'].player_name == from_player.player_name:
                logger.debug(f'{to_player.player_name} already signed contract with {from_player.player_name}')
                return action_choices.flag_config_dict['failure_code']

    if 'interaction_schema' in current_gameboard:
        # inject rent_agreement key into agent memory for further usage
        if 'rent_agreement' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['rent_agreement'] = dict()
        if 'rent_agreement' not in to_player.agent._agent_memory:
            to_player.agent._agent_memory['rent_agreement'] = dict()

        interaction_id = current_gameboard['default_interaction_id']

        # from_player populate its memory
        from_player.agent._agent_memory['rent_agreement'][interaction_id] = dict()
        from_player.agent._agent_memory['rent_agreement'][interaction_id]['to_player'] = to_player
        from_player.agent._agent_memory['rent_agreement'][interaction_id]['fraction'] = interaction_params_dict['fraction']
        from_player.agent._agent_memory['rent_agreement'][interaction_id]['num_rounds_left'] = interaction_params_dict['num_rounds_left']

        # send request to to_player
        interaction_params_dict['from_player'] = from_player
        to_player.interaction_dict[interaction_id] = interaction_params_dict

        # increase interaction id for next potential interaction id created by agent
        current_gameboard['default_interaction_id'] += 1
        print(f'{from_player.player_name} send request to {to_player.player_name} for rent agreement')
        logger.debug(f'{from_player.player_name} send request to {to_player.player_name} for rent agreement')

        if 'auxiliary_check_for_go' not in current_gameboard:
            current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], "_ask_for_rent_agreement")
        return action_choices.flag_config_dict['successful_action']
    else:
        logger.debug('something wrong with novelty injection...')
        raise Exception


def _ask_for_rent_agreement(player, position, current_gameboard):
    """
    replace check for go function. number of rounds left reduce 1 if pass go
    :param player: from_player
    :param position:
    :param current_gameboard:
    :return:
    """
    if 'rent_agreement' in player.agent._agent_memory:
        potential_delete_item = set()
        to_player_list = dict()
        for interaction_id, item in player.agent._agent_memory['rent_agreement'].items():
            # this interaction id is from_player
            # if 'from_player' in item then we do not want to reduce number of rounds since we count based on player who make offer
            if 'to_player' in item: # added by Peter
                to_player = player.agent._agent_memory['rent_agreement'][interaction_id]['to_player']  # to_player object
                if to_player.agent._agent_memory['rent_agreement']:

                    # from_player reduces number of rounds
                    player.agent._agent_memory['rent_agreement'][interaction_id]['num_rounds_left'] -= 1
                    # to_player reduces number of rounds
                    to_player.agent._agent_memory['rent_agreement'][interaction_id]['num_rounds_left'] -= 1

                    # usually number of rounds for from_player and to_player should always be equal
                    if player.agent._agent_memory['rent_agreement'][interaction_id]['num_rounds_left'] != \
                            to_player.agent._agent_memory['rent_agreement'][interaction_id]['num_rounds_left']:
                        logger.debug(f'Number of rounds for from_player and to_player is different, something went wrong...')
                        raise Exception

                    # from_player & to_player complete the contract
                    if player.agent._agent_memory['rent_agreement'][interaction_id]['num_rounds_left'] == 0 and \
                            to_player.agent._agent_memory['rent_agreement'][interaction_id]['num_rounds_left'] == 0:
                        potential_delete_item.add(interaction_id)
                        if to_player not in to_player_list:
                            to_player_list[to_player] = [interaction_id]
                        else:
                            to_player_list[to_player].append(interaction_id)
                else:
                    logger.debug(f'{to_player.player_name} have not signed rent agreement yet')

        # agreement finish for from_player
        for del_id in potential_delete_item:
            del player.agent._agent_memory['rent_agreement'][del_id]
        # agreement finish for to_player
        for to_player, interaction_list in to_player_list.items():
            for del_id in interaction_list:
                del to_player.agent._agent_memory['rent_agreement'][del_id]
    else:
        logger.debug(f'{player.player_name} does not have rent agreement yet')
        print(f'{player.player_name} does not have rent agreement yet')
    """if 'rent_agreement' in player.agent._agent_memory:
        potential_delete_item = set()
        to_player_list = dict()
        for interaction_id, item in player.agent._agent_memory['rent_agreement'].items():
            # this interaction id is from_player
            # if 'from_player' in item then we do not want to reduce number of rounds since we count based on player who make offer
            if 'to_player' in item:
                to_player = player.agent._agent_memory['rent_agreement'][interaction_id]['to_player']  # to_player object

                # from_player reduces number of rounds
                player.agent._agent_memory['rent_agreement'][interaction_id]['num_rounds_left'] -= 1
                # to_player reduces number of rounds
                to_player.agent._agent_memory['rent_agreement'][interaction_id]['num_rounds_left'] -= 1

                # usually number of rounds for from_player and to_player should always be equal
                if player.agent._agent_memory['rent_agreement'][interaction_id]['num_rounds_left'] != \
                        to_player.agent._agent_memory['rent_agreement'][interaction_id]['num_rounds_left']:
                    logger.debug(f'Number of rounds for from_player and to_player is different, something went wrong...')
                    raise Exception

                # from_player & to_player complete the contract
                if player.agent._agent_memory['rent_agreement'][interaction_id]['num_rounds_left'] == 0 and \
                        to_player.agent._agent_memory['rent_agreement'][interaction_id]['num_rounds_left'] == 0:
                    potential_delete_item.add(interaction_id)
                    if to_player not in to_player_list:
                        to_player_list[to_player] = [interaction_id]
                    else:
                        to_player_list[to_player].append(interaction_id)

        # agreement finish for from_player
        for del_id in potential_delete_item:
            del player.agent._agent_memory['rent_agreement'][del_id]
        # agreement finish for to_player
        for to_player, interaction_list in to_player_list.items():
            for del_id in interaction_list:
                del to_player.agent._agent_memory['rent_agreement'][del_id]
    else:
        logger.debug(f'{player.player_name} does not have rent agreement yet')
        print(f'{player.player_name} does not have rent agreement yet')
    """

def accept_ask_for_rent_agreement(from_player, to_player, interaction_id, decision, current_gameboard):
    """
    if accept to_player and from_player should have memory about this contract which would be used when charge rent
    if reject to_player would not be populated and from_player del the interaction from memory
    :param from_player:
    :param to_player:
    :param interaction_id:
    :param decision:
    :param current_gameboard:
    :return:
    """
    if interaction_id not in to_player.interaction_dict:
        logger.debug("Incorrect interaction id")
        return flag_config_dict['failure_code']
    if from_player == to_player:
        logger.debug('cannot make interaction offer with itself')
        return flag_config_dict['failure_code']

    interaction_dict = to_player.interaction_dict[interaction_id]
    if decision:  # if accept the offer

        # populate to_player, from_player is already be populate when make offer
        to_player.agent._agent_memory['rent_agreement'][interaction_id] = dict()
        to_player.agent._agent_memory['rent_agreement'][interaction_id]['fraction'] = interaction_dict['fraction']
        to_player.agent._agent_memory['rent_agreement'][interaction_id]['num_rounds_left'] = interaction_dict['num_rounds_left']
        to_player.agent._agent_memory['rent_agreement'][interaction_id]['from_player'] = from_player

    # to_player reject, from_player remove interaction from memory
    if not decision:
        del from_player.agent._agent_memory['rent_agreement'][interaction_id]

    # if reach here, either accept or reject, remove interaction_id from to_player's interaction_dict
    del to_player.interaction_dict[interaction_id]
    logger.debug(f'{to_player.player_name} accept request for rent agreement to {from_player.player_name}')
    return flag_config_dict['successful_action']


def process_move_consequences_rent_agreement(self, current_gameboard):
    """
    if two player has agreement means that they are in the same incoming group with some defined fraction to pay rent
    :param self: player who need to pay rent
    :param current_gameboard:
    :return:
    """
    current_location = current_gameboard['location_sequence'][self.current_position] # get the Location object corresponding to player's current position
    if current_location.loc_class == 'do_nothing': # we now look at each location class case by case
        logger.debug(self.player_name+' is on a do_nothing location, namely '+current_location.name+'. Nothing to process. Returning...')
        return
    elif current_location.loc_class == 'real_estate':
        logger.debug(self.player_name+ ' is on a real estate location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+' is owned by Bank. Setting _option_to_buy to true for '+self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+current_location.owned_by.player_name+' and is not mortgaged. Proceeding to calculate and pay rent.')
            self.calculate_and_pay_rent_dues(current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(self.calculate_and_pay_rent_dues)
            params = dict()
            params['self'] = self
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            return
    elif current_location.loc_class == 'tax':
        logger.debug(self.player_name+ ' is on a tax location, namely '+ current_location.name+ '. Deducting tax...')
        tax_due = TaxLocation.calculate_tax(current_location, self, current_gameboard)
        self.charge_player(tax_due, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(self.charge_player)
        params = dict()
        params['self'] = self
        params['amount'] = tax_due
        params['description'] = 'tax'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return
    elif current_location.loc_class == 'railroad':
        logger.debug(self.player_name+ ' is on a railroad location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            recipient = current_location.owned_by

            # if have agreement, get fraction
            curr_fraction = 1
            if 'rent_agreement' in self.agent._agent_memory and 'rent_agreement' in recipient.agent._agent_memory:
                intersection_res = self.agent._agent_memory['rent_agreement'].keys() & recipient.agent._agent_memory['rent_agreement'].keys()
                if intersection_res:
                    for interaction_id in intersection_res:
                        curr_fraction = self.agent._agent_memory['rent_agreement'][interaction_id]['fraction']
                        break

            dues = curr_fraction * RailroadLocation.calculate_railroad_dues(current_location, current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(RailroadLocation.calculate_railroad_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of railroads'] = recipient.num_railroads_possessed
                params['description'] = 'railroad dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of railroads'] = recipient.num_railroads_possessed
            params['description'] = 'railroad dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            return
    elif current_location.loc_class == 'utility':
        logger.debug(self.player_name+ ' is on a utility location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')
            recipient = current_location.owned_by

            # if have agreement, get fraction
            curr_fraction = 1
            if 'rent_agreement' in self.agent._agent_memory and 'rent_agreement' in recipient.agent._agent_memory:
                intersection_res = self.agent._agent_memory['rent_agreement'].keys() & recipient.agent._agent_memory['rent_agreement'].keys()
                if intersection_res:
                    for interaction_id in intersection_res:
                        curr_fraction = self.agent._agent_memory['rent_agreement'][interaction_id]['fraction']
                        break

            dues = curr_fraction * UtilityLocation.calculate_utility_dues(current_location, current_gameboard, current_gameboard['current_die_total'])
            # add to game history
            current_gameboard['history']['function'].append(UtilityLocation.calculate_utility_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            params['die_total'] = current_gameboard['current_die_total']
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(recipient.receive_cash)
                params = dict()
                params['self'] = recipient
                params['amount'] = dues
                params['number of utilities'] = recipient.num_utilities_possessed
                params['description'] = 'utility dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of utilities'] = recipient.num_utilities_possessed
            params['description'] = 'utility dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            return
    elif current_location.loc_class == 'action':
        logger.debug(self.player_name+ ' is on an action location, namely '+ current_location.name+ '. Performing action...')
        current_location.perform_action(self, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(current_location.perform_action)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return
    else:
        logger.error(self.player_name+' is on an unidentified location type. Raising exception.')
        logger.error("Exception")
        raise Exception


def calculate_and_pay_rent_dues_rent_agreement(self, current_gameboard):
    """
    calculate rent with fraction if from_player and to_player have agreement
    :param self:
    :param current_gameboard:
    :return:
    """
    current_loc = current_gameboard['location_sequence'][self.current_position]
    logger.debug('calculating and paying rent dues for '+ self.player_name+ ' who is in property '+current_loc.name+' which is owned by '+current_loc.owned_by.player_name)

    # determine if two players have agreement
    owner = current_loc.owned_by
    curr_fraction = 1
    if 'rent_agreement' in self.agent._agent_memory and 'rent_agreement' in owner.agent._agent_memory:
        intersection_res = self.agent._agent_memory['rent_agreement'].keys() & owner.agent._agent_memory['rent_agreement'].keys()
        if intersection_res:
            for interaction_id in intersection_res:
                curr_fraction = self.agent._agent_memory['rent_agreement'][interaction_id]['fraction']
                break

    rent = curr_fraction * RealEstateLocation.calculate_rent(current_loc, current_gameboard)
    # add to game history
    current_gameboard['history']['function'].append(RealEstateLocation.calculate_rent)
    params = dict()
    params['asset'] = current_loc
    params['current_gameboard'] = current_gameboard
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(rent)
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

    recipient = current_loc.owned_by
    code = recipient.receive_cash(rent, current_gameboard, bank_flag=False)
    # add to game history
    if code == action_choices.flag_config_dict['successful_action']:
        current_gameboard['history']['function'].append(recipient.receive_cash)
        params = dict()
        params['self'] = recipient
        params['amount'] = rent
        params['description'] = 'rent'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
    else:
        logger.debug("Not sure what happened! Something broke!")
        logger.error("Exception")
        raise Exception

    self.charge_player(rent, current_gameboard, bank_flag=False)
    # add to game history
    current_gameboard['history']['function'].append(self.charge_player)
    params = dict()
    params['self'] = self
    params['amount'] = rent
    params['description'] = 'rent'
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


# Interaction 4
def ask_for_invest_property(from_player, to_player, interaction_params_dict, current_gameboard):
    """
    from_player want to invest some property with a specific amount and also provide a percent which is used for
    compute dividend from the property

    Note: if the property in contract is selled, then the contract is no longer available
    :param from_player:
    :param to_player:
    :param interaction_params_dict: player decide interaction parameters from interaction schema provided in game board
    :param current_gameboard:
    :return:
    """
    # -------------------------- Peter add
    if interaction_params_dict['location'].loc_class != 'real_estate' and \
            interaction_params_dict['location'].loc_class != 'railroad' and \
            interaction_params_dict['location'].loc_class != 'utility':
        logger.debug('Location needs to be a real estate/railroad/utility location to execute this action choice.')
        return action_choices.flag_config_dict['failure_code']
    # --------------------------

    if from_player == to_player:
        logger.debug('cannot ask interaction offer to itself')
        return flag_config_dict['failure_code']
    if interaction_params_dict['location'].owned_by != to_player:
        logger.debug(f'{interaction_params_dict["location"].name} is not owned by {to_player.player_name}')
        return flag_config_dict['failure_code']

    if interaction_params_dict['percent'] > 1.0 or interaction_params_dict['percent'] < 0:
        logger.debug('percentage should be between 0 and 1')
        return flag_config_dict['failure_code']

    if 'properties_in_contract' in from_player.agent._agent_memory and interaction_params_dict['location'].name in from_player.agent._agent_memory['properties_in_contract']:
        logger.debug('cannot make an offer that is already in contract')
        return flag_config_dict['failure_code']

    if 'interaction_schema' in current_gameboard:
        # if interaction_params_dict['location'].name in current_gameboard['properties_in_contract']:
        #     logger.debug(f'{interaction_params_dict["location"].name} already in the contract, cannot be assigned again')
        #     return action_choices.flag_config_dict['failure_code']

        # inject rent_agreement key into agent memory for further usage
        if 'invest_contract' not in from_player.agent._agent_memory:
            from_player.agent._agent_memory['invest_contract'] = dict()
            from_player.agent._agent_memory['properties_in_contract'] = set()
        if 'invest_contract' not in to_player.agent._agent_memory:
            to_player.agent._agent_memory['invest_contract'] = dict()
            to_player.agent._agent_memory['properties_in_contract'] = set()

        # only real_estate/railroad/utitlity could be paid with installment
        if interaction_params_dict['location'].loc_class == 'real_estate' or \
                interaction_params_dict['location'].loc_class == 'railroad' or \
                interaction_params_dict['location'].loc_class == 'utility':

            interaction_id = current_gameboard['default_interaction_id']
            # interaction_params_dict should include fraction and number of rounds for the agreement
            # and from_player
            #interaction_params_dict['from_player'] = from_player.player_name
            interaction_params_dict['from_player'] = from_player
            to_player.interaction_dict[interaction_id] = interaction_params_dict

            # increase interaction id for next potential interaction id created by agent
            current_gameboard['default_interaction_id'] += 1
            logger.debug(f'{from_player.player_name} send request to {to_player.player_name} for investing')

        else:
            logger.debug('Cannot pay rent with installment on this location since its not real_estate/utility/railroad')
            return action_choices.flag_config_dict['failure_code']

        # if 'auxiliary_check_for_go' not in current_gameboard:
        #     current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], "_ask_for_rent_agreement")
        logger.debug(f'{from_player.player_name} send request to {to_player.player_name} for investing')
        return action_choices.flag_config_dict['successful_action']
    else:
        logger.debug('something wrong with novelty injection...')
        raise Exception


def accept_ask_for_invest_property(from_player, to_player, interaction_id, decision, current_gameboard):
    """

    :param from_player:
    :param to_player:
    :param interaction_id:
    :param decision:
    :param current_gameboard:
    :return:
    """
    if interaction_id not in to_player.interaction_dict:
        logger.debug("Incorrect interaction id")
        return flag_config_dict['failure_code']
    if from_player == to_player:
        logger.debug('cannot accept offer from itself')
        return flag_config_dict['failure_code']

    interaction_dict = to_player.interaction_dict[interaction_id]
    if decision:  # if accept the offer
        # only add this to from_player because there might be others want to make interaction offer with to_player as well
        from_player.agent._agent_memory['properties_in_contract'].add(interaction_dict['location'].name)
        # current_gameboard['properties_in_contract'].add(interaction_dict['location'].name)
        print(f'{to_player.player_name} accept interaction offer from {from_player.player_name} of interaction_id {interaction_id}')

        # populate from_player and to_player _agent_memory because to_player accept the action
        from_player.agent._agent_memory['invest_contract'][interaction_id] = dict()
        from_player.agent._agent_memory['invest_contract'][interaction_id]['invest_amount'] = interaction_dict['invest_amount']
        from_player.agent._agent_memory['invest_contract'][interaction_id]['percent'] = interaction_dict['percent']
        from_player.agent._agent_memory['invest_contract'][interaction_id]['location'] = interaction_dict['location']
        from_player.agent._agent_memory['invest_contract'][interaction_id]['to_player'] = to_player

        to_player.agent._agent_memory['invest_contract'][interaction_id] = dict()
        to_player.agent._agent_memory['invest_contract'][interaction_id]['invest_amount'] = interaction_dict['invest_amount']
        to_player.agent._agent_memory['invest_contract'][interaction_id]['percent'] = interaction_dict['percent']
        to_player.agent._agent_memory['invest_contract'][interaction_id]['location'] = interaction_dict['location']
        to_player.agent._agent_memory['invest_contract'][interaction_id]['from_player'] = from_player

        # to_player immediately get cash; from_player charge the amount
        code = to_player.receive_cash(interaction_dict['invest_amount'], current_gameboard, bank_flag=False)
        # add to game history
        if code == action_choices.flag_config_dict['successful_action']:
            current_gameboard['history']['function'].append(to_player.receive_cash)
            params = dict()
            params['self'] = to_player
            params['amount'] = interaction_dict['invest_amount']
            params['description'] = 'invested amount'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(code)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        else:
            logger.debug("Not sure what happened! Something broke!")
            logger.error("Exception")
            raise Exception

        # from_player is charge by amount it invest
        from_player.charge_player(interaction_dict['invest_amount'], current_gameboard, bank_flag=False)
        # add to game history
        current_gameboard['history']['function'].append(from_player.charge_player)
        params = dict()
        params['self'] = from_player
        params['amount'] = interaction_dict['invest_amount']
        params['description'] = 'investing amount'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

    # if reach here, either accept or reject, remove interaction_id from to_player's interaction_dict
    del to_player.interaction_dict[interaction_id]
    logger.debug(f'{to_player.player_name} accept request for investing to {from_player.player_name}')
    return flag_config_dict['successful_action']


def process_move_consequences_invest_contract(self, current_gameboard):
    """
    if two player has agreement means that they are in the same incoming group with some defined fraction to pay rent
    :param self: player who need to pay rent
    :param current_gameboard:
    :return:
    """
    current_location = current_gameboard['location_sequence'][self.current_position] # get the Location object corresponding to player's current position
    if current_location.loc_class == 'do_nothing': # we now look at each location class case by case
        logger.debug(self.player_name+' is on a do_nothing location, namely '+current_location.name+'. Nothing to process. Returning...')
        return
    elif current_location.loc_class == 'real_estate':
        logger.debug(self.player_name+ ' is on a real estate location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+' is owned by Bank. Setting _option_to_buy to true for '+self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+current_location.owned_by.player_name+' and is not mortgaged. Proceeding to calculate and pay rent.')
            self.calculate_and_pay_rent_dues(current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(self.calculate_and_pay_rent_dues)
            params = dict()
            params['self'] = self
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            return
    elif current_location.loc_class == 'tax':
        logger.debug(self.player_name+ ' is on a tax location, namely '+ current_location.name+ '. Deducting tax...')
        tax_due = TaxLocation.calculate_tax(current_location, self, current_gameboard)
        self.charge_player(tax_due, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(self.charge_player)
        params = dict()
        params['self'] = self
        params['amount'] = tax_due
        params['description'] = 'tax'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return
    elif current_location.loc_class == 'railroad':
        logger.debug(self.player_name+ ' is on a railroad location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')

            to_player = current_location.owned_by
            from_player = None
            from_player_percent = 0

            if 'invest_contract' in to_player.agent._agent_memory:
                for inter_id, item in to_player.agent._agent_memory['invest_contract'].items():
                    if 'from_player' in item and current_location.name == item['location'].name:  # find a contract with this property
                        from_player = item['from_player']
                        from_player_percent = item['percent']
                        break
            # if current_location.name in current_gameboard['properties_in_contract']:  # property in the contract
            #     for interaction_id, item in to_player.interaction_dict.items():
            #         if item['location'].name == current_location.name:
            #             from_player = item['from_player']
            #             from_player_percent = item['percent']
            #             break

            dues = RailroadLocation.calculate_railroad_dues(current_location, current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(RailroadLocation.calculate_railroad_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            code = to_player.receive_cash((1 - from_player_percent) * dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(to_player.receive_cash)
                params = dict()
                params['self'] = to_player
                params['amount'] = (1 - from_player_percent) * dues
                params['number of railroads'] = to_player.num_railroads_possessed
                params['description'] = 'railroad dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            if from_player:
                code = from_player.receive_cash(from_player_percent * dues, current_gameboard, bank_flag=False)
                # add to game history
                if code == action_choices.flag_config_dict['successful_action']:
                    current_gameboard['history']['function'].append(from_player.receive_cash)
                    params = dict()
                    params['self'] = from_player
                    params['amount'] = from_player_percent * dues
                    params['description'] = 'railroad invest dividend'
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(code)
                    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
                else:
                    logger.debug("Not sure what happened! Something broke!")
                    logger.error("Exception")
                    raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of railroads'] = to_player.num_railroads_possessed
            params['description'] = 'railroad dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            return
    elif current_location.loc_class == 'utility':
        logger.debug(self.player_name+ ' is on a utility location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')

            to_player = current_location.owned_by
            from_player = None
            from_player_percent = 0

            if 'invest_contract' in to_player.agent._agent_memory:
                for inter_id, item in to_player.agent._agent_memory['invest_contract'].items():
                    if 'from_player' in item and current_location.name == item['location'].name:  # find a contract with this property
                        from_player = item['from_player']
                        from_player_percent = item['percent']
                        break

            # if current_location.name in current_gameboard['properties_in_contract']:  # property in the contract
            #     for interaction_id, item in to_player.interaction_dict.items():
            #         if item['location'].name == current_location.name:
            #             from_player = item['from_player']
            #             from_player_percent = item['percent']
            #             break

            dues = UtilityLocation.calculate_utility_dues(current_location, current_gameboard, current_gameboard['current_die_total'])
            # add to game history
            current_gameboard['history']['function'].append(UtilityLocation.calculate_utility_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            params['die_total'] = current_gameboard['current_die_total']
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            code = to_player.receive_cash((1 - from_player_percent) * dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(to_player.receive_cash)
                params = dict()
                params['self'] = to_player
                params['amount'] = (1 - from_player_percent) * dues
                params['number of utilities'] = to_player.num_utilities_possessed
                params['description'] = 'utility dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            if from_player:
                code = from_player.receive_cash(from_player_percent * dues, current_gameboard, bank_flag=False)
                # add to game history
                if code == action_choices.flag_config_dict['successful_action']:
                    current_gameboard['history']['function'].append(from_player.receive_cash)
                    params = dict()
                    params['self'] = from_player
                    params['amount'] = from_player_percent * dues
                    params['description'] = 'utility invest dividend'
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(code)
                    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
                else:
                    logger.debug("Not sure what happened! Something broke!")
                    logger.error("Exception")
                    raise Exception

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of utilities'] = to_player.num_utilities_possessed
            params['description'] = 'utility dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            return
    elif current_location.loc_class == 'action':
        logger.debug(self.player_name+ ' is on an action location, namely '+ current_location.name+ '. Performing action...')
        current_location.perform_action(self, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(current_location.perform_action)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return
    else:
        logger.error(self.player_name+' is on an unidentified location type. Raising exception.')
        logger.error("Exception")
        raise Exception


def calculate_and_pay_rent_dues_invest_contract(self, current_gameboard):
    """

    :param self:
    :param current_gameboard:
    :return:
    """
    current_loc = current_gameboard['location_sequence'][self.current_position]
    logger.debug('calculating and paying rent dues for '+ self.player_name+ ' who is in property '+current_loc.name+' which is owned by '+current_loc.owned_by.player_name)

    # determine if two players have agreement
    to_player = current_loc.owned_by
    from_player = None
    from_player_percent = 0

    # print(to_player.agent._agent_memory)
    if 'invest_contract' in to_player.agent._agent_memory:
        for inter_id, item in to_player.agent._agent_memory['invest_contract'].items():
            if 'from_player' in item and current_loc.name == item['location'].name:  # find a contract with this property
                from_player = item['from_player']
                from_player_percent = item['percent']
                break

    # if current_loc.name in current_gameboard['properties_in_contract']:  # property in the contract
    #     for interaction_id, item in to_player.interaction_dict.items():
    #         if item['location'].name == current_loc.name:
    #             from_player = item['from_player']
    #             from_player_percent = item['percent']
    #             break

    rent = RealEstateLocation.calculate_rent(current_loc, current_gameboard)
    # add to game history
    current_gameboard['history']['function'].append(RealEstateLocation.calculate_rent)
    params = dict()
    params['asset'] = current_loc
    params['current_gameboard'] = current_gameboard
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(rent)
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

    # to_player get 1 - percent of rent
    code = to_player.receive_cash((1 - from_player_percent) * rent, current_gameboard, bank_flag=False)
    # add to game history
    if code == action_choices.flag_config_dict['successful_action']:
        current_gameboard['history']['function'].append(to_player.receive_cash)
        params = dict()
        params['self'] = to_player
        params['amount'] = (1 - from_player_percent) * rent
        params['description'] = 'rent'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
    else:
        logger.debug("Not sure what happened! Something broke!")
        logger.error("Exception")
        raise Exception

    # from_player get percent of rent
    if from_player:
        code = from_player.receive_cash(from_player_percent * rent, current_gameboard, bank_flag=False)
        # add to game history
        if code == action_choices.flag_config_dict['successful_action']:
            current_gameboard['history']['function'].append(from_player.receive_cash)
            params = dict()
            params['self'] = from_player
            params['amount'] = from_player_percent * rent
            params['description'] = 'rent'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        else:
            logger.debug("Not sure what happened! Something broke!")
            logger.error("Exception")
            raise Exception

    self.charge_player(rent, current_gameboard, bank_flag=False)
    # add to game history
    current_gameboard['history']['function'].append(self.charge_player)
    params = dict()
    params['self'] = self
    params['amount'] = rent
    params['description'] = 'rent'
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])


def sell_property_invest_remove(player, asset, current_gameboard):
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

            # remove contract from both from_player and to_player
            if 'properties_in_contract' in player.agent._agent_memory and asset.name in player.agent._agent_memory['properties_in_contract']:
                player.agent._agent_memory['properties_in_contract'].remove(asset.name)

            candidate_id = None
            from_player = None
            if 'invest_contract' in player.agent._agent_memory:
                for interaction_id, item in player.agent._agent_memory['invest_contract'].items():
                    if item['location'].name == asset.name and 'from_player' in item:
                        logger.debug(f'to_player {player.player_name} selling {asset.name} with interaction id {interaction_id}')
                        # print(f'to_player {player.player_name} selling {asset.name} with interaction id {interaction_id}')
                        from_player = item['from_player']
                        candidate_id = interaction_id
                        break

                if from_player and candidate_id:
                    del from_player.agent._agent_memory['invest_contract'][candidate_id]
                if candidate_id:
                    del player.agent._agent_memory['invest_contract'][candidate_id]

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


# interaction 11
def accept_ask_for_invest_property_with_turns(from_player, to_player, interaction_id, decision, current_gameboard):
    """

    :param from_player:
    :param to_player:
    :param interaction_id:
    :param decision:
    :param current_gameboard:
    :return:
    """
    if interaction_id not in to_player.interaction_dict:
        logger.debug("Incorrect interaction id")
        return flag_config_dict['failure_code']
    if from_player == to_player:
        logger.debug('cannot accept offer from itself')
        return flag_config_dict['failure_code']

    interaction_dict = to_player.interaction_dict[interaction_id]
    if decision:  # if accept the offer
        # only add this to from_player because there might be others want to make interaction offer with to_player as well
        from_player.agent._agent_memory['properties_in_contract'].add(interaction_dict['location'].name)
        # current_gameboard['properties_in_contract'].add(interaction_dict['location'].name)
        print(f'{to_player.player_name} accept interaction offer from {from_player.player_name} of interaction_id {interaction_id}')

        # populate from_player and to_player _agent_memory because to_player accept the action
        from_player.agent._agent_memory['invest_contract'][interaction_id] = dict()
        from_player.agent._agent_memory['invest_contract'][interaction_id]['invest_amount'] = interaction_dict['invest_amount']
        from_player.agent._agent_memory['invest_contract'][interaction_id]['percent'] = interaction_dict['percent']
        from_player.agent._agent_memory['invest_contract'][interaction_id]['location'] = interaction_dict['location']
        from_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] = interaction_dict['num_rounds_left']
        from_player.agent._agent_memory['invest_contract'][interaction_id]['to_player'] = to_player

        to_player.agent._agent_memory['invest_contract'][interaction_id] = dict()
        to_player.agent._agent_memory['invest_contract'][interaction_id]['invest_amount'] = interaction_dict['invest_amount']
        to_player.agent._agent_memory['invest_contract'][interaction_id]['percent'] = interaction_dict['percent']
        to_player.agent._agent_memory['invest_contract'][interaction_id]['location'] = interaction_dict['location']
        to_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] = interaction_dict['num_rounds_left']
        to_player.agent._agent_memory['invest_contract'][interaction_id]['from_player'] = from_player

        # to_player immediately get cash; from_player charge the amount
        code = to_player.receive_cash(interaction_dict['invest_amount'], current_gameboard, bank_flag=False)
        # add to game history
        if code == action_choices.flag_config_dict['successful_action']:
            current_gameboard['history']['function'].append(to_player.receive_cash)
            params = dict()
            params['self'] = to_player
            params['amount'] = interaction_dict['invest_amount']
            params['description'] = 'invested amount'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(code)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        else:
            logger.debug("Not sure what happened! Something broke!")
            logger.error("Exception")
            raise Exception

        # from_player is charge by amount it invest
        from_player.charge_player(interaction_dict['invest_amount'], current_gameboard, bank_flag=False)
        # add to game history
        current_gameboard['history']['function'].append(from_player.charge_player)
        params = dict()
        params['self'] = from_player
        params['amount'] = interaction_dict['invest_amount']
        params['description'] = 'investing amount'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

    # if reach here, either accept or reject, remove interaction_id from to_player's interaction_dict
    del to_player.interaction_dict[interaction_id]
    logger.debug(f'{to_player.player_name} accept request for investing to {from_player.player_name}')
    return flag_config_dict['successful_action']


def process_move_consequences_invest_contract_with_turns(self, current_gameboard):
    """
    if two player has agreement means that they are in the same incoming group with some defined fraction to pay rent
    :param self: player who need to pay rent
    :param current_gameboard:
    :return:
    """
    current_location = current_gameboard['location_sequence'][self.current_position] # get the Location object corresponding to player's current position
    if current_location.loc_class == 'do_nothing': # we now look at each location class case by case
        logger.debug(self.player_name+' is on a do_nothing location, namely '+current_location.name+'. Nothing to process. Returning...')
        return
    elif current_location.loc_class == 'real_estate':
        logger.debug(self.player_name+ ' is on a real estate location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+' is owned by Bank. Setting _option_to_buy to true for '+self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+current_location.owned_by.player_name+' and is not mortgaged. Proceeding to calculate and pay rent.')
            self.calculate_and_pay_rent_dues(current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(self.calculate_and_pay_rent_dues)
            params = dict()
            params['self'] = self
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            return
    elif current_location.loc_class == 'tax':
        logger.debug(self.player_name+ ' is on a tax location, namely '+ current_location.name+ '. Deducting tax...')
        tax_due = TaxLocation.calculate_tax(current_location, self, current_gameboard)
        self.charge_player(tax_due, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(self.charge_player)
        params = dict()
        params['self'] = self
        params['amount'] = tax_due
        params['description'] = 'tax'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return
    elif current_location.loc_class == 'railroad':
        logger.debug(self.player_name+ ' is on a railroad location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')

            to_player = current_location.owned_by
            from_player = None
            from_player_percent = 0
            potential_delete_item = set()

            if 'invest_contract' in to_player.agent._agent_memory:
                for inter_id, item in to_player.agent._agent_memory['invest_contract'].items():
                    if 'from_player' in item and current_location.name == item['location'].name:  # find a contract with this property
                        interaction_id = inter_id
                        from_player = item['from_player']
                        from_player_percent = item['percent']
                        break
            # if current_location.name in current_gameboard['properties_in_contract']:  # property in the contract
            #     for interaction_id, item in to_player.interaction_dict.items():
            #         if item['location'].name == current_location.name:
            #             from_player = item['from_player']
            #             from_player_percent = item['percent']
            #             break

            dues = RailroadLocation.calculate_railroad_dues(current_location, current_gameboard)
            # add to game history
            current_gameboard['history']['function'].append(RailroadLocation.calculate_railroad_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            code = to_player.receive_cash((1 - from_player_percent) * dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(to_player.receive_cash)
                params = dict()
                params['self'] = to_player
                params['amount'] = (1 - from_player_percent) * dues
                params['number of railroads'] = to_player.num_railroads_possessed
                params['description'] = 'railroad dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            if from_player:
                code = from_player.receive_cash(from_player_percent * dues, current_gameboard, bank_flag=False)
                # add to game history
                if code == action_choices.flag_config_dict['successful_action']:
                    current_gameboard['history']['function'].append(from_player.receive_cash)
                    params = dict()
                    params['self'] = from_player
                    params['amount'] = from_player_percent * dues
                    params['description'] = 'railroad invest dividend'
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(code)
                    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
                else:
                    logger.debug("Not sure what happened! Something broke!")
                    logger.error("Exception")
                    raise Exception

                ###############
                from_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] -= 1
                # to_player reduces number of rounds
                to_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] -= 1

                logger.debug('contract num_runds_left decrease to ' + str(to_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left']))

                # usually number of rounds for from_player and to_player should always be equal
                if from_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] != \
                        to_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left']:
                    logger.debug(
                        f'Number of rounds for from_player and to_player is different, something went wrong...')
                    raise Exception

                # from_player & to_player complete the contract
                if from_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] == 0 and \
                        to_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] == 0:
                    potential_delete_item.add(interaction_id)
                else:
                    logger.debug(f'{to_player.player_name} have not signed rent agreement yet')

                    # agreement finish for from_player
                for del_id in potential_delete_item:
                    del from_player.agent._agent_memory['invest_contract'][del_id]
                    del to_player.agent._agent_memory['invest_contract'][del_id]
                    logger.debug('invest_contract is finished')
                ###############

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of railroads'] = to_player.num_railroads_possessed
            params['description'] = 'railroad dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            return
    elif current_location.loc_class == 'utility':
        logger.debug(self.player_name+ ' is on a utility location, namely '+ current_location.name)
        if 'bank.Bank' in str(type(current_location.owned_by)):
            logger.debug(current_location.name+ ' is owned by Bank. Setting _option_to_buy to true for '+ self.player_name)
            self._option_to_buy = True
            return
        elif current_location.owned_by == self:
            logger.debug(current_location.name+' is owned by current player. Player does not need to do anything.')
            return
        elif current_location.is_mortgaged is True:
            logger.debug(current_location.name+ ' is mortgaged. Player does not have to do or pay anything. Returning...')
            return
        else:
            logger.debug(current_location.name+ ' is owned by '+ current_location.owned_by.player_name+ ' and is not mortgaged. Proceeding to calculate and pay dues.')

            to_player = current_location.owned_by
            from_player = None
            from_player_percent = 0
            potential_delete_item = set()

            if 'invest_contract' in to_player.agent._agent_memory:
                for inter_id, item in to_player.agent._agent_memory['invest_contract'].items():
                    if 'from_player' in item and current_location.name == item['location'].name:  # find a contract with this property
                        interaction_id = inter_id
                        from_player = item['from_player']
                        from_player_percent = item['percent']
                        break

            # if current_location.name in current_gameboard['properties_in_contract']:  # property in the contract
            #     for interaction_id, item in to_player.interaction_dict.items():
            #         if item['location'].name == current_location.name:
            #             from_player = item['from_player']
            #             from_player_percent = item['percent']
            #             break

            dues = UtilityLocation.calculate_utility_dues(current_location, current_gameboard, current_gameboard['current_die_total'])
            # add to game history
            current_gameboard['history']['function'].append(UtilityLocation.calculate_utility_dues)
            params = dict()
            params['asset'] = current_location
            params['current_gameboard'] = current_gameboard
            params['die_total'] = current_gameboard['current_die_total']
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(dues)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            code = to_player.receive_cash((1 - from_player_percent) * dues, current_gameboard, bank_flag=False)
            # add to game history
            if code == action_choices.flag_config_dict['successful_action']:
                current_gameboard['history']['function'].append(to_player.receive_cash)
                params = dict()
                params['self'] = to_player
                params['amount'] = (1 - from_player_percent) * dues
                params['number of utilities'] = to_player.num_utilities_possessed
                params['description'] = 'utility dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(code)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
            else:
                logger.debug("Not sure what happened! Something broke!")
                logger.error("Exception")
                raise Exception

            if from_player:
                code = from_player.receive_cash(from_player_percent * dues, current_gameboard, bank_flag=False)
                # add to game history
                if code == action_choices.flag_config_dict['successful_action']:
                    current_gameboard['history']['function'].append(from_player.receive_cash)
                    params = dict()
                    params['self'] = from_player
                    params['amount'] = from_player_percent * dues
                    params['description'] = 'utility invest dividend'
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(code)
                    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
                else:
                    logger.debug("Not sure what happened! Something broke!")
                    logger.error("Exception")
                    raise Exception

                ###############
                from_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] -= 1
                # to_player reduces number of rounds
                to_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] -= 1

                logger.debug('contract num_runds_left decrease to ' + str(to_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left']))

                # usually number of rounds for from_player and to_player should always be equal
                if from_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] != \
                        to_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left']:
                    logger.debug(
                        f'Number of rounds for from_player and to_player is different, something went wrong...')
                    raise Exception

                # from_player & to_player complete the contract
                if from_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] == 0 and \
                        to_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] == 0:
                    potential_delete_item.add(interaction_id)
                else:
                    logger.debug(f'{to_player.player_name} have not signed rent agreement yet')

                    # agreement finish for from_player
                for del_id in potential_delete_item:
                    del from_player.agent._agent_memory['invest_contract'][del_id]
                    del to_player.agent._agent_memory['invest_contract'][del_id]
                    logger.debug('invest_contract is finished')
                ###############

            self.charge_player(dues, current_gameboard, bank_flag=False)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = dues
            params['number of utilities'] = to_player.num_utilities_possessed
            params['description'] = 'utility dues'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

            return
    elif current_location.loc_class == 'action':
        logger.debug(self.player_name+ ' is on an action location, namely '+ current_location.name+ '. Performing action...')
        current_location.perform_action(self, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(current_location.perform_action)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return
    else:
        logger.error(self.player_name+' is on an unidentified location type. Raising exception.')
        logger.error("Exception")
        raise Exception


def calculate_and_pay_rent_dues_invest_contract_with_turns(self, current_gameboard):
    """

    :param self:
    :param current_gameboard:
    :return:
    """
    current_loc = current_gameboard['location_sequence'][self.current_position]
    logger.debug('calculating and paying rent dues for '+ self.player_name+ ' who is in property '+current_loc.name+' which is owned by '+current_loc.owned_by.player_name)

    # determine if two players have agreement
    to_player = current_loc.owned_by
    from_player = None
    from_player_percent = 0
    potential_delete_item = set()

    # print(to_player.agent._agent_memory)
    if 'invest_contract' in to_player.agent._agent_memory:
        for inter_id, item in to_player.agent._agent_memory['invest_contract'].items():
            if 'from_player' in item and current_loc.name == item['location'].name:  # find a contract with this property
                interaction_id = inter_id
                from_player = item['from_player']
                from_player_percent = item['percent']
                break

    # if current_loc.name in current_gameboard['properties_in_contract']:  # property in the contract
    #     for interaction_id, item in to_player.interaction_dict.items():
    #         if item['location'].name == current_loc.name:
    #             from_player = item['from_player']
    #             from_player_percent = item['percent']
    #             break

    rent = RealEstateLocation.calculate_rent(current_loc, current_gameboard)
    # add to game history
    current_gameboard['history']['function'].append(RealEstateLocation.calculate_rent)
    params = dict()
    params['asset'] = current_loc
    params['current_gameboard'] = current_gameboard
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(rent)
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

    # to_player get 1 - percent of rent
    code = to_player.receive_cash((1 - from_player_percent) * rent, current_gameboard, bank_flag=False)
    # add to game history
    if code == action_choices.flag_config_dict['successful_action']:
        current_gameboard['history']['function'].append(to_player.receive_cash)
        params = dict()
        params['self'] = to_player
        params['amount'] = (1 - from_player_percent) * rent
        params['description'] = 'rent'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
    else:
        logger.debug("Not sure what happened! Something broke!")
        logger.error("Exception")
        raise Exception

    # from_player get percent of rent
    if from_player:
        code = from_player.receive_cash(from_player_percent * rent, current_gameboard, bank_flag=False)
        # add to game history
        if code == action_choices.flag_config_dict['successful_action']:
            current_gameboard['history']['function'].append(from_player.receive_cash)
            params = dict()
            params['self'] = from_player
            params['amount'] = from_player_percent * rent
            params['description'] = 'rent'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
            current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])
        else:
            logger.debug("Not sure what happened! Something broke!")
            logger.error("Exception")
            raise Exception

        ###############
        from_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] -= 1
        # to_player reduces number of rounds
        to_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] -= 1

        logger.debug('contract num_runds_left decrease to ' + str(to_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left']))

        # usually number of rounds for from_player and to_player should always be equal
        if from_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] != \
                to_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left']:
            logger.debug(f'Number of rounds for from_player and to_player is different, something went wrong...')
            raise Exception

        # from_player & to_player complete the contract
        if from_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] == 0 and \
                to_player.agent._agent_memory['invest_contract'][interaction_id]['num_rounds_left'] == 0:
            potential_delete_item.add(interaction_id)
        else:
            logger.debug(f'{to_player.player_name} have not signed rent agreement yet')

        # agreement finish
        for del_id in potential_delete_item:
            del from_player.agent._agent_memory['invest_contract'][del_id]
            del to_player.agent._agent_memory['invest_contract'][del_id]
            logger.debug('invest_contract is finished')
        ###############

    self.charge_player(rent, current_gameboard, bank_flag=False)
    # add to game history
    current_gameboard['history']['function'].append(self.charge_player)
    params = dict()
    params['self'] = self
    params['amount'] = rent
    params['description'] = 'rent'
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])



# when the interaction novelty is injected, this function will be used
def populate_param_dict_with_location_check(param_dict, player, current_gameboard):
    if not param_dict:   # check if param_dict is an empty dictionary --> skip turn and conclude_actions
        return param_dict

    #-----------------action---------------
    if 'action_params_dict' in param_dict and param_dict['action_params_dict'] is not None:
        if 'location' in param_dict['action_params_dict']:
            param_location_name = param_dict['action_params_dict']['location']
            # make the first word in location string to Capital
            param_location_name = param_location_name.title()
            #
            for loc in current_gameboard['location_sequence']:
                if loc.name == param_location_name:
                    param_dict['action_params_dict']['location'] = loc
                    break
        # make the first word in location string to Capital
        if 'choice_list' in param_dict['action_params_dict']:
            for idx, x in  enumerate(param_dict['action_params_dict']['choice_list']):
                param_dict['action_params_dict']['choice_list'][idx] = x.title()
    #--------------------------------------

    #-----------------interaction---------------------
    if 'interaction_params_dict' in param_dict and param_dict['interaction_params_dict'] is not None:
        if 'location' in param_dict['interaction_params_dict']:
            param_location_name = param_dict['interaction_params_dict']['location']
            # make the first word in location string to Capital
            param_location_name = param_location_name.title()
            #
            for loc in current_gameboard['location_sequence']:
                if loc.name == param_location_name:
                    param_dict['interaction_params_dict']['location'] = loc
                    break
        if 'to_location' in param_dict['interaction_params_dict']:
            param_location_name = param_dict['interaction_params_dict']['to_location']
            # make the first word in location string to Capital
            param_location_name = param_location_name.title()
            #
            for loc in current_gameboard['location_sequence']:
                if loc.name == param_location_name:
                    param_dict['interaction_params_dict']['to_location'] = loc
                    break
    #_-------------------------------------------------

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