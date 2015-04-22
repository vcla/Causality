# dict keys are frame numbers
# frames are only reported when a fluent changes, and only for the fluent(s) that changed; fluents are considered to be on or off ("light" is treated as "light_on", and then "light_off" is calculated from that internally, for instance)

onsoffs = { "door": ["open","closed"], "light": ["on","off"], "screen": ["on","off"], "phone": ["active","off"], "ringer": ["ring","no_ring"] }  #ringer actions: act_received_call, act_no_call <- mean "used phone" or "not".
# filling in these, assuming they're the DB on/off values
onsoffs["thirst"] = ["thirsty", "not"]  #actions: act_drink, act_no_drink, act_dispensed, act_no_dispense (maybe)
onsoffs["waterstream"] = ["water_on", "water_off"] #actions act_dispensed, act_no_dispense
onsoffs["doorlock"] = ["locked", "unlocked"] # TODO: uhoh, the change is lock_unlocked/unlocked_lock. need to catch.  #actions act_knock, act_none
# and these below here are the lovely 3-case answer...
# onsoffs["trash"] = ["more", "less", "same"] # actions: act_benddown, act_no_benddown
# onsoffs["water"] = ["more", "less", "same"]  # actions:  act_drink, act_no_drink, act_dispensed, act_no_dispense, 

actionPairings = {
	"screen":(["usecomputer_START","usecomputer_END"],),
	#"water":(["benddown_START","benddown_END"],["drink_START","drink_END"]),
	"door":(["standing_START","standing_END"],),
	"light":(["pressbutton_START","pressbutton_END"],),
	#"trash":(["throwtrash_START","throwtrash_END"],["PICKUP TRASH]_START","[PICKUP TRASH]_END"],),
}

if __name__ == '__main__':
	import causal_grammar
	import causal_grammar_summerdata # sets up causal_forest

	kActionDetections = 'results/CVPR2012_reverse_slidingwindow_action_detection_logspace'

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

	import_failed = list()
	causal_forest_orig = causal_grammar_summerdata.causal_forest
	for example in args.example:
		try:
			if args.simplify:
				causal_grammar_summerdata.causal_forest = causal_grammar.get_simplified_forest_for_example(causal_forest_orig, example)
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
	if len(import_failed):
		print("FAILED IMPORTING: {}".format(", ".join(import_failed)))
