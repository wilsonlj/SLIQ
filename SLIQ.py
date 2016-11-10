# Test 2
# Python 2.7.6
# Test
import random
import sys

# split data file into attributes, training data and testing data
def datasets(dataset, percent):
	f = dataset.replace('\r\n','\n').split('\n')
	attr = {}
	attr['id'] = [x.split(':')[0] for x in f[0].split(',')]
	attr['type'] = [x.split(':')[1] for x in f[0].split(',')]
	attr['length'] = len(attr['id']) - 1
	# extract numerical data
	flag = int(percent * (len(f)-1))
	data = [x.split(',') for x in f[1:] if len(x)>0]
	for itemIndex in xrange(len(data)):
		for attrIndex in xrange(attr['length']):
			if attr['type'][attrIndex] == 'n':
				data[itemIndex][attrIndex] = int(data[itemIndex][attrIndex])
	random.shuffle(data)
	return attr, data[:flag], data[flag:]

# find all subsets of categorical attributes
def subset(set):
	subset = []
	length = len(set)
	for iteration in xrange(2**length):
		curset = []
		for digit in xrange(length):
			if iteration % 2:
				curset.append(set[digit])
			iteration /= 2
		subset.append(curset)
	return subset

# presort each attribute list and class index
def presort(attr, dataset):
	attrList = []
	attr['value'] = {}
	for attrIndex in xrange(attr['length']):
		# all attribute combinations
		if attr['type'][attrIndex] == 'b':	
			attr['value'][attrIndex] = ['yes']
		elif attr['type'][attrIndex] == 'n':	
			attr['value'][attrIndex] = sorted(list(set([data[attrIndex] for data in dataset])))
		elif attr['type'][attrIndex] == 'c':	
			attr['value'][attrIndex] = subset(list(set([data[attrIndex] for data in dataset])))
		# sorted attribute lists
		currAttrList = []
		for dataIndex in xrange(len(dataset)):
			currAttrList.append([dataset[dataIndex][attrIndex], dataIndex])
		attrList.append(sorted(currAttrList))
	return attrList, [[data[attr['length']],1] for data in dataset]

# return Gini
def gini(Ly, Ln, Ry, Rn):
	L = Ly + Ln
	R = Ry + Rn
	if L:
		GL = (1.0-(float(Ly)/L)**2-(float(Ln)/L)**2)*L/(L+R)
	else:
		GL = 0
	if R:
		GR = (1.0-(float(Ry)/R)**2-(float(Rn)/R)**2)*R/(L+R)
	else:
		GR = 0
	return  GL + GR

# return test result: yes/no
def judge(data, attribute, value):
	if attribute == 'n':
		return data < value
	if attribute == 'c':
		return data in value
	if attribute == 'b':
		return data == 'yes'

# test for the node
def print_value(name, attribute, value):
	if attribute == 'n':
		return str(name) + ' < ' + str(value)
	if attribute == 'c':
		return name + ' in {' + (',').join(value) + '}'
	if attribute == 'b':
		return name

# print histogram for each node during middle steps
def print_histogram(node, value, countLy, countLn, countRy, countRn):
	print 'N'+str(node)+' on '+value
	print '\t|yes\t|no'
	print 'L\t|'+str(countLy)+'\t|'+str(countLn)
	print 'R\t|'+str(countRy)+'\t|'+str(countRn)
	print

# print class index for each node during middle steps
def print_class(classList, node):
	print 'N'+str(node)+':'
	for index in xrange(len(classList)):
		if classList[index][1] == node:
			print str(index)+'\t|'+classList[index][0]
	print

# detect whether a node is a leaf or not
def is_leaf(classList, no):
	node = list(set([x[0] for x in classList if x[1]==no]))
	if len(node) != 1:
		return "split"
	else:
		return node[0] # yes/no

# evaluate and split by all attribute and gini funciton
def evaluate_split(attr, attrList, classList, node, middlestep, used):
	dataNum= len(classList)
	minGini = 1
	minIndex = -1
	minValue = 0
	deadlock = False
	for attrIndex in xrange(attr['length']):
		if attrIndex in used:
			continue
		for value in attr['value'][attrIndex]:
			# update histogram
			countLy = 0
			countLn = 0
			countRy = 0
			countRn = 0
			# read attrList			
			for item in xrange(dataNum):
				if classList[attrList[attrIndex][item][1]][1] != node:
					continue
				if judge(attrList[attrIndex][item][0], attr['type'][attrIndex], value):
					if classList[attrList[attrIndex][item][1]][0] == 'yes':
						countLy += 1
					else:
						countLn += 1
				else:
					if classList[attrList[attrIndex][item][1]][0] == 'yes':
						countRy += 1
					else:
						countRn += 1
			if middlestep:
				print_histogram(node, print_value(attr['id'][attrIndex], attr['type'][attrIndex], value), countLy, countLn, countRy, countRn)
			if gini(countLy, countLn, countRy, countRn) < minGini:
				minGini = gini(countLy, countLn, countRy, countRn)
				minValue = value
				minIndex = attrIndex
				# deadlocks stands for those samples are the same attribute values but contradict in classification
				deadlock = ((countLy*countLn>0) and (countRy+countRn)==0) or ((countRy*countRn>0) and (countLy+countLn)==0)
				if deadlock:
					if countLy + countRy > countLn + countRn:
							deadlock = 'yes'
					else:
							deadlock = 'no'
			# free attrList
	return minIndex, minValue, deadlock

# generate decision tree
def generate_tree(attr, attrList, classList, middlestep):
	tree = {}
	tree[1] = 'yes'
	queue = [[1]]
	dataNum= len(classList)
	# breath first search
	while queue:
		tnode= queue.pop(0)
		node = tnode[0]
		used = tnode[1:]
		if middlestep:
			print_class(classList, node)
		# leaf terminates the split
		flag = is_leaf(classList, node)
		if flag != "split":
			tree[node] = flag
			continue
		# evaluate split
		minIndex, minValue, deadlock = evaluate_split(attr, attrList, classList, node, middlestep, used)
		if minIndex == -1:
			continue
		# deadlock terminates the plit
		if deadlock:
			tree[node] = deadlock
			continue
		left = len(tree) + 1
		right = left + 1
		tree[node] = [tree[node], print_value(attr['id'][minIndex], attr['type'][minIndex], minValue), left, right, minIndex, attr['type'][minIndex], minValue]
		tree[left] = 'yes'
		tree[right] = 'no'
		# update node class id
		for item in xrange(dataNum):
			if classList[attrList[minIndex][item][1]][1] != node:
				continue
			if judge(attrList[minIndex][item][0], attr['type'][minIndex], minValue):
				classList[attrList[minIndex][item][1]][1] = left
			else:
				classList[attrList[minIndex][item][1]][1] = right
		# add left and right node to queue
		qleft = [left]
		qright = [right]
		for item in used:
			qleft.append(item)
			qright.append(item)
		if minIndex not in used:
			qleft.append(minIndex)
			qright.append(minIndex)
		queue.append(qleft)
		queue.append(qright)
	return tree

# print decision tree
def print_tree(tree, no, deep, output):
	if tree[no] == 'yes' or tree[no] == 'no':
		return
	#print '-'*deep,
	left = tree[no][2]
	right = tree[no][3]
	if tree[left] == 'yes' or tree[left] == 'no':
		left = tree[left]
	if tree[right] == 'yes' or tree[right] == 'no':
		right = tree[right]
	node = '%d %s %s %s %s' %(no, tree[no][0], tree[no][1], str(left), str(right))
	print node
	output.write(node+'\n')
	print_tree(tree, tree[no][2], deep+1, output)
	print_tree(tree, tree[no][3], deep+1, output)

# find leaf of decision tree recursively
def test_node(tree, node, data):
	if tree[node] == 'yes':
		return 'yes'
	if tree[node] == 'no':
		return 'no'
	if judge(data[tree[node][4]], tree[node][5], tree[node][6]):
		return test_node(tree, tree[node][2], data)
	else:
		return test_node(tree, tree[node][3], data)

# test decision tree
def test_tree(tree, testData):
	length = len(testData)
	if not length:
		return 'Null'
	count = 0
	for data in testData:
		if test_node(tree, 1, data) == data[-1]:
			count += 1
	return float(count)/length

# SLIQ step by step
def train(fname, percent=2.0/3, middlestep=0):
	with open(fname) as f:
	 	file = f.read()
	attr, trainData, testData = datasets(file, percent)
	attrList, classList = presort(attr, trainData)               
	tree = generate_tree(attr, attrList, classList, middlestep)
	print 'SLIQ:'
	output = open('result.txt','w')
	print_tree(tree, 1, 0, output)
	output.close()
	print
	print 'Train Data Precision: %.4f' %test_tree(tree, trainData)
	print 'Test  Data Precision: %.4f' %test_tree(tree, testData)
	return tree

if __name__ == '__main__':
	# params: file, training percentage, show middlesteps
	if len(sys.argv) < 2:
		train('data_exercise_2.csv', 2.0/3, 1)
	else:
		train(sys.argv[1])
