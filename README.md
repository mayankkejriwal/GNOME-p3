## MONOPOLY SIMULATOR

**This branch is developed on the "master" branch code and can be used while developing a player agent not implemented in python to be plugged into the simulator.**

Full code for the Monopoly simulator is in **_GNOME-p3/monopoly-simulator/_** and is written using OOP methodology.

The following steps have to be followed before running the simulator:
* Install __python3__.
* Clone the GNOME-p3 repository - __```$ git clone git@github.com:mayankkejriwal/GNOME-p3.git```__
* Checkout serial_com_over_socket branch - __```$ git checkout serial_com_over_socket```__
* All the python packages required to run a game instance can be installed using __```$ pip install -r requirements.txt```__   *(--user may be required for some systems)*.

**This branch includes a server-client agent implementation that communicates over a socket. This architecture can be used to develop a custom agent. The custom agent would be on the client side (client can be developed in any programming language). The server agent is seated inside the simulator. If a server-client agent is used as one of the players and if this player is in turn to make a decision, the gameboard invokes the server agent which calls the relevant function on the client side and passes a serialized version of the gameboard data (in a JSON format) to the client. The client can then make a decision and sends the decision back to the server over the socket in a serialized format.**

### To run an instance of the game:

Firstly, open **_GNOME-p3_** repo as a project in Pycharm.

Following changes have to be made to file **_GNOME-p3/monopoly_simulator/gameplay_socket.py_** before running a game instance:
* Within the **_play_game()_** function, log folder path and log file path have to be specified for logging of game details in lines 377 and 382 respectively. 
* In lines 401 and 457, modify the default path to the game schema json file with the path where it is saved on your system (give complete path).
* Uncomment the last line **_play_game()_**  (line 493).
* The game can then be run by running **_GNOME-p3/monopoly_simulator/gameplay_socket.py_** file on the Pycharm IDE. This activates the server side.
* Simultaneously run the client side so that the client-server communication is established by running **_GNOME-p3/monopoly_simulator/client_agent_serial.py_** file. Once the connection is established, the game starts playing out.
* The game can also be run on the command line. Open the command line at the **GNOME-p3 project level** and run the following command - __```$ python3 monopoly_simulator/gameplay_socket.py```__ on one window and __```$ python3 monopoly_simulator/client_agent_serial.py```__ on another window.

### Notes
* **_GNOME-p3/monopoly_simulator/client_agent_serial.py_** is a dummy client agent that demonstrates a working prototype model of the client-server communication over a socket using the python socket package. The client can be replaced with a more sophisticated and improved agent capable of better decision making strategies. Use the prototype model as an exmaple for reference.
* **_GNOME-p3/monopoly_simulator/server_agent_serial.py_** is a fully functional server agent and is capable of interfacing with any client as long as it abides by the defined communication protocols.
* While implementing your own custom client agent, all functions in the Agent class as specified in **_GNOME-p3/monopoly_simulator/agent.py_** have to be implemented and the return values have to be serialized to send back over to the server via the socket.

### Other useful tips/features:
* Logging of the game can be onto **console** and and into **log file**. This can be enabled/disabled in **_GNOME-p3/monopoly_simulator/logging_info.py_** file in line 22.
* The seed defined in the **_simulate_game_instance()_** function argument ensures game replication (default seed is already set, pass in new seed in line 423 for a different game instance to be played out). 
* The simulator package comes with a few pre-implemented agents that directly interact with the simulator and do not require a client-server communication protocol (agent implementation in files with names **_background_agent_v[x].py_** and **_baseline_agent.py_**). You are free to plug in any of the implemented agents into each player in lines 396-399 in **_GNOME-p3/monopoly-simulator/gameplay_socket.py_** (default agents are set). The latest updated background agent is **_GNOME-p3/monopoly-simulator/background_agent_V3_1.py_** and the baseline agent is **_GNOME-p3/monopoly-simulator/baseline_agent.py_**.

