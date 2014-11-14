# dict keys are frame numbers
# frames are only reported when a fluent changes, and only for the fluent(s) that changed; fluents are considered to be on or off ("light" is treated as "light_on", and then "light_off" is calculated from that internally, for instance)

import causal_grammar
import causal_grammar_summerdata # sets up causal_forest

kActionDetections = 'CVPR2012_reverse_slidingwindow_action_detection_logspace'

# These thresholds tuned for this fluent data because it's not "flipping between on and off", it's 
# flipping "did transition closed to on" and "didn't transition closed to on"
causal_grammar.kFluentThresholdOnEnergy = 0.6892
causal_grammar.kFluentThresholdOffEnergy = 0.6972

### TODO: deal with trash_6_phone_11_screen_22 because it has timer/jump 
#screen_1_lounge  7f05529dec6a03d3a459fc2ee1969f7f  580  780  
#screen_2_lounge  9b644124fa1eafeb78b4d08652320384  800  800  
#screen_31_9406 74a72568506774709d9c2f2cf3b75e0d 0 200
#screen_58_9404  5b9e2799293b6a2657582cc00cf7bbc8  360  200
#screen_7_lounge	db522a17f579f477a82bfd694aad2378	0	400

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-s","--simplify", action="store_true", required=False, help="simplify the summerdata grammar to only include fluents that start with the example name[s]")
parser.add_argument("example", nargs="+", action="store", help="specific example[s] to run, such as screen_1_lounge, light_5_9406, or door_11_9406")
args = parser.parse_args()

causal_forest_orig = causal_grammar_summerdata.causal_forest

for example in args.example:
	try:
		if args.simplify:
			#TODO: does not work on door_13_light_3_roomname, for instance. could/should split
			# prune causal forest to 'screen' events
			causal_forest = []
			fluent = example.split("_",1)[0]
			for root in causal_forest_orig:
				if root['symbol'].startswith(fluent + "_"):
					causal_forest.append(root)
			causal_grammar_summerdata.causal_forest = causal_forest
		fluent_parses, temporal_parses = causal_grammar.import_summerdata(example,kActionDetections)
		import pprint
		pp = pprint.PrettyPrinter(indent=1)
		pp.pprint(fluent_parses)
		pp.pprint(temporal_parses)
	except ImportError as ie:
		print("IMPORT FAILED: {}".format(ie))
		import_failed.append(example)
		continue
	fluent_and_action_xml = causal_grammar.process_events_and_fluents(causal_grammar_summerdata.causal_forest, fluent_parses, temporal_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy, False) # last true: suppress the xml output
