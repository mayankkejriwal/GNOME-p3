from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.context_instructions import Color
from kivy.graphics import Rectangle, Ellipse, InstructionGroup
from kivy.core.window import Window, WindowBase
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
import threading
import time
import os
from monopoly_simulator import initialize_game_elements
from monopoly_simulator.action_choices import roll_die
import numpy as np
from monopoly_simulator.card_utility_actions import move_player_after_die_roll
from monopoly_simulator import background_agent_v1
from monopoly_simulator import simple_decision_agent_1
from monopoly_simulator import diagnostics
from monopoly_simulator import novelty_generator
from monopoly_simulator.agent import Agent
from monopoly_simulator.logging_info import log_file_create
import json
import logging

logger = logging.getLogger('monopoly_simulator.logging_info')


class CreateBoardWindow(Screen):
    board_id = ObjectProperty(None)
    prop_id = ObjectProperty(None)
    players = []

    def __init__(self, game_elem, **kwargs):
        super().__init__(**kwargs)
        self.game_elem = game_elem
        self.color_dict = {"Brown": [0.5859, 0.3, 0, 1], "SkyBlue": [0.68, 0.85, 0.90, 1],
                           "Orchid": [0.5, 0, 0.5, 1],
                           "Red": [1, 0, 0, 1], "Orange": [0.99, 0.64, 0, 1], "Yellow": [1, 1, 0, 1],
                           "Green": [0, 1, 0, 1],
                           "Blue": [0, 0, 1, 1], 'Pink': [1, 0.75, 0.796], None: [0.96, 0.96, 0.86, 1]}
        self.obj_instr_directory = []
        self.dice_list = []
        self.start_stop_flag = False
        self.create_board()


    def board_layout_caculator(self, num_properties):
        each_side_num_props = (num_properties/4)
        each_block_width = (1 - 2*(0.11)-0.01)/(each_side_num_props+1)
        return (each_side_num_props, each_block_width)


    def board_layout_total_tiles_caculator(self, location_seq):
        num_property_tiles = 0
        for loc_obj in location_seq:
            num_property_tiles +=1
        return num_property_tiles


    def create_board(self):
        total_num_property_tiles = self.board_layout_total_tiles_caculator(self.game_elem['location_sequence'])
        #each_side_number_of_props, each_block_size = self.board_layout_caculator(len(self.game_elem['location_sequence']))
        each_side_number_of_props, each_block_size = self.board_layout_caculator(total_num_property_tiles)
        self.num_tiles = each_side_number_of_props
        self.each_tile_size = each_block_size
        each_side_number_of_props = int(each_side_number_of_props)
        Monopoly_center_button = MonopolyButton(text="Play", background_color=self.color_dict[None])
        self.board_id.add_widget(Monopoly_center_button)
        Monopoly_center_button.bind(on_release=self.playing_the_game)
        pos_x = 0.9 - each_block_size  ### 0.1 margins left on both sides of the board
        pos_y = 0.1


        for i in range(each_side_number_of_props):
            label = (self.game_elem['location_sequence'][i].name).replace(' ', '\n')
            num_tiles_spanned_by_property = self.game_elem['location_sequence'][i].end_position - self.game_elem['location_sequence'][i].start_position
            try:
                color_t = self.color_dict[str(self.game_elem['location_sequence'][i].color)]
            except:
                color_t = self.color_dict[self.game_elem['location_sequence'][i].color]
            for j in range(num_tiles_spanned_by_property):
                property_button = PropertyButton(text=label,
                                                 background_color=color_t,
                                                 pos_hint={"x": pos_x, "y": pos_y}, size_hint=(each_block_size, each_block_size))
                self.board_id.add_widget(property_button)
            pos_x -= each_block_size


        for i in range(each_side_number_of_props, each_side_number_of_props*2):
            if self.game_elem['location_sequence'][i].name == 'St. James Place':
                label = 'St.James\nPlace'
            elif self.game_elem['location_sequence'][i].name == 'St. Charles Place':
                label = 'St.Charles\nPlace'
            elif self.game_elem['location_sequence'][i].name == 'New York Avenue':
                label = 'NewYork\nAvenue'
            else:
                label = (self.game_elem['location_sequence'][i].name).replace(' ', '\n')

            num_tiles_spanned_by_property = self.game_elem['location_sequence'][i].end_position - self.game_elem['location_sequence'][i].start_position
            try:
                color_t = self.color_dict[str(self.game_elem['location_sequence'][i].color)]
            except:
                color_t = self.color_dict[self.game_elem['location_sequence'][i].color]
            for j in range(num_tiles_spanned_by_property):
                property_button = PropertyButton(text=label,
                                                 background_color=color_t,
                                                 pos_hint={"x": pos_x, "y": pos_y}, size_hint=(each_block_size, each_block_size))
                self.board_id.add_widget(property_button)

            pos_y += each_block_size


        for i in range(each_side_number_of_props*2, each_side_number_of_props*3):
            if self.game_elem['location_sequence'][i].name == 'Go to Jail':
                label = 'Goto\nJail'
            else:
                label = (self.game_elem['location_sequence'][i].name).replace(' ', '\n')

            num_tiles_spanned_by_property = self.game_elem['location_sequence'][i].end_position - self.game_elem['location_sequence'][i].start_position
            try:
                color_t = self.color_dict[str(self.game_elem['location_sequence'][i].color)]
            except:
                color_t = self.color_dict[self.game_elem['location_sequence'][i].color]
            for j in range(num_tiles_spanned_by_property):
                property_button = PropertyButton(text=label,
                                                 background_color=color_t,
                                                 pos_hint={"x": pos_x, "y": pos_y}, size_hint=(each_block_size, each_block_size))
                self.board_id.add_widget(property_button)
            pos_x += each_block_size


        for i in range(each_side_number_of_props*3, each_side_number_of_props*4):
            label = (self.game_elem['location_sequence'][i].name).replace(' ', '\n')
            num_tiles_spanned_by_property = self.game_elem['location_sequence'][i].end_position - self.game_elem['location_sequence'][i].start_position
            try:
                color_t = self.color_dict[str(self.game_elem['location_sequence'][i].color)]
            except:
                color_t = self.color_dict[self.game_elem['location_sequence'][i].color]
            for j in range(num_tiles_spanned_by_property):
                property_button = PropertyButton(text=label,
                                                 background_color=color_t,
                                                 pos_hint={"x": pos_x, "y": pos_y}, size_hint=(each_block_size, each_block_size))
                self.board_id.add_widget(property_button)
            pos_y -= each_block_size

        monopoly_display_button = Button(text="MONOPOLY\n PLAY-PAUSE",
                                            background_color=[0.96, 0.96, 0.86, 1],
                                            pos_hint= {"x": 0.48, "y": 0.48}, size_hint= (0.07, 0.07))
        self.board_id.add_widget(monopoly_display_button)
        monopoly_display_button.bind(on_release= self.toggle_button_func)

        self.goo_jail_chance_with_player = " "
        self.goo_jail_cc_with_player = " "

        get_out_of_jail_chestcard_button = Button(text="Community Chest Card" + \
                                                       self.goo_jail_cc_with_player,
                                                  background_color=[0.96, 0.96, 0.86, 1],
                                                  pos_hint={"x": 0.3, "top": 0.7},
                                                  size_hint=(0.12, 0.10))
        self.board_id.add_widget(get_out_of_jail_chestcard_button)

        get_out_of_jail_chancecard_button = Button(text="Chance Card" + \
                                                        self.goo_jail_chance_with_player,
                                                   background_color=[0.96, 0.96, 0.86, 1],
                                                   pos_hint={"x": 0.6, "top": 0.35},
                                                   size_hint=(0.12, 0.10))
        self.board_id.add_widget(get_out_of_jail_chancecard_button)

        self.goo_jail_list = []
        self.goo_jail_list.append(get_out_of_jail_chestcard_button)
        self.goo_jail_list.append(get_out_of_jail_chancecard_button)

        self.color_players_list = [[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1], [0.95, 0.95, 0, 1]]
        player_details_button_pos_y = 0.8
        self.player_detail_list = []
        for i in range(4):
            player_detail_button = Button(text=" ",
                                               background_color=self.color_players_list[i],
                                               pos_hint={"x": 0, "top": player_details_button_pos_y - i * 0.18},
                                               size_hint=(0.11, 0.16))
            self.board_id.add_widget(player_detail_button)
            self.player_detail_list.append(player_detail_button)

        player_details_heading_button = Button(text="Player details",
                                               background_color=[0.96, 0.96, 0.86, 1],
                                               pos_hint={"x": 0, "top": 0.87},
                                               size_hint=(0.11, 0.05))
        self.board_id.add_widget(player_details_heading_button)

        die_roll_heading_button = Button(text="Dice Roll",
                                         background_color=[0.96, 0.96, 0.86, 1],
                                         pos_hint={"x": 0.92, "top": 0.87},
                                         size_hint=(0.07, 0.05))
        self.board_id.add_widget(die_roll_heading_button)

        self.dice_holder_list = []
        for i in range(len(self.game_elem['die_sequence'])):
            die_roll_num = Button(text=" ",
                                             background_color=[0.96, 0.96, 0.86, 1],
                                             pos_hint={"x": 0.93, "top": 0.87-(i+1)*0.10},
                                             size_hint=(0.05, 0.06))
            self.board_id.add_widget(die_roll_num)
            self.dice_holder_list.append(die_roll_num)

    def playing_the_game(self, *args):
        print("playing")
        self.start_stop_flag = True
        threading.Thread(target=self.simulate_game_instance).start()

    def toggle_button_func(self, *args):
        if self.start_stop_flag==False:
            self.start_stop_flag = True
        elif self.start_stop_flag==True:
            self.start_stop_flag = False
            print('PAUSING THE GAME.... CLICK MONOPOLY BUTTON TO RESUME GAME')


    def simulate_game_instance(self, history_log_file=None, np_seed=6):
        """
        Simulate a game instance.
        :param game_elements: The dict output by set_up_board
        :param np_seed: The numpy seed to use to control randomness.
        :return: None
        """
        logger.debug("size of board "+ str(len(self.game_elem['location_sequence'])))
        #for i in range(len(self.game_elem['location_sequence'])):
        #    logger.debug(self.game_elem['location_sequence'][i].name)
        #logger.debug("start pos: " + str(self.game_elem['location_objects']['States Avenue'].start_position) + " end pos: " + str(self.game_elem['location_objects']['States Avenue'].end_position))
        #logger.debug("start pos: " + str(self.game_elem['location_objects']['Virginia Avenue'].start_position) + " end pos: " + str(self.game_elem['location_objects']['Virginia Avenue'].end_position))
        #logger.debug("start pos: " + str(self.game_elem['location_objects']['Pennsylvania Railroad'].start_position) + " end pos: " + str(self.game_elem['location_objects']['Pennsylvania Railroad'].end_position))
        np.random.seed(np_seed)
        np.random.shuffle(self.game_elem['players'])
        self.game_elem['seed'] = np_seed
        self.game_elem['card_seed'] = np_seed
        self.game_elem['choice_function'] = np.random.choice

        num_die_rolls = 0
        # game_elements['go_increment'] = 100 # we should not be modifying this here. It is only for testing purposes.
        # One reason to modify go_increment is if your decision agent is not aggressively trying to monopolize. Since go_increment
        # by default is 200 it can lead to runaway cash increases for simple agents like ours.

        logger.debug('players will play in the following order: '+'->'.join([p.player_name for p in self.game_elem['players']]))
        logger.debug('Beginning play. Rolling first die...')
        current_player_index = 0
        num_active_players = 4
        winner = None

        while num_active_players > 1:
            self.disable_history()
            if self.start_stop_flag==True:
                current_player = self.game_elem['players'][current_player_index]
                while current_player.status == 'lost':
                    current_player_index += 1
                    current_player_index = current_player_index % len(self.game_elem['players'])
                    current_player = self.game_elem['players'][current_player_index]
                current_player.status = 'current_move'

                # pre-roll for current player + out-of-turn moves for everybody else,
                # till we get num_active_players skip turns in a row.

                skip_turn = 0
                if current_player.make_pre_roll_moves(self.game_elem) == 2:  #2 is the special skip-turn code
                    skip_turn += 1
                out_of_turn_player_index = current_player_index + 1
                out_of_turn_count = 0
                while skip_turn != num_active_players and out_of_turn_count<=200:
                    out_of_turn_count += 1
                    # print('checkpoint 1')
                    out_of_turn_player = self.game_elem['players'][out_of_turn_player_index%len(self.game_elem['players'])]
                    if out_of_turn_player.status == 'lost':
                        out_of_turn_player_index += 1
                        continue
                    oot_code = out_of_turn_player.make_out_of_turn_moves(self.game_elem)
                    # add to game history
                    self.game_elem['history']['function'].append(out_of_turn_player.make_out_of_turn_moves)
                    params = dict()
                    params['self']=out_of_turn_player
                    params['current_gameboard']=self.game_elem
                    self.game_elem['history']['param'].append(params)
                    self.game_elem['history']['return'].append(oot_code)

                    if oot_code == 2:
                        skip_turn += 1
                    else:
                        skip_turn = 0
                    out_of_turn_player_index += 1

                # now we roll the dice and get into the post_roll phase,
                # but only if we're not in jail.


                r = roll_die(self.game_elem['dies'], np.random.choice)
                self.dice_list = r
                for i in range(len(r)):
                    self.game_elem['die_sequence'][i].append(r[i])
                # add to game history
                self.game_elem['history']['function'].append(roll_die)
                params = dict()
                params['die_objects'] = self.game_elem['dies']
                params['choice'] = np.random.choice
                self.game_elem['history']['param'].append(params)
                self.game_elem['history']['return'].append(r)

                num_die_rolls += 1
                self.game_elem['current_die_total'] = sum(r)
                logger.debug('dies have come up ' + str(r))
                if not current_player.currently_in_jail:
                    check_for_go = True
                    move_player_after_die_roll(current_player, sum(r), self.game_elem, check_for_go)
                    # add to game history
                    self.game_elem['history']['function'].append(move_player_after_die_roll)
                    params = dict()
                    params['player'] = current_player
                    params['rel_move'] = sum(r)
                    params['current_gameboard'] = self.game_elem
                    params['check_for_go'] = check_for_go
                    self.game_elem['history']['param'].append(params)
                    self.game_elem['history']['return'].append(None)

                    current_player.process_move_consequences(self.game_elem)
                    # add to game history
                    self.game_elem['history']['function'].append(current_player.process_move_consequences)
                    params = dict()
                    params['self'] = current_player
                    params['current_gameboard'] = self.game_elem
                    self.game_elem['history']['param'].append(params)
                    self.game_elem['history']['return'].append(None)

                    # post-roll for current player. No out-of-turn moves allowed at this point.
                    current_player.make_post_roll_moves(self.game_elem)
                    # add to game history
                    self.game_elem['history']['function'].append(current_player.make_post_roll_moves)
                    params = dict()
                    params['self'] = current_player
                    params['current_gameboard'] = self.game_elem
                    self.game_elem['history']['param'].append(params)
                    self.game_elem['history']['return'].append(None)

                else:
                    current_player.currently_in_jail = False # the player is only allowed to skip one turn (i.e. this one)

                if current_player.current_cash < 0:
                    code = current_player.agent.handle_negative_cash_balance(current_player, self.game_elem)
                    # add to game history
                    self.game_elem['history']['function'].append(current_player.agent.handle_negative_cash_balance)
                    params = dict()
                    params['player'] = current_player
                    params['current_gameboard'] = self.game_elem
                    self.game_elem['history']['param'].append(params)
                    self.game_elem['history']['return'].append(code)
                    if code == -1 or current_player.current_cash < 0:
                        current_player.begin_bankruptcy_proceedings(self.game_elem)
                        # add to game history
                        self.game_elem['history']['function'].append(current_player.begin_bankruptcy_proceedings)
                        params = dict()
                        params['self'] = current_player
                        params['current_gameboard'] = self.game_elem
                        self.game_elem['history']['param'].append(params)
                        self.game_elem['history']['return'].append(None)

                        num_active_players -= 1
                        diagnostics.print_asset_owners(self.game_elem)
                        diagnostics.print_player_cash_balances(self.game_elem)

                        if num_active_players == 1:
                            for p in self.game_elem['players']:
                                if p.status != 'lost':
                                    winner = p
                                    p.status = 'won'
                else:
                    current_player.status = 'waiting_for_move'

                current_player_index = (current_player_index+1)%len(self.game_elem['players'])

                time.sleep(0.1)
                self.update_board()

                if diagnostics.max_cash_balance(self.game_elem) > 300000: # this is our limit for runaway cash for testing purposes only.
                                                                         # We print some diagnostics and return if any player exceeds this.
                    diagnostics.print_asset_owners(self.game_elem)
                    diagnostics.print_player_cash_balances(self.game_elem)
                    return

        logger.debug('printing final asset owners: ')
        diagnostics.print_asset_owners(self.game_elem)
        logger.debug('number of dice rolls: '+ str(num_die_rolls))
        logger.debug('printing final cash balances: ')
        diagnostics.print_player_cash_balances(self.game_elem)

        if winner:
            logger.debug('We have a winner: '+ winner.player_name)

        return

    def disable_history(self):
        self.game_elem['history'] = dict()
        self.game_elem['history']['function'] = list()
        self.game_elem['history']['param'] = list()
        self.game_elem['history']['return'] = list()

    def update_board(self):
        self.canvas.after.clear()
        self.players = []
        pos_x = 0.9 - self.each_tile_size + 0.01
        pos_y = 0.11
        self.color_players_list = [[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1], [1, 1, 0, 1]]
        self.pos_x_list = []
        self.pos_y_list = []

        for i in range(len(self.dice_holder_list)):
            self.dice_holder_list[i].text = str(self.dice_list[i])

        for i in range(4):
            text_on_button = " "+ self.game_elem['players'][i].player_name + \
                            "\n Current Cash = " + str(self.game_elem['players'][i].current_cash) + \
                            "\n # of houses = " + str(self.game_elem['players'][i].num_total_houses) + \
                             "\n # of hotels = " + str(self.game_elem['players'][i].num_total_hotels)
            if (self.game_elem['players'][i].has_get_out_of_jail_community_chest_card == True):
                text_on_button = text_on_button + "\nGOO_Jail community card"
            if (self.game_elem['players'][i].has_get_out_of_jail_chance_card == True):
                text_on_button = text_on_button + "\nGOO_Jail chance card"

            self.player_detail_list[i].text = text_on_button
            self.obj_instr_player = InstructionGroup()
            self.obj_instr_player.add(
                Color(self.color_players_list[i][0], self.color_players_list[i][1], self.color_players_list[i][2],
                      self.color_players_list[i][3]))
            try:
                pos_x_n = int(self.game_elem['players'][i].current_position / 10)
                pos_y_n = int(self.game_elem['players'][i].current_position % 10)
            except:
                pos_x_n = 0
                pos_y_n = 0

            if (pos_x_n == 0):
                pos_x = (0.9 - self.each_tile_size + 0.01) - (pos_y_n * self.each_tile_size)
                pos_y = 0.11
            elif (pos_x_n == 2):
                pos_x = (0.9 - self.each_tile_size + 0.01) - (self.num_tiles * (self.each_tile_size)) + (pos_y_n * self.each_tile_size)
                pos_y = 0.11 + (self.num_tiles * self.each_tile_size)
            elif (pos_x_n == 1):
                pos_x = (0.9 - self.each_tile_size + 0.01) - (self.num_tiles * (self.each_tile_size))
                pos_y = 0.11 + (pos_y_n * self.each_tile_size)
            elif (pos_x_n == 3):
                pos_x = (0.9 - self.each_tile_size + 0.01)
                pos_y = 0.11 + (self.num_tiles * self.each_tile_size) - (pos_y_n * self.each_tile_size)

            self.obj_instr_player.add(
                Ellipse(pos=((pos_x + i * 0.01) * Window.width, pos_y * Window.height), size=(10, 10)))
            self.players.append(self.obj_instr_player)
            self.pos_x_list.append(pos_x)
            self.pos_y_list.append(pos_y)
            self.canvas.after.add(self.obj_instr_player)

            count_house = 0
            count_hotel = 0
            if (self.game_elem['players'][i].assets) != None:
                self.player_props = []
                self.player_props_x = []
                self.player_props_y = []

                for k in range(len(list(self.game_elem['players'][i].assets))):
                    prop_name = list(self.game_elem['players'][i].assets)[k].name
                    pos_prop = self.game_elem['location_objects'][prop_name].start_position

                    self.obj_instr = InstructionGroup()
                    self.obj_instr.add(Color(self.color_players_list[i][0], self.color_players_list[i][1],
                                             self.color_players_list[i][2],
                                             self.color_players_list[i][3]))

                    each_side_num_tiles = self.num_tiles
                    side = 0
                    if pos_prop >=0 and pos_prop < each_side_num_tiles:
                        side = 0
                    elif pos_prop >= each_side_num_tiles and pos_prop < 2*each_side_num_tiles:
                        side = 1
                    elif pos_prop >= 2*each_side_num_tiles and pos_prop < 3*each_side_num_tiles:
                        side = 2
                    else:
                        side = 3
                    #prop_x = int(pos_prop / 10)
                    prop_y = pos_prop - side*each_side_num_tiles
                    pos_x_prop = 0
                    pos_y_prop = 0

                    if (side == 0):
                        pos_x_prop = 0.9 - self.each_tile_size + 0.01 - (prop_y * self.each_tile_size)
                        pos_y_prop = 0.14
                    elif (side == 2):
                        pos_x_prop = 0.9 - self.each_tile_size + 0.01 - (self.num_tiles * (self.each_tile_size)) + (prop_y * self.each_tile_size)
                        pos_y_prop = 0.14 + (self.num_tiles * self.each_tile_size)
                    elif (side == 1):
                        pos_x_prop = 0.9 - self.each_tile_size + 0.01 - (self.num_tiles * (self.each_tile_size))
                        pos_y_prop = 0.14 + (prop_y * self.each_tile_size)
                    elif (side == 3):
                        pos_x_prop = 0.9 - self.each_tile_size + 0.01
                        pos_y_prop = 0.14 + (self.num_tiles * self.each_tile_size) - (prop_y * self.each_tile_size)
                    self.obj_instr.add(Rectangle(pos=(pos_x_prop * Window.width, pos_y_prop * Window.height),
                                                 size=(12, 12)))
                    if list(self.game_elem['players'][i].assets)[k].loc_class=='real_estate':
                        if list(self.game_elem['players'][i].assets)[k].num_houses>0:
                            for m in range(list(self.game_elem['players'][i].assets)[k].num_houses):
                                self.obj_instr.add(Color(1,1,1,1))
                                self.obj_instr.add(Ellipse(pos=((pos_x_prop + (m+1)*0.01) * Window.width, pos_y_prop * Window.height),
                                                             size=(12, 12)))
                                count_house += list(self.game_elem['players'][i].assets)[k].num_houses

                        if list(self.game_elem['players'][i].assets)[k].num_hotels>0:
                            for m in range(list(self.game_elem['players'][i].assets)[k].num_hotels):
                                self.obj_instr.add(Color(1,0.1,0.5,1))
                                self.obj_instr.add(Ellipse(pos=((pos_x_prop + (m+1)*0.01) * Window.width, pos_y_prop * Window.height),
                                                             size=(12, 12)))
                                count_hotel += list(self.game_elem['players'][i].assets)[k].num_hotels

                    self.player_props.append(self.obj_instr)
                    self.player_props_x.append(pos_x_prop)
                    self.player_props_y.append(pos_y_prop)
                    self.canvas.after.add(self.obj_instr)
                    self.obj_instr_directory.append(self.obj_instr)
            self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.players[0].pos = (self.pos_x_list[0] * Window.width, self.pos_y_list[0] * Window.height)
        self.players[1].pos = ((self.pos_x_list[1] + 0.01) * Window.width, self.pos_y_list[0] * Window.height)
        self.players[2].pos = ((self.pos_x_list[2] + 0.02) * Window.width, self.pos_y_list[1] * Window.height)
        self.players[3].pos = ((self.pos_x_list[3] + 0.03) * Window.width, self.pos_y_list[3] * Window.height)
        for i in range(len(self.player_props)):
            self.player_props[i].children[2].pos = (
                self.player_props_x[i] * Window.width, self.player_props_y[i] * Window.height)

    def popup_window(self, property_name):
        show = P()
        property_name_mod = property_name.replace("\n", " ")
        str_prop = "Name of the property: " + property_name_mod

        if self.game_elem['location_objects'][str(property_name_mod)].loc_class == 'real_estate':
            str_prop = str_prop + "\nCost: $" + str(self.game_elem['location_objects'][str(property_name_mod)].price) + \
                       "\nRent: $" + str(self.game_elem['location_objects'][str(property_name_mod)].rent) + \
                       "\nRent with 1 house: $" + str(
                self.game_elem['location_objects'][str(property_name_mod)].rent_1_house) + \
                       "\nRent with 2 house: $" + str(
                self.game_elem['location_objects'][str(property_name_mod)].rent_2_houses) + \
                       "\nRent with 3 house: $" + str(
                self.game_elem['location_objects'][str(property_name_mod)].rent_3_houses) + \
                       "\nRent with 4 house: $" + str(
                self.game_elem['location_objects'][str(property_name_mod)].rent_4_houses) + \
                       "\nRent with a hotel: $" + str(
                self.game_elem['location_objects'][str(property_name_mod)].rent_hotel) + \
                       "\nMortgage: $" + str(self.game_elem['location_objects'][str(property_name_mod)].mortgage) + \
                       "\nHouse cost: $" + str(
                self.game_elem['location_objects'][str(property_name_mod)].price_per_house)

        elif self.game_elem['location_objects'][str(property_name_mod)].loc_class == 'tax':
            str_prop = str_prop + "Pay as TAX $" + str(
                self.game_elem['location_objects'][str(property_name_mod)].amount_due)

        elif self.game_elem['location_objects'][str(property_name_mod)].loc_class == 'railroad':
            str_prop = str_prop + "\nCost: $" + str(self.game_elem['location_objects'][str(property_name_mod)].price) + \
                       "\nMortgage: $" + str(self.game_elem['location_objects'][str(property_name_mod)].mortgage)

        elif self.game_elem['location_objects'][str(property_name_mod)].loc_class == 'utility':
            str_prop = str_prop + "\nCost: $" + str(self.game_elem['location_objects'][str(property_name_mod)].price) + \
                       "\nMortgage: $" + str(self.game_elem['location_objects'][str(property_name_mod)].mortgage) + \
                       "\n\nIf one UTILITY is owned, rent is 4 times\n amount shown on dice." + \
                       "\nIf both utilities are owned, rent is 10 times\n amount shown on dice."

        elif self.game_elem['location_objects'][str(property_name_mod)].loc_class == 'action':
            str_prop = "Pick a " + property_name_mod + " Card"

        elif self.game_elem['location_objects'][str(property_name_mod)].loc_class == 'do_nothing':
            pass

        show.ids.popup_id.text = str_prop
        popup_window = Popup(title=property_name_mod, content=show, size_hint=(None, None), size=(400, 400))
        popup_window.open()


class P(FloatLayout):
    pass


class MonopolyButton(Button):
    pass


class PropertyLabel(Label):
    pass


class WindowManager(ScreenManager):
    pass


class PropertyButton(Button):
    pass


class PlayerWidget(Ellipse):
    pass


class MyMainApp(App):

    def __init__(self, game_elem):
        super().__init__()
        self.game_elem = game_elem

    def build(self):
        print('Game Visualization being rendered')
        sm = self.run_func()

        return sm

    def run_func(self):
        Builder.load_file("my.kv")
        sm = WindowManager()
        screens = [CreateBoardWindow(self.game_elem)]
        for screen in screens:
            sm.add_widget(screen)
        self.screen = screens[0]
        sm.current = "GameBoard"
        return sm


def set_up_board(game_schema_file_path, player_decision_agents):
    game_schema = json.load(open(game_schema_file_path, 'r'))
    return initialize_game_elements.initialize_board(game_schema, player_decision_agents)

def inject_class_novelty_1(current_gameboard, novelty_schema=None):
    """
    Function for illustrating how we inject novelty
    ONLY FOR ILLUSTRATIVE PURPOSES
    :param current_gameboard: the current gameboard into which novelty will be injected. This gameboard will be modified
    :param novelty_schema: the novelty schema json, read in from file. It is more useful for running experiments at scale
    rather than in functions like these. For the most part, we advise writing your novelty generation routines, just like
    we do below, and for using the novelty schema for informational purposes (i.e. for making sense of the novelty_generator.py
    file and its functions.
    :return: None
    """

    ###Below are examples of Level 1, Level 2 and Level 3 Novelties
    ###Uncomment only the Level of novelty that needs to run (i.e, either Level1 or Level 2 or Level 3). Do not mix up novelties from different levels.

    '''
    #Level 1 Novelty

    numberDieNovelty = novelty_generator.NumberClassNovelty()
    numberDieNovelty.die_novelty(current_gameboard, 4, die_state_vector=[[1,2,3,4,5],[1,2,3,4],[5,6,7],[2,3,4]])

    classDieNovelty = novelty_generator.TypeClassNovelty()
    die_state_distribution_vector = ['uniform','uniform','biased','biased']
    die_type_vector = ['odd_only','even_only','consecutive','consecutive']
    classDieNovelty.die_novelty(current_gameboard, die_state_distribution_vector, die_type_vector)

    classCardNovelty = novelty_generator.TypeClassNovelty()
    novel_cc = dict()
    novel_cc["street_repairs"] = "alternate_contingency_function_1"
    novel_chance = dict()
    novel_chance["general_repairs"] = "alternate_contingency_function_1"
    classCardNovelty.card_novelty(current_gameboard, novel_cc, novel_chance)
    '''

    '''
    #Level 2 Novelty

    #The below combination reassigns property groups and individual properties to different colors.
    #On playing the game it is verified that the newly added property to the color group is taken into account for monopolizing a color group,
    # i,e the orchid color group now has Baltic Avenue besides St. Charles Place, States Avenue and Virginia Avenue. The player acquires a monopoly
    # only on the ownership of all the 4 properties in this case.
    inanimateNovelty = novelty_generator.InanimateAttributeNovelty()
    inanimateNovelty.map_property_set_to_color(current_gameboard, [current_gameboard['location_objects']['Park Place'], current_gameboard['location_objects']['Boardwalk']], 'Brown')
    inanimateNovelty.map_property_to_color(current_gameboard, current_gameboard['location_objects']['Baltic Avenue'], 'Orchid')

    #setting new rents for Indiana Avenue
    inanimateNovelty.rent_novelty(current_gameboard['location_objects']['Indiana Avenue'], {'rent': 50, 'rent_1_house': 150})
    '''

    '''
    #Level 3 Novelty
    #NOTE: The GUI only supports EVEN number of property tiles on the board. Make sure that the number of tiles on the board remains an "EVEN number" after
    #introducing granularity novelty.
    
    granularityNovelty = novelty_generator.GranularityRepresentationNovelty()
    granularityNovelty.granularity_novelty(current_gameboard, current_gameboard['location_objects']['Baltic Avenue'], 6)
    granularityNovelty.granularity_novelty(current_gameboard, current_gameboard['location_objects']['States Avenue'], 20)
    granularityNovelty.granularity_novelty(current_gameboard, current_gameboard['location_objects']['Tennessee Avenue'], 27)

    spatialNovelty = novelty_generator.SpatialRepresentationNovelty()
    spatialNovelty.color_reordering(current_gameboard, ['Boardwalk', 'Park Place'], 'Blue')

    granularityNovelty.granularity_novelty(current_gameboard, current_gameboard['location_objects']['Park Place'], 52)
    '''

try:
    os.makedirs('../single_tournament/')
    print('Creating folder and logging gameplay.')
except:
    print('Logging gameplay.')

##Logs game play in the single_tournament folder
logger = log_file_create('../single_tournament/seed_6.log')
player_decision_agents = dict()
player_decision_agents['player_1'] = Agent(**background_agent_v1.decision_agent_methods)
player_decision_agents['player_2'] = Agent(**background_agent_v1.decision_agent_methods)
player_decision_agents['player_3'] = Agent(**background_agent_v1.decision_agent_methods)
player_decision_agents['player_4'] = Agent(**background_agent_v1.decision_agent_methods)
game_elements = set_up_board('../monopoly_game_schema_v1-2.json',
                             player_decision_agents)
inject_class_novelty_1(game_elements)
MyMainApp(game_elements).run()

