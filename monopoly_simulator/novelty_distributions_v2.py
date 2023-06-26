from monopoly_simulator import novelty_generator_v2
from monopoly_simulator import novelty_functions_v2
from monopoly_simulator.player import Player
from monopoly_simulator.location import RealEstateLocation
import json
import numpy as np
import os

cwd = os.getcwd()
json_dir = os.path.join(cwd)
json_file_path = os.path.join(json_dir, "monopoly_game_schema_v1-2.json")
###########Automate this file through novelty_generator_random.py
###########Config file should be the json of novelty_generator_v2.py
##########Config file should contain some functions from novelty_generator_v2.py
# and also well set of parameter space for those functions

def M6_L1_T1(current_gameboard, chance_card_num=14, cc_card_num=17, alternate_cont_func_SR="alternate_contingency_function_SR_1",
             alternate_cont_func_GR="alternate_contingency_function_GR_1"):

    numberCardNovelty = novelty_generator_v2.NumberClassNovelty()
    classCardNovelty = novelty_generator_v2.TypeClassNovelty()

    #inject first primitive
    community_chest_cards_num = dict()
    chance_cards_num = dict()
    game_schema = json.load(open(json_file_path, 'r'))
    for specific_card in game_schema['cards']['community_chest']['card_states']:
        if specific_card['name'] == 'general_repairs' or specific_card['name'] == 'street_repairs':
            community_chest_cards_num[specific_card['name']] = chance_card_num
        else:
            community_chest_cards_num[specific_card['name']] = specific_card['num']

    for specific_card in game_schema['cards']['chance']['card_states']:
        if specific_card['name'] == 'general_repairs' or specific_card['name'] == 'street_repairs':
            chance_cards_num[specific_card['name']] = cc_card_num
        else:
            chance_cards_num[specific_card['name']] = specific_card['num']

    numberCardNovelty.card_novelty(current_gameboard, chance_cards_num=chance_cards_num,
                                   community_chest_cards_num=community_chest_cards_num)

    #now inject second primitive
    novel_cc = dict()
    novel_cc["street_repairs"] = alternate_cont_func_SR
    novel_chance = dict()
    novel_chance["general_repairs"] = alternate_cont_func_GR
    classCardNovelty.card_novelty(current_gameboard, novel_cc, novel_chance)


def M6_L1_T2(current_gameboard, dist_vec=('uniform', 'biased'), type_vec=('odd_only', 'even_only')):
    classDieNovelty = novelty_generator_v2.TypeClassNovelty() ##Automate this through reflection calling from config
    dist_vec = list(dist_vec) ##Sample this from config
    die_state_distribution_vector = dist_vec  ##Sample this from config
    type_vec = list(type_vec)  ##Sample this from config
    die_type_vector = type_vec  ##Sample this from config
    classDieNovelty.die_novelty(current_gameboard, die_state_distribution_vector, die_type_vector)##Automate this through reflection calling from config


def M6_L1_E1(current_gameboard, chance_card_name='go_to_boardwalk', cc_card_name='go_to_boardwalk', chance_card_num=100, cc_card_num=100):
    numberCardNovelty = novelty_generator_v2.NumberClassNovelty()
    community_chest_cards_num = dict()
    chance_cards_num = dict()
    game_schema = json.load(open(json_file_path, 'r'))
    for specific_card in game_schema['cards']['community_chest']['card_states']:
        if specific_card['name'] == chance_card_name:
            community_chest_cards_num[specific_card['name']] = chance_card_num
        else:
            community_chest_cards_num[specific_card['name']] = specific_card['num']

    for specific_card in game_schema['cards']['chance']['card_states']:
        if specific_card['name'] == cc_card_name:
            chance_cards_num[specific_card['name']] = cc_card_num
        else:
            chance_cards_num[specific_card['name']] = specific_card['num']

    numberCardNovelty.card_novelty(current_gameboard, chance_cards_num=chance_cards_num,
                                   community_chest_cards_num=community_chest_cards_num)


def M6_L1_E2(current_gameboard, auction_transaction_tax_amount=250, alternate_func='alternate_auction'):
    current_gameboard['auction_transaction_tax'] = auction_transaction_tax_amount
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.auction_novelty(current_gameboard, alternate_func)


def M6_L1_M1(current_gameboard, forbidden_colors=['Blue', 'Brown', 'Red'], alternate_func='alternate_improvement_possible'):
    forbidden_colors = list(forbidden_colors)
    current_gameboard['forbidden_improvement_color'] = set()
    for color in forbidden_colors:
        current_gameboard['forbidden_improvement_color'].add(color)
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.forbid_improvement(current_gameboard, alternate_func)


def M6_L1_M2(current_gameboard, utility_tax=50, railroad_tax=75, alternate_func='utility_railroad_taxation'):
    current_gameboard['utility_tax'] = utility_tax
    current_gameboard['railroad_tax'] = railroad_tax
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.auxiliary_go(current_gameboard, alternate_func)


def M6_L1_H1(current_gameboard, die_sig=1, alternate_func='random_player_movement'):
    current_gameboard['die_sig'] = die_sig
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.alternate_move_player_after_die_roll(current_gameboard, alternate_func)


def M6_L1_H2(current_gameboard, wealth_tax=0.15, alternate_func='net_worth_taxation'):
    current_gameboard['wealth_tax'] = wealth_tax
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.auxiliary_go(current_gameboard, alternate_func)


def M6_L2_T1(current_gameboard, new_rent_perc=0.15, new_tax=900):
    inanimateAttributeNovelty = novelty_generator_v2.InanimateAttributeNovelty()
    for l in current_gameboard['location_sequence']:
        if l.loc_class == 'tax':
            inanimateAttributeNovelty.tax_novelty(l, new_tax)
        elif l.loc_class == 'real_estate':
            rent_dict = dict()
            rent_dict['rent_1_house'] = l.rent_1_house * new_rent_perc
            rent_dict['rent_2_houses'] = l.rent_2_houses * new_rent_perc
            rent_dict['rent_3_houses'] = l.rent_3_houses * new_rent_perc
            rent_dict['rent_4_houses'] = l.rent_4_houses * new_rent_perc
            rent_dict['rent_hotel'] = l.rent_hotel * new_rent_perc
            inanimateAttributeNovelty.rent_novelty(l, rent_dict)


def M6_L2_T2(current_gameboard, new_rent_perc=0.1, new_loc_price=1000, new_price_per_house=20):
    inanimateAttributeNovelty = novelty_generator_v2.InanimateAttributeNovelty()
    new_color = 'Green'
    prop_set = set()
    for l in current_gameboard['location_sequence']:
        if l.loc_class == 'real_estate':
            if l.name == 'Boardwalk' or l.name == 'Park Place':
                inanimateAttributeNovelty.price_novelty(l, new_loc_price)
                inanimateAttributeNovelty.price_per_house_novelty(l, new_price_per_house)
            else:
                prop_set.add(l)
                rent_dict = dict()
                rent_dict['rent_1_house'] = l.rent_1_house * new_rent_perc
                rent_dict['rent_2_houses'] = l.rent_2_houses * new_rent_perc
                rent_dict['rent_3_houses'] = l.rent_3_houses * new_rent_perc
                rent_dict['rent_4_houses'] = l.rent_4_houses * new_rent_perc
                rent_dict['rent_hotel'] = l.rent_hotel * new_rent_perc
                inanimateAttributeNovelty.rent_novelty(l, rent_dict)
    inanimateAttributeNovelty.map_property_to_color(current_gameboard, prop_set, new_color)


def M6_L2_E1(current_gameboard, new_go_increment=30, new_player_start_cash=200):
    inanimateAttributeNovelty = novelty_generator_v2.InanimateAttributeNovelty()
    new_color = 'Color-'
    count = 1
    inanimateAttributeNovelty.go_increment_novelty(current_gameboard, new_go_increment)
    for p in current_gameboard['players']:
        inanimateAttributeNovelty.player_starting_cash_novelty(p, new_player_start_cash)
    for l in current_gameboard['location_sequence']:
        if l.loc_class == 'real_estate':
            k = np.random.rand()
            if k <= 0.05:
                continue
            prop_set = set()
            prop_set.add(l)
            new_color_count = new_color + str(count)
            count += 1
            inanimateAttributeNovelty.bank_zero_sum(current_gameboard, prop_set, new_color_count)


def M6_L2_E2(current_gameboard, contingent_go=True, alternate_func='decrease_go_increment'):
    current_gameboard['contingent_go'] = contingent_go
    contingentAttributeNovelty = novelty_generator_v2.ContingentAttributeNovelty()
    if current_gameboard['contingent_go']:
        contingentAttributeNovelty.auxiliary_go(current_gameboard, alternate_func)


def M6_L2_M1(current_gameboard, num_houses=6, new_go_increment=50):
    current_gameboard['bank'].total_houses = num_houses
    inanimateAttributeNovelty = novelty_generator_v2.InanimateAttributeNovelty()
    inanimateAttributeNovelty.go_increment_novelty(current_gameboard, new_go_increment)


def M6_L2_M2(current_gameboard, new_mortgage_perc=0.95, new_mortgage=5):
    inanimateAttributeNovelty = novelty_generator_v2.InanimateAttributeNovelty()
    current_gameboard['bank'].mortgage_percentage = new_mortgage_perc
    for l in current_gameboard['location_sequence']:
        if l.loc_class == 'real_estate' or l.loc_class == 'railroad' or l.loc_class == 'utility':
            inanimateAttributeNovelty.mortgage_novelty(l, new_mortgage)


def M6_L2_H1(current_gameboard, new_mortgage_perc=2.0):
    inanimateAttributeNovelty = novelty_generator_v2.InanimateAttributeNovelty()
    current_gameboard['bank'].mortgage_percentage = new_mortgage_perc
    for l in current_gameboard['location_sequence']:
        if l.loc_class == 'real_estate' or l.loc_class == 'railroad' or l.loc_class == 'utility':
            inanimateAttributeNovelty.mortgage_novelty(l, l.mortgage*6)


def M6_L2_H2(current_gameboard, inflation_inc=20, alternate_func='inflation_increment'):
    current_gameboard['inflation_increment'] = inflation_inc
    contingentAttributeNovelty = novelty_generator_v2.ContingentAttributeNovelty()
    contingentAttributeNovelty.auxiliary_go(current_gameboard, alternate_func)


def M6_L3_T1(current_gameboard):
    granNovelty = novelty_generator_v2.GranularityRepresentationNovelty()
    spatNovelty = novelty_generator_v2.SpatialRepresentationNovelty()
    new_location_sequence = list()
    for l in current_gameboard['location_sequence']:
        if l.name == 'Virginia Avenue':
            new_location_sequence.append('Park Place')
        elif l.name == 'Park Place':
            new_location_sequence.append('Virginia Avenue')
        else:
            new_location_sequence.append(l.name)

    spatNovelty.global_reordering(current_gameboard,new_location_sequence)
    for l in current_gameboard['location_sequence']:
        if l.name == 'Park Place' or l.name == 'Boardwalk':
            granNovelty.granularity_novelty(current_gameboard,l,l.end_position+4)


def M6_L3_T2(current_gameboard, extend_loc_by=4):
    granNovelty = novelty_generator_v2.GranularityRepresentationNovelty()
    for l in current_gameboard['location_sequence']:
        if l.name != 'Go':
            granNovelty.granularity_novelty(current_gameboard, l, l.end_position + extend_loc_by)


def M6_L3_E1(current_gameboard, backward=True, alternate_func='backward_movement'):
    current_gameboard['backward'] = backward
    spatNovelty = novelty_generator_v2.SpatialRepresentationNovelty()
    spatNovelty.alternate_move_player_after_die_roll(current_gameboard, alternate_func)


def M6_L3_E2(current_gameboard, mult_signal=True, alternate_func='multiply_die_roll'):
    current_gameboard['mult_signal'] = mult_signal
    spatNovelty = novelty_generator_v2.SpatialRepresentationNovelty()
    spatNovelty.alternate_move_player_after_die_roll(current_gameboard, alternate_func)


def M6_L3_M1(current_gameboard, tax_loc_extend=4, goto_jail_extend=4):
    granNovelty = novelty_generator_v2.GranularityRepresentationNovelty()
    for l in current_gameboard['location_sequence']:
        if l.name == 'Luxury Tax' or l.name == 'Income Tax':
            granNovelty.granularity_novelty(current_gameboard, l, l.end_position + tax_loc_extend)
        elif l.name == 'Go to Jail':
            granNovelty.granularity_novelty(current_gameboard, l, l.end_position + goto_jail_extend)


def M6_L3_M2(current_gameboard, multiply_by=10,
             alternate_func={'RealEstate':'alternate_rent_dues', 'Railroad':'alternate_railroad_dues', 'Utility':'alternate_utility_dues'}):
    current_gameboard['rent_flag'] = multiply_by
    for l in current_gameboard['location_sequence']:
        if l.loc_class == 'railroad':
            for i in [1, 2, 3, 4]:
                l._railroad_dues[i] *= current_gameboard['rent_flag']
        elif l.loc_class == 'utility':
            for i in [1, 2]:
                l._die_multiples[i] *= current_gameboard['rent_flag']
        elif l.loc_class == 'real_estate':
            l.rent_1_house *= current_gameboard['rent_flag']
            l.rent_2_houses *= current_gameboard['rent_flag']
            l.rent_3_houses *= current_gameboard['rent_flag']
            l.rent_4_houses *= current_gameboard['rent_flag']
            l.rent_hotel *= current_gameboard['rent_flag']
            l.rent *= current_gameboard['rent_flag']
            for i in [1, 2, 3, 4]:
                l._house_rent_dict[i] *= current_gameboard['rent_flag']
    spatNovelty = novelty_generator_v2.SpatialRepresentationNovelty()
    for p in current_gameboard['players']:
        spatNovelty.rent_novelty(current_gameboard, p, alternate_func)


def M6_L3_H1(current_gameboard, new_failure_code=-3, alternate_func='reassign_failure_code'):
    current_gameboard['failure_code'] = new_failure_code
    granNovelty = novelty_generator_v2.GranularityRepresentationNovelty()
    granNovelty.failure_code_novelty(current_gameboard, alternate_func)


def M6_L3_H2(current_gameboard, alternate_func='property_random_distribution_among_players'):
    granNovelty = novelty_generator_v2.GranularityRepresentationNovelty()
    granNovelty.property_distribution_novelty(current_gameboard, alternate_func)


def jail_visitation_fee(current_gameboard, jail_visit_fee=500, alternate_func='pay_jail_visitation_fee'):   # CE3
    current_gameboard['jail_visit_fee'] = jail_visit_fee
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.auxiliary_check_assignment(current_gameboard, alternate_func)


def compound_interest_on_cash_when_passing_go(current_gameboard, interest_perc=0.7, alternate_func='charge_compound_interest_on_cash'):     #CM4
    current_gameboard['cash_interest_perc'] = interest_perc
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.auxiliary_go(current_gameboard, alternate_func)


def increase_hotel_limit(current_gameboard, new_hotel_limit=5):          #AE4
    RealEstateLocation.calculate_rent = novelty_functions_v2.calculate_new_rent_due_to_hotel_limit_novelty
    inanimateAttributeNovelty = novelty_generator_v2.InanimateAttributeNovelty()
    inanimateAttributeNovelty.bank_attribute_novelty(current_gameboard, "hotel_limit", new_hotel_limit)


def change_monopolized_property_rent_factor_2(current_gameboard, new_rent_factor=0.5):          #AE5
    # Note:
    # - if 0 < new_rent_factor < 1 --> AE5
    # - else if new_rent_factor > 1 --> AH3
    inanimateAttributeNovelty = novelty_generator_v2.InanimateAttributeNovelty()
    inanimateAttributeNovelty.bank_attribute_novelty(current_gameboard, "monopolized_property_rent_factor", new_rent_factor)


def change_monopolized_property_rent_factor(current_gameboard, new_rent_factor=0.5):         # AH3
    # Note:
    # - if 0 < new_rent_factor < 1 --> AE5
    # - else if new_rent_factor > 1 --> AH3
    inanimateAttributeNovelty = novelty_generator_v2.InanimateAttributeNovelty()
    inanimateAttributeNovelty.bank_attribute_novelty(current_gameboard, "monopolized_property_rent_factor", new_rent_factor)


def dynamic_bank_attribute_inflation(current_gameboard, inflation_params={'property_sell_percentage':0.1, 'house_sell_percentage':0.1, 'hotel_sell_percentage':0.1}):          #AH5
    """
    :param current_gameboard:
    :param inflation_params: dictionary with bank params that should undergo inflation during novelty injection. key should be the same name
    as the bank param and value is the changed value upon inflation
    :return:
    """
    # inflation_params = dict()
    # inflation_params['property_sell_percentage'] = 0.1
    # inflation_params['house_sell_percentage'] = 0.1
    # inflation_params['hotel_sell_percentage'] = 0.1
    inanimateAttributeNovelty = novelty_generator_v2.InanimateAttributeNovelty()
    for k, v in inflation_params.items():
        inanimateAttributeNovelty.bank_attribute_novelty(current_gameboard, k, v)


def pay_tax_when_passing_tax_locations(current_gameboard, alternate_func='charge_player_when_passing_tax_loc'):           #RM5
    spatNovelty = novelty_generator_v2.SpatialRepresentationNovelty()
    spatNovelty.auxiliary_check_assignment(current_gameboard, alternate_func)


def move_all_players_after_die_roll(current_gameboard, alternate_func='move_all_players_after_dieroll'):            #RE5
    spatNovelty = novelty_generator_v2.SpatialRepresentationNovelty()
    spatNovelty.alternate_move_player_after_die_roll(current_gameboard, alternate_func)


def change_game_termination_die_roll_limit(current_gameboard, die_roll_limit=50, alternate_func='alternate_check_for_game_termination'):   #RM2
    current_gameboard['die_roll_limit'] = die_roll_limit
    granNovelty = novelty_generator_v2.GranularityRepresentationNovelty()
    granNovelty.game_termination_func_novelty(current_gameboard, alternate_func)


def change_game_termination_time_limit(current_gameboard, time_limit=0.2, alternate_func='alternate_check_for_game_termination'):       #RM3
    # time limit in seconds, usually game runs in <0.5 secs without novelty
    current_gameboard['time_limit'] = time_limit
    granNovelty = novelty_generator_v2.GranularityRepresentationNovelty()
    granNovelty.game_termination_func_novelty(current_gameboard, alternate_func)


def color_taxation(current_gameboard, color_tax_dict={'Blue':50, 'SkyBlue':60, 'Brown':70, 'Orange':80, 'Orchid':110, 'Red':100, 'Green':90, 'Yellow':60},
                   alternate_func='auxiliary_go_tax_on_color_ownership'):          #CE4
    # Note: a dictionary with taxes for each color has to be passed in as a param
    # color_tax_dict = dict()
    # color_tax_dict['Blue'] = 50
    # color_tax_dict['SkyBlue'] = 60
    # color_tax_dict['Brown'] = 70
    # color_tax_dict['Orange'] = 80
    # color_tax_dict['Orchid'] = 110
    # color_tax_dict['Red'] = 100
    # color_tax_dict['Green'] = 90
    # color_tax_dict['Yellow'] = 60
    current_gameboard['color_tax_dict'] = color_tax_dict
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.auxiliary_go(current_gameboard, alternate_func)


def avenue_differential_treatment(current_gameboard, min_cash_limit=1000, alternate_func='avenue_rule_change'):          #CE5
    current_gameboard['avenue_purchase_cash_limit'] = min_cash_limit
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.auxiliary_post_roll(current_gameboard, alternate_func)


def compound_interest_on_mortgage_when_passing_go(current_gameboard, interest_perc=0.5, alternate_func='charge_compound_interest_on_mortgage'):     #CM3
    current_gameboard['mortgage_interest_perc'] = interest_perc
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.auxiliary_go(current_gameboard, alternate_func)


def dynamic_mortgage(current_gameboard, perc=2.0, alternate_func='calculate_mortgage_owed_dynamic'):        #AM2
    current_gameboard['mortgage_dynamic_perc'] = perc
    contingentAttributeNovelty = novelty_generator_v2.ContingentAttributeNovelty()
    contingentAttributeNovelty.dynamic_mortgage(current_gameboard, alternate_func)


def dynamic_rent_change(current_gameboard, perc=0.2, alternate_func='calculate_rent_dynamic'):          #AM4
    current_gameboard['rent_dynamic_perc'] = perc
    contingentAttributeNovelty = novelty_generator_v2.ContingentAttributeNovelty()
    contingentAttributeNovelty.auxiliary_go(current_gameboard, alternate_func)


def increase_house_limit_per_property(current_gameboard, new_house_limit=6):        #AM5
    inanimateAttributeNovelty = novelty_generator_v2.InanimateAttributeNovelty()
    inanimateAttributeNovelty.bank_attribute_novelty(current_gameboard, 'house_limit_before_hotel', new_house_limit)
    for prop in current_gameboard['location_sequence']:
        if prop.loc_class == 'real_estate' and new_house_limit > 4:
            for i in range(5, new_house_limit+1):
                prop._house_rent_dict[i] = prop.rent_4_houses


def fork_at_free_parking(current_gameboard, alternate_func='fork_at_free_parking_func'):     #RH5
    spatNovelty = novelty_generator_v2.SpatialRepresentationNovelty()
    spatNovelty.alternate_move_player_after_die_roll(current_gameboard, alternate_func)


def bank_zero_sum(current_gameboard, bank_cash=100, new_go_inc=50, player_start_cash=600):     #AH4
    # total prices of all property locations combined = 5690
    inanimateAttributeNovelty = novelty_generator_v2.InanimateAttributeNovelty()
    inanimateAttributeNovelty.bank_attribute_novelty(current_gameboard, 'total_cash_with_bank', bank_cash)
    inanimateAttributeNovelty.go_increment_novelty(current_gameboard, new_go_inc)
    for p in current_gameboard['players']:
        inanimateAttributeNovelty.player_starting_cash_novelty(p, player_start_cash)
    for l in current_gameboard['location_sequence']:
        if l.loc_class == 'tax':
            inanimateAttributeNovelty.tax_novelty(l, l.amount_due/2)


def ownership_based_tax(current_gameboard, tax_perc=0.5, alternate_func='ownership_based_tax_func'):          #CM5
    current_gameboard['tax_perc'] = tax_perc
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.alternate_tax_calc(current_gameboard, alternate_func)


def tax_reduces_wealth_inequality(current_gameboard, tax_perc=0.3, alternate_func='tax_reduces_wealth_inequality_func'):          #CH2
    current_gameboard['tax_perc'] = tax_perc
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.alternate_tax_calc(current_gameboard, alternate_func)


def jail_times_limited(current_gameboard, jail_times=3, alternate_func_1='set_send_to_jail_limited',
                       alternate_func_2='alternate_compute_allowable_post_roll_actions',
                       alternate_func_3='alternate_handle_negative_cash_balance',
                       alternate_func_4='alternate_pay_jail_fine'):       #CH3
    current_gameboard['jail_times'] = dict()
    current_gameboard['jail_times']['player_1'] = jail_times
    current_gameboard['jail_times']['player_2'] = jail_times
    current_gameboard['jail_times']['player_3'] = jail_times
    current_gameboard['jail_times']['player_4'] = jail_times
    current_gameboard['jail_limit_player'] = dict()
    current_gameboard['jail_limit_player']['player_1'] = False
    current_gameboard['jail_limit_player']['player_2'] = False
    current_gameboard['jail_limit_player']['player_3'] = False
    current_gameboard['jail_limit_player']['player_4'] = False
    numberClassNovelty = novelty_generator_v2.NumberClassNovelty()
    numberClassNovelty.jail_entry_novelty(current_gameboard, alternate_func_1)
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.assign_compute_postroll(current_gameboard, alternate_func_2)
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.handle_negative_cash_balance_differently(current_gameboard, alternate_func_3)
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.assign_pay_jail_fine(current_gameboard, alternate_func_4)


def multiple_asset_types_not_permissible(current_gameboard, alternate_func='alternate_update_asset_owner'):
    typeClassNovelty = novelty_generator_v2.TypeClassNovelty()
    typeClassNovelty.alternate_update_asset_owner(current_gameboard, alternate_func)


def new_class_of_railroads(current_gameboard, alternate_func='alternate_calculate_railroad_dues'):     #CH1
    numberClassNovelty = novelty_generator_v2.NumberClassNovelty()
    numberClassNovelty.railroad_novelty(current_gameboard, alternate_func)


def hide_player_color_sets(current_gameboard, alternate_func_1='hide_player_color_sets_before', alternate_func_2='hide_player_color_sets_after'):   #RE4
    granNovelty = novelty_generator_v2.GranularityRepresentationNovelty()
    granNovelty.partial_observability(current_gameboard, alternate_func_1, alternate_func_2)


def hide_other_player_assets(current_gameboard, alternate_func_1='hide_player_assets_before', alternate_func_2='hide_player_assets_after'):   #RH2
    granNovelty = novelty_generator_v2.GranularityRepresentationNovelty()
    granNovelty.partial_observability(current_gameboard, alternate_func_1, alternate_func_2)


def incorrect_property_colors(current_gameboard, alternate_func_1='incorrect_property_colors_before', alternate_func_2='incorrect_property_colors_after'):   #RH3
    granNovelty = novelty_generator_v2.GranularityRepresentationNovelty()
    granNovelty.partial_observability(current_gameboard, alternate_func_1, alternate_func_2)


def dummy_player(current_gameboard, alternate_func_1='assign_dummy_players_before', alternate_func_2='assign_dummy_players_after'):     #RH1
    granNovelty = novelty_generator_v2.GranularityRepresentationNovelty()
    granNovelty.partial_observability(current_gameboard, alternate_func_1, alternate_func_2)


def black_white_properties(current_gameboard, alternate_func_1='uncolor_properties_before', alternate_func_2='uncolor_properties_after'):   #RE1
    granNovelty = novelty_generator_v2.GranularityRepresentationNovelty()
    granNovelty.partial_observability(current_gameboard, alternate_func_1, alternate_func_2)


def property_name_change(current_gameboard, alternate_func_1='property_name_change_before', alternate_func_2='property_name_change_after'):     #RM4
    Player._populate_param_dict = novelty_functions_v2.populate_param_dict_mod
    granNovelty = novelty_generator_v2.GranularityRepresentationNovelty()
    granNovelty.partial_observability(current_gameboard, alternate_func_1, alternate_func_2)


def luxury_hotel(current_gameboard, new_hotel_limit=4):     #CH4
    # after one regular hotel, all hotels therafter are considered luxury hotels and will still cost the same as a normal hotel (i.e price per house)
    # but will have a rent of 2 times that of normal hotel
    RealEstateLocation.calculate_rent = novelty_functions_v2.calculate_new_rent_luxury_hotel
    inanimateAttributeNovelty = novelty_generator_v2.InanimateAttributeNovelty()
    inanimateAttributeNovelty.bank_attribute_novelty(current_gameboard, "hotel_limit", new_hotel_limit)


def reduce_house_limit(current_gameboard, new_house_limit=2):          #AM3
    RealEstateLocation.calculate_rent = novelty_functions_v2.calculate_new_rent_due_to_hotel_limit_novelty
    inanimateAttributeNovelty = novelty_generator_v2.InanimateAttributeNovelty()
    inanimateAttributeNovelty.bank_attribute_novelty(current_gameboard, "house_limit_before_hotel", new_house_limit)
