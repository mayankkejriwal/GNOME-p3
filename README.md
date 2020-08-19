## MONOPOLY SIMULATOR

Full code for the Monopoly simulator is in **_GNOME-p3/monopoly-simulator/_** and is written using OOP methodology.

The entry point for the simulator is **_GNOME-p3/monopoly-simulator/gameplay.py_** and can be run on the command line.

The following steps have to be followed before running the simulator:
* Install __python3__.
* Clone the GNOME-p3 repository - __```$ git clone git@github.com:mayankkejriwal/GNOME-p3.git```__
* All the python packages required to run a game instance can be installed using __```$ pip install -r requirements.txt```__   *(--user may be required for some systems)*.

### Repository branches:

**_"master"_: The "master" branch of this repository works ONLY if Pycharm is installed. Pycharm is highly recommended to run the monopoly simulator and the instructions given below are to be followed only if running the simulator using Pycharm IDE.** 

**_"serial_com_over_socket"_: This branch can be used while developing a player agent not implemented in python to be plugged into the simulator. Information transfer happens via a server-client architecture over a socket. More information regarding this branch can be found in the README.md of that branch. To switch branch to "serial_com_over_socket" - ```$ git checkout serial_com_over_socket```**

**_"modified_imports"_: If Pycharm is NOT installed and the simulator can be run only on the terminal, then switch branch from "master" to "modified_imports" and follow the instructions given in that branch. To switch branch to "modified_imports" - ```$ git checkout modified_imports```**


### To run an instance of the game:

Following changes have to be made to file **_GNOME-p3/monopoly_simulator/gameplay.py_** before running a game instance:
* Within the **_play_game()_** function, log folder path and log file path have to be specified for logging of game details in lines 370 and 375 respectively. 
* In lines 385 and 440, modify the default path to the game schema json file with the path where it is saved on your system (give complete path).
* Uncomment the last line **_play_game()_**  (line 476).
* The game can then be run by running **_GNOME-p3/monopoly_simulator/gameplay.py_** on the Pycharm IDE. 
* When Pycharm is installed, the game can also be run on the terminal using the **master branch**. Open the terminal at the **GNOME-p3 folder level** and run the following command - __```$ python3 GNOME-p3/monopoly_simulator/gameplay.py```__

### Other useful tips/features:
* Logging of the game can be onto **console** and and into **log file**. This can be enabled/disabled in **_GNOME-p3/monopoly_simulator/logging_info.py_** file in line 22.
* The seed defined in the **_simulate_game_instance()_** function argument ensures game replication (default seed is already set, pass in new seed in line 407 for a different game instance to be played out). 
* The simulator package comes with a few pre-implemented agents (agent implementation in files with names **_background_agent_v[x].py_** and **_baseline_agent.py_**). You are free to plug in any of the implemented agents into each player in lines 380-383 in **_GNOME-p3/monopoly-simulator/gameplay.py_** (default agents are set). The latest updated background agent is **_GNOME-p3/monopoly-simulator/background_agent_V3_1.py_** and the baseline agent is **_GNOME-p3/monopoly-simulator/baseline_agent.py_**. 
* (Optional) You can implement your own custom agent and replace any of the existing player agents with the new agent. In order to do so, 
all functions in the Agent class as specified in **_GNOME-p3/monopoly_simulator/agent.py_** has to be implemented and imported into **_GNOME-p3/monopoly_simulator/gameplay.py_**. (See existing agent implementations for reference.)
* (Optional) The gameplay can also be viewed in **_2D GUI_** by running **_GNOME-p3/monopoly_simulator/gameplay_GUI.py_** following the same instructions as above.  The packages for the GUI can be installed using **```$ pip install -r requirements_GUI.txt```**.
