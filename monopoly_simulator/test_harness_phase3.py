from monopoly_simulator import gameplay_socket_phase3 as gameplay
#from monopoly_simulator import gameplay_socket as gameplay
from monopoly_simulator import background_agent_v3_1, background_agent_v4_1, background_agent_v5_1, background_agent_v4_1_avoid_accept_trade_with_wealthy
from monopoly_simulator import  background_agent_v4_1_avoid_accept_trade_with_others, background_agent_v4_1_avoid_accept_trade_with_ta2
from monopoly_simulator import background_agent_v3_1_cash_conservator, background_agent_v3_1_railroad_chaser, background_agent_v3_1_sneaky_trader
from monopoly_simulator.logging_info import log_file_create
from monopoly_simulator.novelty_generation_phase3 import *
import monopoly_simulator.novelty_generation_phase3
from monopoly_simulator.server_agent_serial import ServerAgent
#from client_agent_serial import *
import os
import numpy as np
import shutil
import json
import sys
import csv


def play_tournament_with_novelty_v3(tournament_log_folder=None, nov=None, meta_seed=5, num_games=100, novelty_index=25, novelty_info=False, debug_mode = False, novelty_name = None):
    """
    Tournament logging is not currently supported, but will be soon.
    :param tournament_log_folder: String. The path to a folder.
    :param meta_seed: This is the seed we will use to generate a sequence of seeds, that will (in turn) spawn the games in gameplay/simulate_game_instance
    :param num_games: The number of games to simulate in a tournament
    :return: None. Will print out the win-loss metrics, and will write out game logs
    """
    if nov:
        print("novelty function is: " + nov)
    else:
        print("novelty function is: None (Goals)")
    print("novelty name is: " + novelty_name)
    if not tournament_log_folder:
        print("No logging folder specified, cannot log tournaments. Provide a logging folder path.")
        raise Exception

    np.random.seed(meta_seed)
    big_list = list(range(0,1000000))
    np.random.shuffle(big_list)
    tournament_seeds = big_list[0:num_games]
    winners = list()
    count = 1

    for i in range(len(agent_combination_1)):
        folder_name = "../tournament_logs" + tournament_log_folder + '_comb_' + str(i) + '/'
        try:
            os.makedirs(folder_name)
            print('Logging gameplay')
        except:
            print('Given logging folder already exists. Clearing folder before logging new files.')
            shutil.rmtree(folder_name)
            os.makedirs(folder_name)

        metadata_dict = {
            "function": "play_tournament_without_novelty",
            "parameters": {
                "meta_seed": meta_seed,
                "num_game": num_games,
                "novelty_name": novelty_name,
                "nov": nov
            }
        }

        json_filename = folder_name + "tournament_meta_data.json"
        out_file = open(json_filename, "w")
        json.dump(metadata_dict, out_file, indent=4)
        out_file.close()

        for t in range(0,novelty_index):
            print('Logging gameplay without novelty for seed: ', str(tournament_seeds[t]), ' ---> Game ' + str(count))
            filename = folder_name + "meta_seed_" + str(meta_seed) + '_without_novelty' + '_num_games_' + str(count) + '.log'
            logger = log_file_create(filename)

            if debug_mode:
                victor = gameplay.play_game_in_tournament_socket_phase3(tournament_seeds[t], agent_combination_1[i][0], agent_combination_1[i][1],
                                                        agent_combination_1[i][2], agent_combination_1[i][3], novelty_info=novelty_info)
            else:
                try:
                    victor = gameplay.play_game_in_tournament_socket_phase3(tournament_seeds[t], agent_combination_1[i][0],
                                                                            agent_combination_1[i][1],
                                                                            agent_combination_1[i][2],
                                                                            agent_combination_1[i][3],
                                                                            novelty_info=novelty_info)
                except:
                    victor = 'crush'

            winners.append(victor)

            handlers_copy = logger.handlers[:]
            for handler in handlers_copy:
                logger.removeHandler(handler)
                handler.close()
                handler.flush()
            count += 1

        new_winners = list()
        for t in range(novelty_index, len(tournament_seeds)):
            print('Logging gameplay with novelty for seed: ', str(tournament_seeds[t]), ' ---> Game ' + str(count))
            filename = folder_name + "meta_seed_" + str(meta_seed) + '_with_novelty' + '_num_games_' + str(count) + '.log'
            logger = log_file_create(filename)

            if debug_mode:
                if nov == "Goals":
                    victor = gameplay.play_game_in_tournament_socket_phase3(tournament_seeds[t], agent_combination_2[i][0],
                                                                            agent_combination_2[i][1],
                                                                            agent_combination_2[i][2],
                                                                            agent_combination_2[i][3],
                                                                            novelty_info=novelty_info, 
                                                                            inject_novelty_function=True)
                else:
                    victor = gameplay.play_game_in_tournament_socket_phase3(tournament_seeds[t], agent_combination_2[i][0],
                                                                            agent_combination_2[i][1],
                                                                            agent_combination_2[i][2],
                                                                            agent_combination_2[i][3],
                                                                            novelty_info=novelty_info,
                                                                            inject_novelty_function=getattr(sys.modules[__name__], nov),
                                                                            novelty_name = novelty_name)
            else:
                try:
                    if nov == "Goals":
                        victor = gameplay.play_game_in_tournament_socket_phase3(tournament_seeds[t], agent_combination_2[i][0],
                                                                                agent_combination_2[i][1],
                                                                                agent_combination_2[i][2],
                                                                                agent_combination_2[i][3],
                                                                                novelty_info=novelty_info, 
                                                                                inject_novelty_function=True)
                    else:
                        victor = gameplay.play_game_in_tournament_socket_phase3(tournament_seeds[t], agent_combination_2[i][0],
                                                                                agent_combination_2[i][1],
                                                                                agent_combination_2[i][2],
                                                                                agent_combination_2[i][3],
                                                                                novelty_info=novelty_info,
                                                                                inject_novelty_function=getattr(sys.modules[__name__], nov),
                                                                                novelty_name = novelty_name)
                except:
                    victor = 'crush'


            new_winners.append(victor)

            handlers_copy = logger.handlers[:]
            for handler in handlers_copy:
                logger.removeHandler(handler)
                handler.close()
                handler.flush()
            count += 1

        print("Pre-novelty winners: ", winners)
        print("Post-novelty winners: ", new_winners)

        winners_dict = dict()
        winners_dict['player_1'] = 0
        winners_dict['player_2'] = 0
        winners_dict['player_3'] = 0
        winners_dict['player_4'] = 0
        winners_dict['crush'] = 0

        new_winners_dict = dict()
        new_winners_dict['player_1'] = 0
        new_winners_dict['player_2'] = 0
        new_winners_dict['player_3'] = 0
        new_winners_dict['player_4'] = 0
        new_winners_dict['crush'] = 0

        for win in winners:
            winners_dict[win] += 1
        for win in new_winners:
            new_winners_dict[win] += 1

        for k in winners_dict.keys():
            winners_dict[k] = winners_dict[k]/novelty_index
            new_winners_dict[k] = new_winners_dict[k]/(num_games - novelty_index)
        print("Pre-Novelty Player Win Ratio: ")
        print(winners_dict)
        print("Post-Novelty Player Win Ratio: ")
        print(new_winners_dict)

        print("Avg pre-novelty TA2 = ", winners_dict['player_1'])
        print("Avg post-novelty TA2 = ", new_winners_dict['player_1'])
        print("Avg pre-novelty crushed rate = ", winners_dict['crush'])
        print("Avg post-novelty crushed rate = ", new_winners_dict['crush'])

        print("-------------------------------------------------------------------------------------------------------------")



agent_combination_1 = [[background_agent_v3_1, background_agent_v3_1, background_agent_v4_1, background_agent_v4_1]]
agent_combination_2 = [[background_agent_v3_1, background_agent_v3_1, background_agent_v4_1, background_agent_v4_1]]
print('-------------------')
print('---------')
print("agent_combination_2 = ")
for agent_idx, agent_print in enumerate(agent_combination_2[0]):
    if agent_idx == 0:
        print("agent" + str(agent_idx+1) + ": " + agent_print.__name__ + "(will be change to TA2)")
    else:
        print("agent" + str(agent_idx+1) + ": " + agent_print.__name__)
print('---------')

inputArgs = sys.argv[1:]
novelty_name = inputArgs[0]
tournament_idx = inputArgs[1]
metaseed = int(inputArgs[2])
novelty_index = int(inputArgs[3])
novelty_info = inputArgs[4]
if novelty_info == 'True':
    novelty_info = True
    given_system_folder = "given_detection"
else:
    novelty_info = False
    given_system_folder = "system_detection"

port = int(inputArgs[6])
if inputArgs[5] == "TA2-agent":
    agent1 = ServerAgent(address=('localhost', port))
    f_name = 'play game without novelty'
    if not agent1.start_tournament(f_name):
        print("Unable to start tournament")
        exit(0)
    else:
        agent_combination_1[0][0] = agent1
        agent_combination_2[0][0] = agent1
else:
    agent_combination_1[0][0] = None
    agent_combination_2[0][0] = None

num_games = int(inputArgs[7])
debug = inputArgs[8]

if debug == 'False':
    debug = False
elif debug == "True":
    debug = True
else:
    raise ("Please check parameter debug in bash, the current value is " + debug)
print("novelty_name = " + novelty_name) 
print('-------------------')





nov = "phase3_novelty_inject"
play_tournament_with_novelty_v3(f'/{given_system_folder}/tournament_with_novelty_trial_{inputArgs[0]}_{inputArgs[1]}', nov=nov, meta_seed=metaseed, num_games=num_games, novelty_index=novelty_index, novelty_info=novelty_info, debug_mode = debug, novelty_name = novelty_name)

if inputArgs[5] == "TA2-agent":
    agent1.end_tournament()
