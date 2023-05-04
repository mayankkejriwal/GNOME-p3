## MONOPOLY SIMULATOR

For the detailed usage for simulator, please refer to README_serial_com_over_socket_phase2.md.


### Start the tournament with socketing to your AI agent:

__We suggest executing the simulator by high-level bash script instead of executing from test_harness_phase3.py directly__.

-------------------------------------------------
1. ```$ cd monopoly_simulator```
2. Modify the user's parameter in execute_phase3.sh
 * metaseed: the random seed used in the tournament
 * num_games: the total game count played in the tournament
 * novelty_index: the game index that injects novelty(0-indexed)
 * novelty_name: The format is (novelty_class) _ (novelty_idx_in_novelty_list) <br />
novelty_class should be limited to [environments, events, goals] <br />
novelty_idx_in_novelty_list should be bounded by 1 to 15 (inclusive)
 * novelty_info: True if giving the AI agent a digit-hint 
 * debug: True if using debug mode
 * port: socketing port
3. ```$ bash execute_phase3.sh```
-------------------------------------------------
4. execute your AI agent via port
