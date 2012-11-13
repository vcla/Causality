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
	# AGENT THIRSTY
	("root", "fluent", "thirst_on", .4, False, [ # TODO (amy): adjust probabilities to get good results
			# ON INERTIALLY -- stay thirsty and don't complete drinking
			("and", False, False, .5, False, [
					("leaf", "prev_fluent", "thirst_on", False, False, False),
					("leaf", "nonevent", "drink_END", False, 1, False),
				]
			),
			# STAY ON SIGNALED - drinking signals that the person was thristy 
			("and", False, False, .1, False, [
					("leaf", "prev_fluent", "thirst_on", False, False, False),
					("leaf", "event", "drink_START", False, 1, False),
				]
			),
			# ON SPONTANEOUSLY - fluent staying off timed out
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "thirst_off", False, False, False),
					# node_type, symbol_type, symbol, probability, timeout, children
					("leaf", "jump", "become_thirsty", lambda t1, t2: weibull(t1,t2,600,1.5), False, False, "thirst_off"), # TODO: add "jump" for node type -- must be paired with "timer" node on other side
				]
			),
		],
	),
	# AGENT SATIATED (AGENT_THIRSTY_OFF)
	("root", "fluent", "thirst_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "thirst_off", False, False, False),
					("leaf", "timer", "become_thirsty", lambda t1, t2: weibull(t1,t2,600,1.5), False, False, "thirst_on"), # TODO: does this need a new node symbol?
					# TODO: add "timer" for node type.  where do i put the probability on the duration? put it in hte probability slot? also: how to handle unknown time when the scene starts this way?
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "thirst_on", False, False, False),
					("leaf", "event", "drink_END", False, 1, False)
				]
			)
		]
	),
	# cup MORE # TODO on updating db -- merge cup_MORE with cup_LESS for answering queries
	("root", "fluent", "cup_MORE_on", .4, False, [
			# ON CAUSALLY (NEVER ON INERTIALLY)
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_MORE_on", False, False, False),
					("leaf", "event", "benddown_END", False, 1, False), # TODO (amy): maybe ONGOING?
				]
			),
			# ON CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_MORE_off", False, False, False),
					("leaf", "event", "benddown_END", False, 1, False) # TODO (amy): maybe ONGOING?
				]
			)
		]
	),
	# cup MORE OFF (STAYS)
	("root", "fluent", "cup_MORE_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_MORE_off", False, False, False),
					("leaf", "nonevent", "benddown_END", False, 1, False), # TODO (amy): maybe ONGOING?
				]
			),
			# OFF CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_MORE_on", False, False, False),
					("leaf", "nonevent", "benddown_END", False, 1, False), # TODO (amy): maybe ONGOING?
				]
			)
		]
	),
	# cup LESS 
	("root", "fluent", "cup_LESS_on", .4, False, [
			# ON CAUSALLY (NEVER ON INERTIALLY)
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_LESS_on", False, False, False),
					("leaf", "event", "drink_END", False, 1, False), # TODO (amy): maybe ONGOING?
				]
			),
			# ON CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_LESS_off", False, False, False),
					("leaf", "event", "drink_END", False, 1, False) # TODO (amy): maybe ONGOING?
				]
			)
		]
	),
	# cup LESS OFF (STAYS)
	("root", "fluent", "cup_LESS_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_LESS_off", False, False, False),
					("leaf", "nonevent", "drink_END", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_LESS_on", False, False, False),
					("leaf", "nonevent", "drink_END", False, 1, False),
				]
			)
		]
	),
	# WATER STREAM ON
	("root", "fluent", "water_on", .4, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "water_on", False, False, False),
					("leaf", "nonevent", "benddown_END", False, 1, False), # or ONGOING? TODO -- or is this how we signal "ongoing"?
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "water_off", False, False, False),
					("leaf", "event", "benddown_START", False, 1, False),
				]
			)
		]
	),
	# WATER STREAM OFF (water_on_OFF)
	("root", "fluent", "water_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "water_off", False, False, False),
					("leaf", "nonevent", "benddown_START", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "water_on", False, False, False),
					("leaf", "event", "benddown_END", False, 1, False)
				]
			)
		]
	),
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
					("leaf", "event", "standing_END", False, 1, False),
				]
			),
		]
	),
	# PHONE ACTIVE
	("root", "fluent", "PHONE_ACTIVE_on", .4, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "PHONE_ACTIVE_on", False, False, False),
					("leaf", "nonevent", "makecall_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "PHONE_ACTIVE_off", False, False, False),
					("leaf", "event", "makecall_START", False, 1, False),
				]
			)
		]
	),
	# PHONE STANDBY (PHONE_ACTIVE_OFF)
	("root", "fluent", "PHONE_ACTIVE_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "PHONE_ACTIVE_off", False, False, False),
					("leaf", "nonevent", "makecall_START", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "PHONE_ACTIVE_on", False, False, False),
					("leaf", "event", "makecall_END", False, 1, False)
				]
			)
		]
	),
	# LIGHT ON
	("root", "fluent", "light_on", .6, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "light_on", False, False, False),
					("leaf", "nonevent", "pushbutton_START",  False, 10, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "light_off", False, False, False),
					("leaf", "event", "pushbutton_START",  False, 10, False),
				]
			)
		]
	),
	# LIGHT OFF	(LIGHT_ON_OFF)
	("root", "fluent", "light_off", .4, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "light_off", False, False, False),
					("leaf", "nonevent", "pushbutton_START",  False, 10, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "light_on", False, False, False),
					("leaf", "event", "pushbutton_START",  False, 10, False),
				]
			)
		]
	),
	# TRASH MORE
	("root", "fluent", "trash_MORE_on", .4, False, [
			# ON CAUSALLY (NEVER ON INERTIALLY)
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "trash_MORE_on", False, False, False),
					("leaf", "event", "throwtrash_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "trash_MORE_off", False, False, False),
					("leaf", "event", "throwtrash_END", False, 1, False)
				]
			)
		]
	),
	# TRASH MORE OFF (STAYS)
	("root", "fluent", "trash_MORE_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "trash_MORE_off", False, False, False),
					("leaf", "nonevent", "throwtrash_END", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "trash_MORE_on", False, False, False),
					("leaf", "nonevent", "throwtrash_END", False, 1, False),
				]
			)
		]
	),
	# TRASH LESS # NOTE: event described here never happens in XML
	("root", "fluent", "TRASH_LESS_on", .4, False, [
			# ON CAUSALLY (NEVER ON INERTIALLY)
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "TRASH_LESS_on", False, False, False),
					("leaf", "event", "[PICKUP TRASH]_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "TRASH_LESS_off", False, False, False),
					("leaf", "event", "[PICKUP TRASH]_END", False, 1, False)
				]
			)
		]
	),
	# TRASH LESS OFF (STAYS)
	("root", "fluent", "TRASH_LESS_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "TRASH_LESS_off", False, False, False),
					("leaf", "nonevent", "[PICKUP TRASH]_END", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "TRASH_LESS_on", False, False, False),
					("leaf", "nonevent", "[PICKUP TRASH]_END", False, 1, False),
				]
			)
		]
	),
	# SCREEN ON
	("root", "fluent", "screen_on", .4, False, [
			# ON INERTIALLY -- stay screen
			("and", False, False, .5, False, [
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "nonevent", "usecomputer_END", False, 1, False),
				]
			),
			# ON INERTIALLY -- on timer -- STAY ON SIGNALED
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "timer", "become_screensaver", lambda t1, t2: weibull(t1,t2,600,1.5), False, False, "screen_off"), # TODO: put in different probability
				]
			),
			# ON CAUSALLY
			("and", False, False, .1, False, [
					("leaf", "prev_fluent", "screen_off", False, False, False),
					("leaf", "event", "usecomputer_START", False, 1, False),
				]
			),
			# ON SPONTANEOUSLY - TODO
		]
	),
	# SCREEN OFF
	("root", "fluent", "screen_off", .6, False, [
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "event", "usecomputer_END", False, 1, False)
				]
			),
			# OFF SPONTANEOUSLY - fluent staying on timed out (SCREENSAVER ACTIVATED)
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "jump", "become_screensaver", lambda t1, t2: weibull(t1,t2,600,1.5), False, False, "screen_on"), # TODO: put in different probability
				]
			),
			# OFF INERTIALLY
			("and", False, False, .4, False, [
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
