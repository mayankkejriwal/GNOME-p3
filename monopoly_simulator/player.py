from monopoly_simulator.action_choices import *
from monopoly_simulator.location import  RealEstateLocation, UtilityLocation, RailroadLocation
from monopoly_simulator.bank import Bank
import logging
logger = logging.getLogger('monopoly_simulator.logging_info.player')


class Player(object):
    def __init__(self, current_position, status, has_get_out_of_jail_community_chest_card, has_get_out_of_jail_chance_card,
                 current_cash, num_railroads_possessed, player_name, assets,full_color_sets_possessed, currently_in_jail,
                 num_utilities_possessed,
                 agent
                 ):
        """
        An object representing a unique player in the game.

        :param current_position: An integer. Specifies index in the current gameboard's 'location_sequence' list where the player
        is currently situated.
        :param status: A string. One of 'waiting_for_move', 'current_move', 'won' or 'lost'
        :param has_get_out_of_jail_community_chest_card: A boolean. Self-explanatory
        :param has_get_out_of_jail_chance_card: A boolean. Self-explanatory
        :param current_cash: An integer. Your current cash balance.
        :param num_railroads_possessed: An integer. Self-explanatory
        :param player_name: A string. The name of the player
        :param assets: A set. The items in the set are purchaseable Location objects (real estate, railroads or locations)
        :param full_color_sets_possessed: A set. The real estate colors for which the full set is possessed by the player in assets.
        :param currently_in_jail: A boolean. Self-explanatory but with one caveat: if you are only 'visiting' in jail, this flag will not be set to True
        :param num_utilities_possessed: An integer. Self-explanatory
        :param agent: An instance of class Agent. This instance encapsulates the decision-making portion of the program
        that is the domain of TA2


        """
        self.current_position = current_position # this is an integer. Use 'location_sequence' in the game schema to map position into an actual location
        self.status = status
        self.has_get_out_of_jail_chance_card = has_get_out_of_jail_chance_card
        self.has_get_out_of_jail_community_chest_card = has_get_out_of_jail_community_chest_card
        self.current_cash = float(current_cash)
        self.num_railroads_possessed = num_railroads_possessed
        self.player_name = player_name
        self.assets = assets
        self.full_color_sets_possessed = full_color_sets_possessed
        self.currently_in_jail = currently_in_jail
        self.num_utilities_possessed = num_utilities_possessed

        # the agent assigned to this player.
        self.agent=agent

        # all of the variables below are assigned a default initial value, and do not need input arguments/game schema inputs
        self.num_total_houses = 0 # the total number of houses, across all assets, that the player possesses
        self.num_total_hotels = 0 # the total number of hotels, across all assets, that the player possesses
        outstanding_property_offer = dict()
        outstanding_property_offer['from_player'] = None # when is_property_offer_outstanding is true, the expected value is a Player instance
        outstanding_property_offer['asset'] = None # when is_property_offer_outstanding is true, the expected value is a purchaseable Location instance
        outstanding_property_offer['price'] = -1 # when is_property_offer_outstanding is true, the expected value is a non-negative integer

        self.outstanding_property_offer = outstanding_property_offer
        self.is_property_offer_outstanding = False # If True, it means that there is a property offer on the table
        # from another player. Only one property offer at a time can be considered, so when it's your turn you have to
        # decide whether to accept the offer (if you don't, the offer will get rejected, and the field will get re-set)
        # the details of who is offering what and at what price are in outstanding_property_offer

        outstanding_trade_offer = dict()
        outstanding_trade_offer['property_set_offered'] = set()
        outstanding_trade_offer['property_set_wanted'] = set()
        outstanding_trade_offer['cash_offered'] = 0
        outstanding_trade_offer['cash_wanted'] = 0
        outstanding_trade_offer['from_player'] = None

        self.outstanding_trade_offer = outstanding_trade_offer
        self.is_trade_offer_outstanding = False

        self.mortgaged_assets = set() # the set of assets that are currently mortgaged.

        self._option_to_buy = False # this option will turn true when  the player lands on a property that could be bought.
        # We always set it to false again at the end of the post_roll phase. It is an internal variable.

    def change_decision_agent(self, agent):
        self.agent = agent


    def begin_bankruptcy_proceedings(self, current_gameboard):
        """
        Begin bankruptcy proceedings and set the player's status to lost. All assets will be discharged back to the bank,
        and all variables will be reset for the player (except methods) to None or default values, as the case may be.
        If the player possesses get out of jail cards, these will be released back into the pack.
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: None
        """
        logger.debug('Beginning bankruptcy proceedings for '+self.player_name)
        self.current_position = None
        self.status = 'lost'
        self.current_cash = 0
        self.discharge_assets_to_bank(current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(self.discharge_assets_to_bank)
        params = dict()
        params['self'] = self
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        self.num_total_houses = 0
        self.num_total_hotels = 0
        self.num_utilities_possessed = 0
        self.num_railroads_possessed = 0

        self.currently_in_jail = False
        self.outstanding_property_offer['from_player'] = None
        self.outstanding_property_offer['asset'] = None
        self.outstanding_property_offer['price'] = -1

        self.outstanding_trade_offer['property_set_offered'] = set()
        self.outstanding_trade_offer['property_set_wanted'] = set()
        self.outstanding_trade_offer['cash_offered'] = 0
        self.outstanding_trade_offer['cash_wanted'] = 0
        self.outstanding_trade_offer['from_player'] = None

        if self._option_to_buy:
            logger.debug('Warning! option to buy is set to true for '+self.player_name+' even in bankruptcy proceedings.')
        self._option_to_buy = False
        self.is_property_offer_outstanding = False
        self.is_trade_offer_outstanding = False

        if self.has_get_out_of_jail_chance_card:  # we give first preference to chance, then community chest
            self.has_get_out_of_jail_chance_card = False
            logger.debug('releasing get_out_of_jail_chance_card for '+self.player_name)
            current_gameboard['chance_cards'].add(current_gameboard['chance_card_objects']['get_out_of_jail_free'])

        if self.has_get_out_of_jail_community_chest_card:
            self.has_get_out_of_jail_community_chest_card = False
            logger.debug('releasing get_out_of_jail_community_chest_card for '+self.player_name)
            current_gameboard['community_chest_cards'].add(current_gameboard['community_chest_card_objects']['get_out_of_jail_free'])

    def add_asset(self, asset, current_gameboard):
        """
        This is a simple transaction where the asset gets added to the player's portfolio. The asset must have been paid
        for already, since the cash transaction (whether to bank or another player) does not happen here, nor
        do we remove the asset from another player's portfolio. All of this groundwork is done before this function is called.
        Furthermore, asset.owned_by must be updated outside this function.
        :param asset: A purchaseable Location instance (railroad, utility or real estate)
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: None
        """
        logger.debug('Looking to add asset '+asset.name+' to portfolio of '+self.player_name)
        if asset in self.assets:
            logger.error('Error! Player already owns asset!')
            logger.error("Exception")
            raise Exception

        self.assets.add(asset)
        logger.debug('total no. of assets now owned by player: '+str(len(self.assets)))

        if type(asset) == UtilityLocation:
            self.num_utilities_possessed += 1
            logger.debug('incrementing '+self.player_name+ "'s utility count by 1, total utilities owned by player now is "+str(self.num_utilities_possessed))
        elif type(asset) == RailroadLocation:
            self.num_railroads_possessed += 1
            logger.debug('incrementing '+ self.player_name+ "'s railroad count by 1, total railroads owned by player now is "+ str(self.num_railroads_possessed))
        elif type(asset) == RealEstateLocation:
            flag = True
            for o in current_gameboard['color_assets'][asset.color]:
                if o not in self.assets:
                    flag = False
                    break
            if flag: # if this is still True, then that means we now possess all the properties with this asset's color
                self.full_color_sets_possessed.add(asset.color)

            if asset.num_houses > 0:
                self.num_total_houses += asset.num_houses
                logger.debug('incrementing '+self.player_name+ "'s num_total_houses count by "+ str(asset.num_houses)+
                    ". Total houses now owned by player now is "+ str(self.num_total_houses))
                # note that technically, the property should not have been transferred to player
                # if there were improvements on it. But we include this code just in case, and to flag errors later.
            elif asset.num_hotels > 0:
                self.num_total_hotels += asset.num_hotels
                logger.debug('incrementing '+ self.player_name+ "'s num_total_hotels coadd_assunt by "+str(asset.num_hotels)+
                    ". Total hotels now owned by player now is "+ str(self.num_total_hotels))
        else:
            logger.error('You are attempting to add non-purchaseable asset to player\'s portfolio!')
            logger.error("Exception")
            raise Exception

        if asset.is_mortgaged:
            logger.debug('asset ',asset.name," is mortgaged. Adding to player's mortgaged assets.")
            self.mortgaged_assets.add(asset)
            logger.debug('Total number of mortgaged assets owned by player is '+str(len(self.mortgaged_assets)))

    def remove_asset(self, asset):
        """
        This is a simple transaction where the asset gets removed from the player's portfolio.
        All of the groundwork (exchange of cash) must be done before this function is called. For safe behavior, this should always be
        accompanied by post-processing code, especially if the asset is mortgageable and/or is being sold from one player
        to another.

        Improvements are not permitted when removing the asset. We will raise an exception if we detect houses or hotels
        when removing the asset. asset.owned_by is not updated either, make sure to invoke it (e.g., to reflect the new owner
        or to hand it over to the bank) AFTER this function returns
        (if you do it before, an exception will be raised, since we check whether the asset is owned by the player)
        :param asset: A purchaseable Location instance (railroad, utility or real estate)
        :return: None
        """
        logger.debug('Attempting to remove asset '+asset.name+' from ownership of '+self.player_name)
        if asset not in self.assets:
            logger.error('Error! Player does not own asset!')
            logger.error("Exception")
            raise Exception

        self.assets.remove(asset)
        logger.debug('total no. of assets now owned by player: '+str(len(self.assets)))

        if type(asset) == UtilityLocation:
            self.num_utilities_possessed -= 1
            logger.debug('Decrementing '+self.player_name+ "'s utility count by 1, total utilities owned by player now is "+str(self.num_utilities_possessed))
        elif type(asset) == RailroadLocation:
            self.num_railroads_possessed -= 1
            logger.debug('Decrementing '+ self.player_name+ "'s railroad count by 1, total railroads owned by player now is "+ str(self.num_railroads_possessed))
        elif type(asset) == RealEstateLocation:
            if asset.color in self.full_color_sets_possessed:
                self.full_color_sets_possessed.remove(asset.color)

            if asset.num_houses > 0:
                self.num_total_houses -= asset.num_houses
                logger.debug('Decrementing '+self.player_name+ "'s num_total_houses count by "+ str(asset.num_houses),
                    ". Total houses now owned by player now is ", str(self.num_total_houses))
                # note that technically, the property should not have been removed
                # if there were improvements on it. But we include this code just in case, and to flag errors later.
            elif asset.num_hotels > 0:
                self.num_total_hotels -= asset.num_hotels
                logger.debug('Decrementing '+ self.player_name+ "'s num_total_hotels count by "+ str(asset.num_hotels),
                    ". Total hotels now owned by player now is ", str(self.num_total_hotels))
        else:
            logger.error('The property to be removed from the portfolio is not purchaseable. How did it get here?')
            logger.error("Exception")
            raise Exception

        if asset.is_mortgaged: # the asset is still mortgaged after we remove it from the player's portfolio. The next player must free it up.
            logger.debug('asset '+asset.name+" is mortgaged. Removing from player's mortgaged assets.")
            self.mortgaged_assets.remove(asset)
            logger.debug('Total number of mortgaged assets owned by player is '+str(len(self.mortgaged_assets)))

    def charge_player(self, amount, current_gameboard, bank_flag=False):
        """
        Charge the player's current_cash the stated amount. Current_cash could go negative if the amount is greater
        than what the player currently has.
        :param amount: An integer. amount to charge the player. cannot be negative.
        :return: None
        """
        if amount < 0:
            logger.error('You cannot charge player negative amount of cash.')
            logger.error("Exception")
            raise Exception
        logger.debug(self.player_name+ ' is being charged amount: '+str(amount))
        logger.debug('Before charge, player has cash '+str(self.current_cash))
        self.current_cash -= amount
        logger.debug(self.player_name+ ' now has cash: '+str(self.current_cash))
        if bank_flag:
            current_gameboard['bank'].total_cash_with_bank += amount
            logger.debug('Bank received amount ' + str(amount) + ' due to transaction from ' + self.player_name)
            logger.debug('Liquid Cash remaining with Bank = ' + str(current_gameboard['bank'].total_cash_with_bank))


    def discharge_assets_to_bank(self, current_gameboard): # discharge assets to bank
        """
        Discharge the player's assets to the bank and set/re-set all variables (including of the asset itself) as
        appropriate.
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: None
        """
        logger.debug('Discharging assets of '+self.player_name+' to bank.')
        if self.assets:
            for asset in self.assets: # since asset is returning to bank, we can set its mortgage status to False regardless.
                logger.debug('discharging asset '+asset.name)
                asset.is_mortgaged = False
                if asset.loc_class == 'real_estate':
                    asset.owned_by = current_gameboard['bank']
                    logger.debug("Discharging " + str(asset.num_houses) + " houses and " + str(asset.num_hotels) + " hotels to the bank.")
                    current_gameboard['bank'].total_houses += asset.num_houses
                    asset.num_houses = 0
                    current_gameboard['bank'].total_hotels += asset.num_hotels
                    asset.num_hotels = 0
                    logger.debug('Bank now has ' + str(current_gameboard['bank'].total_houses) + ' houses and ' + str(current_gameboard['bank'].total_hotels) + ' hotels left.')
                elif asset.loc_class == 'utility' or asset.loc_class == 'railroad':
                    asset.owned_by = current_gameboard['bank']
                else:
                    logger.error('player owns asset that is not real estate, railroad or utility') # unnecessary, since an
                    # exception will be raised if is_mortgaged does not exist. But we like an extra check.
                    logger.error("Exception")
                    raise Exception

        self.num_railroads_possessed = 0 # now we formally discharge assets on the player's side
        self.assets = None
        self.full_color_sets_possessed = None
        self.num_utilities_possessed = 0
        self.mortgaged_assets = None

    def process_move_consequences(self, current_gameboard):
        """
        Given the current position of the player (e.g., after the dice has rolled and the player has been moved), what
        are the consequences of being on that location? This function provides the main logic, in particular, whether
        the player has the right to purchase a property or has to pay rent on that property etc.
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: None
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

                return
        elif current_location.loc_class == 'tax':
            logger.debug(self.player_name+ ' is on a tax location, namely '+ current_location.name+ '. Deducting tax...')
            self.charge_player(current_location.amount_due, current_gameboard, bank_flag=True)
            # add to game history
            current_gameboard['history']['function'].append(self.charge_player)
            params = dict()
            params['self'] = self
            params['amount'] = current_location.amount_due
            params['description'] = 'tax'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)

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
                dues = current_location.calculate_railroad_dues()
                # add to game history
                current_gameboard['history']['function'].append(current_location.calculate_railroad_dues)
                params = dict()
                params['self'] = current_location
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(dues)

                recipient = current_location.owned_by
                code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
                # add to game history
                if code == 1:
                    current_gameboard['history']['function'].append(recipient.receive_cash)
                    params = dict()
                    params['self'] = recipient
                    params['amount'] = dues
                    params['description'] = 'railroad dues'
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(code)
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
                params['description'] = 'railroad dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)

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
                dues = current_location.calculate_utility_dues(current_gameboard['current_die_total'])
                # add to game history
                current_gameboard['history']['function'].append(current_location.calculate_utility_dues)
                params = dict()
                params['self'] = current_location
                params['die_total'] = current_gameboard['current_die_total']
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(dues)

                recipient = current_location.owned_by
                code = recipient.receive_cash(dues, current_gameboard, bank_flag=False)
                # add to game history
                if code == 1:
                    current_gameboard['history']['function'].append(recipient.receive_cash)
                    params = dict()
                    params['self'] = recipient
                    params['amount'] = dues
                    params['description'] = 'utility dues'
                    current_gameboard['history']['param'].append(params)
                    current_gameboard['history']['return'].append(code)
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
                params['description'] = 'utility dues'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)

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

            return
        else:
            logger.error(self.player_name+' is on an unidentified location type. Raising exception.')
            logger.error("Exception")
            raise Exception

    def update_player_position(self, new_position, current_gameboard):
        """
        Move player to location index specified by new_position
        :param new_position: An integer. Specifies index in location_sequence (in current_gameboard) to which to move the player
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: None
        """
        logger.debug('Player is currently in position '+current_gameboard['location_sequence'][self.current_position].name)
        logger.debug(' and is moving to position '+current_gameboard['location_sequence'][new_position].name)
        self.current_position = new_position

    def send_to_jail(self, current_gameboard):
        """
        Move player to jail. Do not check for Go.
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: None
        """
        logger.debug(self.player_name+' is being sent to jail.')
        jail_position = current_gameboard['jail_position']
        self.currently_in_jail = True
        self.current_position = jail_position

    def calculate_and_pay_rent_dues(self, current_gameboard):
        """
        Calculate the rent for the player on the current position, and pay it to whoever owns that property.
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: None
        """
        current_loc = current_gameboard['location_sequence'][self.current_position]
        logger.debug('calculating and paying rent dues for '+ self.player_name+ ' who is in property '+current_loc.name+' which is owned by '+current_loc.owned_by.player_name)
        rent = RealEstateLocation.calculate_rent(current_loc, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(RealEstateLocation.calculate_rent)
        params = dict()
        params['self'] = current_loc
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(rent)

        recipient = current_loc.owned_by
        code = recipient.receive_cash(rent, current_gameboard, bank_flag=False)
        # add to game history
        if code == 1:
            current_gameboard['history']['function'].append(recipient.receive_cash)
            params = dict()
            params['self'] = recipient
            params['amount'] = rent
            params['description'] = 'rent'
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(None)
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

    def receive_cash(self, amount, current_gameboard, bank_flag=False):
        """
        Player receives a non-negative amount of cash. Current_cash is updated.
        :param amount: Amount of cash to be credited to this player's current cash. If the amount is negative, an exception is raised.
        :return: None
        """
        if amount < 0:
            logger.error(self.player_name+' is receiving negative cash: '+str(amount)+'. This is an unintended use of this function')
            logger.error("Exception")
            raise Exception

        if bank_flag:
            if current_gameboard['bank'].total_cash_with_bank - amount >= 0:
                logger.debug(self.player_name+ ' is receiving amount: '+ str(amount))
                logger.debug('Before receipt, player has cash '+ str(self.current_cash))
                self.current_cash += amount
                logger.debug(self.player_name+ ' now has cash: '+ str(self.current_cash))
                current_gameboard['bank'].total_cash_with_bank -= amount
                logger.debug('Bank paid amount ' + str(amount) + ' to ' + self.player_name)
                logger.debug('Liquid Cash remaining with Bank = ' + str(current_gameboard['bank'].total_cash_with_bank))
                return flag_config_dict['successful_action']
            else:
                logger.debug('Current cash balance with the bank = ' + str(current_gameboard['bank'].total_cash_with_bank))
                logger.debug("Bank has no sufficient liquid cash to pay " + self.player_name + '. Returning failure code.')
                return flag_config_dict['failure_code']
        else:
            logger.debug(self.player_name+ ' is receiving amount: '+ str(amount))
            logger.debug('Before receipt, player has cash '+ str(self.current_cash))
            self.current_cash += amount
            logger.debug(self.player_name+ ' now has cash: '+ str(self.current_cash))
            return flag_config_dict['successful_action']

    def reset_option_to_buy(self):
        """
        Sets the _option_to_buy attribute back to False
        :return: None
        """
        logger.debug('Executing reset_option_to_buy for '+ self.player_name)
        self._option_to_buy = False

    def compute_allowable_pre_roll_actions(self, current_gameboard):
        """
        This function will compute the current set of allowable pre-roll actions for the player. It will weed out
        obvious non-allowable actions, and will return allowable actions (as a set of functions) that are possible
        in principle. Your decision agent, when picking an action from this set, will also have to decide how to
        parameterize the chosen action. For more details, see simple_decision_agent_1

        Note that we pass in current_gameboard, even though it is currently unused. In the near future, we may use it
        to refine allowable_actions.

        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: The set of allowable actions (each item in the set is a function from action_choices)
        """
        logger.debug('computing allowable pre-roll actions for '+self.player_name)
        allowable_actions = set()
        allowable_actions.add(concluded_actions)

        if self.is_property_offer_outstanding is True:
            allowable_actions.add(accept_sell_property_offer)

        if self.is_trade_offer_outstanding is True:
            allowable_actions.add(accept_trade_offer)

        if self.num_total_hotels > 0 or self.num_total_houses > 0:
            allowable_actions.add(sell_house_hotel)

        if len(self.assets) > 0:
            allowable_actions.add(sell_property)
            allowable_actions.add(make_sell_property_offer)
            if len(self.mortgaged_assets) < len(self.assets):
                allowable_actions.add(mortgage_property)

        if len(self.mortgaged_assets) > 0:
            allowable_actions.add(free_mortgage)

        if (self.has_get_out_of_jail_chance_card or self.has_get_out_of_jail_community_chest_card) and self.currently_in_jail:
            allowable_actions.add(use_get_out_of_jail_card)

        if self.currently_in_jail and self.current_cash >= current_gameboard['bank'].jail_fine:
            allowable_actions.add(pay_jail_fine)

        if len(self.full_color_sets_possessed) > 0 :
            allowable_actions.add(improve_property) # there is a chance this is not dynamically allowable because you've improved a property to its maximum.
            # However, you have to make this check in your decision agent.

        allowable_actions.add(make_trade_offer)
        return allowable_actions

    def compute_allowable_out_of_turn_actions(self, current_gameboard):
        """
        This function will compute the current set of allowable out-of-turn actions for the player. It will weed out
        obvious non-allowable actions, and will return allowable actions (as a set of functions) that are possible
        in principle. Your decision agent, when picking an action from this set, will also have to decide how to
        parameterize the chosen action. For more details, see simple_decision_agent_1

        Note that we pass in current_gameboard, even though it is currently unused. In the near future, we may use it
        to refine allowable_actions.

        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: The set of allowable actions (each item in the set is a function from action_choices)
        """
        logger.debug('computing allowable out-of-turn actions for '+ self.player_name)
        allowable_actions = set()
        allowable_actions.add(concluded_actions)

        if self.is_property_offer_outstanding is True:
            allowable_actions.add(accept_sell_property_offer)

        if self.is_trade_offer_outstanding is True:
            allowable_actions.add(accept_trade_offer)

        if self.num_total_hotels > 0 or self.num_total_houses > 0:
            allowable_actions.add(sell_house_hotel)

        if len(self.assets) > 0:
            allowable_actions.add(sell_property)
            allowable_actions.add(make_sell_property_offer)
            if len(self.mortgaged_assets) < len(self.assets):
                allowable_actions.add(mortgage_property)

        if len(self.mortgaged_assets) > 0:
            allowable_actions.add(free_mortgage)

        if len(self.full_color_sets_possessed) > 0:
            allowable_actions.add(
                improve_property)  # there is a chance this is not dynamically allowable because you've improved a property to its maximum.
            # However, you have to make this check in your decision agent.

        allowable_actions.add(make_trade_offer)
        return allowable_actions

    def compute_allowable_post_roll_actions(self, current_gameboard):
        """
        This function will compute the current set of allowable post-roll actions for the player. It will weed out
        obvious non-allowable actions, and will return allowable actions (as a set of functions) that are possible
        in principle. Your decision agent, when picking an action from this set, will also have to decide how to
        parameterize the chosen action. For more details, see simple_decision_agent_1

        Note that we pass in current_gameboard, even though it is currently unused. In the near future, we may use it
        to refine allowable_actions.

        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: The set of allowable actions (each item in the set is a function from action_choices)
        """
        logger.debug('computing allowable post-roll actions for '+ self.player_name)
        allowable_actions = set()
        allowable_actions.add(concluded_actions)

        if self.num_total_hotels > 0 or self.num_total_houses > 0:
            allowable_actions.add(sell_house_hotel)

        if len(self.assets) > 0:
            allowable_actions.add(sell_property)
            if len(self.mortgaged_assets) < len(self.assets):
                allowable_actions.add(mortgage_property)

        if self._option_to_buy is True:
            allowable_actions.add(buy_property)

        return allowable_actions

    def make_pre_roll_moves(self, current_gameboard):
        """
        The player's pre-roll phase. The function will only return either if the player skips the turn on the first move,
        or till the player returns concluded_actions (if the first move was not skip_turn). Otherwise, it keeps prompting
        the player's decision agent.
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: An integer. 2 if the turn is skipped or 1 for concluded actions. No other code should safely
        be returned.
        """
        logger.debug('We are in the pre-roll phase for '+self.player_name)
        allowable_actions = self.compute_allowable_pre_roll_actions(current_gameboard)
        allowable_actions.remove(concluded_actions)
        allowable_actions.add(skip_turn)
        code = 0
        action_to_execute, parameters = self.agent.make_pre_roll_move(self, current_gameboard, allowable_actions, code)
        t = (action_to_execute, parameters)
        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_pre_roll_move)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        params['code'] = code
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(t)

        if action_to_execute == skip_turn:
            if self.is_property_offer_outstanding:
                # player is clearly unwilling to accept the offer, so we negate it
                self.is_property_offer_outstanding = False
                self.outstanding_property_offer['from_player'] = None
                self.outstanding_property_offer['asset'] = None
                self.outstanding_property_offer['price'] = -1

            if self.is_trade_offer_outstanding:
                self.is_trade_offer_outstanding = False
                self.outstanding_trade_offer['property_set_offered'] = set()
                self.outstanding_trade_offer['property_set_wanted'] = set()
                self.outstanding_trade_offer['cash_offered'] = 0
                self.outstanding_trade_offer['cash_wanted'] = 0
                self.outstanding_trade_offer['from_player'] = None
            return self._execute_action(action_to_execute, parameters, current_gameboard)

        allowable_actions.add(concluded_actions)
        allowable_actions.remove(skip_turn) # from this time on, skip turn is not allowed.current_gameboard['bank'].total_houses += asset.num_houses
        count = 0
        while count < 50: # the player is allowed up to 50 actions before we force conclude actions.
            count += 1
            if action_to_execute == concluded_actions:
                if self.is_property_offer_outstanding:
                    # player is clearly unwilling to accept the offer, so we negate it
                    self.is_property_offer_outstanding = False
                    self.outstanding_property_offer['from_player'] = None
                    self.outstanding_property_offer['asset'] = None
                    self.outstanding_property_offer['price'] = -1

                if self.is_trade_offer_outstanding:
                    self.is_trade_offer_outstanding = False
                    self.outstanding_trade_offer['property_set_offered'] = set()
                    self.outstanding_trade_offer['property_set_wanted'] = set()
                    self.outstanding_trade_offer['cash_offered'] = 0
                    self.outstanding_trade_offer['cash_wanted'] = 0
                    self.outstanding_trade_offer['from_player'] = None
                return self._execute_action(action_to_execute, parameters, current_gameboard)
            else:
                code = self._execute_action(action_to_execute, parameters, current_gameboard)
                logger.debug('Received code '+ str(code)+ '. Continuing iteration...')
                allowable_actions = self.compute_allowable_pre_roll_actions(current_gameboard)
                action_to_execute, parameters = self.agent.make_pre_roll_move(self, current_gameboard, allowable_actions, code)
                t = (action_to_execute, parameters)
                # add to game history
                current_gameboard['history']['function'].append(self.agent.make_pre_roll_move)
                params = dict()
                params['player'] = self
                params['current_gameboard'] = current_gameboard
                params['allowable_moves'] = allowable_actions
                params['code'] = code
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(t)

        # if we got here, we resolve property offers and move on.
        if self.is_property_offer_outstanding:
            # player is clearly unwilling to accept the offer, so we negate it
            self.is_property_offer_outstanding = False
            self.outstanding_property_offer['from_player'] = None
            self.outstanding_property_offer['asset'] = None
            self.outstanding_property_offer['price'] = -1

        if self.is_trade_offer_outstanding:
            self.is_trade_offer_outstanding = False
            self.outstanding_trade_offer['property_set_offered'] = set()
            self.outstanding_trade_offer['property_set_wanted'] = set()
            self.outstanding_trade_offer['cash_offered'] = 0
            self.outstanding_trade_offer['cash_wanted'] = 0
            self.outstanding_trade_offer['from_player'] = None
        return self._execute_action(concluded_actions, dict(), current_gameboard)  # now we can conclude actions

    def make_out_of_turn_moves(self, current_gameboard):
        """
        The player's out-of-turn phase. The function will only return either if the player skips the turn on the first move,
        or till the player returns concluded_actions (if the first move was not skip_turn). Otherwise, it keeps prompting
        the player's decision agent.
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: An integer. 2 if the turn is skipped or 1 for concluded actions. No other code should safely
        be returned.
        """
        logger.debug('We are in the out-of-turn phase for '+ self.player_name)
        allowable_actions = self.compute_allowable_out_of_turn_actions(current_gameboard)
        allowable_actions.remove(concluded_actions)
        allowable_actions.add(skip_turn)
        code = 0
        action_to_execute, parameters = self.agent.make_out_of_turn_move(self, current_gameboard, allowable_actions, code)
        t = (action_to_execute, parameters)
        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_out_of_turn_move)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        params['code'] = code
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(t)

        if action_to_execute == skip_turn:
            if self.is_property_offer_outstanding:
                # player is clearly unwilling to accept the offer, so we negate it
                self.is_property_offer_outstanding = False
                self.outstanding_property_offer['from_player'] = None
                self.outstanding_property_offer['asset'] = None
                self.outstanding_property_offer['price'] = -1

            if self.is_trade_offer_outstanding:
                self.is_trade_offer_outstanding = False
                self.outstanding_trade_offer['property_set_offered'] = set()
                self.outstanding_trade_offer['property_set_wanted'] = set()
                self.outstanding_trade_offer['cash_offered'] = 0
                self.outstanding_trade_offer['cash_wanted'] = 0
                self.outstanding_trade_offer['from_player'] = None
            return self._execute_action(action_to_execute, parameters, current_gameboard)

        allowable_actions.add(concluded_actions)
        allowable_actions.remove(skip_turn)  # from this time on, skip turn is not allowed.
        count = 0
        while count < 50:  # the player is allowed up to 50 actions before we force conclude actions.
            count += 1
            if action_to_execute == concluded_actions:
                if self.is_property_offer_outstanding:
                    # player is clearly unwilling to accept the offer, so we negate it
                    self.is_property_offer_outstanding = False
                    self.outstanding_property_offer['from_player'] = None
                    self.outstanding_property_offer['asset'] = None
                    self.outstanding_property_offer['price'] = -1

                if self.is_trade_offer_outstanding:
                    self.is_trade_offer_outstanding = False
                    self.outstanding_trade_offer['property_set_offered'] = set()
                    self.outstanding_trade_offer['property_set_wanted'] = set()
                    self.outstanding_trade_offer['cash_offered'] = 0
                    self.outstanding_trade_offer['cash_wanted'] = 0
                    self.outstanding_trade_offer['from_player'] = None
                return self._execute_action(action_to_execute, parameters, current_gameboard)
            else:
                #Note that during out of turn move, player can make make_trade_offers to multiple players at the same time
                #Thus action_to_execute and parameters will be lists and will have to be iteratively executed.
                #The return code for each executed action from the list will also be stored in a list. Hence, code is
                #a list in this case.
                if isinstance(action_to_execute, list):
                    code = []
                    for i in range(len(action_to_execute)):
                        code_ret = self._execute_action(action_to_execute[i], parameters[i], current_gameboard)
                        logger.debug('Received code '+ str(code_ret)+ '. Continuing iteration...')
                        code.append(code_ret)
                else:
                    code = self._execute_action(action_to_execute, parameters, current_gameboard)
                    logger.debug('Received code '+ str(code)+ '. Continuing iteration...')

                allowable_actions = self.compute_allowable_out_of_turn_actions(current_gameboard)
                action_to_execute, parameters = self.agent.make_out_of_turn_move(self, current_gameboard, allowable_actions, code)
                t = (action_to_execute, parameters)
                # add to game history
                current_gameboard['history']['function'].append(self.agent.make_out_of_turn_move)
                params = dict()
                params['player'] = self
                params['current_gameboard'] = current_gameboard
                params['allowable_moves'] = allowable_actions
                params['code'] = code
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(t)

        # if we got here, we resolve property offers and move on.
        if self.is_property_offer_outstanding:
            # player is clearly unwilling to accept the offer, so we negate it
            self.is_property_offer_outstanding = False
            self.outstanding_property_offer['from_player'] = None
            self.outstanding_property_offer['asset'] = None
            self.outstanding_property_offer['price'] = -1

        if self.is_trade_offer_outstanding:
            self.is_trade_offer_outstanding = False
            self.outstanding_trade_offer['property_set_offered'] = set()
            self.outstanding_trade_offer['property_set_wanted'] = set()
            self.outstanding_trade_offer['cash_offered'] = 0
            self.outstanding_trade_offer['cash_wanted'] = 0
            self.outstanding_trade_offer['from_player'] = None
        return self._execute_action(concluded_actions, dict(), current_gameboard)  # now we can conclude actions


    def make_post_roll_moves(self, current_gameboard):
        """
        The player's post-roll phase. The function will only return when the player returns concluded_actions as the action. Otherwise, it keeps prompting
        the player's decision agent. There is no skip_turn (reflecting what we already showed in the game schema), unlike
        the other two _moves phases, since out-of-turn moves from other players are not allowed in a post-roll phase.

        Another subtlety to note about this phase is that if you landed on a property that is owned by the bank
        and that could have been bought, then we will invoke auction proceedings if you conclude the phase without
        buying that property (we'll allow you one last chance to purchase in _own_or_auction), before concluding the move
        and moving to the next player's pre-roll phase.
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: An integer. Only 1 (for concluded actions) should be safely returned.

        """
        logger.debug('We are in the post-roll phase for '+ self.player_name)
        allowable_actions = self.compute_allowable_post_roll_actions(current_gameboard)
        code = 0
        action_to_execute, parameters = self.agent.make_post_roll_move(self, current_gameboard, allowable_actions, code)
        t = (action_to_execute, parameters)
        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_post_roll_move)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        params['code'] = code
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(t)

        if action_to_execute == concluded_actions:
            self._force_buy_outcome(current_gameboard) # if option to buy is not set, this will make no difference.
            return self._execute_action(action_to_execute, parameters, current_gameboard) # now we can conclude actions

        count = 0
        while count < 50:  # the player is allowed up to 50 actions before we force conclude actions.
            count += 1
            if action_to_execute == concluded_actions:
                self._force_buy_outcome(current_gameboard)
                return self._execute_action(action_to_execute, parameters, current_gameboard)  # now we can conclude actions
            else:
                code = self._execute_action(action_to_execute, parameters, current_gameboard)
                logger.debug('Received code '+ str(code)+ '. Continuing iteration...')
                allowable_actions = self.compute_allowable_post_roll_actions(current_gameboard)
                action_to_execute, parameters = self.agent.make_post_roll_move(self, current_gameboard, allowable_actions, code)
                t = (action_to_execute, parameters)
                # add to game history
                current_gameboard['history']['function'].append(self.agent.make_post_roll_move)
                params = dict()
                params['player'] = self
                params['current_gameboard'] = current_gameboard
                params['allowable_moves'] = allowable_actions
                params['code'] = code
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(t)
                # logger.debug(action_to_execute)

        self._force_buy_outcome(current_gameboard) # if we got here, we need to conclude actions
        return self._execute_action(concluded_actions, dict(), current_gameboard)  # now we can conclude actions

    def _force_buy_outcome(self, current_gameboard):
        """
        If you land on a property owned by the bank, and don't buy it before concluding your turn, this function will do the needful.
        In essence, it will force your decision agent to return a decision on whether you wish to buy the property (the logic for this
        is in the internal function _own_or_auction). Once the matter has been resolved, we reset the option to buy flag.

        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: None
        """
        logger.debug('Executing _force_buy_outcome for '+self.player_name)
        if self._option_to_buy is True:
            self._own_or_auction(current_gameboard, current_gameboard['location_sequence'][self.current_position])

        self.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(self.reset_option_to_buy)
        params = dict()
        params['self'] = self
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)

        return

    def _own_or_auction(self, current_gameboard, asset):
        """
        This internal function will force the decision agent associated with the player to make a decision on whether to
        purchase the asset or not. If the decision is False, then we begin auction proceedings. The auction code is in Bank.
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :param asset: A purchaseable Location instance. If the player does not buy it, we will invoke auction proceedings.
        :return: None
        """
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

            return
        else:
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

            return

    def _execute_action(self, action_to_execute, parameters, current_gameboard):
        """
        if the action successfully executes, a code of 1 will be returned. If it cannot execute, it will return code failure code.
        The most obvious reason this might happens is because you chose an action that is not an allowable action in your
        situation (e.g., you may try to mortgage a property when you have no properties. In other words, you call an action
        that is not in the set returned by the correct compute_allowable_*_actions). It won't break the code. There may
        be cases when an action is allowable in principle but not in practice. For example, you try to buy a property
        when you don't have enough cash. We avoid dynamic checking of this kind when we compute allowable actions.
        :param action_to_execute: a function to execute. It must be a function inside action_choices
        :param parameters: a dictionary of parameters. These will be unrolled inside the action to execute.
        :return: An integer code that is returned by the executed action.
        """
        logger.debug('Executing _execute_action for '+ self.player_name)
        if parameters:
            p = action_to_execute(**parameters)
            # add to game history
            current_gameboard['history']['function'].append(action_to_execute)
            params = parameters.copy()
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(p)

            return p
        else:
            p = action_to_execute()
            # add to game history
            current_gameboard['history']['function'].append(action_to_execute)
            params = dict()
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(p)

            return p
