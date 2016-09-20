import ZombieBreakout as Problem

def runDFS():
	initial_state = Problem.CREATE_INITIAL_STATE()
	print("Initial State:")
	print(Problem.DESCRIBE_STATE(initial_state))
	global COUNT, BACKLINKS
	COUNT = 0
	BACKLINKS = {}
	IterativeDFS(initial_state)
	print(str(COUNT)+" states examined.")

def IterativeDFS(initial_state):
	global COUNT, BACKLINKS
	OPEN = [initial_state]
	CLOSED = []
	BACKLINKS[Problem.HASHCODE(initial_state)] = -1

	while OPEN != []:
		S = OPEN[0]
		del OPEN[0]
		CLOSED.append(S)

		#if Problem.GOAL_TEST(S):
		#	print(Problem.GOAL_MESSAGE_FUNCTION(S))
		#	backtrace(S)
		#	return

		# this part is used only for zombiebreakout 
		goal_message = Problem.goal_criteria(S,COUNT)
		if len(goal_message)>0:
			backtrace(S)
			print(goal_message)
			return
			

		COUNT += 1
		if (COUNT % 32)==0:
			print(".",end="")
			if (COUNT % 128)==0:
				print("COUNT = "+str(COUNT))
				print("len(OPEN)="+str(len(OPEN)))
				print("len(CLOSED)="+str(len(CLOSED)))
		L = []

		for op in Problem.OPERATORS:
			#Optionally uncomment the following when debugging
			#a new problem formulation.
			print("Trying operator: "+op.name)
			if op.precond(S):	
				new_state = op.state_transf(S)
				if not occurs_in(new_state, CLOSED):
					L.append(new_state)
					BACKLINKS[Problem.HASHCODE(new_state)] = S
					#Uncomment for debugging:
					#print(Problem.DESCRIBE_STATE(new_state))

		for s2 in L:
			for i in range(len(OPEN)):
				if Problem.DEEP_EQUALS(s2, OPEN[i]):
					del OPEN[i]; break
					
		OPEN = L + OPEN

	
def backtrace(S):
	global BACKLINKS
	path = []
	while not S == -1:
		path.append(S)
		S = BACKLINKS[Problem.HASHCODE(S)]
	path.reverse()
	print("Solution path: ")
	for s in path:
		print(Problem.DESCRIBE_STATE(s))

	return path


def occurs_in(s1, lst):
	for s2 in lst:
		if Problem.DEEP_EQUALS(s1, s2): 
			return True
	return False

runDFS()