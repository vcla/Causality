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
from math import exp, pow

def weibull(t1, t2, lam, k):
	return 1 - exp(pow(t1 / lam,k) - pow(t2 / lam, k))

abbreviated_summerdata_grammar = [
	# DOOR OPEN
	("root", "fluent", "door_on", .4, False, [
			# inertially ON
			("and", False, False, .2, False, [
					("leaf", "prev_fluent", "door_on", False, False, False),
					("leaf", "nonevent", "standing_END", False, 10, False),
				]
			),
			# causally ON
			("and", False, False, .8, False, [
					("leaf", "prev_fluent", "door_off", False, False, False),
					("leaf", "event", "standing_START", False, 50, False), # TODO: make ONGOING option 
					("leaf", "nonevent", "standing_END", False, 1, False), # TODO: make ONGOING option 
				]
			),
		]
	),
	# DOOR CLOSED (DOOR OPEN OFF) 
	("root", "fluent", "door_off", .6, False, [
			# inertially OFF
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "door_off", False, False, False),
					("leaf", "nonevent", "standing_START", False, 10, False), # TODO: make ONGOING nonaction
				]
			),
			# causally OFF
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "door_on", False, False, False),
					("leaf", "event", "standing_END", False, 10, False),
				]
			),
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
