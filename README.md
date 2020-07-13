## MONOPOLY SIMULATOR

Full code for the simulator is in monopoly-simulator/ and is written using OOP methodology.

The entry point for the simulator is gameplay.py and can be run on the command line.

The following steps have to be followed before running the simulator:
* Install python3.
* Clone the GNOME-p3 repository.
* All the python packages required to run a game instance can be installed using "pip install -r requirements.txt" (--user may be required for some systems).

**Note: The master branch of this repository works only if used on Pycharm. We highly recommend using Pycharm to run the monopoly simulator and the instructions given below are to be followed only if running the simulator using Pycharm IDE.** 

**If Pycharm is not installed and the simulator can be run on the terminal only, then this branch "modified imports" can be used by following the instructions given below.**


To run an instance of the game, following changes have to be made to file GNOME-p3/monopoly_simulator/gameplay.py:
* A seed has to be set in the simulate_game_instance() function argument for game replication (default seed is already set).
* In the play_game() function, log folder path and log file path have to be specified for logging of game details in lines 368 and 373 respectively. 
The required agent for each player also has to be specified in lines 378-381 (default agents are set).
* In lines 383 and 484, modify the default path to the game schema json file with the path where it is saved on your system (give complete path).
* Uncomment the last line "play_game()".
* The latest updated agent is background_agent_V3_1 and the baseline agent is baseline_agent.
* (Optional) You can implement your own custom agent and replace the baseline_agent with yours. In order to do so, 
all functions in the Agent class as specified in monopoly_simulator/agent.py has to be implemented and imported in monopoly_simulator/gameplay.py.
* Logging of the game can be onto console and and log file. This can be enabled/disabled in monopoly_simulator/logging_info.py file in line 22.
* The game can be run on the terminal using "$ python3 monopoly_simulator/gameplay.py" command.
* (Optional) The gameplay can also be viewed in 2D GUI by running monopoly_simulator/gameplay_GUI.py following the same instructions as above. 
The packages for the GUI can be installed using "pip install -r requirements_GUI.txt".
