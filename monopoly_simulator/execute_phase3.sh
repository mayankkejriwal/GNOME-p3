# ---------------------------------------------------
# user's parameters
metaseed=15
num_games=2
novelty_index=1 # the game index that injects novelty(0-indexed)
#novelty_name="events_8"
novelty_name="environments_10"
#novelty_name="goals_5"
novelty_info=False # True if giving the AI agent a digit-hint 
debug=False
port=6010
# ---------------------------------------------------


export PYTHONPATH=${PWD}/../
echo $PWD



IFS='_' read -ra experiment <<< "$novelty_name"
novelty_class=${experiment[0]}
novelty_idx_in_novelty_list=${experiment[1]}
echo $novelty_class




if [ ${novelty_class} = 'goals' ]
then
	python3 test_harness_phase3_goals.py ${novelty_name} 1 ${metaseed} ${novelty_index} ${novelty_info} TA2-agent ${port} ${num_games} ${debug}
else
	python3 test_harness_phase3.py ${novelty_name} 1 ${metaseed} ${novelty_index} ${novelty_info} TA2-agent ${port} ${num_games} ${debug}
fi


