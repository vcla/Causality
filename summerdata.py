# dict keys are frame numbers
# frames are only reported when a fluent changes, and only for the fluent(s) that changed; fluents are considered to be on or off ("light" is treated as "light_on", and then "light_off" is calculated from that internally, for instance)

import causal_grammar

### TODO: deal with trash_6_phone_11_screen_22 because it has timer/jump 
#fluent_parses, temporal_parses = causal_grammar.import_summerdata('door_13_light_3_9406','CVPR2012_reverse_slidingwindow_action_detection')
fluent_parses, temporal_parses = causal_grammar.import_summerdata('door_1_8145','CVPR2012_reverse_slidingwindow_action_detection')
#import causal_grammar_summerdata_justdoor as causal_grammar_summerdata # sets up causal_forest
import causal_grammar_summerdata as causal_grammar_summerdata # sets up causal_forest
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
# These thresholds tuned for this fluent data because it's not "flipping between on and off", it's 
# flipping "did transition closed to on" and "didn't transition closed to on"
causal_grammar.kFluentThresholdOnEnergy = 0.6892
causal_grammar.kFluentThresholdOffEnergy = 0.6972
causal_grammar.process_events_and_fluents(causal_grammar_summerdata.causal_forest, fluent_parses, temporal_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy)
