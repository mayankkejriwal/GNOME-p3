from monopoly_simulator.agent import Agent
import socket
from monopoly_simulator.serialization import serialize_gameboard
import json
import sys
import logging
logger = logging.getLogger('monopoly_simulator.logging_info.server_agent_serial')


def _populate_param_dict(param_dict, player, current_gameboard):
    if 'player' in param_dict:
        param_dict['player'] = player
    if 'current_gameboard' in param_dict:
        param_dict['current_gameboard'] = current_gameboard
    if 'asset' in param_dict:
        for loc in current_gameboard['location_sequence']:
            if loc.name == param_dict['asset']:
                param_dict['asset'] = loc

    # following keys are mostly relevant to trading
    if 'from_player' in param_dict:
        for p in current_gameboard['players']:
            if p.player_name == param_dict['from_player']:
                param_dict['from_player'] = p
    if 'to_player' in param_dict:
        for p in current_gameboard['players']:
            if p.player_name == param_dict['to_player']:
                param_dict['to_player'] = p
    if 'offer' in param_dict:
        property_set_offered = param_dict['offer']['property_set_offered']   # set of property names (not list and does not involve pointers)
        property_set_wanted = param_dict['offer']['property_set_wanted']    # set of property names (not list and does not involve pointers)
        # iterate through these sets of strings and replace with property pointers

        property_set_offered_ptr = set()
        for prop in property_set_offered:
            for loc in current_gameboard['location_sequence']:
                if loc.name == prop.name:
                    property_set_offered_ptr.add(loc)

        property_set_wanted_ptr = set()
        for prop in property_set_wanted:
            for loc in current_gameboard['location_sequence']:
                if loc.name == prop.name:
                    property_set_wanted_ptr.add(loc)

        param_dict['offer']['property_set_offered'] = property_set_offered_ptr
        param_dict['offer']['property_set_wanted'] = property_set_wanted_ptr

    return param_dict


def make_pre_roll_move(player, current_gameboard, allowable_moves, code):
    serial_gameboard = serialize_gameboard(current_gameboard)
    serial_dict_to_client = dict()
    serial_dict_to_client['player'] = player.player_name
    serial_dict_to_client['current_gameboard'] = serial_gameboard
    serial_dict_to_client['allowable_moves'] = list(allowable_moves)
    serial_dict_to_client['code'] = code

    serial_dict_to_client['function'] = "make_pre_roll_move"
    string_serial_dict_to_client = json.dumps(serial_dict_to_client)
    player.agent.conn.sendall(bytes(string_serial_dict_to_client, encoding="utf-8"))

    return_from_client = player.agent.conn.recv(50024)
    result = json.loads(return_from_client.decode("utf-8"))
    func_name = result['function']
    param_dict = result['param_dict']

    return (func_name, param_dict)


def make_out_of_turn_move(player, current_gameboard, allowable_moves, code):
    serial_gameboard = serialize_gameboard(current_gameboard)
    serial_dict_to_client = dict()
    serial_dict_to_client['player'] = player.player_name
    serial_dict_to_client['current_gameboard'] = serial_gameboard
    serial_dict_to_client['allowable_moves'] = list(allowable_moves)
    serial_dict_to_client['code'] = code

    serial_dict_to_client['function'] = "make_out_of_turn_move"
    string_serial_dict_to_client = json.dumps(serial_dict_to_client)
    player.agent.conn.sendall(bytes(string_serial_dict_to_client, encoding="utf-8"))

    return_from_client = player.agent.conn.recv(50024)
    result = json.loads(return_from_client.decode("utf-8"))
    func_name = result['function']
    param_dict = result['param_dict']

    return (func_name, param_dict)


def make_post_roll_move(player, current_gameboard, allowable_moves, code):
    serial_gameboard = serialize_gameboard(current_gameboard)
    serial_dict_to_client = dict()
    serial_dict_to_client['player'] = player.player_name
    serial_dict_to_client['current_gameboard'] = serial_gameboard
    serial_dict_to_client['allowable_moves'] = list(allowable_moves)
    serial_dict_to_client['code'] = code

    serial_dict_to_client['function'] = "make_post_roll_move"
    string_serial_dict_to_client = json.dumps(serial_dict_to_client)
    player.agent.conn.sendall(bytes(string_serial_dict_to_client, encoding="utf-8"))

    return_from_client = player.agent.conn.recv(50024)
    result = json.loads(return_from_client.decode("utf-8"))
    func_name = result['function']
    param_dict = result['param_dict']

    return (func_name, param_dict)


def make_buy_property_decision(player, current_gameboard, asset):
    serial_gameboard = serialize_gameboard(current_gameboard)
    serial_dict_to_client = dict()
    serial_dict_to_client['player'] = player.player_name
    serial_dict_to_client['current_gameboard'] = serial_gameboard
    serial_dict_to_client['asset'] = asset.name

    serial_dict_to_client['function'] = "make_buy_property_decision"
    string_serial_dict_to_client = json.dumps(serial_dict_to_client)
    player.agent.conn.sendall(bytes(string_serial_dict_to_client, encoding="utf-8"))

    return_from_client = player.agent.conn.recv(50024)
    buy_prop_decision_flag = bool(return_from_client.decode("utf-8"))
    return buy_prop_decision_flag


def make_bid(player, current_gameboard, asset, current_bid):
    serial_gameboard = serialize_gameboard(current_gameboard)
    serial_dict_to_client = dict()
    serial_dict_to_client['player'] = player.player_name
    serial_dict_to_client['current_gameboard'] = serial_gameboard
    serial_dict_to_client['asset'] = asset.name
    serial_dict_to_client['current_bid'] = current_bid

    serial_dict_to_client['function'] = "make_bid"
    string_serial_dict_to_client = json.dumps(serial_dict_to_client)
    player.agent.conn.sendall(bytes(string_serial_dict_to_client, encoding="utf-8"))

    return_from_client = player.agent.conn.recv(50024)
    bid_amt = float(return_from_client.decode("utf-8"))
    return bid_amt


def handle_negative_cash_balance(player, current_gameboard):
    serial_gameboard = serialize_gameboard(current_gameboard)
    serial_dict_to_client = dict()
    serial_dict_to_client['player'] = player.player_name
    serial_dict_to_client['current_gameboard'] = serial_gameboard

    serial_dict_to_client['function'] = "handle_negative_cash_balance"
    string_serial_dict_to_client = json.dumps(serial_dict_to_client)
    player.agent.conn.sendall(bytes(string_serial_dict_to_client, encoding="utf-8"))

    return_from_client = player.agent.conn.recv(50024)
    result = json.loads(return_from_client.decode("utf-8"))
    func_name = result['function']
    param_dict = result['param_dict']

    return (func_name, param_dict)


def _build_decision_agent_methods_dict():
    ans = dict()
    ans['handle_negative_cash_balance'] = handle_negative_cash_balance
    ans['make_pre_roll_move'] = make_pre_roll_move
    ans['make_out_of_turn_move'] = make_out_of_turn_move
    ans['make_post_roll_move'] = make_post_roll_move
    ans['make_buy_property_decision'] = make_buy_property_decision
    ans['make_bid'] = make_bid
    ans['type'] = "decision_agent_methods"
    return ans


class ServerAgent(Agent):
    """
    To play over TCP, start a game with at least one ServerAgent. The ServerAgent will wait for a connection from a
    ClientAgent, and then relay all game state information to the client. The client will decide what move to make
    and send the result back to the ServerAgent.
    """

    def __init__(self, address=('localhost', 6010), authkey=b"password"):
        """
        Create a new ServerAgent on a particular port. If you are playing a game with multiple server agents, make sure
        each is operating on a different port.
        @param address: Tuple, the address and port number. Defaults to localhost:6000
        @param authkey: Byte string, the password used to authenticate the client. Defaults to "password"
        """
        super().__init__(**_build_decision_agent_methods_dict())
        print("Waiting for connection...")
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind((address[0], address[1]))
        self.listener.listen()
        conn, addr = self.listener.accept()
        self.conn = conn
        print('Connection accepted by client')

    def __getstate__(self):
        """Make sure that the socket connection doesn't get pickled."""
        out = self.__dict__.copy()
        out['listener'] = None
        out['conn'] = None
        return out

    def startup(self, current_gameboard, indicator=None):
        """Performs normal Agent startup and signals for the client agent to do the same"""
        print("startup")
        super().startup(current_gameboard, indicator)
        serial_gameboard = serialize_gameboard(current_gameboard)
        serial_dict_to_client = dict()
        serial_dict_to_client['current_gameboard'] = serial_gameboard
        serial_dict_to_client['indicator'] = indicator
        serial_dict_to_client['function'] = "startup"
        json_serial_dict_to_client = json.dumps(serial_dict_to_client)
        self.conn.sendall(bytes(json_serial_dict_to_client, encoding="utf-8"))
        return_from_client = self.conn.recv(1024)
        result = return_from_client.decode("utf-8")
        return result

    def shutdown(self):
        """Performs normal Agent shutdown and signals for the client agent to do the same, then closes the connection"""
        print("shutdown")
        serial_dict_to_client = dict()
        serial_dict_to_client['function'] = "shutdown"
        json_serial_dict_to_client = json.dumps(serial_dict_to_client)
        self.conn.sendall(bytes(json_serial_dict_to_client, encoding="utf-8"))
        return_from_client = self.conn.recv(1024)
        result = int(return_from_client.decode("utf-8"))
        return result

    def end_tournament(self):
        print('end_tournament')
        serial_dict_to_client = dict()
        serial_dict_to_client['function'] = "end_tournament"
        json_serial_dict_to_client = json.dumps(serial_dict_to_client)
        self.conn.sendall(bytes(json_serial_dict_to_client, encoding="utf-8"))
        self.conn.close()
        self.listener.close()
        return super().shutdown()

    def start_tournament(self, f_name):
        print('start_tournament')
        serial_dict_to_client = dict()
        serial_dict_to_client['function'] = "start_tournament"
        json_serial_dict_to_client = json.dumps(serial_dict_to_client)
        self.conn.sendall(bytes(json_serial_dict_to_client, encoding="utf-8"))
        return_from_client = self.conn.recv(1024)
        result = int(return_from_client.decode("utf-8"))
        return result


