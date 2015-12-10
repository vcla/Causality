# dict keys are frame numbers
# frames are only reported when a fluent changes, and only for the fluent(s) that changed; fluents are considered to be on or off ("light" is treated as "light_on", and then "light_off" is calculated from that internally, for instance)


#TODO this is essentially redundant data and SHOULD come from causal_grammar_summerdata.py TODO
#TODO let's try to replace onsoffs (and actionPairings) with a more robust framework...yay...

groupings = dict()
from causal_grammar import TYPE_FLUENT, TYPE_ACTION, kNonActionPenaltyEnergy

# note that "negative" action must be the last one sepecified for proper P/R and there must be only one "no action"
# TODO: above note taken from analyzeData-nearesthuman-pr.py which still needs to be refactored appropriately
def addGrouping(groupings, fluent, related_fluents, related_actions):
	groupings[fluent] = {
		TYPE_FLUENT : related_fluents,
		TYPE_ACTION : related_actions,
	}

addGrouping(groupings, 'thirst',
		{ 'thirst' : ["not_thirsty","thirsty_not","thirsty","not",] },
		{ 'water_action' : ["act_drink","act_no_drink",], },
)

# TODO: maybe this is why we think we need 'cup' toplevel instead of 'water' (or vice-versa)???
addGrouping(groupings, 'cup',
		{ 'cup' : ["more","less","same",], },
	{
		'water_action' : ["act_drink","act_no_drink",],    # this. this is why we can't have nice things.
		'dispense' : ["act_dispensed","act_no_dispense",], # also, this. even more, this.
	},
)

addGrouping(groupings, 'waterstream',
		{ 'waterstream' : ["water_on","water_off",], },
	{
		'water_action' : ["act_drink","act_no_drink",],
		'dispense' : ["act_dispensed","act_no_dispense",],
	},
)

addGrouping(groupings, 'door',
		{ 'door' : ["closed_open","open_closed","open","closed",], },
		{ 'door_action' : ["act_opened","act_closed","act_not_opened_closed",], },
)

addGrouping(groupings, 'doorlock',
		{ 'doorlock' : ["lock_unlocked","unlocked_lock","locked","unlocked",], },
		{ 'doorlock_action' : ["act_knock","act_none",],},
)

addGrouping(groupings, 'phone',
		{ 'phone' : ["off_active","active_off","active","off",], 'ringer': ['ring', 'no_ring'], },
		{ 'phone_action' : ["act_received_call","act_no_call",], },
)

addGrouping(groupings, 'trash',
		{ 'trash' : ["more", "less", "same", ], },
		{ 'trash_action' : ['act_benddown', 'act_no_benddown', ], },
)

addGrouping(groupings, 'screen',
		{ 'screen' : ["off_on", "on_off", "on", "off", ], },
		{ 'screen_action' : ['act_mousekeyboard', 'act_no_mousekeyboard', ], },
)

addGrouping(groupings, 'elevator',
		{ 'elevator' : ["closed_open", "open_closed", "open", "closed", ], },
		{ 'elevator_action' : ['act_pushbutton', 'act_no_pushbutton', ], },
)

addGrouping(groupings, 'light',
		{ 'light' : ["off_on", "on_off", "on", "off", ], },
		{ 'light_action' : ['act_pushbutton', 'act_no_pushbutton', ], },
)

def getActionsForMasterFluent(groupings, fluent):
	return groupings[fluent][TYPE_ACTION].keys()

def getFluentsForMasterFluent(groupings, fluent):
	return groupings[fluent][TYPE_FLUENT].keys()

def getMasterFluentsForPrefix(groupings, prefix):
	return [i for i in groupings if prefix in groupings[i][TYPE_FLUENT] or prefix in groupings[i][TYPE_ACTION]]

def getPrefixType(groupings, prefix):
	if [i for i in groupings if prefix in groupings[i][TYPE_FLUENT]]:
		return TYPE_FLUENT
	if [i for i in groupings if prefix in groupings[i][TYPE_ACTION]]:
		return TYPE_ACTION
	raise Exception("prefix not found in groupings: {}".format(prefix))

"""
onsoffs are used by:
	dealWithDBResults ~ buildDictForFluentBetweenFramesIntoResults
	plotResults ~ buildHeatmapForExample STAGE 3 READ CAUSALGRAMMAR RESULTS, seeing if our value changed or stayed the same
actionPairings are used by:
	the same two culprits.
"""
onsoffs = { "door": ["open","closed"], "light": ["on","off"], "screen": ["on","off"], "phone": ["active","off"], "ringer": ["ring","no_ring"] }  #ringer actions: act_received_call, act_no_call <- mean "used phone" or "not".
# filling in these, assuming they're the DB on/off values
onsoffs["thirst"] = ["thirsty", "not"]  #actions: act_drink, act_no_drink, act_dispensed, act_no_dispense (maybe)
onsoffs["waterstream"] = ["water_on", "water_off"] #actions act_dispensed, act_no_dispense
onsoffs["doorlock"] = ["locked", "unlocked"] # TODO: uhoh, the change is lock_unlocked/unlocked_lock. need to catch.  #actions act_knock, act_none
# and these below here are the lovely 3-case answer...
onsoffs["trash"] = ["on", "off"] # actions: act_benddown, act_no_benddown
#TODO: should not have/need both 'cup' and 'water' as top-levels. something here is wrong!
onsoffs["water"] = ["on","off"] # gleep; do we not need cup_MORE, cup_LESS? actions: act_drin, act_no_drink, act_dispensed, act_no_dispense...???
onsoffs["cup"] = ["on","off"] # gleep; do we not need cup_MORE, cup_LESS? actions: act_drin, act_no_drink, act_dispensed, act_no_dispense...???

actionPairings = {
	"screen":(["usecomputer_START","usecomputer_END"],),
	"cup":(["benddown_START","benddown_END"],["drink_START","drink_END"]),
	"waterstream":(["benddown_START","benddown_END"],["drink_START","drink_END"]),
	"door":(["standing_START","standing_END"],),
	"light":(["pressbutton_START","pressbutton_END"],),
	"trash":(["throwtrash_START","throwtrash_END"],),#["PICKUP TRASH]_START","[PICKUP TRASH]_END"],),
}

#water ~ wateraction_#_act_drink, wateraction_#_act_no_drink
#water ~ thirst_#_thirsty, thirst_#_not
#water ~ cup_#_less, cup_#_more, cup_#_same
#waterstream ~ waterstream_#_water_on, waterstream_#_water_off
#waterstream ~ thirst_#_thirsty, thirst_#_not
#waterstream ~ dispense_#_act_dispensed, dispense_#_act_no_dispense
#waterstream ~ cup_#_less, cup_#_more, cup_#_same

# for "file name"-level fluents, what other fluents are important to consider?
fluent_extensions = {
	"water": ["thirst","cup",], # thirst_on, thirst_off
	"waterstream": ["thirst","cup",], # thirst_on, thirst_off
}


if __name__ == '__main__':
	import causal_grammar
	import causal_grammar_summerdata # sets up causal_forest

	kActionDetections = 'results/CVPR2012_reverse_slidingwindow_10_action_detection_logspace'

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
	parser.add_argument('-i','--ignoreoverlaps', action='store_true', required=False, help='skip the "without overlaps" code')
	args = parser.parse_args()

	import_failed = list()
	causal_forest_orig = causal_grammar_summerdata.causal_forest
	withoutoverlaps = not args.ignoreoverlaps
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
		fluent_and_action_xml = causal_grammar.process_events_and_fluents(causal_grammar_summerdata.causal_forest, fluent_parses, temporal_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy, suppress_output = False, handle_overlapping_events = withoutoverlaps)
	if len(import_failed):
		print("FAILED IMPORTING: {}".format(", ".join(import_failed)))
	print groupings
