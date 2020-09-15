import logging
logger = logging.getLogger('monopoly_simulator.logging_info.bank')

class Bank(object):
    def __init__(self):
        """
        :param mortgage_percentage: a float. % of the property mortgage amount that the player owes the bank in addition to the mortgage amount.
        :param total_mortgage_rule: a bool. If true, then mortgage will be calculated as a percentage of total debt the player has outstanding
        :param total_houses: an int. Total num of houses available to the players for improvement in this game.
        :param total_hotels: an int. Total num of hotels available to the players for improvement in this game.
        :param total_cash_with_bank: a float. Total cash that the bank has at the beginning of the game. Bank does not have an
        infinite reserve of cash. If this amount drops to 0 during the game, then players cannot receive cash from bank until the bank replenishes its reserve
        of money by getting tax or any other moves that the players make during the game.
        :param property_sell_percentage: a float. % of the price of a property that a player can get back from the bank upon selling it back to the bank.
        :param house_sell_percentage: a float. % of the price of a house that a player can get back from the bank upon selling it back to the bank.
        :param hotel_sell_percentage: a float. % of the price of a hotel that a player can get back from the bank upon selling it back to the bank.
        :param jail_fine: a float. In the event that a player ends up in jail, the amount that the player has to pay the bank if it has to free itself from jail.
        :param monopolized_property_rent_factor: a float. If a player possess' a monopoly, the rent of the properties within this monopolized color group
        gets multiplied by this factor.
        :param house_limit_before_hotel: an int. The max number of houses that a player can build on a property. Once the num of houses has reached this limit on
        all the properties in that color group (Uniform improvement rule), the player may set up a hotel.
        :param hotel_limit: The max number of hotel(s) that a player can build on a property
        """
        self.mortgage_percentage = 0.1
        self.total_mortgage_rule = False
        self.total_houses = 32
        self.total_hotels = 12
        self.total_cash_with_bank = float(10000)
        self.property_sell_percentage = 0.5
        self.house_sell_percentage = 0.5
        self.hotel_sell_percentage = 0.5
        self.jail_fine = float(50)
        self.monopolized_property_rent_factor = float(2)
        self.house_limit_before_hotel = 4
        self.hotel_limit = 1

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
            if winning_player is not None and len(players_out_of_auction) == len(current_gameboard['players']) - 1:
                logger.debug("Current highest bid player is the last man standing in the auction, hence breaking out of auction loop.")
                break
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
        :param mortgaged_property: a property instance that is mortgaged
        :param current_gameboard: the gloabal gameboard data structure
        :return: the mortgage owed
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
        """
        checks if the asset passed into this function can be improved or not eiither by setting up a house or hotel defined by
        the add_house and add_hotel params
        :param player: player that owns this asset
        :param asset: asset that needs to be checked for improvement capability
        :param current_gameboard: The gameboard data structure
        :param add_house: flag if True indicates that the type of improvement is setting up a house.
        :param add_hotel: flag if True indicates that the type of improvement is setting up a hotel.
        Note: both add_house and add_hotel params cannot be true simulatneously
        :return: bool, True if improvement possible else false
        """
        if add_hotel and add_house:
            logger.debug("Cant build both a house and a hotel on a property at once!! Raising Exception.")
            raise Exception

        if not add_hotel and not add_house:
            logger.debug("Call to this function was unnecessary since both add_hotel and add_house flags are false!!! Raising Exception.")
            raise Exception

        if add_hotel:
            if self.total_hotels > 0:
                return True
        elif add_house:
            if self.total_houses > 0:
                return True

    def serialize(self):
        bank_dict = dict()
        bank_dict['mortgage_percentage'] = self.mortgage_percentage
        bank_dict['total_mortgage_rule'] = self.total_mortgage_rule
        bank_dict['total_houses'] = self.total_houses
        bank_dict['total_hotels'] = self.total_hotels
        bank_dict['total_cash_with_bank'] = self.total_cash_with_bank
        bank_dict['property_sell_percentage'] = self.property_sell_percentage
        bank_dict['house_sell_percentage'] = self.house_sell_percentage
        bank_dict['hotel_sell_percentage'] = self.hotel_sell_percentage
        bank_dict['jail_fine'] = self.jail_fine
        bank_dict['monopolized_property_rent_factor'] = self.monopolized_property_rent_factor
        return bank_dict
