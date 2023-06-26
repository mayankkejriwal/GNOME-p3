from monopoly_simulator import novelty_generator_v2
from monopoly_simulator import novelty_functions_v2
from monopoly_simulator import novelty_generator_v3
from monopoly_simulator.player import Player
from monopoly_simulator.location import RealEstateLocation
import json
import numpy as np
import os
import sys

from monopoly_simulator import initialize_game_elements # for novelty "picked_card_applies_to_all_players"




cwd = os.getcwd()
json_dir = os.path.join(cwd)
json_file_path = os.path.join(json_dir, "monopoly_game_schema_v1-2.json")


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
    classDieNovelty = novelty_generator_v2.TypeClassNovelty()
    dist_vec = list(dist_vec)
    die_state_distribution_vector = dist_vec
    type_vec = list(type_vec)
    die_type_vector = type_vec
    classDieNovelty.die_novelty(current_gameboard, die_state_distribution_vector, die_type_vector)


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
    inanimateAttributeNovelty.map_property_set_to_color(current_gameboard, prop_set, new_color)


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
            inanimateAttributeNovelty.map_property_set_to_color(current_gameboard, prop_set, new_color_count)


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


#-------------------------------------------Phase 2 Novelties---------------------------------------------

#----------------------------------------------Actions----------------------------------------------------

def chat_message_novelty(current_gameboard, phase='pre_roll', alternate_func="chat_assignment"):
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'Player'
    current_gameboard[schema]['message'] = 'String'
    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func)


# Actions1
def give_GOO_jail_card_to_another_player(current_gameboard, phase='pre_roll', alternate_func="transfer_GOO_jail_card"):
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'Player'
    current_gameboard[schema]['action_params_dict'] = 'None'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'

    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func)


# Actions2
def lawsuit_prevent_improvement(current_gameboard, phase='pre_roll', amount=500, rounds=3, alternate_func="lawsuit_prevents_improvements"):
    """
    A player can file a lawsuit against another player for an amount valid for certain number of rounds during which time the other player
    is not allowed to make improvements.
    :param player:
    :param against_player:
    :param current_gameboard:
    :param amount:
    :param rounds:
    :return:
    """
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'Player'
    current_gameboard[schema]['action_params_dict'] = 'None'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'


    lawsuit_dict = dict()
    lawsuit_dict['amount'] = amount
    lawsuit_dict['from_player_num_rounds'] = rounds
    lawsuit_dict['against_player_num_rounds'] = rounds

    current_gameboard['lawsuit_dict'] = lawsuit_dict
    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func)


# Actions3
def increase_monopolized_rent_increase_income_tax(current_gameboard, phase='pre_roll', monopolized_rent_perc=3, income_tax_perc=0.10, alternate_func='monopoly_based_income_tax'):
    """
    monopolized property rents will be increased at the cost of an increased income tax perc that the player will have to
    pay if it owns any monopolized color groups.
    :param current_gameboard:
    :param monopolized_rent_perc:
    :param income_tax_perc: income tax increases by a factor of this percentage depending on the # of monopolies owned by the resp player
    :return:
    """
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'None'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'
    current_gameboard[schema]['action_params_dict'] = 'None'

    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.bank_attribute_novelty(current_gameboard, "monopolized_property_rent_factor", float(monopolized_rent_perc))
    current_gameboard['tax_perc'] = income_tax_perc
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func)


# Actions4
def use_other_player_GOO_jail_card(current_gameboard, phase='pre_roll', alternate_func='illegal_use_of_GOO_jail_card'):
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'Player'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'
    current_gameboard[schema]['action_params_dict'] = 'None'


    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func)


# Actions5
def free_mortgage_in_installments(current_gameboard, phase='pre_roll', installment_fee=20, num_rounds=5, alternate_func='installment_based_free_mortgage',
                                  alternate_func_1='reassign_free_mortgage'):
    """
    If the player decides to mortgage property in installments, then the installments will be paid in the auxiliary_before_pre_roll_check action.
    The details are saved in the player's respective agent memory to keep track on how much has been paid off in the installments.
    Note, if the player has chosen this arbitrary action choice, then the regular free_mortgage() function in action_choices will return failure
    code saying it cannot be invoked to free a mortgage on a property that is being freed in installments. Hence action_choices.free_mortgage()
    function is also lifted
    :param current_gameboard:
    :param phase:
    :param installment_fee:
    :param num_rounds:
    :param alternate_func:
    :return:
    """
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'None'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'
    current_gameboard[schema]['action_params_dict'] = dict()
    current_gameboard[schema]['action_params_dict']['location'] = 'Location'



    current_gameboard['installment_fee'] = installment_fee
    current_gameboard['num_rounds'] = num_rounds

    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func)
    actionNovelty.assign_free_mortgage(current_gameboard, alternate_func_1)


# Actions6
def change_real_estate_color(current_gameboard, phase='pre_roll', times=3, alternate_func='changing_real_estate_colors'):
    """
    Each player can change the colors of real estate locations that they own "times" number of times in a game with this novelty.
    :param current_gameboard:
    :param times: # of times that a player is allowed to change real estate location colors during a gane.
    :param alternate_func:
    :return:
    """
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'None'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'
    current_gameboard[schema]['action_params_dict'] = dict()
    current_gameboard[schema]['action_params_dict']['location'] = 'Location'
    current_gameboard[schema]['action_params_dict']['color'] = 'Color'


    current_gameboard['real_estate_change_colors'] = dict()
    current_gameboard['real_estate_change_colors']['player_1'] = times
    current_gameboard['real_estate_change_colors']['player_2'] = times
    current_gameboard['real_estate_change_colors']['player_3'] = times
    current_gameboard['real_estate_change_colors']['player_4'] = times

    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func)


# Actions7
def stay_in_jail_longer(current_gameboard, phase='pre_roll', jail_tax_perc=0.2, alternate_func1='alternate_set_currently_in_jail_to_false',
                        alternate_func2='alternate_rent_payment', alternate_func3='stay_in_jail_choice'):
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'None'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'
    current_gameboard[schema]['action_params_dict'] = dict()
    current_gameboard[schema]['action_params_dict']['stay_in_jail'] = 'Player_status' # Player_status represent boolean, please refer to the spreadsheet shared with Tufts



    current_gameboard['jail_tax_perc'] = jail_tax_perc


    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.assign_set_currently_in_jail_to_false(current_gameboard, alternate_func1)
    actionNovelty.assign_calculate_and_pay_rent_dues(current_gameboard, alternate_func2)
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func3)


# Actions8
def add_dummy_locations(current_gameboard, phase='pre_roll', times=3, cost=500, alternate_func1='alternate_calculate_rent_based_on_dummy_location',
                        alternate_func2='add_dummy_locs_on_monopolized_color_group'):
    """
    # Note: dummy location will not be added to player's portfolio to avoid trading, improvements, etc
    # solely for the purpose of collecting rent which will be calculated only if the player has a monopoly over that color group,
    # else will return 0.
    :param current_gameboard:
    :param phase:
    :param times:
    :param cost:
    :param alternate_func1:
    :param alternate_func2:
    :return:
    """
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'None'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'
    current_gameboard[schema]['action_params_dict'] = dict()
    current_gameboard[schema]['action_params_dict']['start_pos'] = 'Position'
    current_gameboard[schema]['action_params_dict']['color'] = 'Color'

    current_gameboard['dummy_locs'] = dict()
    current_gameboard['dummy_locs']['player_1'] = times
    current_gameboard['dummy_locs']['player_2'] = times
    current_gameboard['dummy_locs']['player_3'] = times
    current_gameboard['dummy_locs']['player_4'] = times
    current_gameboard['cost'] = cost


    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.alternate_real_estate_rent_calc(current_gameboard, alternate_func1)
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func2)


# Actions9
def dice_reroll_insurance(current_gameboard, phase='pre_roll', insurance_amt=100, alternate_func1='insured_die_roll', alternate_func2='dice_insurance_reroll'):
    """
    Player can reroll the dice if it pays insurance.
    :param current_gameboard:
    :param insurance_amt:
    :param alternate_func:
    :return:
    """
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'None'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'
    current_gameboard[schema]['action_params_dict'] = dict()
    current_gameboard[schema]['action_params_dict']['choice_list'] = 'Location [list]'


    current_gameboard['dice_insurance'] = insurance_amt

    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.assign_die_roll(current_gameboard, alternate_func1)
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func2)


# Actions 10
def save_money_on_properties(current_gameboard, phase='pre_roll', save_amt=100, save_perc=0.5, return_perc=0.3, alternate_func1='alternate_pay_rent', alternate_func2='pay_bank_save_money'):
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'None'
    current_gameboard[schema]['action_params_dict'] = 'None'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'





    current_gameboard['save_perc'] = save_perc
    current_gameboard['return_perc'] = return_perc
    current_gameboard['save_amt'] = save_amt
    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.assign_calculate_and_pay_rent_dues(current_gameboard, alternate_func1)
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func2)


# Actions11
def property_tunneling(current_gameboard, phase='pre_roll', tunneling_fee=0, alternate_func='connect_properties'):
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'None'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'
    current_gameboard[schema]['action_params_dict'] = dict()
    current_gameboard[schema]['action_params_dict']['location'] = 'Location'

    current_gameboard['tunneling_fee'] = tunneling_fee


    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func)


# Actions12
def rent_exemption_leads_to_tax_exemption(current_gameboard, phase='pre_roll', turns=3, alternate_func_Realestate='alt_func_Realestate',
                                          alternate_func_Railroad='alt_func_Railroad', alternate_func_Utility='alt_func_Utility',
                                          alternate_func_income_tax='alternate_func_IncomeTax', alternate_func='rent_and_tax_exemptions'):
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'None'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'
    current_gameboard[schema]['action_params_dict'] = 'None'


    current_gameboard['turns'] = turns
    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.alternate_rent_calc(current_gameboard, alternate_func_Realestate, alternate_func_Railroad, alternate_func_Utility)
    actionNovelty.alternate_tax_calc(current_gameboard, alternate_func_income_tax)
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func)


# Actions13
def auction_hold(current_gameboard, phase='pre_roll', turns=3, auction_hold_amt=100, alternate_func1='auction_holding', alternate_func2='alt_own_or_auction'):
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'None'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'
    current_gameboard[schema]['action_params_dict'] = dict()
    current_gameboard[schema]['action_params_dict']['location'] = 'Location'


    current_gameboard['turns'] = turns
    current_gameboard['auction_hold_amt'] = auction_hold_amt


    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.alternate_own_or_auction(current_gameboard, alternate_func2)
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func1)


# Actions14
def player_with_max_houses_charge_tax(current_gameboard, phase='pre_roll', tax_perc=0.05, max_house_tax=0.10, alternate_func1='alternate_improve_property', alternate_func2='max_house_player_charges_tax'):
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'None'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'
    current_gameboard[schema]['action_params_dict'] = 'None'


    current_gameboard['tax_perc'] = tax_perc
    current_gameboard['max_house_tax'] = max_house_tax
    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.assign_improve_property(current_gameboard, alternate_func1)
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func2)


# Actions15
def player_exchange_properties(current_gameboard, phase='pre_roll', transfer_fee=500, alternate_func="exchange_properties"):
    phase_action = phase + "_arbitrary_action"
    schema = phase_action + "_schema"
    current_gameboard[schema] = dict()
    current_gameboard[schema]['from_player'] = 'Player (self)'
    current_gameboard[schema]['to_player'] = 'Player'
    current_gameboard[schema]['current_gameboard'] = 'current_gameboard'
    current_gameboard[schema]['action_params_dict'] = 'None'


    current_gameboard['transfer_fee'] = transfer_fee
    actionNovelty = novelty_generator_v3.ActionNovelty()
    actionNovelty.assign_arbitrary_action(current_gameboard, phase_action, alternate_func)


#------------------------------------Relations-------------------------------------------

def picked_card_applies_to_all_players(current_gameboard, alternate_func_chance='pick_card_from_chance_temp', alternate_func_cc='pick_card_from_community_chest_temp'):
    """
    Peter's note:
    chance have to move to location that is purchasable, will have bug with player._option_to_buy.
    To keep the simulator same, we just easily use community chest only



    """
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.assign_pick_card_func(current_gameboard, alternate_func_chance, alternate_func_cc)



def reverse_railroad_rent(current_gameboard):
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.change_railroad_rent_calc(current_gameboard)


def utility_owner_pay_rent_instead_of_collect_rent(current_gameboard, alternate_func='process_move_consequences_temp'):
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.reassign_process_move_consequences(current_gameboard, alternate_func)


def property_ownership_based_tax(current_gameboard, alternate_func='alternate_tax_calc_based_on_property_ownership'):
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.change_tax_calc(current_gameboard, alternate_func)


def maximize_rent_based_on_monopolized_color_group(current_gameboard, alternate_func='alternate_rent_calc_based_on_max_rent'):
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.change_rent_calc(current_gameboard, alternate_func)


def reverse_improvements(current_gameboard, alternate_func='reverse_improve_property', alternate_func2 = 'identify_improvement_opportunity_reverse_improvement', alternate_func3 = 'can_asset_be_improved_reverse_improvement', alternate_func4 = 'asset_incremental_improvement_rent_reverse_improvement'):
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.alternate_improve_property(current_gameboard, alternate_func, alternate_func2, alternate_func3, alternate_func4)


def land_on_GO_move_to_nearest_monopoly(current_gameboard, alternate_func='alternate_move_player_on_landing_GO'):
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.alternate_update_player_pos(current_gameboard, alternate_func)


def utility_rent_modifications(current_gameboard, alternate_func_1='alternate_pay_utility_rent', alternate_func_2='alternate_income_tax_payment'):
    """
    utility rent will now be payed to the bank instead of to the player that owns it, thereby the utility owner can
    write off income taxes.
    :param current_gameboard:
    :param alternate_func:
    :return:
    """
    # process_move_consequences modified if the location that the player lands own in a utility loc
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.reassign_process_move_consequences(current_gameboard, alternate_func_1)
    relationsNovelty.change_tax_calc(current_gameboard, alternate_func_2)


def luxury_tax_calculated_differently(current_gameboard, alternate_func='alternate_luxury_tax_calc'):
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.change_tax_calc(current_gameboard, alternate_func)


def tresspassing_fee(current_gameboard, alternate_func='alternate_player_movement'):
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.reassign_process_move_consequences(current_gameboard, alternate_func)


def free_parking_dues(current_gameboard, alternate_func='alternate_free_parking_func'):
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.reassign_process_move_consequences(current_gameboard, alternate_func)


def railroad_loc_leads_to_player_movement(current_gameboard, alternate_func='alternate_railroads_functionality'):
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.reassign_process_move_consequences(current_gameboard, alternate_func)


def GOO_jail_free_card_dues(current_gameboard, alternate_func='alternate_jail_location_func'):
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.reassign_process_move_consequences(current_gameboard, alternate_func)


def last_location_in_monopolized_color_group_taxation(current_gameboard, alternate_func='last_loc_monopoly_tax'):
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.reassign_process_move_consequences(current_gameboard, alternate_func)


def neighbour_tax_while_buying_property(current_gameboard, alternate_func='alternate_buy_property_with_neighbour_tax'):
    relationsNovelty = novelty_generator_v3.RelationsNovelty()
    relationsNovelty.alternate_buy_property(current_gameboard, alternate_func)


#----------------------------------------------Interactions----------------------------------------------------
# Interaction 5
def borrow_money(current_gameboard, alternate_func1='make_borrow_money_offer', alternate_func2='accept_borrow_money_offer', alternate_func3='pay_interest_on_borrowed_money'):
    # interactioni schema
    current_gameboard['interaction_schema'] = dict()
    current_gameboard['interaction_schema']['from_player'] = 'Player (self)'
    current_gameboard['interaction_schema']['to_player'] = 'Player'
    current_gameboard['interaction_schema']['current_gameboard'] = 'current_gameboard'
    current_gameboard['interaction_schema']['interaction_params_dict'] = dict()
    current_gameboard['interaction_schema']['interaction_params_dict']['amount'] = 'Amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['interest_rate'] = 'Perc_of_amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['num_rounds'] = 'Rounds'

    current_gameboard['interaction_id'] = 0
    interactionNovelty = novelty_generator_v3.InteractionNovelty()
    interactionNovelty.assign_make_arbitrary_interaction(current_gameboard, alternate_func1)
    interactionNovelty.assign_accept_arbitrary_interaction(current_gameboard, alternate_func2)
    interactionNovelty.assign_auxiliary_go(current_gameboard, alternate_func3)

# Interaction 12
def borrow_money_with_inflation(current_gameboard, alternate_func1='make_borrow_money_offer', alternate_func2='accept_borrow_money_offer', alternate_func3='pay_interest_on_borrowed_money_with_inflation'):
    # interactioni schema
    current_gameboard['interaction_schema'] = dict()
    current_gameboard['interaction_schema']['from_player'] = 'Player (self)'
    current_gameboard['interaction_schema']['to_player'] = 'Player'
    current_gameboard['interaction_schema']['current_gameboard'] = 'current_gameboard'
    current_gameboard['interaction_schema']['interaction_params_dict'] = dict()
    current_gameboard['interaction_schema']['interaction_params_dict']['amount'] = 'Amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['interest_rate'] = 'Perc_of_amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['num_rounds'] = 'Rounds'

    current_gameboard['interaction_id'] = 0
    interactionNovelty = novelty_generator_v3.InteractionNovelty()
    interactionNovelty.assign_make_arbitrary_interaction(current_gameboard, alternate_func1)
    interactionNovelty.assign_accept_arbitrary_interaction(current_gameboard, alternate_func2)
    interactionNovelty.assign_auxiliary_go(current_gameboard, alternate_func3)

# Interaction 13
def borrow_money_with_restrict1(current_gameboard, alternate_func1='make_borrow_money_offer_with_restrict1', alternate_func2='accept_borrow_money_offer', alternate_func3='pay_interest_on_borrowed_money'):
    # interactioni schema
    current_gameboard['interaction_schema'] = dict()
    current_gameboard['interaction_schema']['from_player'] = 'Player (self)'
    current_gameboard['interaction_schema']['to_player'] = 'Player'
    current_gameboard['interaction_schema']['current_gameboard'] = 'current_gameboard'
    current_gameboard['interaction_schema']['interaction_params_dict'] = dict()
    current_gameboard['interaction_schema']['interaction_params_dict']['amount'] = 'Amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['interest_rate'] = 'Perc_of_amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['num_rounds'] = 'Rounds'

    current_gameboard['interaction_id'] = 0
    interactionNovelty = novelty_generator_v3.InteractionNovelty()
    interactionNovelty.assign_make_arbitrary_interaction(current_gameboard, alternate_func1)
    interactionNovelty.assign_accept_arbitrary_interaction(current_gameboard, alternate_func2)
    interactionNovelty.assign_auxiliary_go(current_gameboard, alternate_func3)

# Interaction 14
def borrow_money_with_restrict2(current_gameboard, alternate_func1='make_borrow_money_offer_with_restrict2', alternate_func2='accept_borrow_money_offer', alternate_func3='pay_interest_on_borrowed_money'):
    # interactioni schema
    current_gameboard['interaction_schema'] = dict()
    current_gameboard['interaction_schema']['from_player'] = 'Player (self)'
    current_gameboard['interaction_schema']['to_player'] = 'Player'
    current_gameboard['interaction_schema']['current_gameboard'] = 'current_gameboard'
    current_gameboard['interaction_schema']['interaction_params_dict'] = dict()
    current_gameboard['interaction_schema']['interaction_params_dict']['amount'] = 'Amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['interest_rate'] = 'Perc_of_amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['num_rounds'] = 'Rounds'

    current_gameboard['interaction_id'] = 0
    interactionNovelty = novelty_generator_v3.InteractionNovelty()
    interactionNovelty.assign_make_arbitrary_interaction(current_gameboard, alternate_func1)
    interactionNovelty.assign_accept_arbitrary_interaction(current_gameboard, alternate_func2)
    interactionNovelty.assign_auxiliary_go(current_gameboard, alternate_func3)

# Interaction 6
def trade_goo_card(current_gameboard, alternate_func1='make_trade_goo_card_offer', alternate_func2='accept_trade_goo_card_offer'):
    # interactioni schema
    current_gameboard['interaction_schema'] = dict()
    current_gameboard['interaction_schema']['from_player'] = 'Player (self)'
    current_gameboard['interaction_schema']['to_player'] = 'Player'
    current_gameboard['interaction_schema']['current_gameboard'] = 'current_gameboard'
    current_gameboard['interaction_schema']['interaction_params_dict'] = dict()
    current_gameboard['interaction_schema']['interaction_params_dict']['amount'] = 'Amount'

    current_gameboard['interaction_id'] = 0
    interactionNovelty = novelty_generator_v3.InteractionNovelty()
    interactionNovelty.assign_make_arbitrary_interaction(current_gameboard, alternate_func1)
    interactionNovelty.assign_accept_arbitrary_interaction(current_gameboard, alternate_func2)

# Interaction 7
def trade_houses_hotels(current_gameboard, alternate_func1='make_trade_house_hotel_offer', alternate_func2='accept_trade_house_hotel_offer'):
    # interactioni schema
    current_gameboard['interaction_schema'] = dict()
    current_gameboard['interaction_schema']['from_player'] = 'Player (self)'
    current_gameboard['interaction_schema']['to_player'] = 'Player'
    current_gameboard['interaction_schema']['current_gameboard'] = 'current_gameboard'
    current_gameboard['interaction_schema']['interaction_params_dict'] = dict()
    current_gameboard['interaction_schema']['interaction_params_dict']['amount'] = 'Amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['house'] = 'Dice_status'
    current_gameboard['interaction_schema']['interaction_params_dict']['hotel'] = 'Dice_status'
    current_gameboard['interaction_schema']['interaction_params_dict']['to_location'] = 'Location'
    current_gameboard['interaction_schema']['interaction_params_dict']['location'] = 'Location'

    current_gameboard['interaction_id'] = 0
    interactionNovelty = novelty_generator_v3.InteractionNovelty()
    interactionNovelty.assign_make_arbitrary_interaction(current_gameboard, alternate_func1)
    interactionNovelty.assign_accept_arbitrary_interaction(current_gameboard, alternate_func2)

# Interaction 8
def futures_contract(current_gameboard, alternate_func1='make_futures_contract', alternate_func2='accept_futures_contract', alternate_func3='transfer_property_on_futures_contract'):
    # interactioni schema
    current_gameboard['interaction_schema'] = dict()
    current_gameboard['interaction_schema']['from_player'] = 'Player (self)'
    current_gameboard['interaction_schema']['to_player'] = 'Player'
    current_gameboard['interaction_schema']['current_gameboard'] = 'current_gameboard'
    current_gameboard['interaction_schema']['interaction_params_dict'] = dict()
    current_gameboard['interaction_schema']['interaction_params_dict']['location'] = 'Location'
    current_gameboard['interaction_schema']['interaction_params_dict']['contract_price'] = 'Amount' # when the contract in signed
    current_gameboard['interaction_schema']['interaction_params_dict']['amount'] = 'Amount' # when transfer the propery, from_player need to give to_player addition fee

    current_gameboard['interaction_id'] = 0
    interactionNovelty = novelty_generator_v3.InteractionNovelty()
    interactionNovelty.assign_make_arbitrary_interaction(current_gameboard, alternate_func1)
    interactionNovelty.assign_accept_arbitrary_interaction(current_gameboard, alternate_func2)
    interactionNovelty.assign_auxiliary_go(current_gameboard, alternate_func3)


# hongyu interaction below
# Interaction 1
def trade_within_incoming_group(current_gameboard, alternate_func='make_trade_offer_within_incoming_group'):
    """
    The novelty make players could only make trade offer to others if they are both in the same incoming group:
        1. rich incoming group: total net worth larger than average of net worth of all players
        2. poor incoming group: total net worth smaller than or equal to average of net worth of all players
    Note: if only two players left, then such incoming group does not exist. Players could make offer properly
    :param current_gameboard:
    :param alternate_func:
    :return:
    """
    interactionsNovelty = novelty_generator_v3.InteractionNovelty()
    interactionsNovelty.alternate_make_trade_offer(current_gameboard, alternate_func)


# Interaction 2
def ask_for_pay_rent_with_installment(current_gameboard,
                                      make_func='ask_for_installment',
                                      accept_func='accept_ask_for_installment',
                                      alternate_func1='move_player_after_die_roll_check_rent_installment',
                                      alternate_func2='process_move_consequences_rent_installment'):
    """
    This novelty would give agents ability to ask for an installment for some rent charge.
    define number of rounds for the contract, if there are rents of some properties larger than high_rent_amount then
    the rents will be paid by installment with installment fee. If number of rounds for the contract become zero then
    the remain rents of all properties will be paid once
    :param current_gameboard:
    :param make_func:
    :param accept_func:
    :param alternate_func1:
    :param alternate_func2:
    :return:
    """
    # transaction id start from 0, once agent create a new interaction, increase by 1
    current_gameboard['default_interaction_id'] = 0

    # schema
    current_gameboard['interaction_schema'] = dict()
    current_gameboard['interaction_schema']['from_player'] = 'Player (self)'
    current_gameboard['interaction_schema']['to_player'] = 'Player'
    current_gameboard['interaction_schema']['current_gameboard'] = 'current_gameboard'
    current_gameboard['interaction_schema']['interaction_params_dict'] = dict()
    current_gameboard['interaction_schema']['interaction_params_dict']['num_rounds_left'] = 'Rounds'
    current_gameboard['interaction_schema']['interaction_params_dict']['installment_fee'] = 'Amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['initial_charge_amount'] = 'Amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['location'] = 'Location'

    # alternate functions
    interactionsNovelty = novelty_generator_v3.InteractionNovelty()
    interactionsNovelty.assign_make_arbitrary_interaction(current_gameboard, make_func)
    interactionsNovelty.assign_accept_arbitrary_interaction(current_gameboard, accept_func)
    # alternate existing functions
    interactionsNovelty.assign_move_player_after_die_roll(current_gameboard, alternate_func1)
    interactionsNovelty.alternate_process_move_consequences(current_gameboard, alternate_func2)

# Interaction 9, based on Interaction 2
def ask_for_pay_rent_with_installment_forever(current_gameboard,
                                      make_func='ask_for_installment_forever',
                                      accept_func='accept_ask_for_installment',
                                      alternate_func1='move_player_after_die_roll_check_rent_installment',
                                      alternate_func2='process_move_consequences_rent_installment'):
    """
    Based on interaction 2, but the contract will never expired
    :param current_gameboard:
    :param make_func:
    :param accept_func:
    :param alternate_func1:
    :param alternate_func2:
    :return:
    """
    # transaction id start from 0, once agent create a new interaction, increase by 1
    current_gameboard['default_interaction_id'] = 0

    # schema
    current_gameboard['interaction_schema'] = dict()
    current_gameboard['interaction_schema']['from_player'] = 'Player (self)'
    current_gameboard['interaction_schema']['to_player'] = 'Player'
    current_gameboard['interaction_schema']['current_gameboard'] = 'current_gameboard'
    current_gameboard['interaction_schema']['interaction_params_dict'] = dict()
    current_gameboard['interaction_schema']['interaction_params_dict']['installment_fee'] = 'Amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['initial_charge_amount'] = 'Amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['location'] = 'Location'

    # alternate functions
    interactionsNovelty = novelty_generator_v3.InteractionNovelty()
    interactionsNovelty.assign_make_arbitrary_interaction(current_gameboard, make_func)
    interactionsNovelty.assign_accept_arbitrary_interaction(current_gameboard, accept_func)
    # alternate existing functions
    interactionsNovelty.assign_move_player_after_die_roll(current_gameboard, alternate_func1)
    interactionsNovelty.alternate_process_move_consequences(current_gameboard, alternate_func2)


# Interaction 10, based on Interaction 2
def make_global_rent_agreement(current_gameboard,
                              make_func='ask_for_global_rent_installment',
                              accept_func='accept_ask_for_installment',
                              alternate_func1='move_player_after_die_roll_check_global_rent_installment',
                              alternate_func2='process_move_consequences_rent_installment'):
    """
    Based on interaction 2, the rent is calculated by all the properties that owned by to_player
    :param current_gameboard:
    :param make_func:
    :param accept_func:
    :param alternate_func1:
    :param alternate_func2:
    :return:
    """
    # transaction id start from 0, once agent create a new interaction, increase by 1
    current_gameboard['default_interaction_id'] = 0

    # schema
    current_gameboard['interaction_schema'] = dict()
    current_gameboard['interaction_schema']['from_player'] = 'Player (self)'
    current_gameboard['interaction_schema']['to_player'] = 'Player'
    current_gameboard['interaction_schema']['current_gameboard'] = 'current_gameboard'
    current_gameboard['interaction_schema']['interaction_params_dict'] = dict()
    current_gameboard['interaction_schema']['interaction_params_dict']['principal_fraction'] = 'Perc_of_amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['interest_rate'] = 'Perc_of_amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['initial_charge_amount'] = 'Amount'

    # alternate functions
    interactionsNovelty = novelty_generator_v3.InteractionNovelty()
    interactionsNovelty.assign_make_arbitrary_interaction(current_gameboard, make_func)
    interactionsNovelty.assign_accept_arbitrary_interaction(current_gameboard, accept_func)
    # alternate existing functions
    interactionsNovelty.assign_move_player_after_die_roll(current_gameboard, alternate_func1)
    interactionsNovelty.alternate_process_move_consequences(current_gameboard, alternate_func2)

# Interaction 15, based on interaction 2
def ask_for_pay_rent_with_installment_with_restriction1(current_gameboard,
                                      make_func='ask_for_installment_with_restriction1',
                                      accept_func='accept_ask_for_installment',
                                      alternate_func1='move_player_after_die_roll_check_rent_installment',
                                      alternate_func2='process_move_consequences_rent_installment'):
    """
    This novelty would give agents ability to ask for an installment for some rent charge.
    define number of rounds for the contract, if there are rents of some properties larger than high_rent_amount then
    the rents will be paid by installment with installment fee. If number of rounds for the contract become zero then
    the remain rents of all properties will be paid once
    :param current_gameboard:
    :param make_func:
    :param accept_func:
    :param alternate_func1:
    :param alternate_func2:
    :return:
    """
    # transaction id start from 0, once agent create a new interaction, increase by 1
    current_gameboard['default_interaction_id'] = 0

    # schema
    current_gameboard['interaction_schema'] = dict()
    current_gameboard['interaction_schema']['from_player'] = 'Player (self)'
    current_gameboard['interaction_schema']['to_player'] = 'Player'
    current_gameboard['interaction_schema']['current_gameboard'] = 'current_gameboard'
    current_gameboard['interaction_schema']['interaction_params_dict'] = dict()
    current_gameboard['interaction_schema']['interaction_params_dict']['num_rounds_left'] = 'Rounds'
    current_gameboard['interaction_schema']['interaction_params_dict']['installment_fee_percentage'] = 'Perc_of_amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['initial_charge_amount'] = 'Amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['location'] = 'Location'

    # alternate functions
    interactionsNovelty = novelty_generator_v3.InteractionNovelty()
    interactionsNovelty.assign_make_arbitrary_interaction(current_gameboard, make_func)
    interactionsNovelty.assign_accept_arbitrary_interaction(current_gameboard, accept_func)
    # alternate existing functions
    interactionsNovelty.assign_move_player_after_die_roll(current_gameboard, alternate_func1)
    interactionsNovelty.alternate_process_move_consequences(current_gameboard, alternate_func2)

# Interaction 3
def rent_aggrement_within_incoming_group(current_gameboard,
                                         make_func='ask_for_rent_agreement',
                                         accept_func='accept_ask_for_rent_agreement',
                                         alternate_func1='process_move_consequences_rent_agreement',
                                         alternate_func2='calculate_and_pay_rent_dues_rent_agreement'):
    """

    :param current_gameboard:
    :param make_func:
    :param accept_func:
    :param alternate_func1:
    :param alternate_func2:
    :return:
    """
    # interaction id default number
    current_gameboard['default_interaction_id'] = 0
    # interactioni schema
    current_gameboard['interaction_schema'] = dict()
    current_gameboard['interaction_schema']['from_player'] = 'Player (self)'
    current_gameboard['interaction_schema']['to_player'] = 'Player'
    current_gameboard['interaction_schema']['current_gameboard'] = 'current_gameboard'
    current_gameboard['interaction_schema']['interaction_params_dict'] = dict()
    current_gameboard['interaction_schema']['interaction_params_dict']['fraction'] = 'Perc_of_amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['num_rounds_left'] = 'Rounds'



    # alternate interaction functions
    interactionsNovelty = novelty_generator_v3.InteractionNovelty()
    interactionsNovelty.assign_make_arbitrary_interaction(current_gameboard, make_func)
    interactionsNovelty.assign_accept_arbitrary_interaction(current_gameboard, accept_func)
    # alternate existing functions
    interactionsNovelty.alternate_process_move_consequences(current_gameboard, alternate_func1)
    interactionsNovelty.alternate_calculate_and_pay_rent_dues(current_gameboard, alternate_func2)


# Interaction 4
def investment_aggrement_with_property(current_gameboard,
                                       make_func='ask_for_invest_property',
                                       accept_func = 'accept_ask_for_invest_property',
                                       alternate_func1='process_move_consequences_invest_contract',
                                       alternate_func2='calculate_and_pay_rent_dues_invest_contract',
                                       alternate_func3='sell_property_invest_remove'):
    """
    from_player and to_player signed a rent agreement
    :param current_gameboard:
    :param make_func:
    :param accept_func:
    :param alternate_func1:
    :param alternate_func2:
    :param alternate_func3:
    :return:
    """
    # interaction id default number
    current_gameboard['default_interaction_id'] = 0
    # interactioni schema
    current_gameboard['interaction_schema'] = dict()
    current_gameboard['interaction_schema']['from_player'] = 'Player (self)'
    current_gameboard['interaction_schema']['to_player'] = 'Player'
    current_gameboard['interaction_schema']['current_gameboard'] = 'current_gameboard'
    current_gameboard['interaction_schema']['interaction_params_dict'] = dict()
    current_gameboard['interaction_schema']['interaction_params_dict']['invest_amount'] = 'Amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['percent'] = 'Perc_of_amount'  # from_player_percent
    current_gameboard['interaction_schema']['interaction_params_dict']['location'] = 'Location'

    # current_gameboard['properties_in_contract'] = set()

    # alternate interaction functions
    interactionsNovelty = novelty_generator_v3.InteractionNovelty()
    interactionsNovelty.assign_make_arbitrary_interaction(current_gameboard, make_func)
    interactionsNovelty.assign_accept_arbitrary_interaction(current_gameboard, accept_func)
    # alternate existing functions
    interactionsNovelty.alternate_process_move_consequences(current_gameboard, alternate_func1)
    interactionsNovelty.alternate_calculate_and_pay_rent_dues(current_gameboard, alternate_func2)
    interactionsNovelty.assign_sell_property(current_gameboard, alternate_func3)

# Interaction 11, based on interaction 4
def investment_aggrement_with_property_with_turn(current_gameboard,
                                       make_func='ask_for_invest_property',
                                       accept_func = 'accept_ask_for_invest_property_with_turns',
                                       alternate_func1='process_move_consequences_invest_contract_with_turns',
                                       alternate_func2='calculate_and_pay_rent_dues_invest_contract_with_turns',
                                       alternate_func3='sell_property_invest_remove'):
    """
    Based on interaction 4, but with num_rounds_left
    :param current_gameboard:
    :param make_func:
    :param accept_func:
    :param alternate_func1:
    :param alternate_func2:
    :param alternate_func3:
    :return:
    """
    # interaction id default number
    current_gameboard['default_interaction_id'] = 0
    # interactioni schema
    current_gameboard['interaction_schema'] = dict()
    current_gameboard['interaction_schema']['from_player'] = 'Player (self)'
    current_gameboard['interaction_schema']['to_player'] = 'Player'
    current_gameboard['interaction_schema']['current_gameboard'] = 'current_gameboard'
    current_gameboard['interaction_schema']['interaction_params_dict'] = dict()
    current_gameboard['interaction_schema']['interaction_params_dict']['invest_amount'] = 'Amount'
    current_gameboard['interaction_schema']['interaction_params_dict']['percent'] = 'Perc_of_amount'  # between 0 and 1
    current_gameboard['interaction_schema']['interaction_params_dict']['num_rounds_left'] = 'Rounds'
    current_gameboard['interaction_schema']['interaction_params_dict']['location'] = 'Location'

    # current_gameboard['properties_in_contract'] = set()

    # alternate interaction functions
    interactionsNovelty = novelty_generator_v3.InteractionNovelty()
    interactionsNovelty.assign_make_arbitrary_interaction(current_gameboard, make_func)
    interactionsNovelty.assign_accept_arbitrary_interaction(current_gameboard, accept_func)
    # alternate existing functions
    interactionsNovelty.alternate_process_move_consequences(current_gameboard, alternate_func1)
    interactionsNovelty.alternate_calculate_and_pay_rent_dues(current_gameboard, alternate_func2)
    interactionsNovelty.assign_sell_property(current_gameboard, alternate_func3)