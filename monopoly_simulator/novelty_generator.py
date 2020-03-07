from monopoly_simulator.dice import Dice
from monopoly_simulator.novelty_functions import *
import copy
import sys
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

file_handler = logging.FileHandler('gameplay_logs.log', mode='a')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
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


class ContingentAttributeNovelty(AttributeNovelty):
    def __init__(self):
        super().__init__()

    def change_mortgage_percentage(self, current_gameboard, new_percentage):
        current_gameboard['bank'].mortgage_percentage = new_percentage

    def percent_of_total_mortgage_outstanding(self, current_gameboard, new_percentage):
        current_gameboard['bank'].mortgage_percentage = new_percentage
        current_gameboard['bank'].total_mortgage_rule = True


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

        current_gameboard['dies'] = list() # wipe out what was there before.
        for i in range(0, die_count):
            current_gameboard['dies'].append(Dice(die_state_vector[i]))

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
        current_gameboard['community_chest_cards'] = list()
        for card_name, num in community_chest_cards_num.items():
            card = current_gameboard['community_chest_card_objects'][card_name]
            for i in range(0, num):
                current_gameboard['community_chest_cards'].append(copy.deepcopy(card))

        current_gameboard['chance_cards'] = list()
        for card_name, num in chance_cards_num.items():
            card = current_gameboard['chance_card_objects'][card_name]
            for i in range(0, num):
                current_gameboard['chance_cards'].append(copy.deepcopy(card))


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
        if len(die_state_distribution_vector) != len(current_gameboard['dies']):
            logger.error('die state distributions and die types are unequal to number of dies in board. Raising exception...')
            logger.error("Exception")

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

        for index in range(0, len(new_location_sequence)):
            loc = new_location_sequence[index]
            if loc in new_location_sequence_dict:
                new_location_sequence[index] = new_location_sequence_dict[loc]

        if len(set(new_location_sequence)) != len(new_location_sequence):
            logger.error("Exception") # somehow we've ended up introducing duplicate names in the list.

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

