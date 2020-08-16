import logging
logger = logging.getLogger('monopoly_simulator.logging_info.bank')

class Bank(object):
    def __init__(self):
        self.mortgage_percentage = 0.1
        self.total_mortgage_rule = False  # if true, then mortgage will be calculated as a percentage of total debt the player has outstanding
        self.total_houses = 32
        self.total_hotels = 12
        self.total_cash_with_bank = float(10000)
        self.property_sell_percentage = 0.5
        self.house_sell_percentage = 0.5
        self.hotel_sell_percentage = 0.5
        self.jail_fine = float(50)
        self.monopolized_property_rent_factor = float(2)   #default = 2, players have to pay "twice" the property rent on "monopolized" unimproved properties

    @staticmethod
    def auction(starting_player_index, current_gameboard, asset):
        """
        This function will be called when a player lands on a purchaseable property (real estate, railroad or utility)
        but decides not to make the purchase. 
        :param starting_player_index:  An integer. The index of the player in current_gameboard['players'] who will be starting the auction
        :param current_gameboard: A dict. Specifies the global game board data structure
        :param asset: A purchaseable instance of Location (i.e. RealEstateLocation, UtilityLocation or RailroadLocation)
        :return: None
        """

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


    @staticmethod
    def calculate_mortgage_owed(mortgaged_property, current_gameboard=None):
        """
        calculate the mortgage owed on mortgaged_property
        :param player: Player instance. not used in this function, but the signature is important because of the novelty generator
        which could use other information from the player (like total debt) besides just the info in mortgaged_property.
        :param mortgaged_property: a property instance that is mortgaged
        :return:
        """

        if not mortgaged_property.is_mortgaged:
            logger.error("Exception")
            raise Exception
        else:
            if current_gameboard['bank'].total_mortgage_rule is False:
                return (1.0+current_gameboard['bank'].mortgage_percentage) * mortgaged_property.mortgage
            else:
                # to avoid passing in a player object, I am going to use the owner of the mortgaged_property as the player whose
                # total debt outstanding we have to compute the mortgage against.
                player = mortgaged_property.owned_by
                total = 0
                for a in player.mortgaged_assets:
                    total += ((1.0+current_gameboard['bank'].mortgage_percentage)*a.mortgage)
                return total


    def improvement_possible(self, player, asset, current_gameboard, add_house=True, add_hotel=False):
        if add_hotel and add_house:
            logger.debug("Cant build both a house and a hotel on a property at once!! Raising Exception.")
            raise Exception
        if add_hotel:
            if self.total_hotels > 0:
                return True
        elif add_house:
            if self.total_houses > 0:
                return True
