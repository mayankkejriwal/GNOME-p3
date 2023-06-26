from monopoly_simulator import test_harness_phase3_test

metaseed=23
tournament_idx=1
num_games=2
novelty_index=1
debug=True
#novelty_name="environments_18"
novelty_name="environments_17"
novelty_info=False
visulization=False
port=6010
agent_type="background"



test_harness_phase3_test.execute_tournament(novelty_name, tournament_idx, metaseed, novelty_index, novelty_info, agent_type, port, num_games, debug)