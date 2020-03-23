import os
from monopoly_simulator.metrics_helper import generate_rank_matrix, generate_win_matrix


def compute_win_loss_ratio(mypath, player_name=None):
    """
    This function calculates the win-ratio of the players who played the tournament.
    :param mypath: path to the all tournament_logs folder or to the individual tournament folder. This function checks if the path is directly to the
    parent tournament logs folder where win-ratio has to be calculated for all the tournaments or directly to an individual tournament folder.
    :param player_name: specific player whose win-ratio has to be calculated. If None, then the win-ratio of all players are printed.
    :return: None. Prints out the win ratios of the different players in winners via the print_win_ratio function call.
    """
    flag = 0
    for files in os.listdir(mypath):
        if files.endswith(".log"):
            flag = 1

    if flag==1:
        win_matrix = generate_win_matrix(mypath)
        if isinstance(win_matrix, list):
            print_win_ratio(win_matrix, player_name)
        else:
            print("Pre-Novelty stats: ")
            print_win_ratio(win_matrix['with_novelty'], player_name)
            print("Post-Novelty stats: ")
            print_win_ratio(win_matrix['without_novelty'], player_name)

    elif flag==0:
        folders = []
        for foldername in os.listdir(mypath):
            folders.append(foldername)

        for folder in folders:
            path = mypath + '/' + folder
            win_matrix = generate_win_matrix(path)
            if isinstance(win_matrix, list):
                print_win_ratio(win_matrix, player_name)
            else:
                print("Pre-Novelty stats: ")
                print_win_ratio(win_matrix['with_novelty'], player_name)
                print("Post-Novelty stats: ")
                print_win_ratio(win_matrix['without_novelty'], player_name)


def compute_average_rank_of_player(mypath, player_name=None):
    """
    This function calculates the average rank of the players who played the tournament.
    :param mypath: path to the all tournament_logs folder or to the individual tournament folder. This function checks if the path is directly to the
    parent tournament folder where average rank has to be calculated for all the tournaments or directly to an individual tournament folder.
    :param player_name: specific player whose average rank has to be calculated. If None, then the average rank of all players are printed.
    :return: None. Prints out the average rank of the different players across all tournaments via the print_avg_rank function call.
    """
    flag = 0
    for files in os.listdir(mypath):
        if files.endswith(".log"):
            flag = 1

    if flag==1:
        rank_matrix = generate_rank_matrix(mypath)
        if isinstance(rank_matrix, list):
            print_avg_rank(rank_matrix, player_name)
        else:
            print("Pre-Novelty stats: ")
            print_avg_rank(rank_matrix['with_novelty'], player_name)
            print("Post-Novelty stats: ")
            print_avg_rank(rank_matrix['without_novelty'], player_name)

    elif flag==0:
        folders = []
        for foldername in os.listdir(mypath):
            folders.append(foldername)

        for folder in folders:
            path = mypath + '/' + folder
            rank_matrix = generate_rank_matrix(path)
            if isinstance(rank_matrix, list):
                print_avg_rank(rank_matrix, player_name)
            else:
                print("Pre-Novelty stats: ")
                print_avg_rank(rank_matrix['with_novelty'], player_name)
                print("Post-Novelty stats: ")
                print_avg_rank(rank_matrix['without_novelty'], player_name)


def print_win_ratio(winners_matrix, player_name=None):
    """
    :param winners_matrix: a matrix of the winner and losers in each of the games in the tournament. The matrix is a list of lists.
    Each list is a list of the players with 0 indicating that the player lost the game and 1 indicating that the player won the game.
    There will be only one 1 in each list implying that that player is the winner in the respective game.
    :param player_name: specific player whose win-ratio has to be printed. If None, then the win-ratio of all players are printed.
    :return: None. Prints out the win ratios of the different players in winners.
    """
    win_dict = dict()
    win_dict['player_1'] = 0
    win_dict['player_2'] = 0
    win_dict['player_3'] = 0
    win_dict['player_4'] = 0
    total = 0
    for list_l in winners_matrix:
        for index in range(len(list_l)):
            if list_l[index]==1 and ('player_' + str(index + 1)) in win_dict:
                win_dict['player_' + str(index + 1)] += 1
                total += 1
    print(total)
    if not player_name:
        for w, v in win_dict.items():
            print(w, ' has win-ratio ', str(v * 1.0 / total))

    else:
        print(player_name, 'has a win-ratio ', str(win_dict[player_name]*1/total))


def print_avg_rank(winners_matrix, player_name=None):
    """
    :param winners_matrix: a matrix of the rank of all the players in each of the games in the tournament. The matrix is a list of lists.
    Each list is a list of ranks of the players with 1 indicating that the player won the game and 4 indicating that the player came last in that game in the tournament.
    :param player_name: specific player whose average rank across all the games has to be printed. If None, then the average rank of all players are printed.
    :return: None. Prints out the win ratios of the different players in winners.
    """
    win_dict = dict()
    win_dict['player_1'] = 0
    win_dict['player_2'] = 0
    win_dict['player_3'] = 0
    win_dict['player_4'] = 0
    total = 0
    for list_l in winners_matrix:
        for index in range(len(list_l)):
            if ('player_' + str(index + 1)) in win_dict:
                win_dict['player_' + str(index + 1)] += list_l[index]
        total += 1

    if not player_name:
        for w, v in win_dict.items():
            print(w, ' has an average rank of  ', str(v * 1.0 / total))

    else:
        print(player_name, ' has an average rank of ', str(win_dict[player_name]*1/total))



'''
To compute_win_loss_ratio or to compute_average_rank_of_player, either 
1. specify the specific tournament log folder (eg: "../tournament_logs/tournament_without_novelty_4") in which case the statistics for the players for that game will be calculated or 
    eg: compute_win_loss_ratio("../tournament_logs/tournament_without_novelty_4", 'player_1')
    eg: compute_win_loss_ratio("../tournament_logs/tournament_without_novelty_4")
    
2. just specify "../tournament_logs/" in which case the player statistics will be calculated iteratively for all the tournaments.
    eg: compute_win_loss_ratio("../tournament_logs/", 'player_1')
    eg: compute_average_rank_of_player("../tournament_logs/")
    
Specifying the player name will compute statistics only for that particular player.
If no player name is specified, then statistics of all the players will be printed.
'''


compute_win_loss_ratio("../tournament_logs/", 'player_1')
#compute_average_rank_of_player("../tournament_logs/tournament_without_novelty_4")
#compute_average_rank_of_player("../tournament_logs/", 'player_1')
