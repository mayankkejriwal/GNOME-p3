class Dice(object):

    def __init__(self, die_state):
        """
        A class to represent dies.
        :param die_state: A list. Represents a vector of integers, and indicates the possibilities for the dice (e.g., [1-6]).
        In future editions, we may add other states to the dice (with changes correspondingly reflected in the schema).
        """
        self.die_state = die_state