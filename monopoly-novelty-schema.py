def specify_board_state():

    board_state['board_shape'] = 'linear'
    board_state['go_position'] = 0
    board_state['go_increment'] = 200
    # taken from https://en.wikipedia.org/wiki/Template:Monopoly_board_layout also saved in local
    board_state['location_sequence'] = ['Go','Mediterranean Avenue', 'Community Chest',
                'Baltic Avenue', 'Income Tax', 'Reading Railroad', 'Oriental Avenue',
                'Chance', 'Vermont Avenue', 'Connecticut Avenue', 'In Jail/Just Visiting',
                'St. Charles Place', 'Electric Company', 'States Avenue', 'Virginia Avenue',
                'Pennsylvania Railroad', 'St. James Place', 'Community Chest', 'Tennessee Avenue',
                'New York Avenue', 'Free Parking', 'Kentucky Avenue', 'Chance', 'Indiana Avenue',
                'Illinois Avenue', 'B&O Railroad', 'Atlantic Avenue', 'Ventnor Avenue',
                'Water Works', 'Marvin Gardens', 'Go to Jail', 'Pacific Avenue', 'North Carolina Avenue',
                'Community Chest', 'Pennsylvania Avenue', 'Short Line', 'Chance', 'Park Place',
                                        'Luxury Tax', 'Boardwalk']

    # these are functions that will re-order the location sequence
    # as well as position attributes in 'locations' (and go_position) so that they are in sync.

    # color_reordering: color blocks + non-color positions will all stay where they are in default location sequence,
    # but within the color block, the properties will be reordered. Re-orderings will be based on a permutation
    # scheme (which may or may not be dependent on price) that will be uniformly applied to ALL color blocks when this
    # novelty is generated.

    #global_reordering: any board ordering is fair here as long as it is linear (we do not introduce non-linear
    #layouts in Month 6). There will be a logic to the reordering that will be manually determined but will not be
    #revealed in advance. For example, we may decide to make all railroads and utilities consecutive in the new sequence.

    board_state['reorder_location_sequence'] = ['default', 'color_reordering', 'global_reordering']

    board_state['location_colors'] = ['default','map_property_set_to_color', 'map_property_to_color', 'exchange_colors_between_properties'] # color novelty at the attribute level.
    # note that we will not be introducing 'new' colors i.e. when a color changes (whether on a full block or an individual property), it will be to one of
    # the colors that currently exists in the game schema.

    board_state['location_free_mortgage_rule'] = ['default', 'percent_of_total_mortgage_outstanding', 'change_percentage'] # these are Level 2 attribute novelties at the contingent sub-level
    # recall, the default rule simply says that to free the mortgage on a property you have to pay the principle (mortgage field on that property) + 10% of principle
    # change percentage will change the percent from 10% to a range of [1,5,10,20,40,70]. The lower end makes it cheaper to mortgage, the higher end more expensive to do so.
    # percent_of_total_mortgage_outstanding will compute interest against the total outstanding mortgage rather than just the mortgage to be freed (see google
    # slides for an example we've provided). Think of it as a way to discourage the agent from taking on too much debt all at once. The percent can vary, again from
    # the range of [1,5,10,20,40,70].

    #populate die
    board_state['die'] = _specify_die_state()

    #populate cards
    board_state['cards'] = _specify_card_state()

    # populate actions
    board_state['action_choices'] = _specify_action_state()

    #populate location details
    board_state['locations'] = _specify_location_state(board_state['location_sequence'])

    # populate player details
    board_state['players'] = _specify_player_state(len(board_state['location_sequence']))



def _specify_action_state():
    ans = dict()
    ans['pre_die_roll'] = ['mortgage_property', 'improve_property', 'use_get_out_of_jail_card', 'pay_jail_fine',
                           'skip_turn', 'free_mortgage', 'sell_property', 'sell_house_hotel', 'accept_sell_property_offer'
                           , 'roll_die', 'concluded_actions', 'make_trade_offer', 'accept_trade_offer']
    ans['post_die_roll'] = ['mortgage_property', 'buy_property', 'sell_property',
                            'sell_house_hotel', 'concluded_actions'] # treat auction as a special case
    ans['out_of_turn'] = ['free_mortgage','sell_property','sell_house_hotel','accept_sell_property_offer',
                          'make_trade_offer', 'accept_trade_offer','skip_turn', 'concluded_actions', 'mortgage_property', 'improve_property']

    return ans

def _specify_player_state(num_board_positions):
    ans = dict()
    count = 4
    ans['player_count'] = count
    # ans['player_states'] = list()
    inner_dict = {'player_name':['player_1','player_2','player_3','player_4'],
                  'starting_cash': 1500,
                  'current_cash': 1500,
                  'current_position':list(range(0,num_board_positions)),
                  'status': ['waiting_for_move', 'current_move', 'won', 'lost'],
                  'assets': ['Mediterranean Avenue',
                'Baltic Avenue', 'Reading Railroad', 'Oriental Avenue',
                'Vermont Avenue', 'Connecticut Avenue',
                'St. Charles Place', 'Electric Company', 'States Avenue', 'Virginia Avenue',
                'Pennsylvania Railroad', 'St. James Place', 'Tennessee Avenue',
                'New York Avenue', 'Kentucky Avenue', 'Indiana Avenue',
                'Illinois Avenue', 'B&O Railroad', 'Atlantic Avenue', 'Ventnor Avenue',
                'Water Works', 'Marvin Gardens', 'Pacific Avenue', 'North Carolina Avenue',
                'Pennsylvania Avenue', 'Short Line', 'Park Place','Boardwalk'
                               ],
                  'full_color_sets_possessed': [['Brown', 'SkyBlue', 'Orchid', 'Red', 'Orange', 'Yellow',
                                            'Green', 'Blue']],
                  'num_utilities_possessed':[0,1,2],
                  'num_railroads_possessed': [0, 1, 2,3,4],
                  'currently_in_jail':[True,False],
                  'has_get_out_of_jail_chance_card': [True,False],
                  'has_get_out_of_jail_community_chest_card': [True, False]
                  }

    # for i in range(0,count):
    #     ans['player_states'].append(inner_dict)
    ans['player_states'] = inner_dict
    return ans

def _specify_card_state():
    ans = dict()
    ans['community_chest'] = dict()
    ans['chance'] = dict()

    # community chest
    # update card count range due to Number novelty
    ans['community_chest']['card_count'] = list(range(0,340))
    ans['community_chest']['card_states'] = _build_community_chest_card_details()

    # chance
    # update card count range due to Number novelty
    ans['chance']['card_count'] = list(range(0,320))
    ans['chance']['card_states'] = _build_chance_card_details()
    return ans

def _build_community_chest_card_details():
    cards = list()

    go_to_jail = {'action':'move_player', 'name':'go_to_jail', 'card_type':'movement', 'destination':'In Jail/Just Visiting', 'num':1}
    cards.append(go_to_jail)

    get_out_of_jail_free = {'action':'set_get_out_of_jail_card_status', 'name':'get_out_of_jail_free', 'card_type':'contingent_movement', 'num':1}
    cards.append(get_out_of_jail_free)

    sale_of_stock = {'action':'bank_cash_transaction', 'name':'sale_of_stock', 'card_type':'positive_cash_from_bank', 'amount':[200,150,100,50], 'num':1}
    cards.append(sale_of_stock)

    bank_error = {'action':'bank_cash_transaction', 'name':'bank_error', 'card_type':'positive_cash_from_bank', 'amount':[100,200,300,400,500], 'num':1}
    cards.append(bank_error)

    doctor_fee = {'action':'bank_cash_transaction', 'name':'doctor_fee', 'card_type':'negative_cash_from_bank', 'amount':[-200,-150,-100,-50], 'num':1}
    cards.append(doctor_fee)

    advance_to_go = {'action':'move_player', 'name':'advance_to_go', 'card_type':'movement', 'destination':'Go', 'num':1}
    cards.append(advance_to_go)

    grand_opera_night = {'action':'player_cash_transaction', 'name':'grand_opera_night', 'card_type':'positive_cash_from_players',
                         'amount_per_player':[200,150,100,50], 'num':1}
    cards.append(grand_opera_night)

    holiday_fund_matures = {'action':'bank_cash_transaction', 'name':'holiday_fund_matures', 'card_type':'positive_cash_from_bank', 'amount':[100,200,300,400,500], 'num':1}
    cards.append(holiday_fund_matures)

    income_tax_refund = {'action':'bank_cash_transaction', 'name':'income_tax_refund', 'card_type':'positive_cash_from_bank', 'amount':[20,40,60,80,100,150,200], 'num':1}
    cards.append(income_tax_refund)

    birthday = {'action':'player_cash_transaction', 'name':'birthday', 'card_type':'positive_cash_from_players', 'amount_per_player':[10,30,50,70,100,150,200], 'num':1}
    cards.append(birthday)

    life_insurance_matures = {'action':'bank_cash_transaction', 'name':'life_insurance_matures', 'card_type':'positive_cash_from_bank', 'amount':[100,200,300,400,500], 'num':1}
    cards.append(life_insurance_matures)

    hospital_fee = {'action':'bank_cash_transaction', 'name':'hospital_fee', 'card_type':'negative_cash_from_bank', 'amount':[-200,-150,-100,-50], 'num':1}
    cards.append(hospital_fee)

    school_fee = {'action':'bank_cash_transaction', 'name':'school_fee', 'card_type':'negative_cash_from_bank', 'amount':[-200,-150,-100,-50], 'num':1}
    cards.append(school_fee)

    consultancy_fee = {'action':'bank_cash_transaction', 'name':'consultancy_fee', 'card_type':'positive_cash_from_bank', 'amount':[25,50,75,100,150,300], 'num':1}
    cards.append(consultancy_fee)

    street_repairs = {'action':'contingent_bank_cash_transaction', 'name':'street_repairs',
                      'card_type':'contingent_cash_from_bank',
                      'contingency':'calculate_street_repair_cost', 'num':1}
    cards.append(street_repairs)

    win_beauty_contest = {'action':'bank_cash_transaction', 'name':'win_beauty_contest', 'card_type':'positive_cash_from_bank', 'amount':[10,30,50,70,100,150,200], 'num':1}
    cards.append(win_beauty_contest)

    inherit_money = {'action':'bank_cash_transaction', 'name':'inherit_money', 'card_type':'positive_cash_from_bank', 'amount':[100,200,300,400,500], 'num':1}
    cards.append(inherit_money)

    # Number novelty: community chest cards
    for c in cards:
        c['num'] = list(range(0, 21))

    # Attribute novelty: expand range of destinations
    for c in cards:
        if 'destination' in c:
            c['destination'] = board_state['location_sequence']

    # Type novelty: introduce novelty in contingency function
    for c in cards:
        if c['card_type'] == 'contingent_cash_from_bank':
            c['contingency'] = [c['contingency'],'novel_contingency_function']

    return cards

def _build_chance_card_details():
    cards = list()
    go_to_jail = {'action': 'move_player', 'name': 'go_to_jail', 'card_type': 'movement',
                  'destination': 'In Jail/Just Visiting', 'num':1}
    cards.append(go_to_jail)

    get_out_of_jail_free = {'action': 'set_get_out_of_jail_card_status', 'name': 'get_out_of_jail_free',
                            'card_type': 'contingent_movement', 'num':1}
    cards.append(get_out_of_jail_free)

    go_to_illinois_avenue = {'action': 'move_player__check_for_go', 'name': 'go_to_illinois_avenue', 'card_type': 'movement',
                  'destination': 'Illinois Avenue', 'num':1}
    cards.append(go_to_illinois_avenue)

    advance_to_go = {'action': 'move_player', 'name': 'advance_to_go', 'card_type': 'movement', 'destination': 'Go',
                     'num': 1}
    cards.append(advance_to_go)

    go_to_st_charles = {'action': 'move_player__check_for_go', 'name': 'go_to_st_charles', 'card_type': 'movement',
                  'destination': 'St. Charles Place', 'num':1}
    cards.append(go_to_st_charles)

    go_to_nearest_utility = {'action': 'move_to_nearest_utility__pay_or_buy__check_for_go', 'name': 'go_to_nearest_utility',
                             'card_type': 'movement_payment', 'num':1}
    cards.append(go_to_nearest_utility)

    go_to_nearest_railroad_pay_double = {'action': 'move_to_nearest_railroad__pay_double_or_buy__check_for_go', 'name': 'go_to_nearest_railroad_pay_double',
                                         'card_type': 'movement_payment', 'num':2}
    cards.append(go_to_nearest_railroad_pay_double)

    bank_dividend = {'action': 'bank_cash_transaction', 'name': 'bank_dividend', 'card_type': 'positive_cash_from_bank',
                  'amount': [10,30,50,70,100,150,200], 'num':1}
    cards.append(bank_dividend)

    general_repairs = {'action': 'contingent_bank_cash_transaction', 'name': 'general_repairs',
                      'card_type': 'contingent_cash_from_bank',
                      'contingency': 'calculate_general_repair_cost', 'num':1}
    cards.append(general_repairs)

    go_back_three_spaces = {'action': 'move_player_relative', 'name': 'go_back_three_spaces', 'card_type': 'movement_relative',
                   'new_relative_position': -3, 'num':1}
    cards.append(go_back_three_spaces)

    go_to_reading_railroad = {'action': 'move_player__check_for_go', 'name': 'go_to_reading_railroad',
                             'card_type': 'movement',
                             'destination': 'Reading Railroad', 'num': 1}
    cards.append(go_to_reading_railroad)

    go_to_boardwalk = {'action': 'move_player__check_for_go', 'name': 'go_to_boardwalk',
                              'card_type': 'movement',
                              'destination': 'Boardwalk', 'num': 1}
    cards.append(go_to_boardwalk)

    pay_poor_tax = {'action': 'bank_cash_transaction', 'name': 'pay_poor_tax', 'card_type': 'negative_cash_from_bank',
                    'amount': [-15,-30,-50,-100,-200], 'num': 1}
    cards.append(pay_poor_tax)

    building_loan_matures = {'action': 'bank_cash_transaction', 'name': 'building_loan_matures', 'card_type': 'positive_cash_from_bank',
                     'amount': [50,150,250,450,600], 'num': 1}
    cards.append(building_loan_matures)

    win_crossword_competition = {'action': 'bank_cash_transaction', 'name': 'win_crossword_competition',
                             'card_type': 'positive_cash_from_bank',
                             'amount': [50, 100,150,200,300,500], 'num': 1}
    cards.append(win_crossword_competition)

    elected_board_chairman = {'action': 'player_cash_transaction', 'name': 'elected_board_chairman',
                         'card_type': 'negative_cash_from_players',
                         'amount_per_player': [-50,-100,-200,-300], 'num': 1}
    cards.append(elected_board_chairman)

    # Number novelty: chance cards
    for c in cards:
        c['num'] = list(range(0,21))

    # Attribute novelty: expand range of destinations
    for c in cards:
        if 'destination' in c:
            c['destination'] = board_state['location_sequence']

    # Type novelty: introduce novelty in contingency function
    for c in cards:
        if c['card_type'] == 'contingent_cash_from_bank':
            c['contingency'] = [c['contingency'], 'novel_contingency_function']

    return cards

def _specify_location_state(location_sequence):
    """
    location is defined broadly here, could include any 'spot' where a player could land. Properties may span locations,
    though they do not in the default board.
    :param location_sequence: a list of strings, where each string is the name of a location
    :return: the location dictionary
    """
    ans = dict()
    ans['location_count'] = len(location_sequence)
    ans['location_states'] = list()
    location_details = _build_individual_location_details()
    index = 0
    for loc in location_sequence:
        ans['location_states'].append(location_details[loc])
        ans['location_states'][index]['start_position'] = index
        # Representation Novelty: end position may not be start_position+1 but can 'span' more than one dice-block on the board.
        # the span will never be non-consecutive. In Month 6, when we introduce this novelty, we will limit to only one property
        # at a time, though which property and at what end-position will not be revealed in advance.
        ans['location_states'][index]['end_position'] = list(range(index+1,index+6))
        index += 1


    return ans

def _specify_die_state():
    ans = dict()
    # count = 2
    ans['die_count'] = list(range(2,7))
    #  Number novelty: introduce new numbers and types in die state
    ans['die_state'] = list(range(1,21))
    ans['die_state_distribution'] = ['uniform', 'biased'] # For Month 6, the dice will still be fair i.e. will not change based on player
    ans['die_type'] = ['consecutive', 'even_only', 'odd_only'] # it is not necessary for the consecutive type to always start from 1. Within
    # our novelty generator, we will pass in a  start and end state to 'consecutive' e.g., the dice could be from [8..12].
    return ans


def _build_individual_location_details():

    ans = dict()
    # class Brown
    ans['Mediterranean Avenue'] = {'color':'Brown','price':60, 'name':'Mediterranean Avenue', 'rent':2,
                                   'price_per_house':50, 'rent_1_house':10, 'rent_2_houses':30,
                                   'rent_3_houses': 90, 'rent_4_houses':160, 'rent_hotel':250,
                                   'mortgage':30, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    ans['Baltic Avenue'] = {'color': 'Brown', 'price': 60, 'name': 'Baltic Avenue', 'rent': 4,
                                   'price_per_house': 50, 'rent_1_house': 20, 'rent_2_houses': 60,
                                   'rent_3_houses': 180, 'rent_4_houses': 320, 'rent_hotel': 450,
                                   'mortgage': 30, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    #class SkyBlue
    ans['Oriental Avenue'] = {'color': 'SkyBlue', 'price': 100, 'name': 'Oriental Avenue', 'rent': 6,
                                   'price_per_house': 50, 'rent_1_house': 30, 'rent_2_houses': 90,
                                   'rent_3_houses': 270, 'rent_4_houses': 400, 'rent_hotel': 550,
                                   'mortgage': 50, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    ans['Vermont Avenue'] = {'color': 'SkyBlue', 'price': 100, 'name': 'Vermont Avenue', 'rent': 6,
                              'price_per_house': 50, 'rent_1_house': 30, 'rent_2_houses': 90,
                                   'rent_3_houses': 270, 'rent_4_houses': 400, 'rent_hotel': 550,
                                   'mortgage': 50, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    ans['Connecticut Avenue'] = {'color': 'SkyBlue', 'price': 120, 'name': 'Connecticut Avenue', 'rent': 8,
                              'price_per_house': 50, 'rent_1_house': 40, 'rent_2_houses': 100,
                              'rent_3_houses': 300, 'rent_4_houses': 450, 'rent_hotel': 600,
                              'mortgage': 60, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}
    # class Orchid
    ans['St. Charles Place'] = {'color': 'Orchid', 'price': 140, 'name': 'St. Charles Place', 'rent': 10,
                              'price_per_house': 10, 'rent_1_house': 50, 'rent_2_houses': 150,
                              'rent_3_houses': 450, 'rent_4_houses': 625, 'rent_hotel': 750,
                              'mortgage': 70, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    ans['States Avenue'] = {'color': 'Orchid', 'price': 140, 'name': 'States Avenue', 'rent': 10,
                              'price_per_house': 10, 'rent_1_house': 50, 'rent_2_houses': 150,
                              'rent_3_houses': 450, 'rent_4_houses': 625, 'rent_hotel': 750,
                              'mortgage': 70, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    ans['Virginia Avenue'] = {'color': 'Orchid', 'price': 160, 'name': 'Virginia Avenue', 'rent': 12,
                              'price_per_house': 12, 'rent_1_house': 60, 'rent_2_houses': 180,
                              'rent_3_houses': 500, 'rent_4_houses': 700, 'rent_hotel': 900,
                              'mortgage': 80, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    # class Orange
    ans['St. James Place'] = {'color': 'Orange', 'price': 180, 'name': 'St. James Place', 'rent': 14,
                                'price_per_house': 100, 'rent_1_house': 70, 'rent_2_houses': 200,
                                'rent_3_houses': 550, 'rent_4_houses': 750, 'rent_hotel': 950,
                                'mortgage': 90, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    ans['Tennessee Avenue'] = {'color': 'Orange', 'price': 180, 'name': 'Tennessee Avenue', 'rent': 14,
                            'price_per_house': 100, 'rent_1_house': 70, 'rent_2_houses': 200,
                                'rent_3_houses': 550, 'rent_4_houses': 750, 'rent_hotel': 950,
                                'mortgage': 90, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    ans['New York Avenue'] = {'color': 'Orange', 'price': 200, 'name': 'New York Avenue', 'rent': 16,
                              'price_per_house': 100, 'rent_1_house': 80, 'rent_2_houses': 220,
                              'rent_3_houses': 600, 'rent_4_houses': 800, 'rent_hotel': 1000,
                              'mortgage': 100, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    # class Red
    ans['Kentucky Avenue'] = {'color': 'Red', 'price': 220, 'name': 'Kentucky Avenue', 'rent': 18,
                              'price_per_house': 150, 'rent_1_house': 90, 'rent_2_houses': 250,
                              'rent_3_houses': 700, 'rent_4_houses': 875, 'rent_hotel': 1050,
                              'mortgage': 110, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    ans['Indiana Avenue'] = {'color': 'Red', 'price': 220, 'name': 'Indiana Avenue', 'rent': 18,
                               'price_per_house': 150, 'rent_1_house': 90, 'rent_2_houses': 250,
                              'rent_3_houses': 700, 'rent_4_houses': 875, 'rent_hotel': 1050,
                              'mortgage': 110, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    ans['Illinois Avenue'] = {'color': 'Red', 'price': 240, 'name': 'Illinois Avenue', 'rent': 20,
                              'price_per_house': 150, 'rent_1_house': 100, 'rent_2_houses': 300,
                              'rent_3_houses': 750, 'rent_4_houses': 925, 'rent_hotel': 1100,
                              'mortgage': 120, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    # class Yellow
    ans['Atlantic Avenue'] = {'color': 'Yellow', 'price': 260, 'name': 'Atlantic Avenue', 'rent': 22,
                              'price_per_house': 150, 'rent_1_house': 110, 'rent_2_houses': 330,
                              'rent_3_houses': 800, 'rent_4_houses': 975, 'rent_hotel': 1150,
                              'mortgage': 130, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    ans['Ventnor Avenue'] = {'color': 'Yellow', 'price': 260, 'name': 'Ventnor Avenue', 'rent': 22,
                             'price_per_house': 150, 'rent_1_house': 110, 'rent_2_houses': 330,
                              'rent_3_houses': 800, 'rent_4_houses': 975, 'rent_hotel': 1150,
                              'mortgage': 130, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    ans['Marvin Gardens'] = {'color': 'Yellow', 'price': 280, 'name': 'Marvin Gardens', 'rent': 24,
                              'price_per_house': 150, 'rent_1_house': 120, 'rent_2_houses': 360,
                              'rent_3_houses': 850, 'rent_4_houses': 1025, 'rent_hotel': 1200,
                              'mortgage': 140, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    # class Green
    ans['Pacific Avenue'] = {'color': 'Green', 'price': 300, 'name': 'Pacific Avenue', 'rent': 26,
                              'price_per_house': 200, 'rent_1_house': 130, 'rent_2_houses': 390,
                              'rent_3_houses': 900, 'rent_4_houses': 1100, 'rent_hotel': 1275,
                              'mortgage': 150, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    ans['North Carolina Avenue'] = {'color': 'Green', 'price': 300, 'name': 'North Carolina Avenue', 'rent': 26,
                             'price_per_house': 200, 'rent_1_house': 130, 'rent_2_houses': 390,
                              'rent_3_houses': 900, 'rent_4_houses': 1100, 'rent_hotel': 1275,
                              'mortgage': 150, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    ans['Pennsylvania Avenue'] = {'color': 'Green', 'price': 320, 'name': 'Pennsylvania Avenue', 'rent': 28,
                             'price_per_house': 200, 'rent_1_house': 150, 'rent_2_houses': 450,
                             'rent_3_houses': 1000, 'rent_4_houses': 1200, 'rent_hotel': 1400,
                             'mortgage': 160, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    # class Blue
    ans['Park Place'] = {'color': 'Blue', 'price': 350, 'name': 'Park Place', 'rent': 35,
                             'price_per_house': 200, 'rent_1_house': 175, 'rent_2_houses': 500,
                             'rent_3_houses': 1100, 'rent_4_houses': 1300, 'rent_hotel': 1500,
                             'mortgage': 175, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    ans['Boardwalk'] = {'color': 'Blue', 'price': 400, 'name': 'Boardwalk', 'rent': 50,
                                    'price_per_house': 200, 'rent_1_house': 200, 'rent_2_houses': 600,
                                    'rent_3_houses': 1400, 'rent_4_houses': 1700, 'rent_hotel': 2000,
                                 'mortgage': 200, 'loc_class':'real_estate',
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4'],
                                   'num_houses':[0,1,2,3,4], 'num_hotels': [0,1]}

    # Railroads
    ans['Reading Railroad'] = {'name':'Reading Railroad','color': 'None','loc_class':'railroad',
                               'price': 200, 'mortgage': 100,
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4']}
    ans['B&O Railroad'] = {'name':'B&O Railroad','color': 'None','loc_class':'railroad',
                               'price': 200, 'mortgage': 100,
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4']}
    ans['Pennsylvania Railroad'] = {'name': 'Pennsylvania Railroad', 'color': 'None', 'loc_class': 'railroad',
                           'price': 200, 'mortgage': 100,
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4']}
    ans['Short Line'] = {'name': 'Short Line', 'color': 'None', 'loc_class': 'railroad',
                           'price': 200, 'mortgage': 100,
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4']}

    #Utilities
    ans['Electric Company'] = {'name': 'Electric Company', 'color': 'None', 'loc_class': 'utility',
                               'price': 150, 'mortgage': 75,
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4']}
    ans['Water Works'] = {'name': 'Water Works', 'color': 'None', 'loc_class': 'utility',
                               'price': 150, 'mortgage': 75,
                                   'owned_by':['bank', 'player_1', 'player_2', 'player_3', 'player_4']}

    # Tax
    ans['Income Tax'] = {'name': 'Income Tax', 'color': 'None', 'loc_class': 'tax', 'amount_due':[100,200,400,700]}
    ans['Luxury Tax'] = {'name': 'Luxury Tax', 'color': 'None', 'loc_class': 'tax', 'amount_due':[50,100,200,300,400,500,600]}

    # Do Nothing
    ans['Go'] = {'name': 'Go', 'color': 'None', 'loc_class': 'do_nothing'}
    ans['In Jail/Just Visiting'] = {'name': 'In Jail/Just Visiting', 'color': 'None', 'loc_class': 'do_nothing'}
    ans['Free Parking'] = {'name': 'Free Parking', 'color': 'None', 'loc_class': 'do_nothing'}

    # Action
    ans['Chance'] = {'name': 'Chance', 'color': 'None', 'loc_class': 'action',
                     'perform_action':'pick_card_from_chance'}
    ans['Community Chest'] = {'name': 'Community Chest', 'color': 'None', 'loc_class': 'action',
                              'perform_action':'pick_card_from_community_chest'}
    ans['Go to Jail'] = {'name': 'Go to Jail', 'color': 'None', 'loc_class': 'action',
                              'perform_action': 'go_to_jail'}

    # introduce attribute novelty for price/mortgage on houses
    for k, v in ans.items():
        if 'price' in v:
            if 'mortgage' not in v: # just making sure
                raise Exception
            else:
                new_price = list()
                new_price.append(v['price'])
                new_price.append(v['price']/2)
                new_price.append(v['price'] * 2)
                new_price.append(v['price'] * 3)
                new_price.append(v['price'] * 4)

                new_mortgage = list()
                new_mortgage.append(v['mortgage'])
                new_mortgage.append(v['mortgage'] / 2)
                new_mortgage.append(v['mortgage'] * 2)
                new_mortgage.append(v['mortgage'] * 3)
                new_mortgage.append(v['mortgage'] * 4)

                v['price'] = new_price
                v['mortgage'] = new_mortgage

                if v['loc_class'] == 'real_estate':

                    v['rent'] = _build_novelty_list(v['rent'])
                    v['price_per_house'] = _build_novelty_list(v['price_per_house'])
                    v['rent_1_house'] = _build_novelty_list(v['rent_1_house'])
                    v['rent_2_houses'] = _build_novelty_list(v['rent_2_houses'])
                    v['rent_3_houses'] = _build_novelty_list(v['rent_3_houses'])
                    v['rent_4_houses'] = _build_novelty_list(v['rent_4_houses'])
                    v['rent_hotel'] = _build_novelty_list(v['rent_hotel'])



    return ans


def _build_novelty_list(base_num):
    ans_list = list()
    ans_list.append(base_num)
    ans_list.append(base_num / 2)
    ans_list.append(base_num * 2)
    ans_list.append(base_num * 3)
    ans_list.append(base_num * 4)

    return ans_list

board_state = dict()
specify_board_state()
import json

json.dump(board_state, open('monopoly_novelty_schema_v2.json', 'w'))



