## MONOPOLY SIMULATOR

Full code for the simulator is in monopoly-simulator/ and is written using OOP methodology.

The entry point for the simulator is gameplay.py and can be run on the command line.

The following steps have to be followed before running the game:

* All the packages required to run a game instance can be installed using "pip install -r requirements.txt".
* A seed has to be set in the simulate_game_instance() function argument for game replication.
* In the play_game() function, log file path has to be specified for logging of game details in lines 343 and 348. 
The required agent for each player also has to be specified in lines 353-356.
* The latest updated agent is background_agent_V3 and the baseline agent is baseline_agent.
* You can implement your own custom agent and replace the baseline_agent with yours. In order to do so, 
all functions in the Agent class as specified in agent.py has to be implemented and imported in gameplay.py.
* Logging of the game can be onto console and and log file. This can be enabled/disabled in logging_info.py file.
* The game can be run on the terminal using "$ python3 gameplay.py > game-log.txt"
* The gameplay can also be viewed in 2D GUI by running gameplay_GUI.py following the same instructions as above. 
The packages for the GUI can be installed using "pip install -r requirements_GUI.txt".
