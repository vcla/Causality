import causal_grammar
import causal_grammar_summerdata_justscreen as causal_grammar_summerdata # sets up causal_forest
# These thresholds tuned for this fluent data because it's not "flipping between on and off", it's 
# flipping "did transition closed to on" and "didn't transition closed to on"
causal_grammar.kFluentThresholdOnEnergy = 0.6892
causal_grammar.kFluentThresholdOffEnergy = 0.6972
examples = ['screen_1_lounge',]

#screen_1_lounge  7f05529dec6a03d3a459fc2ee1969f7f  580  780  
#screen_2_lounge  9b644124fa1eafeb78b4d08652320384  800  800  
#screen_31_9406 74a72568506774709d9c2f2cf3b75e0d 0 200
#screen_58_9404  5b9e2799293b6a2657582cc00cf7bbc8  360  200

for example in examples:
	try:
		fluent_parses, temporal_parses = causal_grammar.import_summerdata(example,'CVPR2012_reverse_slidingwindow_action_detection_logspace')
		import pprint
		pp = pprint.PrettyPrinter(indent=1)
		pp.pprint(fluent_parses)
		pp.pprint(temporal_parses)
	except ImportError as ie:
		print("IMPORT FAILED: {}".format(ie))
		import_failed.append(example)
		continue
	#orig_xml = munge_parses_to_xml(fluent_parses,temporal_parses)
	fluent_and_action_xml = causal_grammar.process_events_and_fluents(causal_grammar_summerdata.causal_forest, fluent_parses, temporal_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy, False) # last true: suppress the xml output
	#print orig_xml.toprettyxml(indent="\t")
	print fluent_and_action_xml.toprettyxml(indent="\t")
