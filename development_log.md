## GUI:

A new file called gameplay_GUI.py has been added. A single game with a 2D board visualization of the game being played can be run by running gameplay_GUI.py instead of gameplay.py.
Line 238 in gameplay_GUI.py determines the speed of the game. Setting the argument to a higher value slows the gameplay and setting a lower value makes the game run faster.

### Board rules:

* The GUI version supports almost all the features of the normal gameplay including novelty injection, however a tournament cannot be run. 
* The GUI is implemented using KIVY and novelty can be injected following the same procedure as in gameplay.py.
* The only additional package that has to be installed before running gameplay_GUI.py is kivy using "pip install kivy" (the dependencies will automatically be installed).
* On running the gameplay_GUI.py file, a GUI will be launched.
* Click the "PLAY" button on the top left corner to start gameplay.
* Gameplay can be paused and resumed at anytime in between the game (in case you want to observe what's on the board or the console) by clicking the "MONOPOLY PLAY-PAUSE" button on the center of the board. Clicking it once will pause the game and clicking it again will resume the game from where it paused. 
* The EXIT button on the top right can only be used BEFORE clicking PLAY button or AFTER the game has terminated to close the GUI. NOTE that it doesnot work during gameplay. If clicked during gameplay, it only stops the GUI from rendering further and willnot close it since gameplay is still running in the background.
* Each of the property tiles are clickable. On clicking each tile, the title deed card for the respective property pops up with all the details such as rent, mortgage, etc (just as on a title deed card) displayed. Clicking anywhere else on the screen pushes the title deed card back in.
* The GUI window is resizable by clicking the minimize or maximize button on the taskbar (just like in any other window). Note that this works at anytime before the game has terminated. Once the game has terminated, resizing the window doesnot render correctly. 

### Dice:
* Dice and numbers that appear on each dice roll are visible on the right side of the GUI window.
* If the number of dice are increased by injecting the respective novelty, the GUI also adjusts accordingly.

### Players and Properties:
* The players are indicated by the tiny dots that move along the bottom area of the properties. 
* Color of the players are maintained as in gameplay.py
* The leftside of the GUI allocates colored boxes according to the color allocated to each player. These boxes store information about the players current cash, count of houses and hotels, and whether the player possesses a get out of jail card and each of these values get updated on the go.
* Whenever a player buys a property, a square of the color of the player will be placed on the top left area of the respective property tile to indicate ownership of the property by that player.
* When a player buys a house on a property after he has monopolized a color group, a WHITE filled circle will be placed beside the square that was placed to show ownership of that property.
* When a player buys a hotel on a property, the 4 white circles (4 houses) will be replaced by a PINK filled circle adjacent to the square on that property.

The GUI has been implemented mainly for debug purposes to visualize gameplay and injection of novelty and to get an idea of how and where the players and properties move during the game.


## GAME LOGGING:

* GNOME-p3 currently supports logging of gameplay in a logfile as well as on the console.
* A file handler and stream handler takes care of the above functionalities respectively.
* This has been implemented in the ../monopoly_simulator/logging_info.py file. 
* Each tournament is logged into a seperate folder based on the use of novelty and meta_seeds.

## MONOPOLY SIMULATOR:

Full code for the simulator is in monopoly-simulator/ and is written using OOP methodology.

The entry point for the simulator is gameplay.py and can be run on the command line:

$ python3 gameplay.py > game-log.txt

The simulator currently relies on Python 3.8.x. Because inheritance has a different syntax between 2.7 and 3, you should use the repository https://github.com/mayankkejriwal/GNOME  if you are using Python 2.7.x. For this current package, we recommend setting up a Python 3 interpreter and running the code therein.

An important difference between GNOME and GNOME-p3 (besides the Python 2.7->Python 3.8 change) is the way that agents are represented. In GNOME, the agents are not object-oriented; each agent is a dictionary of decision-making functions that is used to supplement a player's data structure. In GNOME-p3, there is an agent.py file that encapsulates these functions within an Agent class. Now, instead of passing agent function pointers directly into a Player object's instantiation, we pass in an Agent object instead. We believe this is a more elegant and long-term solution since you could create your own agent classes by sub-classing, and adding fields and state variables to your sub-class as necessary.

We print out a log that tracks the game at a fairly detailed level. The prints are routed to stdout by default, but you could pipe them to a file if you want to retain a file log. 

To run the simulator, you need to assign a decision agent to each of the four players and the game schema. We have provided the schema already (monopoly_game_schema_v1-2.json) in the outer folder, although you will have to specify the path to the schema once you clone this repo on your own system. In gameplay, we also have to specify the numpy seed (currently a default is set) and if we want, we can modify elements of the game schema for testing purposes. For simple agents that do not try to monopolize or trade, we recommend modifying go_increment to avoid runaway cash increases from the bank to the players.

We have provided two example decision agents to guide you on how to build out your own decision agent; the code also shows how to assign these agents to players. Currently, one of the decision agents is a simply 'dummy' agent, while the other is a 'background' agent that will be assigned to three of the four players during evaluations. The former is very simplistic, and often leads to cash runaway increases. The latter, though simple, is capable of monopolizing and trading and plays the game fairly well. Sometime in March, we will release the baseline agent used in our novelty evaluations, which will also be a rule-based, sophisticated decision maker who weighs the state of the board carefully before deciding what to do.

The code has been fairly well documented, and we've done a lot of testing on it. That does not mean it's completely clear
or that mistakes might not appear. On our part, we are continuously running tests but if you see something that's unclear
or that seems like an error we'd appreciate feedback!

## GAME SCHEMA:

The current version of the schema, generated using monopoly-game-schema.py is monopoly_game_schema_v1-2.json. We provide
_v1-1.json for comparison only. It should not be used in the game. Here's a succinct version of some of the more
important changes in going from v1-1 to v1-2:

* In location_states, we have changed 'class' to 'loc_class'. The reason is (and we should have realized it earlier)
that class is a reserved word in Python.

* we have added a new field called go_increment. This is the amount you get when you pass go each time.

* has_get_out_of_jail card has been replaced with its community chest and chance equivalents.
The reason is that a player can have two of these at the same time (one from each of the card categories), and we need
to be able to track this (e.g., if the player uses the chance card, it should go back to the chance pile.
Unlike the other cards, which get used and replaced immediately in the pile, this one is something the player can hold
on to for a while, which complicates matters)

* another change in location is that we now keep track of who owns the location WITHIN the location itself, and also
how many houses/hotels are on that location. We decided to make this change to avoid too many function
calls/indirections when calculating rent. This means that under 'assets' in player_states, we have removed hotels and
houses; now, we only track which properties the player owns, along with an derivatory data structure that tracks
whether the players possesses full color sets. In turn, this means the 'assets' has been considerably simplified,
since we only need to keep track of the names of the properties the player owns. More details are provided in the
player.py file.

* chance cards were previously missing from the schema due to a glitch in the JSON generation (these have now been added)

* in chance/community chest, we have added a new card class called 'contingent_cash_from_bank' that was previously in
the class positive/negative_cash_from_bank. The reason is that the positive/negative class always involves a
fixed amount, while contingent cash requires a function calculation (e.g., calculating street repair cost),
which makes the structure of the class different.

* name of 'go_to_nearest_railroad_pay_double_1' card is now just 'go_to_nearest_railroad_pay_double'. Note that the
'name' of a card does not have to be unique since there could be multiple identical cards (such as in this case)

* we've added skip_turn and concluded_actions to out_of_turn action choices. skip_turn in this context just means that we
won't take action on out_of_turn (at least right now). concluded_actions means that we're done with whatever actions we
wanted to take. concluded_actions must follow at least one action, otherwise skip_turn should be invoked. Only when
all out_of_turn players have skipped the turn and the current player rolls the die will the die be rolled, and the
post die roll phase begin. The exception is the post-die roll phase where concluded_actions can be called as the very
first action.

* we have simplified player_states since it contained redundant information. Now it refers to a single dictionary.

* there is a small chance my current cash might become negative even if it's not my turn (if another player collects
from me due to a card draw, and I have low cash). Because the chances are so small of this happening, we do not force
that player to take action just yet but once it's his turn, he'll have to deal with the negative cash before he can
conclude his turn (or declare bankruptcy)

* the 'player' objects now have some additional fields that will be useful for keeping track of the game state. In general, we have continued to refine and update the player data structure to ensure the game plays smoothly, quickly and in a well-defined manner.

* I've added 'mortgage_property', 'improve_property' to the list of functions that are allowed in out_of_turn moves.
'bid_on_property' has been removed. The reason is that currently, the only way you can bid on a property is at auction,
which is conducted by the bank as a special process when a player refuses to buy a property on which he/she has
landed. So you can't really 'choose' to bid in an out_of_turn move; instead, you can bid only in a player's
post-roll phase.

### REMINDERS:

* it IS possible to sell a mortgaged property

### GENERAL UPDATES:

February 15, 2020:

* We have released the first version of the novelty schema in the outer folder. The novelty generator that uses this schema to inject novelty into the game will be released within February. 

February 5, 2020:

* A background agent that is significantly more advanced than the previous simple decision agent has been added, along with
some agent helper functions in a separate file. When building your own agent, you should make use of the helper file as
a guide only, since some elements are strategic rather than logical (e.g., how to decide which property we should sell
to another player) and can be done in other (probably more optimal) ways. 

* To ensure the game continues without a single player having the ability to 'hang' things up, we have instituted limits
on (i) how many actions you are allowed to take in pre/post/out-of-turn moves before you are forced to conclude actions
(currently 50), and (ii) how many out-of-turn 'rounds' we allow before we force the current player to roll the dice
and enter post-roll. Currently it is set at 200. We believe these limits are more than adequate to ensure that players
have the opportunity to take all moves they may want to take before passing the baton. Currently, the game ends within
150-500 die rolls, and does not enter into a runaway state. This is due to aggressive trading on the part of the
background agents. 

January 27, 2020:

* We've added a 'history' facility (a dict) to the game_elements data structure (also called current_gameboard in much of the
game). There are three lists inside 'history', all of equal length, keyed respectively by 'function', 'param' and 'return'.
Each time a function is called (starting from within gameplay/simulate_game_instance), we append the function to 'function',
the parameters passed inside the function to 'param' and the return value to 'return'. We always make this update after
the function returns (if the function does not return anything, then we simply append None). 'function' is a list of
function pointers, and 'return' can be heterogeneous, depending on what a function is returning. 'param' is a list of
dicts, with the keys in the dicts corresponding to exactly the expected arguments in the function (including 'self') and
the values shallow copies of the corresponding arguments passed to the function. Note that if a function takes on no values,
we still append an empty dictionary to param to maintain equal length of all three lists. Furthermore, functions that
are internal (starting with _ or __) are not recorded. Anything called before simulate_game_instance (particularly, the
initialization of the game board itself) is not recorded either. Finally, diagnostics functions are not recorded since
they are 'extra-game' conceptually; they should only be used by a developer for stress-testing agents/games and not
by agents themselves.

* Note that since the parameters can be objects, and we do not do a deep copy of objects when we insert them into
a param dict, the state of objects can (and in many cases, will) change between the time an object is inserted as
a parameter or return value into a list, and the time when it is queried by an external agent. With this caveat in mind,
there are many core values in each object that stay constant over the tenure of the game e.g., a player's name,
an asset's name, card details etc. Dereference with caution.

* Because of the history facility, we had to modify the signatures of action_choices/mortgage_property & pay_jail_fine slightly
(we added current_gameboard to the argument list of both functions). This was necessary since each of these functions
itself calls a function, and in order to accurately update history, needs access to the gameboard. If you have already
implemented a decision agent that expects the old signature (without current_gameboard) you may want to update; it should
be a very small change.
