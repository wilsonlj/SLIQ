import pydot
import SLIQ
import sys

# plot the decision tree
def graph_tree(tree):
	graph = pydot.Dot(graph_type='digraph')
	nodes = {}
	queue = [1]
	# plot nodes
	while queue:
		node = queue.pop(0)
		if tree[node]=='yes' or tree[node]=='no':
			nodes[node] = pydot.Node(str(node)+'#'+tree[node])
			continue
		nodes[node] = pydot.Node(str(node)+'#'+tree[node][1])
		queue.append(tree[node][2])
		queue.append(tree[node][3])
	for node in nodes:
		graph.add_node(nodes[node])
	# plot edges
	queue = [1]
	while queue:
		node = queue.pop(0)
		if tree[node]=='yes' or tree[node]=='no':
			continue
		graph.add_edge(pydot.Edge(nodes[node], nodes[tree[node][2]], label="yes"))
		graph.add_edge(pydot.Edge(nodes[node], nodes[tree[node][3]], label="no"))
		queue.append(tree[node][2])
		queue.append(tree[node][3])
	# output
	graph.write_png('tree.png')

if __name__ == '__main__':
	# construct decision tree
	if len(sys.argv) < 2:
		tree = SLIQ.train('data_exercise_2.csv')
	else:
		tree = SLIQ.train(sys.argv[1])
	# plot decision tree
	graph_tree(tree)