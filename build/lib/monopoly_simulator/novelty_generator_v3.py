from monopoly_simulator.dice import Dice
from monopoly_simulator.bank import Bank
from monopoly_simulator.player import Player
from monopoly_simulator.location import Location, RealEstateLocation, RailroadLocation, UtilityLocation, ActionLocation
from monopoly_simulator import card_utility_actions
from monopoly_simulator.card_utility_actions import pick_card_from_community_chest
# from monopoly_simulator.novelty_functions_v2 import *
from monopoly_simulator.novelty_functions_v3 import *
from monopoly_simulator import action_choices
from monopoly_simulator import player
import copy
import sys
import logging
import importlib

from monopoly_simulator.agent_helper_functions_v2 import *
from monopoly_simulator import agent_helper_functions_v2 as agent_helper_functions

"""
# for reinitilize 
import json
import location
from monopoly_simulator.card_utility_actions import *
"""
logger = logging.getLogger('monopoly_simulator.logging_info.novelty_gen')

"""
The novelty methods in here should be called after an initial game board has been set up, but before simulate has
been called within gameplay. It is unsafe to introduce novelty in the middle of a 'game'. The novelties should
only operate at the tournament level and be introduced prior to game instance simulation.

This generator should be used for the Month 6 SAIL-ON evals.

The consistency_check function should be called after all novelties have been generated. If the function finds problems
it will print them out and then raise an Exception. Otherwise, you're good to start using the updated gameboard
to start playing the game.
"""

class Novelty(object):
    def __init__(self):
        pass


class ClassNovelty(Novelty):
    def __init__(self):
        super().__init__()

class AttributeNovelty(Novelty):
    def __init__(self):
        super().__init__()


class RepresentationNovelty(Novelty):
    def __init__(self):
        super().__init__()


class InanimateAttributeNovelty(AttributeNovelty):
    def __init__(self):
        super().__init__()


    def map_property_set_to_color(self, current_gameboard, property_set, new_color):
        """

        :param current_gameboard: the current gameboard. current_gameboard['color_assets'] may get modified, along
        with the color attribute of individual location instances in property_set
        :param property_set: a set of location instances
        :param new_color: the new color that should be assigned to each property in the property set
        :return: None
        """

        for p in property_set:
            p.color = new_color

        if new_color not in current_gameboard['color_assets']:
            current_gameboard['color_assets'][new_color] = set()

        # now we need to repair the color_assets
        for color, loc_set in current_gameboard['color_assets'].items():
            loc_list = list(loc_set) # to avoid iterating over set while modifying it
            for loc in loc_list:
                if loc.color != color:
                    loc_set.remove(loc)
                current_gameboard['color_assets'][loc.color].add(loc)


    def map_property_to_color(self, current_gameboard, property, new_color):
        """

        :param current_gameboard: the current gameboard. current_gameboard['color_assets'] may get modified, along
        with the color attribute of the individual location instance represented by property
        :param property: a location instance
        :param new_color: the new color that should be assigned to each property in the property set
        :return: None
        """
        p_set = set()
        p_set.add(property)
        self.map_property_set_to_color(current_gameboard, p_set, new_color)

    def exchange_colors_between_properties(self, current_gameboard, property_1, property_2):
        """

        :param current_gameboard: the current gameboard. current_gameboard['color_assets'] may get modified, along
        with the color attribute of the individual location instancesrepresented by property_1 and property_2
        :param property_1: location instance
        :param property_2: location instance
        :return: None
        """
        p_set1 = set()
        p_set1.add(property_1)
        p_set2 = set()
        p_set2.add(property_2)
        color1 = property_1.color
        color2 = property_2.color
        self.map_property_set_to_color(current_gameboard, p_set1, color2)
        self.map_property_set_to_color(current_gameboard, p_set2, color1)

    def tax_novelty(self, tax_location, new_tax):
        """
        Change tax amount either for income or luxury tax
        :param tax_location: An instance of TaxLocation (which is either income or luxury tax)
        :param new_tax: the new amount due at the tax location
        :return: None
        """
        tax_location.amount_due = new_tax


    def rent_novelty(self, location, rent_dict):
        """
        Modify rents in a location.
        :param location: A location instance. Make sure it is from the current gameboard, and not some kind of copy,
        to introduce the novelty at the game level.
        :param rent_dict: A dictionary containing the rent attribute (e.g., rent_1_house, rent_hotel etc.) and the new
        values for those attributes. Any values not being changed should not be included in the dictionary.
        :return: None
        """
        for k, v in rent_dict.items():
            setattr(location, k, v)

        if location.loc_class == 'real_estate':
            location._house_rent_dict[1] = location.rent_1_house
            location._house_rent_dict[2] = location.rent_2_houses
            location._house_rent_dict[3] = location.rent_3_houses
            location._house_rent_dict[4] = location.rent_4_houses


    def mortgage_novelty(self, location, new_mortgage):
        """
        Modify mortgage in a location.
        :param location: A location instance. Make sure it is from the current gameboard, and not some kind of copy,
        to introduce the novelty at the game level.
        :param new_mortgage: the new mortgage amount
        :return: None
        """
        location.mortgage = new_mortgage

    def price_novelty(self, location, new_price):
        """
        Modify mortgage in a location.
        :param location: A location instance. Make sure it is from the current gameboard, and not some kind of copy,
        to introduce the novelty at the game level.
        :param new_price: the new price
        :return: None
        """
        location.price = new_price

    def price_per_house_novelty(self, location, new_price_per_house):
        """
        Modify mortgage in a location.
        :param location: A location instance. Make sure it is from the current gameboard, and not some kind of copy,
        to introduce the novelty at the game level.
        :param new_price_per_house: the new price/house amount
        :return: None
        """
        location.price_per_house = new_price_per_house


    def card_amount_novelty(self, current_gameboard, community_chest_card_amounts=None, chance_card_amounts=None):
        """
        Modify amounts on some cards
        :param community_chest_card_amounts: A dictionary with the name of the community chest card as key, and the new amount as value.
        if a card is not getting changed, it should not be here.
        :param chance_card_amounts:  A dictionary with the chance card as key, and the new amount as value.
        if a card is not getting changed, it should not be here.
        :return: None
        """
        if community_chest_card_amounts:
            for card in current_gameboard['community_chest_cards']:
                if card.name in community_chest_card_amounts:
                    card.amount = community_chest_card_amounts[card.name]

            for card_name, amt in community_chest_card_amounts.items():
                current_gameboard['community_chest_card_objects'][card_name].amount = amt

        if chance_card_amounts:
            for card in current_gameboard['chance_cards']:
                if card.name in chance_card_amounts:
                    card.amount = chance_card_amounts[card.name]

            for card_name, amt in chance_card_amounts.items():
                current_gameboard['chance_card_objects'][card_name].amount = amt


    def card_destination_novelty(self, current_gameboard, community_chest_card_destinations, chance_card_destinations):
        """
        Modify destinations on some cards
        :param community_chest_card_destinations: A dictionary with the name of the community chest card as key, and the new destination as value.
        if a card is not getting changed, it should not be here.
        :param chance_card_destinations:  A dictionary with the chance card as key, and the new destination as value.
        if a card is not getting changed, it should not be here.
        :return: None
        """
        if community_chest_card_destinations:
            for card in current_gameboard['community_chest_cards']:
                if card.name in community_chest_card_destinations:
                    card.destination = community_chest_card_destinations[card.name]

            for card_name, dest in community_chest_card_destinations.items():
                current_gameboard['community_chest_card_objects'][card_name].destination = dest

        if chance_card_destinations:
            for card in current_gameboard['chance_cards']:
                if card.name in chance_card_destinations:
                    card.destination = chance_card_destinations[card.name]

            for card_name, dest in chance_card_destinations.items():
                current_gameboard['chance_card_objects'][card_name].destination = dest

    def go_increment_novelty(self, current_gameboard, new_go_increment):
        """

        :param current_gameboard:
        :param new_go_increment:
        :return:
        """
        current_gameboard['go_increment'] = new_go_increment

    def player_starting_cash_novelty(self, player, new_start_cash):
        """

        :param player:
        :param new_start_cash:
        :return:
        """
        player.current_cash = float(new_start_cash)

    def bank_attribute_novelty(self, current_gameboard, attribute, new_value):
        """

        :param current_gameboard:
        :param new_hotel_limit:
        :return:
        """
        if attribute == 'mortgage_percentage':
            current_gameboard['bank'].mortgage_percentage = new_value
        elif attribute == 'total_houses':
            current_gameboard['bank'].total_houses = new_value
        elif attribute == 'total_hotels':
            current_gameboard['bank'].total_hotels = new_value
        elif attribute == 'total_cash_with_bank':
            current_gameboard['bank'].total_cash_with_bank = new_value
        elif attribute == 'property_sell_percentage':
            current_gameboard['bank'].property_sell_percentage = new_value
        elif attribute == 'house_sell_percentage':
            current_gameboard['bank'].house_sell_percentage = new_value
        elif attribute == 'hotel_sell_percentage':
            current_gameboard['bank'].hotel_sell_percentage = new_value
        elif attribute == 'jail_fine':
            current_gameboard['bank'].jail_fine = new_value
        elif attribute == 'monopolized_property_rent_factor':
            current_gameboard['bank'].monopolized_property_rent_factor = new_value
        elif attribute == 'house_limit_before_hotel':
            current_gameboard['bank'].house_limit_before_hotel = new_value
        elif attribute == 'hotel_limit':
            current_gameboard['bank'].hotel_limit = new_value


class ContingentAttributeNovelty(AttributeNovelty):
    def __init__(self):
        super().__init__()

    def change_mortgage_percentage(self, current_gameboard, new_percentage):
        current_gameboard['bank'].mortgage_percentage = new_percentage

    def percent_of_total_mortgage_outstanding(self, current_gameboard, new_percentage):
        current_gameboard['bank'].mortgage_percentage = new_percentage
        current_gameboard['bank'].total_mortgage_rule = True

    def auxiliary_go(self, current_gameboard, auxiliary_go_func):
        current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], auxiliary_go_func)

    def dynamic_mortgage(self, current_gameboard, alternate_func):
        for v in current_gameboard['location_sequence']:
            v.calculate_mortgage_owed = getattr(sys.modules[__name__], alternate_func)


class NumberClassNovelty(ClassNovelty):
    def __init__(self):
        super().__init__()

    def die_novelty(self, current_gameboard, die_count, die_state_vector):
        """
        Introduce sub-level novelty (class/number) for dice.
        :param current_gameboard: The current gameboard dict. Note that this dict will be modified.
        :param die_count: number of dice
        :param die_state_vector: A list of lists, where each inner list represents the die state for each dice
        :return: None
        """
        if len(die_state_vector) != die_count:
            logger.error('die states are unequal to die count. Raising exception...')
            logger.error("Exception")
            raise Exception

        current_gameboard['dies'] = list() # wipe out what was there before.
        die_sequence = []
        for i in range(0, die_count):
            current_gameboard['dies'].append(Dice(die_state_vector[i]))
            die_sequence.append([])
        current_gameboard['die_sequence'] = die_sequence

    def card_novelty(self, current_gameboard, community_chest_cards_num, chance_cards_num):
        """

        :param current_gameboard: current_gameboard['chance_cards'] and current_gameboard['community_chest_cards'] will
        both be modified. However, current_gameboard['chance_card_objects'] and current_gameboard['community_chest_card_objects']
        will stay as it is.
        :param community_chest_cards_num: a dict where the key is the card's name, and the value is the num. You must pass in the
        complete description (of the cards and nums), not just
        cards for which you're changing the num value, since we will re-initialize and populate current_gameboard['community_chest_cards']
        and current_gameboard['chance_cards'] from scratch.
        :param chance_cards_num: a dict where the key is the card's name, and the value is the num
        :return: None
        """

        current_gameboard['community_chest_cards'] = set()
        for card_name, num in community_chest_cards_num.items():
            card = current_gameboard['community_chest_card_objects'][card_name]
            for i in range(0, num):
                current_gameboard['community_chest_cards'].add(copy.deepcopy(card))

        current_gameboard['chance_cards'] = set()
        for card_name, num in chance_cards_num.items():
            card = current_gameboard['chance_card_objects'][card_name]
            for i in range(0, num):
                current_gameboard['chance_cards'].add(copy.deepcopy(card))

    def jail_entry_novelty(self, current_gameboard, alternate_func):
        card_utility_actions._set_send_to_jail = getattr(sys.modules[__name__], alternate_func)


    def railroad_novelty(self, current_gameboard, alternate_func):
        """
        2 of the pre-existing railroads get assigned to a new class of railroads,
        ie, the railroad dues for these 2 railroads are calculated differently
        :param current_gameboard:
        :param new_price:
        :param new_mortgage:
        :param alternate_func:
        :return:
        """
        RailroadLocation.calculate_railroad_dues = getattr(sys.modules[__name__], alternate_func)



class TypeClassNovelty(ClassNovelty):
    def __init__(self):
        super().__init__()

    def die_novelty(self, current_gameboard, die_state_distribution_vector, die_type_vector):
        """
        Introduce sub-level novelty (class/type) for dice.
        :param current_gameboard: The current gameboard dict. Note that this dict will be modified.
        :param die_state_distribution_vector: list of die_state_distributions
        :param die_type_vector: list of die_types
        :return: None
        """
        if len(die_state_distribution_vector) != len(die_type_vector):
            logger.error('die state distributions are unequal to die types. Raising exception...')
            logger.error("Exception")
            raise Exception
        if len(die_state_distribution_vector) != len(current_gameboard['dies']):
            logger.error('die state distributions and die types are unequal to number of dies in board. Raising exception...')
            logger.error("Exception")
            raise Exception

        for i in range(0, len(die_state_distribution_vector)):
            current_gameboard['dies'][i].die_state_distribution = die_state_distribution_vector[i]
            current_gameboard['dies'][i].die_type = die_type_vector[i]

        for die in current_gameboard['dies']:
            if die.die_type == 'even_only':
                new_die_state = list()
                for i in die.die_state:
                    if i%2 == 0:
                        new_die_state.append(i)
                die.die_state = new_die_state
            elif die.die_type == 'odd_only':
                new_die_state = list()
                for i in die.die_state:
                    if i % 2 != 0:
                        new_die_state.append(i)
                die.die_state = new_die_state

    def card_novelty(self, current_gameboard, community_chest_cards_contingency, chance_cards_contingency):
        """

        :param current_gameboard: current_gameboard['chance_cards'] and current_gameboard['community_chest_cards'] will
        both be modified. However, current_gameboard['chance_card_objects'] and current_gameboard['community_chest_card_objects']
        will stay as it is.
        :param community_chest_cards_contingency: a dict where the key is the card's name, and the value is a contingency function
        from novelty_functions. If there is no change in a card's contingency function, do not include it in this dict.
        :param chance_cards_contingency: a dict where the key is the card's name, and the value is a contingency function
        from novelty_functions. If there is no change in a card's contingency function, do not include it in this dict.
        :return: None
        """
        for card in current_gameboard['chance_cards']:
            if card.name in chance_cards_contingency and hasattr(card, 'contingency'):
                card.contingency = getattr(sys.modules[__name__], chance_cards_contingency[card.name])

        for card in current_gameboard['community_chest_cards']:
            if card.name in community_chest_cards_contingency and hasattr(card, 'contingency'):
                card.contingency = getattr(sys.modules[__name__], community_chest_cards_contingency[card.name])

    def auction_novelty(self, current_gameboard, alternate_auction_func):
        """
        Assigns the Bank auction method to a novel auction function that charges the player who won the auction an extra transaction amount.
        This function is defined inside the novelty_function.py file
        :param current_gameboard:
        :return:
        """
        Bank.auction = getattr(sys.modules[__name__], alternate_auction_func)

    def forbid_improvement(self, current_gameboard, alternate_improvement_possible_func):
        """
        assigns imrpovement function of bank to another novel function that checks for properties that are forbidden from improvements.
        :param current_gameboard:
        :param alternate_improvement_possible_func:
        :return:
        """
        # Note: assign the new novelty fuction pointer to the class method and not the instance method,
        # else self cannot be used when the object tried to access the function, "self" wont work then.
        # Now, in this case, you can retain the same function arguments, keeping the self and current_gameboard['self']
        # gets passed into self when the function is called
        Bank.improvement_possible = getattr(sys.modules[__name__], alternate_improvement_possible_func)

    def alternate_move_player_after_die_roll(self, current_gamboard, alternate_move_player_func):
        """

        :param current_gamboard:
        :param alternate_move_player_func:
        :return:
        """
        current_gamboard['move_player_after_die_roll'] = getattr(sys.modules[__name__], alternate_move_player_func)

    def auxiliary_check_assignment(self, current_gameboard, alternate_action_during_movement):
        """

        :param current_gameboard:
        :param alternate_action_during_movement:
        :return:
        """
        current_gameboard['auxiliary_check'] = getattr(sys.modules[__name__], alternate_action_during_movement)

    def auxiliary_go(self, current_gameboard, auxiliary_go_func):
        """

        :param current_gameboard:
        :param auxiliary_go_func:
        :return:
        """
        current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], auxiliary_go_func)

    def auxiliary_post_roll(self, current_gameboard, alternate_func):
        current_gameboard['auxiliary_before_post_roll_check'] = getattr(sys.modules[__name__], alternate_func)

    def alternate_tax_calc(self, current_gameboard, alternate_func):
        TaxLocation.calculate_tax = getattr(sys.modules[__name__], alternate_func)

    def assign_compute_postroll(self, current_gameboard, alternate_func):
        Player.compute_allowable_post_roll_actions = getattr(sys.modules[__name__], alternate_func)

    def handle_negative_cash_balance_differently(self, current_gameboard, alternate_func):
        Player.handle_negative_cash_balance = getattr(sys.modules[__name__], alternate_func)

    def assign_pay_jail_fine(self, current_gameboard, alternate_func):
        action_choices.pay_jail_fine = getattr(sys.modules[__name__], alternate_func)

    def alternate_update_asset_owner(self, current_gameboard, alternate_func):
        Location.update_asset_owner = getattr(sys.modules[__name__], alternate_func)


class SpatialRepresentationNovelty(RepresentationNovelty):
    def __init__(self):
        super().__init__()

    def color_reordering(self, current_gameboard, relative_location_list, color):
        """
        Currently, we are not checking if all the locations in relative location list correspond to the same color ('color') but
        this is a safety check that may get imposed later.
        :param current_gameboard: current_gameboard['location_sequence'], current_gameboard['location_objects'] may get modified.
        :param relative_location_list: a list that only contains properties of the same color, and that indicates the new relative
         positions. For example, ['Boardwalk', 'Park Place'] indicates that boardwalk should now come first in the board among its color set, which
         will effectively reverse boardwalk and park place.
        :return: None
        """
        new_location_sequence_dict = dict()
        new_location_sequence = list()
        count = 0
        for loc in current_gameboard['location_sequence']:
            new_location_sequence.append(loc.name)
            if loc.name in relative_location_list:
                new_location_sequence_dict[loc.name] = relative_location_list[count]
                count += 1
        if count != len(relative_location_list):
            logger.error("Exception") # the number of items in the dictionary should correspond to the length of the list, otherwise something is going wrong
            raise Exception

        for index in range(0, len(new_location_sequence)):
            loc = new_location_sequence[index]
            if loc in new_location_sequence_dict:
                new_location_sequence[index] = new_location_sequence_dict[loc]

        if len(set(new_location_sequence)) != len(new_location_sequence):
            logger.error("Exception") # somehow we've ended up introducing duplicate names in the list.
            # raise Exception

        self.global_reordering(current_gameboard, new_location_sequence)


    def global_reordering(self, current_gameboard, new_location_sequence):
        """

        :param current_gameboard: current_gameboard['location_sequence'], current_gameboard['location_objects'], current_gameboard['go_position'],
        current_gameboard['jail_position'], current_gameboard['railroad_positions']
        and current_gameboard['utility_positions'] may all potentially get modified.
        :param new_location_sequence: a list of location names. Note that this is not a list of location objects
        :return: None
        """
        current_gameboard['railroad_positions'] = list()
        current_gameboard['utility_positions'] = list()

        for index, loc_name in enumerate(new_location_sequence):
            diff = current_gameboard['location_objects'][loc_name].end_position-current_gameboard['location_objects'][loc_name].start_position
            current_gameboard['location_objects'][loc_name].start_position = index
            current_gameboard['location_objects'][loc_name].end_position = index+diff
            current_gameboard['location_sequence'][index] = current_gameboard['location_objects'][loc_name]
            if current_gameboard['location_objects'][loc_name].loc_class == 'railroad':
                for i in range(index, index+diff):
                    current_gameboard['railroad_positions'].append(i)

            elif current_gameboard['location_objects'][loc_name].loc_class == 'utility':
                for i in range(index, index + diff):
                    current_gameboard['utility_positions'].append(i)

            elif current_gameboard['location_objects'][loc_name].name == 'In Jail/Just Visiting':
                current_gameboard['jail_position'] = index


            if current_gameboard['location_objects'][loc_name].name == 'Go':
                current_gameboard['go_position'] = index

    def alternate_move_player_after_die_roll(self, current_gamboard, alternate_move_player_func):
        """

        :param current_gamboard:
        :param alternate_move_player_func:
        :return:
        """
        current_gamboard['move_player_after_die_roll'] = getattr(sys.modules[__name__], alternate_move_player_func)

    def rent_novelty(self, current_gamboard, player, alternate_rent_calc_func_dict):
        """

        :param current_gamboard:
        :param alternate_rent_func:
        :return:
        """
        # Note: assign the new novelty function pointer to the class method and not the instance method,
        # else self cannot be used when the object tried to access the function, "self" wont work then.
        # Now, in this case, you can retain the same function arguments, keeping the self and current_gameboard['players'][<player object>]
        # gets passed into self when the function is called
        RealEstateLocation.calculate_rent = getattr(sys.modules[__name__], alternate_rent_calc_func_dict['RealEstate'])
        RailroadLocation.calculate_railroad_dues = getattr(sys.modules[__name__], alternate_rent_calc_func_dict['Railroad'])
        UtilityLocation.calculate_utility_dues = getattr(sys.modules[__name__], alternate_rent_calc_func_dict['Utility'])


    def auxiliary_check_assignment(self, current_gameboard, alternate_action_during_movement):
        """

        :param current_gameboard:
        :param alternate_action_during_movement:
        :return:
        """
        current_gameboard['auxiliary_check'] = getattr(sys.modules[__name__], alternate_action_during_movement)


class GranularityRepresentationNovelty(RepresentationNovelty):
    def __init__(self):
        super().__init__()

    def granularity_novelty(self, current_gameboard, location, new_end_position):
        """
        current_gameboard['location_sequence'], current_gameboard['location_objects'], current_gameboard['go_position'],
        current_gameboard['jail_position'], current_gameboard['railroad_positions']
        and current_gameboard['utility_positions'] may all potentially get modified. current_gameboard['location_objects']
        gets modified not only via location, which will change its end_position field but also via the start
        :param current_gameboard:
        :param location:
        :param new_end_position:
        :return:
        """

        location.end_position = new_end_position
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

                if (loc.name!=location.name):
                    break

            loc.start_position = new_start_position
            loc.end_position = new_end_position
            forbidden_loc_names.add(loc.name)
        current_gameboard['location_sequence'] = new_location_sequence

    def failure_code_novelty(self, current_gameboard, alternate_func):
        assign_failure_code = getattr(sys.modules[__name__], alternate_func)
        assign_failure_code(current_gameboard)

    def property_distribution_novelty(self, current_gameboard, alternate_func):
        randomly_distr_prop_among_player = getattr(sys.modules[__name__], alternate_func)
        randomly_distr_prop_among_player(current_gameboard)

    def game_termination_func_novelty(self, current_gameboard, alternate_func):
        card_utility_actions.check_for_game_termination = getattr(sys.modules[__name__], alternate_func)

    def partial_observability(self, current_gameboard, alternate_func_1, alternate_func_2):
        current_gameboard['auxiliary_before_pre_roll_check'] = getattr(sys.modules[__name__], alternate_func_1)
        current_gameboard['auxiliary_after_pre_roll_check'] = getattr(sys.modules[__name__], alternate_func_2)

        current_gameboard['auxiliary_before_out_of_turn_check'] = getattr(sys.modules[__name__], alternate_func_1)
        current_gameboard['auxiliary_after_out_of_turn_check'] = getattr(sys.modules[__name__], alternate_func_2)

        current_gameboard['auxiliary_before_post_roll_check'] = getattr(sys.modules[__name__], alternate_func_1)
        current_gameboard['auxiliary_after_post_roll_check'] = getattr(sys.modules[__name__], alternate_func_2)


#-------------------------------------------Phase 2 Novelties---------------------------------------------

#----------------------------------------------Actions----------------------------------------------------


class ActionNovelty(Novelty):
    def __init__(self):
        super().__init__()

    def assign_arbitrary_action(self, current_gameboard, phase, alternate_func):
        """
        phase has to be of the format 'pre_roll', 'post_roll', 'out_of_turn'
        :param current_gameboard:
        :param phase:
        :param alternate_func:
        :return:
        """
        # phase_func = phase + "_arbitrary_action"
        setattr(action_choices, phase, getattr(sys.modules[__name__], alternate_func))
        Player._populate_param_dict = getattr(sys.modules[__name__], 'populate_param_dict_with_location_check')


    def assign_dummy_action(self, current_gameboard, alternate_func):
        act = getattr(action_choices, "pre_roll_arbitrary_action")
        print(act)
        action_choices.dummy_action = getattr(sys.modules[__name__], alternate_func)

    def assign_set_currently_in_jail_to_false(self, current_gameboard, alternate_func):
        card_utility_actions.set_currently_in_jail_to_false = getattr(sys.modules[__name__], alternate_func)

    def assign_calculate_and_pay_rent_dues(self, current_gameboard, alternate_func):
        Player.calculate_and_pay_rent_dues = getattr(sys.modules[__name__], alternate_func)

    def assign_die_roll(self, current_gameboard, alternate_func):
        action_choices.roll_die = getattr(sys.modules[__name__], alternate_func)

    def alternate_rent_calc(self, current_gameboard, alternate_func_realestate, alternate_func_railroad, alternate_func_utility):
        RealEstateLocation.calculate_rent = getattr(sys.modules[__name__], alternate_func_realestate)
        RailroadLocation.calculate_railroad_dues = getattr(sys.modules[__name__], alternate_func_railroad)
        UtilityLocation.calculate_utility_dues = getattr(sys.modules[__name__], alternate_func_utility)

    def alternate_tax_calc(self, current_gameboard, alternate_func):
        TaxLocation.calculate_tax = getattr(sys.modules[__name__], alternate_func)

    def alternate_own_or_auction(self, current_gameboard, alternate_func):
        Player._own_or_auction = getattr(sys.modules[__name__], alternate_func)

    def assign_improve_property(self, current_gameboard, alternate_func):
        action_choices.improve_property = getattr(sys.modules[__name__], alternate_func)

    def assign_free_mortgage(self, current_gameboard, alternate_func):
        action_choices.free_mortgage = getattr(sys.modules[__name__], alternate_func)

    def alternate_real_estate_rent_calc(self, current_gameboard, alternate_func_realestate):
        RealEstateLocation.calculate_rent = getattr(sys.modules[__name__], alternate_func_realestate)

    def bank_attribute_novelty(self, current_gameboard, attribute, new_value):
        """

        :param current_gameboard:
        :param new_hotel_limit:
        :return:
        """
        if attribute == 'mortgage_percentage':
            current_gameboard['bank'].mortgage_percentage = new_value
        elif attribute == 'total_houses':
            current_gameboard['bank'].total_houses = new_value
        elif attribute == 'total_hotels':
            current_gameboard['bank'].total_hotels = new_value
        elif attribute == 'total_cash_with_bank':
            current_gameboard['bank'].total_cash_with_bank = float(new_value)
        elif attribute == 'property_sell_percentage':
            current_gameboard['bank'].property_sell_percentage = new_value
        elif attribute == 'house_sell_percentage':
            current_gameboard['bank'].house_sell_percentage = new_value
        elif attribute == 'hotel_sell_percentage':
            current_gameboard['bank'].hotel_sell_percentage = new_value
        elif attribute == 'jail_fine':
            current_gameboard['bank'].jail_fine = float(new_value)
        elif attribute == 'monopolized_property_rent_factor':
            current_gameboard['bank'].monopolized_property_rent_factor = float(new_value)
        elif attribute == 'house_limit_before_hotel':
            current_gameboard['bank'].house_limit_before_hotel = new_value
        elif attribute == 'hotel_limit':
            current_gameboard['bank'].hotel_limit = new_value


class RelationsNovelty(Novelty):
    def __init__(self):
        super().__init__()
    """
    # Peter added
    def _reinitialize_game_elements(self, current_gameboard, game_schema_file_path='../monopoly_game_schema_v1-2.json'):
        # reinitialize_game_elements
        game_schema = json.load(open(game_schema_file_path, 'r'))
        for l in game_schema['locations']['location_states']:
            if l['loc_class'] == 'action':
                action_args = l.copy()
                action_args['perform_action'] = getattr(sys.modules[__name__], l['perform_action'])
                # location_objects[l['name']] = location.ActionLocation(**action_args)
                current_gameboard['location_objects'][l['name']] = location.ActionLocation(**action_args)
        return (current_gameboard)
   
    def assign_pick_card_func(self, current_gameboard, alternate_func_chance, alternate_func_cc):
        #card_utility_actions.pick_card_from_chance = getattr(sys.modules[__name__], alternate_func_chance)
        #card_utility_actions.pick_card_from_community_chest = getattr(sys.modules[__name__], alternate_func_cc)
        pick_card_from_chance = getattr(sys.modules[__name__], alternate_func_chance)
        pick_card_from_community_chest = getattr(sys.modules[__name__], alternate_func_cc)
        self._reinitialize_game_elements(current_gameboard)

    """
    def assign_pick_card_func(self, current_gameboard, alternate_func_chance, alternate_func_cc):
        #card_utility_actions.pick_card_from_chance = getattr(sys.modules[__name__], alternate_func_chance)
        global pick_card_from_community_chest
        from card_utility_actions import pick_card_from_community_chest
        #import inspect
        #import os
        #print(os.path.abspath(inspect.getfile(pick_card_from_community_chest)))
        #print(pick_card_from_community_chest.__name__)
        pick_card_from_community_chest = getattr(sys.modules[__name__], alternate_func_cc)
        #print(os.path.abspath(inspect.getfile(pick_card_from_community_chest)))
        pick_card_from_community_chest.__name__ = 'pick_card_from_community_chest'
        #print(pick_card_from_community_chest.__name__)

        #"""
        location_objects = current_gameboard['location_objects'].copy()
        for loc in current_gameboard['location_objects']:
            
            # if loc == 'Chance':
            #    action_args = copy.deepcopy(location_objects[loc])
            #    setattr(action_args, 'perform_action', getattr(sys.modules[__name__], alternate_func_chance))
            #    location_objects[loc] = action_args
            
            if loc == 'Community Chest':
                action_args = copy.deepcopy(location_objects[loc])
                setattr(action_args, 'perform_action', getattr(sys.modules[__name__], 'pick_card_from_community_chest'))
                location_objects[loc] = action_args

        for idx, ls in enumerate(current_gameboard['location_sequence']):
            if ls.name == 'Chance' or ls.name == 'Community Chest':
                current_gameboard['location_sequence'][idx] = location_objects[ls.name]
        current_gameboard['location_objects'] = location_objects
        #"""

    def change_railroad_rent_calc(self, current_gameboard):
        logger.debug("Reversing railroad rents")
        for loc in current_gameboard['location_sequence']:
            if loc.loc_class == 'railroad':
                objt = dict()
                objt[1] = 200
                objt[2] = 100
                objt[3] = 50
                objt[4] = 25
                loc._railroad_dues = objt

    def reassign_process_move_consequences(self, current_gameboard, alternate_func):
        Player.process_move_consequences = getattr(sys.modules[__name__], alternate_func)

    def change_tax_calc(self, current_gameboard, alternate_func):
        TaxLocation.calculate_tax = getattr(sys.modules[__name__], alternate_func)

    def change_rent_calc(self, current_gameboard, alternate_func):
        RealEstateLocation.calculate_rent = getattr(sys.modules[__name__], alternate_func)

    def alternate_improve_property(self, current_gameboard, alternate_func, alternate_func2, alternate_func3, alternate_func4):
        action_choices.improve_property = getattr(sys.modules[__name__], alternate_func)
        agent_helper_functions.identify_improvement_opportunity = getattr(sys.modules[__name__], alternate_func2)
        agent_helper_functions.can_asset_be_improved = getattr(sys.modules[__name__], alternate_func3)
        agent_helper_functions.asset_incremental_improvement_rent = getattr(sys.modules[__name__], alternate_func4)


    def alternate_update_player_pos(self, current_gameboard, alternate_func):
        Player.update_player_position = getattr(sys.modules[__name__], alternate_func)

    def alternate_buy_property(self, current_gameboard, alternate_func):
        action_choices.buy_property = getattr(sys.modules[__name__], alternate_func)


#----------------------------------------------Interactions----------------------------------------------------

class InteractionNovelty(Novelty):
    def __init__(self):
        super().__init__()
        # added by Peter


    def assign_make_arbitrary_interaction(self, current_gameboard, alternate_func):
        """
        phase has to be of the format 'pre_roll', 'post_roll', 'out_of_turn'
        :param current_gameboard:
        :param phase:
        :param alternate_func:
        :return:
        """
        # phase_func = phase + "_arbitrary_action"
        # setattr(action_choices, phase, getattr(sys.modules[__name__], alternate_func))
        action_choices.make_arbitrary_interaction = getattr(sys.modules[__name__], alternate_func)
        Player._populate_param_dict = getattr(sys.modules[__name__], 'populate_param_dict_with_location_check')

    def assign_accept_arbitrary_interaction(self, current_gameboard, alternate_func):
        """
        phase has to be of the format 'pre_roll', 'post_roll', 'out_of_turn'
        :param current_gameboard:
        :param phase:
        :param alternate_func:
        :return:
        """
        # phase_func = phase + "_arbitrary_action"
        # setattr(action_choices, phase, getattr(sys.modules[__name__], alternate_func))
        action_choices.accept_arbitrary_interaction = getattr(sys.modules[__name__], alternate_func)

    def assign_auxiliary_go(self, current_gameboard, auxiliary_go_func):
        current_gameboard['auxiliary_check_for_go'] = getattr(sys.modules[__name__], auxiliary_go_func)


    # hongyu below
    def alternate_make_trade_offer(self, current_gameboard, alternate_func):
        """
        alternate make_trade_offer func in the action_choices file
        :param self:
        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        action_choices.make_trade_offer = getattr(sys.modules[__name__], alternate_func)

    def alternate_process_move_consequences(self, current_gameboard, alternate_func):
        """

        :param self:
        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        Player.process_move_consequences = getattr(sys.modules[__name__], alternate_func)

    def alternate_calculate_and_pay_rent_dues(self, current_gameboard, alternate_func):
        """

        :param self:
        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        Player.calculate_and_pay_rent_dues = getattr(sys.modules[__name__], alternate_func)

    def assign_sell_property(self, current_gameboard, alternate_func):
        """

        :param self:
        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        action_choices.sell_property = getattr(sys.modules[__name__], alternate_func)

    def assign_move_player_after_die_roll(self, current_gameboard, alternate_func):
        """

        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        current_gameboard['move_player_after_die_roll'] = getattr(sys.modules[__name__], alternate_func)
        card_utility_actions.move_player_after_die_roll = getattr(sys.modules[__name__], alternate_func)
