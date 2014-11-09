# This Python file uses the following encoding: utf-8
### SUMMERDATA GRAMMAR ###
#("node_type", "symbol_type", "symbol", probability, timeout, [children])
"""
abbreviated_xxx_grammar = [
	("root", "fluent", "dooropen_on", .5, False, [
			("leaf", "prev_fluent", "dooropen_on", .3, False, False),
			("and", False, False, .7, False, [
					("leaf", "prev_fluent", "dooropen_off", False, False, False),
					("leaf", "event", "OpenDoor", False, False, False)
				]
			)
		]
	),
]
"""

# NOTE: unsure of what to put in for probabilities -- using mostly False for now
### GRAMMAR FOR SUMMER DATA -- CVPR 2012 ###

abbreviated_summerdata_grammar = [
	# LIGHT ON
	("root", "fluent", "light_on", .6, False, [
			# ON INERTIALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "light_on", False, False, False),
					("leaf", "nonevent", "pressbutton_START",  False, 50, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "light_off", False, False, False),
					("leaf", "event", "pressbutton_START",  False, 50, False),
				]
			)
		]
	),
	# LIGHT OFF	(LIGHT_ON_OFF)
	("root", "fluent", "light_off", .4, False, [
			# ON INERTIALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "light_off", False, False, False),
					("leaf", "nonevent", "pressbutton_START",  False, 50, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "light_on", False, False, False),
					("leaf", "event", "pressbutton_START",  False, 50, False),
				]
			)
		]
	),
]
"""
	### NOT INCLUDED ###
	# SKIPPED: ELEVATOR (because this set didn't have elevators)
	# ELEVATOR DOOR OPEN 
	# ELEVATOR DOOR CLOSED 
	# SKIPPED: add "ringing"...  don't have enough action information for this
	# PHONE RINGING #
	# PHONE NOT RINGING (PHONE_RINGING_OFF)
	# AGENT HAS PHONE/NOT
"""

import causal_grammar
causal_forest = causal_grammar.generate_causal_forest_from_abbreviated_forest(abbreviated_summerdata_grammar)
