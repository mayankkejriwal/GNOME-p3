This is the simulator to use in phase3 using automatic novelty generator.

------------------------------------------------------------------------------
automatic novelty generator files:
1. novelty_generator_v2.py
2. novelty_functions_v3.py
3. novelty_generation_phase3.py

simulation files:
1. test_harness_phase3.py
2. gamplayplay_socket_phase3.py

executing files:
1. execute_phase3.sh
2. phase3_novelty_config.json

------------------------------------------------------------------------------
------------------------------------------------------------------------------
------------------------------------------------------------------------------
usage:
1. modify six needed parameters in execute_phase3.sh
	(1) metaseed
	(2) num_games
	(3) novelty_index (the starting novelty-injected game number)
	(4) debug (True: debug mode, raising error, False: will not raise error) debug mode
	(5) novelty_name: this name corresponding to the novelty_name in phase3_novelty_config.json
	(6) novelty_info (True: give the boolean hint to AI agent, False: not giving the boolean hing to AI agent)

2. modify composite novelty in phase3_novelty_config.json
	----
	the structure:
	{
		novelty_name: {
			"class_list": []
			"func_list": []
			"arg_list": []
		}

	}
	----

3. (For Shafkat, RL agent):
	This version is for the TA2 eval, I put TA2 agent at player_1,

	so you need to modify:
	1. agnet_combination in test_harness_phase3.py
	2. player_decision_agents in function play_game_in_tournament_socket_phase3 in file gamplayplay_socket_phase3.py

4. execute the bash script by using: 
	bash execute_phase3.sh
	
notes: 
	1. this json file will be read in function phase3_novelty_inject in file novelty_generation_phase3.py
	2. "arg_list" might have int, float, or str
	 
