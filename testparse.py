import causal_grammar

# our causal forest:
tree = {
	"node_type": "root",
	"symbol": "f1",
	"children": [
		{ "node_type": "and", "symbol": "a", "children": [
				{ "node_type": "leaf", "symbol": "e1"},
				{ "node_type": "or", "symbol": "c", "children": [
						{ "node_type": "leaf", "symbol": "f2"},
						{ "node_type": "leaf", "symbol": "f3"},
					]
				},
			],
		},
		{ "node_type": "and", "symbol": "b", "children": [
				{ "node_type": "leaf", "symbol": "e2"},
				{ "node_type": "or", "symbol": "d", "children": [
						{ "node_type": "leaf", "symbol": "f2"},
						{ "node_type": "leaf", "symbol": "f4"},
					]
				},
			],
		},
	],
}
# print "TREE: {}".format(tree)
# for foo in causal_grammar.generate_parses(tree["children"][0]):
for foo in causal_grammar.generate_parses(tree):
	# print "PARSE: {}".format(foo)
	print causal_grammar.make_tree_like_lisp(foo)
