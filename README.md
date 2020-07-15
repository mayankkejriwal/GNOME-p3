## MONOPOLY SIMULATOR

Full code for the simulator is in GNOME-p3/monopoly-simulator/ and is written using OOP methodology.

The entry point for the simulator is GNOME-p3/monopoly-simulator/gameplay.py and can be run on the command line.

The following steps have to be followed before running the simulator:
* Install python3.
* Clone the GNOME-p3 repository - "git clone git@github.com:mayankkejriwal/GNOME-p3.git"
and **switch branch to "modified_imports" - "git checkout modified_imports".**
* All the python packages required to run a game instance can be installed using "pip install -r requirements.txt" (--user may be required for some systems).

**Note: The "master" branch of this repository works ONLY if Pycharm is installed. We highly recommend using Pycharm to run the monopoly simulator and the instructions given below are to be followed only if running the simulator using Pycharm IDE.** 

**If Pycharm is NOT installed and the simulator can be run on the terminal only, then switch branch from "master" to "modified_imports" and follow the instructions given below.** 


To run an instance of the game, following changes have to be made to file GNOME-p3/monopoly_simulator/gameplay.py:
* In the play_game() function, log folder path and log file path have to be specified for logging of game details in lines 368 and 373 respectively. 
* In lines 383 and 484, modify the default path to the game schema json file with the path where it is saved on your system (give complete path).
* Uncomment the last line "play_game()".
* Open the terminal at the GNOME-p3 folder level and run the following command - "$ python3 monopoly_simulator/gameplay.py" command.

Other useful tips/features:
* Logging of the game can be onto console and and log file. This can be enabled/disabled in GNOME-p3/monopoly_simulator/logging_info.py file in line 22.
* A seed can be set in the simulate_game_instance() function argument for game replication (default seed is already set). 
* The required agent of choice for each player can be specified in lines 378-381 (default agents are set). The latest updated background agent is background_agent_V3_1 and the baseline agent is baseline_agent. 
* (Optional) You can implement your own custom agent and replace the baseline_agent with yours. In order to do so, 
all functions in the Agent class as specified in GNOME-p3/monopoly_simulator/agent.py has to be implemented and imported into GNOME-p3/monopoly_simulator/gameplay.py.
* (Optional) The gameplay can also be viewed in 2D GUI by running GNOME-p3/monopoly_simulator/gameplay_GUI.py following the same instructions as above. 
The packages for the GUI can be installed using "pip install -r requirements_GUI.txt".
