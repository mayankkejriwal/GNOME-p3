class Card(object):
    def __init__(self, action, card_type, name):
        """

        :param action: A function from card_utility_actions, with the same name as specified in the game schema. Note
        that all such functions will have the same signature (player, card, current_gameboard). For details on these, see
        card_utility_actions.
        :param card_type: A string. Should be taken from the game schema.
        :param name: A string. Should be taken from the game schema.
        """
        self.action = action
        self.card_type = card_type
        self.name = name


class MovementCard(Card):

    def __init__(self, action, card_type, name, destination):
        """
        A card of card_type 'movement'. The picking player will be moved to the destination specified in
        destination.

        :param action: A function from card_utility_actions, with the same name as specified in the game schema. Note
        that all such functions will have the same signature (player, card, current_gameboard). For details on these, see
        card_utility_actions.
        :param card_type: A string. Should be taken from the game schema.
        :param name: A string. Should be taken from the game schema.
        :param destination: Location instance corresponding to the destination specified in the schema for
        the card.
        """
        super().__init__(action, card_type, name)
        self.destination = destination

    def serialize(self):
        card_dict = dict()
        card_dict['action'] = self.action.__name__
        card_dict['card_type'] = self.card_type
        card_dict['name'] = self.name
        card_dict['destination'] = self.destination.name
        return card_dict


class MovementPaymentCard(Card):
    def __init__(self, action, card_type, name):
        """
        A card of card_type 'movement_payment'. Generally, this card involves moving to a utility or railroad
        and making a payment as specified in the card (i.e. the payment could be different compared to if the player
        had landed on the utility or railroad the normal way)
        :param action: A function from card_utility_actions, with the same name as specified in the game schema. Note
        that all such functions will have the same signature (player, card, current_gameboard). For details on these, see
        card_utility_actions.
        :param card_type: A string. Should be taken from the game schema.
        :param name: A string. Should be taken from the game schema.
        """
        super().__init__(action, card_type, name)

    def serialize(self):
        card_dict = dict()
        card_dict['action'] = self.action.__name__
        card_dict['card_type'] = self.card_type
        card_dict['name'] = self.name
        return card_dict


class ContingentMovementCard(Card):
    def __init__(self, action, card_type, name):
        """
        A card of card_type 'contingent_movement'. In the default game, this is usually a get_out_jail_free card.
        :param action: A function from card_utility_actions, with the same name as specified in the game schema. Note
        that all such functions will have the same signature (player, card, current_gameboard). For details on these, see
        card_utility_actions.
        :param card_type: A string. Should be taken from the game schema.
        :param name: A string. Should be taken from the game schema.
        """
        super().__init__(action, card_type, name)

    def serialize(self):
        card_dict = dict()
        card_dict['action'] = self.action.__name__
        card_dict['card_type'] = self.card_type
        card_dict['name'] = self.name
        return card_dict



class MovementRelativeCard(Card):
    def __init__(self, action, card_type, name, new_relative_position):
        """
        A card of card_type 'movement_relative'. The picking player will be moved by new_relative_position steps
        from their current location
        :param action: A function from card_utility_actions, with the same name as specified in the game schema. Note
        that all such functions will have the same signature (player, card, current_gameboard). For details on these, see
        card_utility_actions.
        :param card_type: A string. Should be taken from the game schema.
        :param name: A string. Should be taken from the game schema.
        :param new_relative_position: An integer. Specifies relative movement from the picking player's current
        position. For example, if it is -3, the player will be moved 'back' three steps. Similarly, if it is 2
        the player will be moved forward 2 steps.
        """
        super().__init__(action, card_type, name)
        self.new_relative_position = new_relative_position

    def serialize(self):
        card_dict = dict()
        card_dict['action'] = self.action.__name__
        card_dict['card_type'] = self.card_type
        card_dict['name'] = self.name
        card_dict['new_relative_position'] = self.new_relative_position
        return card_dict



class CashFromBankCard(Card):
    def __init__(self, action, card_type, name, amount):
        """
        A card of card_type either 'positive_cash_from_bank' or 'negative_cash_from_bank' (in which case the amount
        parameter will be negative). The picking player will receive from (or give to) the bank the specified amount.
        :param action: A function from card_utility_actions, with the same name as specified in the game schema. Note
        that all such functions will have the same signature (player, card, current_gameboard). For details on these, see
        card_utility_actions.
        :param card_type: A string. Should be taken from the game schema.
        :param name: A string. Should be taken from the game schema.
        :param amount: An integer. The amount to be received from the bank. If negative, the player picking this card
        will have to pay the (positive) amount to the bank.
        """
        super().__init__(action, card_type, name)
        self.amount = float(amount)

    def serialize(self):
        card_dict = dict()
        card_dict['action'] = self.action.__name__
        card_dict['card_type'] = self.card_type
        card_dict['name'] = self.name
        card_dict['amount'] = self.amount
        return card_dict



class ContingentCashFromBankCard(Card):
    def __init__(self, action, card_type, name, contingency):
        """
        A card of card_type 'contingent_cash_from_bank'. The reason it is called this is because the actual payment
        made to/from the bank will depend on the player's current state (e.g., number of houses possessed), and will
        be calculated by the 'contingency' function that is passed in as a parameter.
        :param action: A function from card_utility_actions, with the same name as specified in the game schema. Note
        that all such functions will have the same signature (player, card, current_gameboard). For details on these, see
        card_utility_actions.
        :param card_type: A string. Should be taken from the game schema.
        :param name: A string. Should be taken from the game schema.
        :param contingency: A function from card_utility_actions, with the same name as specified in the game schema.
        """
        super().__init__(action, card_type, name)
        self.contingency = contingency

    def serialize(self):
        card_dict = dict()
        card_dict['action'] = self.action.__name__
        card_dict['card_type'] = self.card_type
        card_dict['name'] = self.name
        card_dict['contingency'] = self.contingency.__name__
        return card_dict


class CashFromPlayersCard(Card):
    def __init__(self, action, card_type, name, amount_per_player):
        """
        A card of card_type either 'positive_cash_from_players' or 'negative_cash_from_players' (in which case the amount
        parameter will be negative). The picking player will receive from (or give to) each other active player the specified amount.
        :param action: A function from card_utility_actions, with the same name as specified in the game schema. Note
        that all such functions will have the same signature (player, card, current_gameboard). For details on these, see
        card_utility_actions.
        :param card_type: A string. Should be taken from the game schema.
        :param name: A string. Should be taken from the game schema.
        :param amount_per_player: An integer. The amount to be taken from each ACTIVE player and credited to the player who picked the card.
        If the amount is negative, the picking player has to pay this (positive) amount TO each active player.
        """
        super().__init__(action, card_type, name)
        self.amount_per_player = float(amount_per_player)

    def serialize(self):
        card_dict = dict()
        card_dict['action'] = self.action.__name__
        card_dict['card_type'] = self.card_type
        card_dict['name'] = self.name
        card_dict['amount_per_player'] = self.amount_per_player
        return card_dict
