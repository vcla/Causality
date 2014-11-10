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
	# SCREEN ON
	("root", "fluent", "screen_on", .5, False, [
			# ON INERTIALLY -- stay screen
			("and", False, False, .3, False, [
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "nonevent", "usecomputer_END", False, 1, False),
				]
			),
			# ON INERTIALLY -- on timer -- STAY ON SIGNALED
			#("and", False, False, .6, False, [
			#		("leaf", "prev_fluent", "screen_on", False, False, False),
			#		("leaf", "timer", "become_screensaver", lambda t1, t2: weibull(t1,t2,600,1.5), False, False, "screen_off"), # TODO: put in different probability
			#	]
			#),
			# ON CAUSALLY
			("and", False, False, .7, False, [
					("leaf", "prev_fluent", "screen_off", False, False, False),
					("leaf", "event", "usecomputer_START", False, 20, False),
				]
			),
			# ON SPONTANEOUSLY - TODO
		]
	),
	# SCREEN OFF
	("root", "fluent", "screen_off", .5, False, [
			# OFF CAUSALLY
			#("and", False, False, .3, False, [
			#		("leaf", "prev_fluent", "screen_on", False, False, False),
			#		("leaf", "event", "usecomputer_END", False, 20, False)
			#	]
			#),
			# OFF SPONTANEOUSLY - fluent staying on timed out (SCREENSAVER ACTIVATED)
			#("and", False, False, .4, False, [
			#		("leaf", "prev_fluent", "screen_on", False, False, False),
			#		#("leaf", "jump", "become_screensaver", lambda t1, t2: weibull(t1,t2,600,1.5), False, False, "screen_on"), # TODO: put in different probability
			#	]
			#),
			# OFF INERTIALLY - due to the screensaver kicking on (so causally changed because of non-action)
			("and", False, False, .5, False, [
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "nonevent", "usecomputer_START", False, 100, False),
					("leaf", "nonevent", "usecomputer_END", False, 100, False)
				]
			),
			# OFF INERTIALLY - no change because didn't start using the computer
			("and", False, False, .5, False, [
					("leaf", "prev_fluent", "screen_off", False, False, False),
					("leaf", "nonevent", "usecomputer_START", False, 1, False)
				]
			)
		]
	),
	# TODO: DOORLOCK -- might be possible if standing is good enough
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
