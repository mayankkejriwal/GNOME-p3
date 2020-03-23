import os
import re


def generate_win_matrix(path):
    """
    This function generates a matrix of tournaments with its respective winner-loser lists. It will be of size number_of_tournaments * number_of_players.
    For each tournament a list of the size of the number of players is generated. 0 indicates that the respective player lost that game.
    1 indicates that the respective player won the game.
    :param path: path to the folder that contains the tournament gameplay log files from which a matrix of tournaments vs winner-loser list is generated.
    :return: the matrix of tournaments vs winner-loser lists is returned. It will be of size number_of_tournaments * number_of_players
    """
    print("\nGenerating tournament win matrix for tournament: " + path)
    flag = 0

    for files in os.listdir(path):
        if "with_novelty_num_games" in files:
            flag = 1

    if not flag:
        tournament_winners_matrix = []
        for r, d, f in os.walk(path):
            for file in f:
                if not(file.endswith('log')):
                    continue
                winner_list = [0]*4
                filenm = path+ '/' + file
                with open(filenm, "r") as fileread:
                    for line in fileread:
                        winner = re.findall("We have a winner.*$", line, re.MULTILINE)
                        if (len(winner)!=0):
                            winner = winner[0].split("_")[1]
                            winner_list[int(winner)-1] = 1
                tournament_winners_matrix.append(winner_list)
        return tournament_winners_matrix

    else:
        tournament_with_novelty_winners_matrix = []
        tournament_without_novelty_winners_matrix = []
        for r, d, f in os.walk(path):
            for file in f:
                if not(file.endswith('log')):
                    continue
                winner_list = [0]*4
                filenm = path+ '/' + file
                with open(filenm, "r") as fileread:
                    for line in fileread:
                        winner = re.findall("We have a winner.*$", line, re.MULTILINE)
                        if (len(winner)!=0):
                            winner = winner[0].split("_")[1]
                            winner_list[int(winner)-1] = 1
                if "with_novelty_num_games" in filenm:
                    tournament_with_novelty_winners_matrix.append(winner_list)
                else:
                    tournament_without_novelty_winners_matrix.append(winner_list)
        ret_dict = dict()
        ret_dict['with_novelty'] = tournament_with_novelty_winners_matrix
        ret_dict['without_novelty'] = tournament_without_novelty_winners_matrix
        return ret_dict


def generate_rank_matrix(path):
    """
    This function generates a matrix of tournaments with its respective player rank lists. It will be of size number_of_tournaments * number_of_players.
    For each tournament a list of the size of the number of players is generated. 1 indicates that the respective player won the game.
    2-4 indicates that the respective players came 2nd, 3rd or 4th respectively in the game.
    :param path: path to the folder that contains the tournament gameplay log files from which a matrix of tournaments vs player rank list is generated.
    :return: the matrix of tournaments vs player rank lists is returned. It will be of size number_of_tournaments * number_of_players
    """
    print("\nGenerating tournament rank matrix for tournament: " + path)
    flag = 0
    for files in os.listdir(path):
        if "with_novelty_num_games" in files:
            flag = 1

    if not flag:
        tournament_rank_matrix = []
        for r, d, f in os.walk(path):
            for file in f:
                if not(file.endswith('log')):
                    continue
                game_terminate_flag = 0
                winner_list = [0]*4
                filenm = path+ '/' + file
                with open(filenm, "r") as fileread:
                    losers_l = []
                    for line in fileread:
                        winner = re.findall("We have a winner.*$", line, re.MULTILINE)
                        if (len(winner)!=0):
                            game_terminate_flag = 1
                            winner = winner[0].split("_")[1]
                            winner_list[int(winner)-1] = 1
                        loser = re.findall("Discharging assets of.*$", line, re.MULTILINE)
                        if (len(loser)!=0):
                            loser = loser[0].split("_")[1]
                            loser = loser[0].split(" ")[0]
                            losers_l.append(loser)
                if game_terminate_flag:
                    count = 2
                    for l in losers_l:
                        winner_list[int(l)-1] = count
                        count += 1

                tournament_rank_matrix.append(winner_list)
        return tournament_rank_matrix

    else:
        tournament_with_novelty_rank_matrix = []
        tournament_without_novelty_rank_matrix = []
        for r, d, f in os.walk(path):
            for file in f:
                if not(file.endswith('log')):
                    continue
                game_terminate_flag = 0
                winner_list = [0]*4
                filenm = path+ '/' + file
                with open(filenm, "r") as fileread:
                    losers_l = []
                    for line in fileread:
                        winner = re.findall("We have a winner.*$", line, re.MULTILINE)
                        if (len(winner)!=0):
                            game_terminate_flag = 1
                            winner = winner[0].split("_")[1]
                            winner_list[int(winner)-1] = 1
                        loser = re.findall("Discharging assets of.*$", line, re.MULTILINE)
                        if (len(loser)!=0):
                            loser = loser[0].split("_")[1]
                            loser = loser[0].split(" ")[0]
                            losers_l.append(loser)
                if game_terminate_flag:
                    count = 2
                    for l in losers_l:
                        winner_list[int(l)-1] = count
                        count += 1
                if "with_novelty_num_games" in filenm:
                    tournament_with_novelty_rank_matrix.append(winner_list)
                else:
                    tournament_without_novelty_rank_matrix.append(winner_list)
        ret_dict = dict()
        ret_dict['with_novelty'] = tournament_with_novelty_rank_matrix
        ret_dict['without_novelty'] = tournament_without_novelty_rank_matrix
        return ret_dict

