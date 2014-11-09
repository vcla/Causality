import causal_grammar
import causal_grammar_summerdata_justlight as causal_grammar_summerdata # sets up causal_forest
# These thresholds tuned for this fluent data because it's not "flipping between on and off", it's 
# flipping "did transition closed to on" and "didn't transition closed to on"
causal_grammar.kFluentThresholdOnEnergy = 0.6892
causal_grammar.kFluentThresholdOffEnergy = 0.6972
examples = ['light_5_9406',]
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
