from monopoly_simulator.agent import Agent
from multiprocessing.connection import Listener
import monopoly_simulator.action_choices as action_choices
from monopoly_simulator.serialization import serialize_gameboard
import json
import logging
logger = logging.getLogger('monopoly_simulator.logging_info.server_agent')

# All of the gameplay functions just send a request to the client to call the function with the given arguments and send
# back a reply which is then returned.


def recover(back, player, current_gameboard):
    if 'player' in back[1].keys():
        back[1]['player'] = player
    if 'current_gameboard' in back[1].keys():
        back[1]['current_gameboard'] = current_gameboard


def make_pre_roll_move(player, current_gameboard, allowable_moves, code):
    player.agent.conn.send(("make_pre_roll_move", (player, current_gameboard, allowable_moves, code)))
    back = player.agent.conn.recv()

    if back[0] == action_choices.skip_turn:
        logger.debug(player.player_name + ': I am skipping turn')

    return back


def make_out_of_turn_move(player, current_gameboard, allowable_moves, code):
    player.agent.conn.send(("make_out_of_turn_move", (player, current_gameboard, allowable_moves, code)))
    back = player.agent.conn.recv()

    if back[0] == action_choices.skip_turn:
        logger.debug(player.player_name + ': I am skipping turn')

    return back


def make_post_roll_move(player, current_gameboard, allowable_moves, code):
    player.agent.conn.send(("make_post_roll_move", (player, current_gameboard, allowable_moves, code)))
    back = player.agent.conn.recv()
    recover(back, player, current_gameboard)

    # log
    if back[0] == action_choices.buy_property:
        logger.debug(player.player_name + ': I am attempting to buy property ' + back[1]['asset'].name)
    elif back[0] == action_choices.concluded_actions:
        logger.debug(player.player_name + ': I am skipping turn')

    return back


def make_buy_property_decision(player, current_gameboard, asset):
    player.agent.conn.send(("make_buy_property_decision", (player, current_gameboard, asset)))
    back = player.agent.conn.recv()
    return back


def make_bid(player, current_gameboard, asset, current_bid):
    player.agent.conn.send(("make_bid", (player, current_gameboard, asset, current_bid)))
    back = player.agent.conn.recv()
    return back


def handle_negative_cash_balance(player, current_gameboard):
    player.agent.conn.send(("handle_negative_cash_balance", (player, current_gameboard)))
    back = player.agent.conn.recv()
    return back


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
        self.listener = Listener(address, authkey=authkey)
        self.conn = self.listener.accept()
        #print(self.conn)
        print('Connection accepted from', self.listener.last_accepted)

    def __getstate__(self):
        """Make sure that the socket connection doesn't get pickled."""
        # print("__getstate__ getting called")
        # print(self.__dict__)
        out = self.__dict__.copy()
        out['listener'] = None
        out['conn'] = None
        return out

    def startup(self, current_gameboard, indicator=None):
        """Performs normal Agent startup and signals for the client agent to do the same"""
        print("startup")
        super().startup(current_gameboard, indicator)
        self.conn.send(("startup", (current_gameboard, indicator)))
        return self.conn.recv()

    def shutdown(self):
        """Performs normal Agent shutdown and signals for the client agent to do the same, then closes the connection"""
        print("shutdown")
        self.conn.send(("shutdown", ()))
        result = self.conn.recv()
        return result

    def end_tournament(self):
        print('end_tournament')
        self.conn.send(("end_tournament", ()))
        self.conn.close()
        self.listener.close()
        return super().shutdown()

    def start_tournament(self, f_name):
        print('start_tournament')
        self.conn.send(("start_tournament", (f_name)))
        return self.conn.recv()


