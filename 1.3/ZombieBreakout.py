# Designing a state representation
# Designing a set of operators
# Listing constraints and desiderata
# Specifying in code the state representation, operators,
# constraints, evaluation criteria, and goal criterion. 

#<METADATA>
QUIET_VERSION = "0.1"
PROBLEM_NAME = "ZombieBreakout"
PROBLEM_VERSION = "1.3"
PROBLEM_AUTHORS = ['T. Luo, Y. Zheng']
PROBLEM_CREATION_DATE = "24-May-2016"
PROBLEM_DESC=\
'''This formulation of Zombie Breakout uses generic
Python 3 constructs and has been tested with Python 3.5.
It is designed to work according to the QUIET tools interface.
'''
#</METADATA>

import random
import math
import copy


#<PARAMETER>
DIST_SIZE = 16 
LENGTH = int(math.sqrt(DIST_SIZE))
DIST_POPULATION = 100
DOMINATION_RATE = 0.9
# less is more powerful, 1 is maximum.
HUMAN_ATTACK_POWER = 8
HUMAN_DEFENCE_POWER = 0.25
# adjust zombie's infection ability:
ZOMBIE_INFECTION_RATE = 1
# infected human zombify rate:
ZOMBIFY_RATE = 80
TIME_LIMIT = 4*365
#</PARAMETER>

#<COMMON_CODE>

def HASHCODE(s):
	hash_value = ""
	for dist in sorted(s.keys()):
		hash_value += "d" + str(dist[4:])
		hash_value += "h" + str(s[dist][0])+"i"+str(s[dist][1])+"z"+str(s[dist][2])+"a"+str(s[dist][3])+"d"+str(s[dist][4])+"r"+str(s[dist][5])

	return hash_value

def DEEP_EQUALS(s1, s2):
	for dist_num in range(DIST_SIZE):
		if s1[dist_str(dist_num)] != s2[dist_str(dist_num)]:
			return False
	return True

def dist_info(state,dist):
	output_string= ""
	output_string += str(state[dist][0])
	for i in range(1,6):
		if i == 1:
			output_string +=  "/" + str(state[dist][i])
		if i == 2:
			output_string +=  "/" + str(state[dist][i]) + "("
		if i == 3:
			output_string += "{0:.2f}".format(state[dist][i]) + ","		
		if i == 4:
			output_string += "{0:.2f}".format(state[dist][i]) +","
		if i == 5:
			output_string +=   str(state[dist][i]) + ")"
	return output_string


def DESCRIBE_STATE(state):
	'''print state in grid map'''
	output_grid = [[" " for i in range(LENGTH)] for j in  range(LENGTH)]
	for i in range(DIST_SIZE):
		for dist in state.keys():
			if str(i) == dist[4:]:
				x = i // LENGTH
				y = i % LENGTH
				output_grid[x][y] = dist +" H/I/Z(A,D,R) = " +dist_info(state,dist)

	print("+", end="")
	print(("{:-^46}".format('') + "+" )*LENGTH)
	for row in output_grid:
		print("|",end="")
		for col in row:
			print("{:^46}".format(col), end="|")	

		print("")
		print("+",end="")
		print(("{:-^46}".format('') + "+" )*LENGTH)

def copy_state(s):
	return copy.deepcopy(s)

def neighbors(dist_num):
	'''return all adjacent neighbors dist_number'''
	neighbors_list = []
	if dist_num - LENGTH >= 0: neighbors_list.append(dist_num - LENGTH)
	if dist_num + LENGTH <= DIST_SIZE-1: neighbors_list.append(dist_num + LENGTH)
	if dist_num - 1 >= 0 and dist_num % LENGTH != 0: neighbors_list.append(dist_num-1)
	if dist_num + 1 <= DIST_SIZE and dist_num % LENGTH != (LENGTH-1): neighbors_list.append(dist_num+1)
	return neighbors_list

def dominated_by(s,dist_num):
	human, infected, zombie = s[dist_str(dist_num)][:3]
	if (human+infected) >= DOMINATION_RATE*(human+infected+zombie): return "human"
	elif zombie >= DOMINATION_RATE*(human+infected+zombie): return "zombie"
	else: return "mixed"

def goal_message(s):
	return "human won!"

def dist_str(dist_num):
	return "Dist"+str(dist_num)

# operator class
class Operator:
	def __init__(self, name, precond, state_transf):
		self.name = name
		self.precond = precond
		self.state_transf = state_transf

	def is_applicable(self, s):
		return self.precond(s)

	def apply(self, s):
		return self.state_transf(s)
#<COMMON_CODE>

#<OPERATORS>

def zombie_action(s):
	'''zombie try to infect nearby humans'''
	# move phase
	new_state = copy_state(s)
	for dist in range(DIST_SIZE):
		human, infected, zombie = new_state[dist_str(dist)][:3]
		if zombie > 0 and human < 0.15 * zombie:
			for neighbor in neighbors(dist):
				walking_dead = zombie // random.randint(5,7)
				new_state[dist_str(dist)][2] -= walking_dead
				new_state[dist_str(neighbor)][2] += walking_dead

	# attack phase: (coef(in,out):1.3,0.2)
	for dist in range(DIST_SIZE):
		human, infected, zombie = new_state[dist_str(dist)][:3]
		# in dist zombie
		attack_ability = zombie
		# out dist zombie
		for neighbor in neighbors(dist):
			attack_ability += int(new_state[dist_str(neighbor)][2] * 0.20)

		attack_limit = int(min(human, attack_ability*ZOMBIE_INFECTION_RATE))
		new_state[dist_str(dist)][0] -= attack_limit
		new_state[dist_str(dist)][1] += attack_limit

	# infecteds zombify
	for dist in range(DIST_SIZE):
		infected = new_state[dist_str(dist)][1]
		zombify_rate = new_state[dist_str(dist)][5]
		if infected > 0:
			zombified = int(infected*(random.randint(zombify_rate-15,zombify_rate+15)/100))
			new_state[dist_str(dist)][1] -= zombified
			new_state[dist_str(dist)][2] += zombified

	return new_state

def domination(s):
	'''clean up other race if dominated by a race(optional)'''
	new_state = copy_state(s)
	for dist in range(DIST_SIZE):
		dominated_race = dominated_by(s,dist)
		if dominated_race == "human":
			new_state[dist_str(dist)][2] = 0
		elif dominated_race == "zombie":
			new_state[dist_str(dist)][0] = 0
			new_state[dist_str(dist)][1] = 0
	return new_state

def lonely_elimination(s):
	'''clean up other race if dominated by a race(optional)'''
	for dist in range(DIST_SIZE):
		human, infected, zombie = s[dist_str(dist)]
		if (human <= 1 or infected <= 1) and zombie > 2:
			s[dist_str(dist)][0] = 0
			s[dist_str(dist)][1] = 0


def attack(s, dist_num):
	new_state = copy_state(s)
	# non human-dominated state could only attack within dist
	# attack inside the dist & human will be infected
	if dominated_by(s,dist_num) == "mixed":
		human, infected, zombie, attack_power = new_state[dist_str(dist_num)][:4]
		attack_ability = (human + infected) // (attack_power - 1)
		attack_limit = min(attack_ability, human, zombie)
		new_state[dist_str(dist_num)][1] += attack_limit
		new_state[dist_str(dist_num)][0] -= attack_limit
		new_state[dist_str(dist_num)][2] -= attack_limit
 	
	# human-dominated dist could attack all adjacent dist with zombies
	# less powerful, no human infected
	else:
		human1, infected1, zombie1, attack_power1 = new_state[dist_str(dist_num)][:4]
		attack_ability = (human1 + infected1) // (attack_power1 + 2)
		for neighbor in neighbors(dist_num):
			human2, infected2, zombie2 = new_state[dist_str(neighbor)][:3]
			attack_limit = min(attack_ability, zombie2)
			new_state[dist_str(neighbor)][2] -= attack_limit
		
	# after every attack, zombie attack back and infected will become zombies
	# dominated_dist will elimate all other races(optional)
	# domination(new_state)
	# last human die lonely(optional)
	# lonely_elimination(new_state)
	return new_state

def can_attack(s,dist_num):
	#  if dominated by zombie, cannot attack
	if dominated_by(s,dist_num) == "zombie": return 0
	# mixed dist,  zombie in dist, can attack:
	elif dominated_by(s,dist_num) == "mixed": return 100
	# human-domi dist, check neighbors have zombie
	else:
		eval_score = 0
		for neighbor in neighbors(dist_num):
			if dominated_by(s, neighbor) != "human":
				eval_score += 50
		return eval_score

def upgrade_wall(s,dist_num):
	new_state = copy_state(s)
	current_defence_power = new_state[dist_str(dist_num)][4]
	new_state[dist_str(dist_num)][4] = current_defence_power + 0.3
	return new_state

def can_upgrade_wall(s,dist_num):
	if dominated_by(s,dist_num) == "zombie": return 0
	elif dominated_by(s,dist_num) == "mixed": return 20
	else:
		eval_score = 0
		for neighbor in neighbors(dist_num):
			if dominated_by(s, neighbor) == "human":
				eval_score += 25

		return eval_score


def develop_weapon(s,dist_num):
	new_state = copy_state(s)
	current_attack_power = new_state[dist_str(dist_num)][3]
	new_state[dist_str(dist_num)][4] = current_attack_power - 0.2
	return new_state

def can_develop_weapon(s,dist_num):
	if dominated_by(s,dist_num) == "zombie": return 0
	elif s[dist_str(dist_num)][3] <= 3: return 0
	elif dominated_by(s,dist_num) == "mixed": return 20
	else:
		eval_score = 0
		for neighbor in neighbors(dist_num):
			if dominated_by(s, neighbor) == "human":
				eval_score += 25
	return eval_score

def develop_medicine(s,dist_num):
	new_state = copy_state(s)
	current_zombify_rate = new_state[dist_str(dist_num)][5]
	new_state[dist_str(dist_num)][5] = current_zombify_rate - 1
	return new_state

def can_develop_medicine(s,dist_num):
	if dominated_by(s,dist_num) == "zombie": return 0
	elif s[dist_str(dist_num)][5] <= 20: return 0
	elif dominated_by(s,dist_num) == "mixed": return 20
	else:
		eval_score = 0
		for neighbor in neighbors(dist_num):
			if dominated_by(s, neighbor) == "human":
				eval_score += 25
	return eval_score

action_name = ["attack", "upgrade_wall", "develop_weapon", "develop_medicine"]
action_function = [attack, upgrade_wall, develop_weapon, develop_medicine]
action_check_function = [can_attack, can_upgrade_wall, can_develop_weapon, can_develop_medicine]


def Q(s,dist,action):
	# every action check function will return a evaluation score 
	return action_check_function[action_name.index(action)](s,dist)

def dist_operator_fomulator(s):
	# help each state choose an action and take action
	new_state = copy_state(s)
	
	state_score = 0
	for dist in range(DIST_SIZE):
		best_action = []
		dist_max_score = -10000
		for action in action_name:
			dist_score = Q(new_state,dist,action)
			if dist_score == dist_max_score:
				best_action.append(action)
			elif dist_score > dist_max_score:
				best_action = []
				best_action.append(action)
				dist_max_score = dist_score

		# take the best action
		action_number = len(best_action)
		if  action_number == 1:
			new_state = action_function[action_name.index(best_action[0])](new_state,dist)
		# if there are more than one best actions, take an random choice
		elif action_number > 1:
			current_best_action = random.choice(best_action)
			new_state = action_function[action_name.index(current_best_action)](new_state,dist)
	
		state_score += dist_max_score

	new_state = zombie_action(new_state) 
	# print(state_score)
	return new_state

def valid_operator(s):
	return True

OPERATORS = [Operator("Operator",
				lambda s: valid_operator(s),
				lambda s: dist_operator_fomulator(s))]

#</OPERATORS>

#<INITIAL_STATE>
def CREATE_INITIAL_STATE():
	#default1.0: 100 human per dist. Outbreak dist has 100 zombies
	initial_state = {}
	zombie_dist1 = random.randint(0, DIST_SIZE-1)
	for i in range(DIST_SIZE):
		if i == zombie_dist1: initial_state["Dist"+str(i)] = [0,0,DIST_POPULATION,HUMAN_ATTACK_POWER,HUMAN_DEFENCE_POWER,ZOMBIFY_RATE]
		else: initial_state["Dist"+str(i)] = [DIST_POPULATION,0,0,HUMAN_ATTACK_POWER,HUMAN_DEFENCE_POWER, ZOMBIFY_RATE]

	return initial_state
#</INITIAL_STATE>


#<GOAL_TEST> (optional)
def GOAL_TEST(state):
	for dist in state.keys():
		if dominated_by(state,int(dist[4:])) != "human":
			return False
	return True
 
def	all_dominated_by(s, name):
	for dist in s.keys():
		if dominated_by(s, int(dist[4:])) != name and sum(s[dist]) != 0:
			return False
	return True

def turn_limit(count):
	if count >= TIME_LIMIT: return True
	return False

def goal_criteria(s,count):
	goal_message = ""
	if all_dominated_by(s, "human"):
		goal_message = "Human won!"
	elif all_dominated_by(s, "zombie"):
		goal_message = "zombie won!"
	elif turn_limit(count):
		goal_message = "After "+str(count)+" days, humans are still fighting zombies."
	
	return goal_message
#</GOAL_TEST>

#<GOAL_MESSAGE_FUNCTION> (optional)
GOAL_MESSAGE_FUNCTION = lambda s: goal_message(s)
#</GOAL_MESSAGE_FUNCTION>

def test():
	i_s = CREATE_INITIAL_STATE()
	DESCRIBE_STATE(i_s)

 test()