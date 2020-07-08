import json
from bank import Bank
import copy
import location
from dice import Dice
from bank import Bank
from card_utility_actions import * # functions from this module will be used in reflections in initialize_board,
                                    # and excluding this import will lead to run-time errors
import sys
from player import Player
import card
import action_choices


def read_in_current_state_from_file(infile, player_decision_agents):
    """
    This function initializes the gameboard with values that were saved from a particular state of another game board.
    This function acts as the proxy for initialize_game_elements.py which would have initialized the gameboard with
    default initial values.
    This function thus loads a pre-existing game board and then lets you play from that point onwards although replication
    of gameplay wouldn't be possible given the uncertainty involved during gameplay.
    :param infile: the .json file from where the game state has to be loaded.
    :param player_decision_agents: agents assigned to each player.
    :return: returns the initialized current_gameboard which will be passed to simulate_game_instance.
    """
    file = open(infile, 'r+')
    current_gameboard = dict()

    game_schema = json.load(file)
    _initialize_bank(current_gameboard, game_schema)
    _initialize_players(current_gameboard, game_schema, player_decision_agents)
    _initialize_locations(current_gameboard, game_schema)
    _initialize_dies(current_gameboard, game_schema)
    _initialize_cards(current_gameboard, game_schema)
    _initialize_game_history_structs(current_gameboard)
    current_gameboard['type'] = "current_gameboard"
    return current_gameboard


def write_out_current_state_to_file(current_gameboard, outfile):
    """
    This function saves all the elements of the gameboard and players to a .json file at some point during the gameplay
    which is upto you. This feature lets you then load this file when starting a new game to recreate the gameboard as it was
    when you wrote it out to the .json file.
    :param current_gameboard: the current gameboard as it is at the point at which you chose to write it out to a .json file.
    :param outfile: the .json file to which you want to write out your gameboard state.
    :return: returns 1 if writing to file has been successful.
    """
    file = open(outfile, 'w+')
    default_schema = '../monopoly_game_schema_v1-2.json'
    game_schema = json.load(open(default_schema, 'r'))
    ans = dict()
    _populate_dict_with_bank(current_gameboard, ans)
    _populate_dict_with_locations(current_gameboard, ans, game_schema)
    _populate_dict_with_dice(current_gameboard, ans)
    _populate_dict_with_cards(current_gameboard, ans, game_schema)
    _populate_dict_with_players(current_gameboard, ans)
    _populate_dict_with_dice(current_gameboard, ans)
    json.dump(ans, file)
    file.close()
    return 1


def _populate_dict_with_bank(current_gameboard, ans):
    ans['bank'] = dict()
    ans['bank']['mortgage_percentage'] = current_gameboard['bank'].mortgage_percentage
    ans['bank']['total_mortgage_rule'] = current_gameboard['bank'].total_mortgage_rule
    ans['bank']['total_houses'] = current_gameboard['bank'].total_houses
    ans['bank']['total_hotels'] = current_gameboard['bank'].total_hotels


def _populate_dict_with_locations(current_gameboard, ans, game_schema):
    ans['locations'] = dict()
    location_objects = list()
    location_sequence = list()
    for item in current_gameboard['location_sequence']:
        location_sequence.append(item.name)

    for k, v in current_gameboard['location_objects'].items():
        obj = dict()
        obj['loc_class'] = v.loc_class
        obj['name'] = v.name
        obj['start_position'] = v.start_position
        obj['end_position'] = v.end_position
        if v.color == 'None':
            obj['color'] = 'None'
        else:
            obj['color'] = v.color
        if v.loc_class == 'action':
            for l in game_schema['locations']['location_states']:
                if l['name'] == v.name:
                    perform_action = l['perform_action']
                    obj['perform_action'] = perform_action
                    break

        elif v.loc_class == 'real_estate':
            obj['rent_1_house'] = v.rent_1_house
            obj['rent_2_houses'] = v.rent_2_houses
            obj['rent_3_houses'] = v.rent_3_houses
            obj['rent_4_houses'] = v.rent_4_houses
            obj['rent_hotel'] = v.rent_hotel
            obj['rent'] = v.rent
            obj['price'] = v.price
            obj['price_per_house'] = v.price_per_house
            obj['mortgage'] = v.mortgage
            if isinstance(v.owned_by, Bank):
                obj['owned_by'] = 'bank'
            else:
                obj['owned_by'] = v.owned_by.player_name

            obj['num_houses'] = v.num_houses
            obj['num_hotels'] = v.num_hotels
            obj['is_mortgaged'] = v.is_mortgaged

        elif v.loc_class == 'tax':
            obj['amount_due'] = v.amount_due

        elif v.loc_class == 'railroad':
            obj['price'] = v.price
            obj['mortgage'] = v.mortgage
            if isinstance(v.owned_by, Bank):
                obj['owned_by'] = 'bank'
            else:
                obj['owned_by'] = v.owned_by.player_name
            obj['is_mortgaged'] = v.is_mortgaged

        elif v.loc_class == 'utility':
            obj['price'] = v.price
            obj['mortgage'] = v.mortgage
            if isinstance(v.owned_by, Bank):
                obj['owned_by'] = 'bank'
            else:
                obj['owned_by'] = v.owned_by.player_name
            obj['is_mortgaged'] = v.is_mortgaged
        location_objects.append(obj)

    ans['locations']['location_objects'] = location_objects
    ans['locations']['location_sequence'] = location_sequence
    ans['locations']['location_count'] = len(current_gameboard['location_sequence'])
    ans['go_position'] = current_gameboard['go_position']
    ans['go_increment'] = current_gameboard['go_increment']
    ans['full_color_sets_possessed'] = game_schema['players']['player_states']['full_color_sets_possessed'][0]


def _populate_dict_with_dice(current_gameboard, ans):
    ans['die'] = dict()
    seq = []
    for item in current_gameboard['die_sequence']:
        l = []
        for i in item:
            l.append(int(i))
        seq.append(l)
    ans['die']['die_sequence'] = seq

    ans['die']['current_die_total'] = int(current_gameboard['current_die_total'])
    ans['die']['die_state'] = []
    ans['die']['die_state_distribution'] = []
    ans['die']['die_type'] = []

    for die in current_gameboard['dies']:
        ans['die']['die_state'].append(die.die_state)
        ans['die']['die_state_distribution'].append(die.die_state_distribution)
        ans['die']['die_type'].append(die.die_type)
    ans['die']['die_count'] = len(current_gameboard['dies'])


def _populate_dict_with_cards(current_gameboard, ans, game_schema):
    ans['cards'] = dict()
    ans['cards']['community_chest_cards'] = dict()
    ans['cards']['chance_cards'] = dict()
    ans['cards']['picked_chance_cards'] = []
    ans['cards']['picked_community_chest_cards'] = []

    chance_card_nums = dict()
    chance_count = 0
    for item in current_gameboard['chance_cards']:
        try:
            chance_card_nums[item.name] += 1
            chance_count += 1
        except:
            chance_card_nums[item.name] = 1
            chance_count += 1
    for item in current_gameboard['picked_chance_cards']:
        if item.name == 'get_out_of_jail_free':
            try:
                chance_card_nums[item.name] += 1
                chance_count += 1
            except:
                chance_card_nums[item.name] = 1
                chance_count += 1

    ans['cards']['chance_cards']['card_states'] = []
    for k, item in current_gameboard['chance_card_objects'].items():
        chance_card = dict()
        chance_card['num'] = chance_card_nums[item.name]
        chance_card['card_type'] = item.card_type
        chance_card['name'] = item.name

        if item.card_type == 'movement':
            chance_card['destination'] = item.destination.name

        elif item.card_type == 'movement_relative':
            chance_card['new_relative_position'] = item.new_relative_position

        elif item.card_type == 'positive_cash_from_bank' or item.card_type == 'negative_cash_from_bank':
            chance_card['amount'] = item.amount

        elif item.card_type == 'positive_cash_from_players' or item.card_type == 'negative_cash_from_players':
            chance_card['amount_per_player'] = item.amount_per_player

        for l in game_schema['cards']['chance']['card_states']:
            if item.name == l['name']:
                chance_card['action'] = l['action']
            if item.card_type == 'contingent_cash_from_bank' and item.card_type == l['card_type']:
                chance_card['contingency'] = l['contingency']

        ans['cards']['chance_cards']['card_states'].append(chance_card)
    ans['cards']['chance_cards']['card_count'] = chance_count

    community_chest_card_nums = dict()
    cc_count = 0
    for item in current_gameboard['community_chest_cards']:
        try:
            community_chest_card_nums[item.name] += 1
            cc_count += 1
        except:
            community_chest_card_nums[item.name] = 1
            cc_count += 1

    for item in current_gameboard['picked_community_chest_cards']:
        if item.name == 'get_out_of_jail_free':
            try:
                community_chest_card_nums[item.name] += 1
                cc_count += 1
            except:
                community_chest_card_nums[item.name] = 1
                cc_count += 1

    ans['cards']['community_chest_cards']['card_states'] = []
    for k, item in current_gameboard['community_chest_card_objects'].items():
        cc_card = dict()
        cc_card['num'] = community_chest_card_nums[item.name]
        cc_card['card_type'] = item.card_type
        cc_card['name'] = item.name

        if item.card_type == 'movement':
            cc_card['destination'] = item.destination.name

        elif item.card_type == 'positive_cash_from_bank' or item.card_type == 'negative_cash_from_bank':
            cc_card['amount'] = item.amount

        elif item.card_type == 'positive_cash_from_players' or item.card_type == 'negative_cash_from_players':
            cc_card['amount_per_player'] = item.amount_per_player

        for l in game_schema['cards']['community_chest']['card_states']:
            if item.name == l['name']:
                cc_card['action'] = l['action']
            if item.card_type == 'contingent_cash_from_bank' and item.card_type == l['card_type']:
                cc_card['contingency'] = l['contingency']

        ans['cards']['community_chest_cards']['card_states'].append(cc_card)
    ans['cards']['community_chest_cards']['card_count'] = cc_count

    ans['cards']['picked_community_chest_cards'] = []
    ans['cards']['picked_chance_cards'] = []
    for item in current_gameboard['picked_community_chest_cards']:
        ans['cards']['picked_community_chest_cards'].append(item.name)
    for item in current_gameboard['picked_chance_cards']:
        ans['cards']['picked_chance_cards'].append(item.name)


def _populate_dict_with_players(current_gameboard, ans):
    players = list()
    for player in current_gameboard['players']:
        pdict = dict()
        pdict['player_name'] = player.player_name
        pdict['status'] = player.status
        if player.current_position:
            pdict['current_position'] = int(player.current_position)
        else:
            pdict['current_position'] = None
        pdict['has_get_out_of_jail_chance_card'] = player.has_get_out_of_jail_chance_card
        pdict['has_get_out_of_jail_community_chest_card'] = player.has_get_out_of_jail_community_chest_card
        pdict['current_cash'] = player.current_cash
        pdict['num_railroads_possessed'] = player.num_railroads_possessed
        pdict['num_utilities_possessed'] = player.num_utilities_possessed
        pdict['full_color_sets_possessed'] = []
        if player.full_color_sets_possessed:
            for item in player.full_color_sets_possessed:
                 pdict['full_color_sets_possessed'].append(item)

        pdict['assets'] = []
        if player.assets:
            for item in player.assets:
                pdict['assets'].append(item.name)
        pdict['currently_in_jail'] = player.currently_in_jail
        pdict['num_total_houses'] = player.num_total_houses
        pdict['num_total_hotels'] = player.num_total_hotels

        pdict['is_property_offer_outstanding'] = player.is_property_offer_outstanding
        outstanding_property_offer = dict()
        if player.is_property_offer_outstanding:
            outstanding_property_offer['from_player'] = player.outstanding_property_offer['from_player']
            outstanding_property_offer['asset'] = player.outstanding_property_offer['asset'].name
            outstanding_property_offer['price'] = player.outstanding_property_offer['price']
        else:
            outstanding_property_offer['from_player'] = None
            outstanding_property_offer['asset'] = None
            outstanding_property_offer['price'] = -1
        pdict['outstanding_property_offer'] = outstanding_property_offer

        pdict['is_trade_offer_outstanding'] = player.is_trade_offer_outstanding
        outstanding_trade_offer = dict()
        if player.is_trade_offer_outstanding:
            outstanding_trade_offer['property_set_offered'] = []
            for item in player.outstanding_trade_offer['property_set_offered']:
                outstanding_trade_offer['property_set_offered'].append(item.name)
            outstanding_trade_offer['property_set_wanted'] = []
            for item in player.outstanding_trade_offer['property_set_wanted']:
                outstanding_trade_offer['property_set_wanted'].append(item.name)
            outstanding_trade_offer['cash_offered'] = player.outstanding_trade_offer['cash_offered']
            outstanding_trade_offer['cash_wanted'] = player.outstanding_trade_offer['cash_wanted']
            outstanding_trade_offer['from_player'] = player.outstanding_trade_offer['from_player']
        else:
            outstanding_trade_offer['property_set_offered'] = []
            outstanding_trade_offer['property_set_wanted'] = []
            outstanding_trade_offer['cash_offered'] = 0
            outstanding_trade_offer['cash_wanted'] = 0
            outstanding_trade_offer['from_player'] = None
        pdict['outstanding_trade_offer'] = outstanding_trade_offer

        pdict['mortgaged_assets'] = []
        if player.mortgaged_assets:
            for item in player.mortgaged_assets:
                pdict['mortgaged_assets'].append(item.name)
        pdict['_option_to_buy'] = player._option_to_buy
        pdict['previous_action'] = player.agent._agent_memory['previous_action'].__name__

        players.append(pdict)
    ans['players'] = players


def _initialize_bank(current_gameboard, game_schema):
    current_gameboard['bank'] = Bank()
    current_gameboard['bank'].mortgage_percentage = game_schema['bank']['mortgage_percentage']
    current_gameboard['bank'].total_mortgage_rule = game_schema['bank']['total_mortgage_rule']
    current_gameboard['bank'].total_houses = game_schema['bank']['total_houses']
    current_gameboard['bank'].total_hotels = game_schema['bank']['total_hotels']


def _initialize_players(current_gameboard, game_schema, player_decision_agents):
    players = list()
    for player in game_schema['players']:
        player_args = dict()
        player_args['status'] = player['status']
        if player['current_position']:
            player_args['current_position'] = int(player['current_position'])
        else:
            player_args['current_position'] = None
        player_args['has_get_out_of_jail_chance_card'] = player['has_get_out_of_jail_chance_card']
        player_args['has_get_out_of_jail_community_chest_card'] = player['has_get_out_of_jail_community_chest_card']
        player_args['current_cash'] = player['current_cash']
        player_args['num_railroads_possessed'] = int(player['num_railroads_possessed'])
        player_args['num_utilities_possessed'] = int(player['num_utilities_possessed'])
        player_args['full_color_sets_possessed'] = set(player['full_color_sets_possessed'])
        player_args['assets'] = set()   #will be populated inside _initialize_locations since location objects not currenty available
        player_args['currently_in_jail'] = player['currently_in_jail']

        player_args['player_name'] = player['player_name']
        player_args['agent'] = player_decision_agents[player['player_name']]
        player_obj = Player(**player_args)
        player_obj.agent._agent_memory['previous_action'] = getattr(action_choices, player['previous_action'])

        player_obj.num_total_houses = player['num_total_houses']
        player_obj.num_total_hotels = player['num_total_hotels']
        player_obj.mortgaged_assets = []   #will be populated inside _initialize_locations since location objects not currenty available
        player_obj._option_to_buy = player['_option_to_buy']
        player_obj.is_property_offer_outstanding = player['is_property_offer_outstanding']
        player_obj.is_trade_offer_outstanding = player['is_trade_offer_outstanding']
        #outstanding_trade_offer and outstanding_property_offer will be populated inside _initialize_locations since location objects not currenty available

        players.append(player_obj)

    current_gameboard['players'] = players


def _initialize_locations(current_gameboard, game_schema):
    location_objects = dict() # key is a location name, and value is a Location object
    railroad_positions = list() # list of integers, with each integer corresponding to a railroad location in
    # game_elements['location_sequence']
    utility_positions = list() # list of integers, with each integer corresponding to a utility location in
    # game_elements['location_sequence']
    location_sequence = list() # list of Location objects in sequence, as they would be ordered on a linear game board.
    color_assets = dict()  # key is a string color (of a real estate property) and value is the set of location objects
    # that have that color. Any asset that does not have a color or where the color is None in the schema will not be
    # included in any set, since we do not insert None in as a key

    for l in game_schema['locations']['location_objects']:
        if l['loc_class'] == 'action':
            action_args = l.copy()
            action_args['perform_action'] = getattr(sys.modules[__name__], l['perform_action'])
            location_objects[l['name']] = location.ActionLocation(**action_args)

        elif l['loc_class'] == 'do_nothing':
            location_objects[l['name']] = location.DoNothingLocation(**l)

        elif l['loc_class'] == 'real_estate':
            real_estate_args = l.copy()
            flag = 0
            if l['owned_by'] == 'bank':
                real_estate_args['owned_by'] = current_gameboard['bank']
            else:
                for item in current_gameboard['players']:
                    if item.player_name == l['owned_by']:
                        real_estate_args['owned_by'] = item
                        flag = 1
            is_mortgaged_flag = l['is_mortgaged']
            del real_estate_args['is_mortgaged']
            location_objects[l['name']] = location.RealEstateLocation(**real_estate_args)
            location_objects[l['name']].is_mortgaged = is_mortgaged_flag
            if flag == 1:
                for player in current_gameboard['players']:
                    if player.player_name == l['owned_by']:
                        player.assets.add(location_objects[l['name']])

        elif l['loc_class'] == 'tax':
            location_objects[l['name']] = location.TaxLocation(**l)

        elif l['loc_class'] == 'railroad':
            railroad_args = l.copy()
            flag = 0
            if l['owned_by'] == 'bank':
                railroad_args['owned_by'] = current_gameboard['bank']
            else:
                for item in current_gameboard['players']:
                    if item.player_name == l['owned_by']:
                        railroad_args['owned_by'] = item
                        flag = 1
            is_mortgaged_flag = l['is_mortgaged']
            del railroad_args['is_mortgaged']
            location_objects[l['name']] = location.RailroadLocation(**railroad_args)
            location_objects[l['name']].is_mortgaged = is_mortgaged_flag
            if flag == 1:
                for player in current_gameboard['players']:
                    if player.player_name == l['owned_by']:
                        player.assets.add(location_objects[l['name']])

        elif l['loc_class'] == 'utility':
            utility_args = l.copy()
            flag = 0
            if l['owned_by'] == 'bank':
                utility_args['owned_by'] = current_gameboard['bank']
            else:
                for item in current_gameboard['players']:
                    if item.player_name == l['owned_by']:
                        utility_args['owned_by'] = item
                        flag = 1
            is_mortgaged_flag = l['is_mortgaged']
            del utility_args['is_mortgaged']
            location_objects[l['name']] = location.UtilityLocation(**utility_args)
            location_objects[l['name']].is_mortgaged = is_mortgaged_flag
            if flag == 1:
                for player in current_gameboard['players']:
                    if player.player_name == l['owned_by']:
                        player.assets.add(location_objects[l['name']])

        else:
            logger.debug('encountered unexpected location class: '+ l['loc_class'])
            logger.error("Exception")

    for i in range(len(game_schema['locations']['location_sequence'])):
        loc = location_objects[game_schema['locations']['location_sequence'][i]]
        location_sequence.append(loc) # we first get the name of
        # the location at index i of the game schema, and then use it in location_objects to get the actual location
        # object (loc) corresponding to that location name. We then append it to location_sequence. The net result is
        # that we have gone from a sequence of location names to the corresponding sequence of objects.
        if loc.loc_class == 'railroad':
            railroad_positions.append(i)
        elif loc.loc_class == 'utility':
            utility_positions.append(i)
        elif loc.name == 'In Jail/Just Visiting':
            current_gameboard['jail_position'] = i

    current_gameboard['railroad_positions'] = railroad_positions
    current_gameboard['utility_positions'] = utility_positions

    if len(location_sequence) != game_schema['locations']['location_count']:
        logger.debug('location count: '+ str(game_schema['locations']['location_count'])+ ', length of location sequence: '+
        str(len(location_sequence))+ ' are unequal.')
        logger.error("Exception")

    if location_sequence[game_schema['go_position']].name != 'Go':
        logger.debug('go positions are not aligned')
        logger.error("Exception")
    else:
        current_gameboard['go_position'] = game_schema['go_position']
        current_gameboard['go_increment'] = game_schema['go_increment']

    current_gameboard['location_objects'] = location_objects
    current_gameboard['location_sequence'] = location_sequence

    for o in location_sequence:
        if o.color is None:
            continue
        elif o.color not in game_schema['full_color_sets_possessed']:
            logger.debug(o.color)
            logger.error("Exception")
        else:
            if o.color not in color_assets:
                color_assets[o.color] = set()
            color_assets[o.color].add(o)

    current_gameboard['color_assets'] = color_assets

    for item in game_schema['players']:
        for player in current_gameboard['players']:
            if item['player_name'] == player.player_name:
                player.mortgaged_assets = set()
                for loc in item['mortgaged_assets']:
                    player.mortgaged_assets.add(current_gameboard['location_objects'][loc])

                outstanding_property_offer = dict()
                outstanding_property_offer['from_player'] = item['outstanding_property_offer']['from_player']
                outstanding_property_offer['price'] = item['outstanding_property_offer']['price']
                outstanding_property_offer['asset'] = set()
                if item['outstanding_property_offer']['asset']:
                    for loc in item['outstanding_property_offer']['asset']:
                        outstanding_property_offer['asset'].add(current_gameboard['location_objects'][loc])

                player.outstanding_property_offer = outstanding_property_offer

                outstanding_trade_offer = dict()
                outstanding_trade_offer['from_player'] = item['outstanding_trade_offer']['from_player']
                outstanding_trade_offer['cash_offered'] = item['outstanding_trade_offer']['cash_offered']
                outstanding_trade_offer['cash_wanted'] = item['outstanding_trade_offer']['cash_wanted']
                outstanding_trade_offer['property_set_wanted'] = set()
                for loc in item['outstanding_trade_offer']['property_set_wanted']:
                    outstanding_trade_offer['property_set_wanted'].add(current_gameboard['location_objects'][loc])
                outstanding_trade_offer['property_set_offered'] = set()
                for loc in item['outstanding_trade_offer']['property_set_offered']:
                    outstanding_trade_offer['property_set_offered'].add(current_gameboard['location_objects'][loc])

                player.outstanding_trade_offer = outstanding_trade_offer
                break


def _initialize_dies(current_gameboard, game_schema):
    die_sequence = []
    for item in game_schema['die']['die_sequence']:
        die_sequence.append(item)
    
    if len(game_schema['die']['die_state']) != game_schema['die']['die_count']:
        logger.debug('dice count is unequal to number of specified dice state-vectors...')
        logger.error("Exception")
    die_count = game_schema['die']['die_count']
    die_objects = list()
    for i in range(0, die_count):
        die_objects.append(Dice(game_schema['die']['die_state'][i])) # send in the vector
        die_objects[i].die_state_distribution = game_schema['die']['die_state_distribution'][i]
        die_objects[i].die_type = game_schema['die']['die_type'][i]

    current_gameboard['dies'] = die_objects
    current_gameboard['current_die_total'] = game_schema['die']['current_die_total']
    current_gameboard['die_sequence'] = die_sequence


def _initialize_cards(current_gameboard, game_schema):
    community_chest_cards = set() # community chest card objects
    chance_cards = set() # chance card objects

    community_chest_card_objects = dict() # key is a community chest card name and value is an object
    chance_card_objects = dict() # key is a chance card name and value is an object

    picked_community_chest_cards = []  #list of all picked community chest cards throughout the gameplay
    picked_chance_cards = []  #list of all picked chance cards throughout the gameplay

    for specific_card in game_schema['cards']['community_chest_cards']['card_states']:
        card_obj = None
        if specific_card['card_type'] == 'movement':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_args['destination'] = current_gameboard['location_objects'][specific_card['destination']]
                card_obj = card.MovementCard(**card_args)
                community_chest_cards.add(card_obj)

        elif specific_card['card_type'] == 'contingent_movement':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_obj = card.ContingentMovementCard(**card_args)
                community_chest_cards.add(card_obj)

        elif specific_card['card_type'] == 'positive_cash_from_bank' or specific_card[
            'card_type'] == 'negative_cash_from_bank':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_args['amount'] = specific_card['amount']
                card_obj = card.CashFromBankCard(**card_args)
                community_chest_cards.add(card_obj)

        elif specific_card['card_type'] == 'contingent_cash_from_bank':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_args['contingency'] = getattr(sys.modules[__name__], specific_card['contingency'])
                card_obj = card.ContingentCashFromBankCard(**card_args)
                community_chest_cards.add(card_obj)

        elif specific_card['card_type'] == 'positive_cash_from_players' or card[
            'card_type'] == 'negative_cash_from_players':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_args['amount_per_player'] = specific_card['amount_per_player']
                card_obj = card.CashFromPlayersCard(**card_args)
                community_chest_cards.add(card_obj)
        else:
            logger.debug('community chest card type is not recognized: '+ specific_card['card_type'])
            logger.error("Exception")

        community_chest_card_objects[card_obj.name] = copy.deepcopy(card_obj)

    if len(community_chest_cards) != game_schema['cards']['community_chest_cards']['card_count']:
        logger.debug('community chest card count and number of items in community chest card set are inconsistent')

    for specific_card in game_schema['cards']['chance_cards']['card_states']:
        card_obj = None
        if specific_card['card_type'] == 'movement':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_args['destination'] = current_gameboard['location_objects'][specific_card['destination']]
                card_obj = card.MovementCard(**card_args)
                chance_cards.add(card_obj)

        elif specific_card['card_type'] == 'movement_payment':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_obj = card.MovementPaymentCard(**card_args)
                chance_cards.add(card_obj)

        elif specific_card['card_type'] == 'contingent_movement':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_obj = card.ContingentMovementCard(**card_args)
                chance_cards.add(card_obj)

        elif specific_card['card_type'] == 'movement_relative':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_args['new_relative_position'] = specific_card['new_relative_position']
                card_obj = card.MovementRelativeCard(**card_args)
                chance_cards.add(card_obj)

        elif specific_card['card_type'] == 'positive_cash_from_bank' or specific_card[
            'card_type'] == 'negative_cash_from_bank':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_args['amount'] = specific_card['amount']
                card_obj = card.CashFromBankCard(**card_args)
                chance_cards.add(card_obj)

        elif specific_card['card_type'] == 'contingent_cash_from_bank':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_args['contingency'] = getattr(sys.modules[__name__], specific_card['contingency'])
                card_obj = card.ContingentCashFromBankCard(**card_args)
                chance_cards.add(card_obj)

        elif specific_card['card_type'] == 'positive_cash_from_players' or specific_card[
            'card_type'] == 'negative_cash_from_players':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_args['amount_per_player'] = specific_card['amount_per_player']
                card_obj = card.CashFromPlayersCard(**card_args)
                chance_cards.add(card_obj)
        else:
            logger.debug('chance card type is not recognized: '+ specific_card['card_type'])
            logger.error("Exception")

        chance_card_objects[card_obj.name] = copy.deepcopy(card_obj)

    if len(chance_cards) != game_schema['cards']['chance_cards']['card_count']:
        logger.debug('chance card count and number of items in chance card set are inconsistent')

    for item in game_schema['cards']['picked_chance_cards']:
        picked_chance_cards.append(chance_card_objects[item])

    for item in game_schema['cards']['picked_community_chest_cards']:
        picked_community_chest_cards.append(community_chest_card_objects[item])

    current_gameboard['chance_cards'] = chance_cards
    current_gameboard['community_chest_cards'] = community_chest_cards
    current_gameboard['chance_card_objects'] = chance_card_objects
    current_gameboard['community_chest_card_objects'] = community_chest_card_objects
    current_gameboard['picked_chance_cards'] = picked_chance_cards
    current_gameboard['picked_community_chest_cards'] = picked_community_chest_cards


def _initialize_game_history_structs(current_gameboard):
    current_gameboard['history'] = dict()
    current_gameboard['history']['function'] = list()
    current_gameboard['history']['param'] = list()
    current_gameboard['history']['return'] = list()
