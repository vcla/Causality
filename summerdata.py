# dict keys are frame numbers
# frames are only reported when a fluent changes, and only for the fluent(s) that changed; fluents are considered to be on or off ("light" is treated as "light_on", and then "light_off" is calculated from that internally, for instance)

import causal_grammar

fluent_parses, temporal_parses = causal_grammar.import_summerdata('door_13_light_3_9406','CVPR2012_slidingwindow_action_detection')
import causal_grammar_summerdata # sets up causal_forest
"""
for tree in causal_grammar_hallway.causal_forest:
	for foo in causal_grammar.generate_parses(tree):
		print causal_grammar.make_tree_like_lisp(foo)

import pprint
pp = pprint.PrettyPrinter(indent=1)
pp.pprint(temporal_parses)
causal_grammar.hr()
pp.pprint(causal_grammar_hallway.causal_forest)
causal_grammar.hr()
"""
causal_grammar.process_events_and_fluents(causal_grammar_summerdata.causal_forest, fluent_parses, temporal_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy)