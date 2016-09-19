action_name = ["attack", "isolate", "develop_weapon", "develop_medicine"]

def best_action(i, j):
	if i > j:
		return "aaa"
	else:
		return "bbb"

# action_function = [attack]
# index = action_name.index("attack")
# action_function[index]("aaa")
op = [best_action(i,j) for i in range(3) for j in range(3)]

print(op)

HAP = 5

# BL = [(1, 'a'), (2, 'b')]
# BL.append((3, 'c'))
# number, name = BL[2]
# print (str(number) + " " + name)

test = {'A' : 1, 'B' : 2, 'C':3}
print(max(test))