# Designing a state representation
# Designing a set of operators
# Listing constraints and desiderata
# Specifying in code the state representation, operators,
# constraints, evaluation criteria, and goal criterion. 

#<METADATA>
QUIET_VERSION = "0.1"
PROBLEM_NAME = "ZombieBreakout"
PROBLEM_VERSION = "1.1"
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
HUMAN_ATTACK_POWER = 5
HUMAN_DEFENCE_POWER = 0
# adjust zombie's infection ability:
ZOMBIE_INFECTION_RATE = 0.165
# infected human zombify rate:
ZOMBIFY_LOWER = 35
ZOMBIFY_UPPER = 65
TIME_LIMIT = 2*365
#</PARAMETER>

#<COMMON_CODE>

def HASHCODE(s):
	hash_value = ""
	for dist in sorted(s.keys()):
		hash_value += "dist" + str(dist[4:])
		hash_value += "h" + str(s[dist][0])+"i"+str(s[dist][1])+"z"+str(s[dist][2])+"a"+str(s[dist][3])+"d"+str(s[dist][4])

	return hash_value

def DEEP_EQUALS(s1, s2):
	for dist_num in range(DIST_SIZE):
		if s1[dist_str(dist_num)] != s2[dist_str(dist_num)]:
			return False
	return True

def DESCRIBE_STATE(state):
	'''print state in grid map'''
	output_grid = [["" for i in range(LENGTH)] for j in  range(LENGTH)]
	for i in range(DIST_SIZE):
		for dist in state.keys():
			if str(i) == dist[4:]:
				x = i // LENGTH
				y = i % LENGTH
				output_grid[x][y] = dist +" H/I/Z/A/D:" + str(state[dist])
	print("+", end="")
	print(("{:-^38}".format('') + "+" )*LENGTH)
	for row in output_grid:
		print("|",end="")
		for col in row:
			print("{:^38}".format(col), end="|")	
		print()
		print("+",end="")
		print(("{:-^38}".format('') + "+" )*LENGTH)

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
def infected_zombify(s):
	# 25% percent zombiefy
	new_state = copy_state(s)
	for dist in range(DIST_SIZE):
		infected = s[dist_str(dist)][1]
		if infected > 0:
			# 80-100% become zombie
			zombified = int(infected*(random.randint(ZOMBIFY_LOWER,ZOMBIFY_UPPER)/100))
			new_state[dist_str(dist)][1] -= zombified
			new_state[dist_str(dist)][2] += zombified
	return new_state


def zombie_action(s):
	'''zombie try to infect nearby humans'''
	new_state = copy_state(s)
	# move phase
	for dist in range(DIST_SIZE):
		human, infected, zombie = s[dist_str(dist)][:3]
		if zombie > 0 and human < 0.1 * zombie:
			for neighbor in neighbors(dist):
				walking_dead = zombie // random.randint(5,6)
				new_state[dist_str(dist)][2] -= walking_dead
				new_state[dist_str(neighbor)][2] += walking_dead
	return new_state

	# attack phase: (coef(in,out):1.3,0.2)
	for dist in range(DIST_SIZE):
		human, infected, zombie = s[dist_str(dist)][:3]
		attack_ability = 0
		# in dist zombie
		attack_ability += int(zombie*1.3)
		# out dist zombie
		for neighbor in neighbors(dist):
			attack_ability += int(s[dist_str(neighbor)][2] * 0.2)

		attack_limit = int(min(human, attack_ability)*ZOMBIE_INFECTION_RATE)
		s[dist_str(dist)][0] -= attack_limit
		s[dist_str(dist)][1] += attack_limit

def domination(s):
	'''clean up other race if dominated by a race(optional)'''
	for dist in range(DIST_SIZE):
		dominated_race = dominated_by(s,dist)
		if dominated_race == "human":
			s[dist_str(dist)][2] = 0
		elif dominated_race == "zombie":
			s[dist_str(dist)][0] = 0
			s[dist_str(dist)][1] = 0

def lonely_elimination(s):
	'''clean up other race if dominated by a race(optional)'''
	for dist in range(DIST_SIZE):
		human, infected, zombie = s[dist_str(dist)]
		if (human <= 1 or infected <= 1) and zombie > 2:
			s[dist_str(dist)][0] = 0
			s[dist_str(dist)][1] = 0


def attack(s,dist1_num,dist2_num):
	new_state = copy_state(s)
	# attack inside the dist &
	# non human-dominated state could only attack within dist
	# human will be infected
	if dist1_num == dist2_num or dominated_by(s,dist1_num) == "mixed":
		human, infected, zombie, attack_power = new_state[dist_str(dist1_num)][:4]
		attack_ability = (human+infected) // (attack_power-1)
		attack_limit = min(attack_ability, human, zombie)
		new_state[dist_str(dist1_num)][1] += attack_limit
		new_state[dist_str(dist1_num)][0] -= attack_limit
		new_state[dist_str(dist1_num)][2] -= attack_limit
 	
	# out-dist attack
	# human-dominated dist could attack an adjacent dist with zombies
	else:
		human1, infected1, zombie1, attack_power= new_state[dist_str(dist1_num)][:4]
		human2, infected2, zombie2 = new_state[dist_str(dist2_num)][:3]
		attack_ability = (human1 + infected1) // (attack_power)
		attack_limit = min(attack_ability, zombie2, human1)
		new_state[dist_str(dist2_num)][2] -= attack_limit
		new_state[dist_str(dist1_num)][1] += attack_limit 
		new_state[dist_str(dist1_num)][0] -= attack_limit 
		
	# after every attack, zombie attack back and infected will become zombies
	new_state = zombie_action(new_state) 
	new_state = infected_zombify(new_state)
	
	# dominated_dist will elimate all other races(optional)
	# domination(new_state)
	# last human die lonely(optional)
	#lonely_elimination(new_state)

	return new_state

def can_attack(s,dist1_num,dist2_num):
	#  if dominated by zombie, cannot attack
	if dominated_by(s,dist1_num) != "zombie":
		# attack within dist/there are zombies inside dist/human not dominated: 
		if dist1_num == dist2_num:
			if s[dist_str(dist1_num)][2] > 0 and dominated_by(s, dist1_num) != "human":
				return True
		else:
			# if there are zombies in neighbor dist
			if dist2_num in neighbors(dist1_num):	
				# get target dist status
				if s[dist_str(dist2_num)][2] > 0 and dominated_by(s,dist2_num) != "human":
					return True
	return False

def isolate(s,dist1_num,dist2_num):
	global HUMAN_DEFENCE_POWER 
	HUMAN_DEFENCE_POWER = HUMAN_DEFENCE_POWER + 1
	new_state = copy_state(s)
	new_state[dist_str(dist1_num)][4] += 1
	new_state = zombie_action(new_state) 
	new_state = infected_zombify(new_state)
	return new_state

def can_isolate(s,dist1_num,dist2_num):
	if dist1_num != dist2_num: return False
	if dominated_by(s,dist1_num) != "zombie": return False
	return True

def develop_weapon(s,dist1_num,dist2_num):
	new_state = copy_state(s)
	new_state[dist_str(dist1_num)][3] += 1
	new_state = zombie_action(new_state) 
	new_state = infected_zombify(new_state)
	return new_state

def can_develop_weapon(s,dist1_num,dist2_num):
	if dist1_num != dist2_num: return False
	if dominated_by(s,dist1_num) != "zombie": return False
	return True

def develop_medicine(s,dist1_num,dist2_num):
	# global ZOMBIFY_LOWER
	# global ZOMBIFY_UPPER
	# ZOMBIFY_UPPER = ZOMBIFY_UPPER - 5
	# ZOMBIFY_LOWER = ZOMBIFY_LOWER - 5
	new_state = copy_state(s)
	new_state = zombie_action(new_state) 
	new_state = infected_zombify(new_state)
	return new_state

def can_develop_medicine(s,dist1_num,dist2_num):
	if dist1_num != dist2_num: return False
	if dominated_by(s,dist1_num) != "zombie": return False
	return True

action_name = ["attack", "isolate", "develop_weapon", "develop_medicine"]
action_function = [attack, isolate, develop_weapon, develop_medicine]
action_check_function = [can_attack, can_isolate, can_develop_weapon, can_develop_medicine]

OPERATORS = [Operator("Dist" + str(i) + " " + a + " " + "Dist" + str(j),
				lambda s,i = i, j = j, a = a: action_check_function[action_name.index(a)](s,i,j),
				lambda s,i = i, j = j, a = a: action_function[action_name.index(a)](s,i,j))
			for i in range(DIST_SIZE) for j in range(DIST_SIZE) for a in action_name]

#</OPERATORS>

#<INITIAL_STATE>
def CREATE_INITIAL_STATE():
	#default1.0: 100 human per dist. Outbreak dist has 100 zombies
	initial_state = {}
	zombie_dist1 = random.randint(0, DIST_SIZE-1)
	for i in range(DIST_SIZE):
		if i == zombie_dist1: initial_state["Dist"+str(i)] = [0,0,DIST_POPULATION,HUMAN_ATTACK_POWER,HUMAN_DEFENCE_POWER]
		else: initial_state["Dist"+str(i)] = [DIST_POPULATION,0,0,HUMAN_ATTACK_POWER,HUMAN_DEFENCE_POWER]

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

# test()