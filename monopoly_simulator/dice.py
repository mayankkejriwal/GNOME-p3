class Dice(object):

    def __init__(self, die_state):
        """
        A class to represent dies.
        :param die_state: A list. Represents a vector of integers, and indicates the possibilities for the dice (e.g., [1-6]).
        In future editions, we may add other states to the dice (with changes correspondingly reflected in the schema).
        """
        self.die_state = die_state

        self.die_state_distribution = 'uniform'
        self.die_type = 'consecutive'

    @staticmethod
    def biased_die_roll(die_state, choice):
        """
        When the die type is biased, this function is an example of how the bias on a die can be defined. This function can be defined
        in anyway that you want to define it.
        :param die_state: A list. Represents a vector of integers, and indicates the possibilities for the dice (e.g., [1-6])
        :param choice: The numpy choice function.
        :return: choice function with an associated bias to make the die roll biased.
        """
        p = list()
        die_total = sum(die_state)
        for i in die_state:
            p.append(i*1.0/die_total)
        return choice(a=die_state, p=p)
