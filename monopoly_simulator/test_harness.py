import numpy as np
from monopoly_simulator import gameplay
from monopoly_simulator import novelty_generator

def play_tournament_without_novelty(tournament_log_folder=None, meta_seed=5, num_games=100):
    """
    Tournament logging is not currently supported, but will be soon.
    :param tournament_log_folder: String. The path to a folder.
    :param meta_seed: This is the seed we will use to generate a sequence of seeds, that will (in turn) spawn the games in gameplay/simulate_game_instance
    :param num_games: The number of games to simulate in a tournament
    :return: None. Will print out the win-loss metrics, and will write out game logs
    """
    np.random.seed(meta_seed)
    big_list = list(range(0,1000000))
    np.random.shuffle(big_list)
    tournament_seeds = big_list[0:num_games]
    winners = list()
    for t in tournament_seeds:
        winners.append(gameplay.play_game_in_tournament(t))

    print_win_ratio(winners)


def play_tournament_with_novelty_1(tournament_log_folder='',meta_seed=5, num_games=100,novelty_index=23):
    """

    :param tournament_log_folder:
    :param meta_seed:
    :param num_games:
    :param novelty_index: an integer between 1 and num_games-1. We will play this many games BEFORE introducing novelty.
    :return:
    """
    np.random.seed(meta_seed)
    big_list = list(range(0, 1000000))
    np.random.shuffle(big_list)
    tournament_seeds = big_list[0:num_games]
    winners = list()
    for t in range(0,novelty_index):
        winners.append(gameplay.play_game_in_tournament(tournament_seeds[t]))

    print('pre-novelty stats:')
    print_win_ratio(winners)

    new_winners = list()
    for t in range(novelty_index, len(tournament_seeds)):
        new_winners.append(gameplay.play_game_in_tournament(tournament_seeds[t], class_novelty_1))

    print('pre-novelty stats:')
    print_win_ratio(winners)
    print('post-novelty stats:')
    print_win_ratio(new_winners)



def class_novelty_1(current_gameboard):

    classCardNovelty = novelty_generator.TypeClassNovelty()
    novel_cc = dict()
    novel_cc["street_repairs"] = "alternate_contingency_function_1"
    novel_chance = dict()
    novel_chance["general_repairs"] = "alternate_contingency_function_1"
    classCardNovelty.card_novelty(current_gameboard, novel_cc, novel_chance)

def print_win_ratio(winners):
    """

    :param winners: a list of player names (can also contain None, these will not be counted) who have won the game played at that index in the tourney.
    :return: None. Prints out the win ratios of the different players in winners.
    """
    win_dict = dict()
    win_dict['player_1'] = 0
    win_dict['player_2'] = 0
    win_dict['player_3'] = 0
    win_dict['player_4'] = 0
    total = 0
    for w in winners:
        if w in win_dict:
            win_dict[w] += 1
            total += 1
    for w, v in win_dict.items():
        print(w, ' has win-ratio ', str(v * 1.0 / total))

play_tournament_with_novelty_1()