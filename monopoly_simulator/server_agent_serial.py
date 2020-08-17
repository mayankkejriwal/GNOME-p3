from monopoly_simulator.agent import Agent
from multiprocessing.connection import Listener
import socket
from monopoly_simulator.action_choices import *
from monopoly_simulator.serialization import serialize_gameboard
import json
import sys
import logging
logger = logging.getLogger('monopoly_simulator.logging_info.server_agent')

# All of the gameplay functions just send a request to the client to call the function with the given arguments and send
# back a reply which is then returned.


def _populate_param_dict(param_dict, player, current_gameboard, asset=None):
    # Support for trade not added yet
    if 'player' in param_dict:
        param_dict['player'] = player
    if 'current_gameboard' in param_dict:
        param_dict['current_gameboard'] = current_gameboard
    if 'asset' in param_dict:
        for loc in current_gameboard['location_sequence']:
            if loc.name == param_dict['asset']:
                param_dict['asset'] = loc
    return param_dict


def make_pre_roll_move(player, current_gameboard, allowable_moves, code):
    serial_gameboard = serialize_gameboard(current_gameboard)
    serial_dict_to_client = dict()
    serial_dict_to_client['player'] = player.player_name
    serial_dict_to_client['current_gameboard'] = serial_gameboard
    allowable_moves_list = list()
    for move in allowable_moves:
        allowable_moves_list.append(move.__name__)
    serial_dict_to_client['allowable_moves'] = allowable_moves_list
    serial_dict_to_client['code'] = code

    serial_dict_to_client['function'] = "make_pre_roll_move"
    string_serial_dict_to_client = json.dumps(serial_dict_to_client)
    player.agent.conn.sendall(bytes(string_serial_dict_to_client, encoding="utf-8"))

    return_from_client = player.agent.conn.recv(50024)
    result = json.loads(return_from_client.decode("utf-8"))
    func_name = result['function']
    param_dict = result['param_dict']
    param_dict = _populate_param_dict(param_dict, player, current_gameboard)

    func_ptr = getattr(sys.modules[__name__], func_name)
    if func_name == "skip_turn":
        logger.debug(player.player_name + ': I am skipping turn')
    elif func_name == "concluded_actions":
        logger.debug(player.player_name + ': I am concluding actions')
    elif func_name == "use_get_out_of_jail_card":
        logger.debug(player.player_name + ': I am using get out of jail card')
    elif func_name == "pay_jail_fine":
        logger.debug(player.player_name + ': I am paying jail fine')
    else:
        logger.error("Calling invalid action choice")
        logger.error("raising Exception")
        raise Exception

    return (func_ptr, param_dict)


def make_out_of_turn_move(player, current_gameboard, allowable_moves, code):
    serial_gameboard = serialize_gameboard(current_gameboard)
    serial_dict_to_client = dict()
    serial_dict_to_client['player'] = player.player_name
    serial_dict_to_client['current_gameboard'] = serial_gameboard
    allowable_moves_list = list()
    for move in allowable_moves:
        allowable_moves_list.append(move.__name__)
    serial_dict_to_client['allowable_moves'] = allowable_moves_list
    serial_dict_to_client['code'] = code

    serial_dict_to_client['function'] = "make_out_of_turn_move"
    string_serial_dict_to_client = json.dumps(serial_dict_to_client)
    player.agent.conn.sendall(bytes(string_serial_dict_to_client, encoding="utf-8"))

    return_from_client = player.agent.conn.recv(50024)
    result = json.loads(return_from_client.decode("utf-8"))
    func_name = result['function']
    param_dict = result['param_dict']

    if isinstance(func_name, list):
        func_ptr = list()
        for func in func_name:
            func_ptr.append(getattr(sys.modules[__name__], func))
        for prm in param_dict:
            prm = _populate_param_dict(prm, player, current_gameboard)
        logger.debug("I am making multiple trade offers")

    else:
        param_dict = _populate_param_dict(param_dict, player, current_gameboard)

        func_ptr = getattr(sys.modules[__name__], func_name)
        if func_name == "skip_turn":
            logger.debug(player.player_name + ': I am skipping turn')
        elif func_name == "concluded_actions":
            logger.debug(player.player_name + ': I am concluding actions')
        elif func_name == "accept_trade_offer":     # Support for trading not added yet
            logger.debug(player.player_name + ': I am accepting trade offer')
        elif func_name == "make_trade_offer":       # Support for trading not added yet
            logger.debug(player.player_name + ': I am making trade offer')
        elif func_name == "improve_property":
            logger.debug(player.player_name + ': I am improving property')
        elif func_name == "free_mortgage":
            logger.debug(player.player_name + ': I am going to free mortgage')
        else:
            logger.error("Calling invalid action choice")
            logger.error("raising Exception")
            raise Exception

    return (func_ptr, param_dict)


def make_post_roll_move(player, current_gameboard, allowable_moves, code):
    serial_gameboard = serialize_gameboard(current_gameboard)
    serial_dict_to_client = dict()
    serial_dict_to_client['player'] = player.player_name
    serial_dict_to_client['current_gameboard'] = serial_gameboard
    allowable_moves_list = list()
    for move in allowable_moves:
        allowable_moves_list.append(move.__name__)
    serial_dict_to_client['allowable_moves'] = allowable_moves_list
    serial_dict_to_client['code'] = code

    serial_dict_to_client['function'] = "make_post_roll_move"
    string_serial_dict_to_client = json.dumps(serial_dict_to_client)
    player.agent.conn.sendall(bytes(string_serial_dict_to_client, encoding="utf-8"))

    return_from_client = player.agent.conn.recv(50024)
    result = json.loads(return_from_client.decode("utf-8"))
    func_name = result['function']
    param_dict = result['param_dict']

    param_dict = _populate_param_dict(param_dict, player, current_gameboard)

    func_ptr = getattr(sys.modules[__name__], func_name)
    if func_name == "buy_property":
        logger.debug(player.player_name + ': I am attempting to buy property')
    elif func_name == "mortgage_property":
        logger.debug(player.player_name + ': I am attempting to mortgage property')
    elif func_name == 'sell_property':
        logger.debug(player.player_name + ': I am attempting to sell property')
    elif func_name == "concluded_actions":
        logger.debug(player.player_name + ': I am concluding actions')
    else:
        logger.error("Calling invalid action choice")
        logger.error("raising Exception")
        raise Exception

    return (func_ptr, param_dict)


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
    current_gameboard['history']['function'].append(player.agent.handle_negative_cash_balance)
    code = 0
    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard
    params['code'] = code
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(code)

    negative_cash_bal_flag = True
    while negative_cash_bal_flag:
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
        if func_name is None:
            return param_dict['code']
        else:
            param_dict = _populate_param_dict(param_dict, player, current_gameboard)

            func_ptr = getattr(sys.modules[__name__], func_name)
            if func_name == "mortgage_property":
                logger.debug(player.player_name + ': I am attempting to mortgage property')
                ret_code = mortgage_property(param_dict['player'], param_dict['asset'], current_gameboard)
            elif func_name == 'sell_house_hotel':
                logger.debug(player.player_name + ': I am going to sell improvements')
                ret_code = sell_house_hotel(param_dict['player'], param_dict['asset'], current_gameboard, param_dict['house'], param_dict['hotel'])
            elif func_name == 'sell_property':
                logger.debug(player.player_name + ': I am attempting to sell property')
                ret_code = sell_property(param_dict['player'], param_dict['asset'], current_gameboard)
            elif func_name == "mortgage_property":
                logger.debug(player.player_name + ': I am attempting to mortgage property')
                ret_code = mortgage_property(param_dict['player'], param_dict['asset'], current_gameboard)
            else:
                logger.error("Calling invalid action choice")
                logger.error("raising Exception")
                raise Exception

            current_gameboard['history']['function'].append(func_ptr)
            new_params = dict()
            new_params['player'] = param_dict['player']
            new_params['asset'] = param_dict['asset']
            new_params['current_gameboard'] = current_gameboard
            current_gameboard['history']['param'].append(new_params)
            current_gameboard['history']['return'].append(ret_code)


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


