class Bank(object):
    def __init__(self):
        self.mortgage_percentage = 0.1
        self.total_mortgage_rule = False  # if true, then mortgage will be calculated as a percentage of total debt the player has outstanding

    def auction(self, starting_player_index, current_gameboard, asset):
        """
        This function will be called when a player lands on a purchaseable property (real estate, railroad or utility)
        but decides not to make the purchase. 
        :param starting_player_index:  An integer. The index of the player in current_gameboard['players'] who will be starting the auction
        :param current_gameboard: A dict. Specifies the global game board data structure
        :param asset: A purchaseable instance of Location (i.e. RealEstateLocation, UtilityLocation or RailroadLocation)
        :return: None
        """

        print('Entering auctioning for asset ',asset.name)

        current_bid = 0
        players_out_of_auction = set()
        winning_player = None
        bidding_player_index = None

        # Since the starting player may be out of the game, we first check if we should update the starting player
        for p in current_gameboard['players']:
            if p.status == 'lost':
                players_out_of_auction.add(p)
            else:
                print(p.player_name,' is an auction participant.')

        count = 0
        while count < len(current_gameboard['players']):
            if current_gameboard['players'][starting_player_index] in players_out_of_auction:
                count += 1
                starting_player_index = (starting_player_index+1)%len(current_gameboard['players'])
            else:
                bidding_player_index = starting_player_index
                break

        if bidding_player_index is None: # no one left to auction. This is a failsafe, the code should never get here.
            print('No one is left in the game that can participate in the auction! Why are we here?')
            return
        else:
            print(current_gameboard['players'][bidding_player_index].player_name,' will place the first bid')

        while len(players_out_of_auction) < len(current_gameboard['players'])-1: # we iterate and bid till just one player remains
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

            print(bidding_player.player_name,' proposed bid ',str(proposed_bid))

            if proposed_bid == 0:
                players_out_of_auction.add(bidding_player)
                print(bidding_player.player_name, ' is out of the auction.')
                bidding_player_index = (bidding_player_index + 1) % len(current_gameboard['players'])
                continue
            elif proposed_bid <= current_bid: # the <= serves as a forcing function to ensure the proposed bid must be non-zero
                players_out_of_auction.add(bidding_player)
                print(bidding_player.player_name, ' is out of the auction.')
                bidding_player_index = (bidding_player_index + 1) % len(current_gameboard['players'])
                continue

            current_bid = proposed_bid
            print('The current highest bid is ',str(current_bid), ' and is held with ',bidding_player.player_name)
            winning_player = bidding_player
            bidding_player_index = (bidding_player_index + 1) % len(current_gameboard['players'])


        if winning_player:
            winning_player.charge_player(current_bid) # if it got here then current_bid is non-zero.
            # add to game history
            current_gameboard['history']['function'].append(winning_player.charge_player)
            params = dict()
            params['self'] = winning_player
            params['amount'] = current_bid
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
            print('Auction did not succeed in a sale.')
        return
