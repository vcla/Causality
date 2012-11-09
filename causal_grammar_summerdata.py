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
	# AGENT THIRSTY
	("root", "fluent", "thirst_on", .4, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "thirst_on", False, False, False),
					("leaf", "nonevent", "act_drink_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "thirst_off", False, False, False),
					("leaf", "event", "act_drink_START", False, 1, False),
					# TODO: this is the timer one...  
				]
			)
		]
	),
	# AGENT SATIATED (AGENT_THIRSTY_OFF)
	("root", "fluent", "thirst_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "thirst_off", False, False, False),
					# TODO: Timer for on causally
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "thirst_on", False, False, False),
					("leaf", "event", "act_drink_END", False, 1, False)
				]
			)
		]
	),
	# cup MORE
	("root", "fluent", "cup_MORE_on", .4, False, [
			# ON CAUSALLY (NEVER ON INERTIALLY)
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_MORE_on", False, False, False),
					("leaf", "event", "act_dispensed_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_MORE_off", False, False, False),
					("leaf", "event", "act_dispensed_END", False, 1, False)
				]
			)
		]
	),
	# cup MORE OFF (STAYS)
	("root", "fluent", "cup_MORE_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_MORE_off", False, False, False),
					("leaf", "nonevent", "act_dispensed_END", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_MORE_on", False, False, False),
					("leaf", "nonevent", "act_dispensed_END", False, 1, False),
				]
			)
		]
	),
	# cup LESS 
	("root", "fluent", "cup_LESS_on", .4, False, [
			# ON CAUSALLY (NEVER ON INERTIALLY)
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_LESS_on", False, False, False),
					("leaf", "event", "act_drink_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_LESS_off", False, False, False),
					("leaf", "event", "act_drink_END", False, 1, False)
				]
			)
		]
	),
	# cup LESS OFF (STAYS)
	("root", "fluent", "cup_LESS_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_LESS_off", False, False, False),
					("leaf", "nonevent", "act_drink_END", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "cup_LESS_on", False, False, False),
					("leaf", "nonevent", "act_drink_END", False, 1, False),
				]
			)
		]
	),
	# WATER STREAM ON
	("root", "fluent", "waterstream_on", .4, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "waterstream_on", False, False, False),
					("leaf", "nonevent", "benddown_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "waterstream_off", False, False, False),
					("leaf", "event", "benddown_START", False, 1, False),
				]
			)
		]
	),
	# WATER STREAM OFF (WATERSTREAM_ON_OFF)
	("root", "fluent", "waterstream_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "waterstream_off", False, False, False),
					("leaf", "nonevent", "benddown_START", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "waterstream_on", False, False, False),
					("leaf", "event", "benddown_END", False, 1, False)
				]
			)
		]
	),
	# DOOR OPEN
	("root", "fluent", "door_open_on", .4, False, [
			# inertially ON
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "door_open_on", False, False, False),
					("leaf", "nonevent", "@TODO@", False, 10, False), # TODO: non-action
				]
			),
			# causally ON (open door inside)  # TODO
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "door_open_off", False, False, False),
					("leaf", "event", "standing_ONGOING", False, 10, False), # TODO: make ONGOING option 
				]
			),
		]
	),
	# DOOR CLOSED (DOOR OPEN OFF) 
	("root", "fluent", "door_open_on", .4, False, [
			# inertially OFF
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "door_open_ooff", False, False, False),
					("leaf", "nonevent", "standing_ONGOING", False, 10, False), # TODO: non-action
				]
			),
			# causally ON (open door inside)  # TODO
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "door_open_off", False, False, False),
					("leaf", "event", "standing_ONGOING", False, 10, False), # TODO: make ONGOING option 
				]
			),
		]
	),
	# TODO: DOORLOCK -- might be possible if standing is good enough
	# PHONE ACTIVE
	("root", "fluent", "PHONE_ACTIVE_on", .4, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "PHONE_ACTIVE_on", False, False, False),
					("leaf", "nonevent", "[USE CELLPHONE]_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "PHONE_ACTIVE_off", False, False, False),
					("leaf", "event", "[USE CELLPHONE]_START", False, 1, False),
				]
			)
		]
	),
	# PHONE STANDBY (PHONE_ACTIVE_OFF)
	("root", "fluent", "PHONE_ACTIVE_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "PHONE_ACTIVE_off", False, False, False),
					("leaf", "nonevent", "[USE CELLPHONE]_START", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "PHONE_ACTIVE_on", False, False, False),
					("leaf", "event", "[USE CELLPHONE]_END", False, 1, False)
				]
			)
		]
	),
	# TODO
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
	# AGENT HAS TRASH # NOTE: EVENT [REMOVE TRASH] NEVER REALIZED!
	# TODO: This is one of the ones that needs the "reset agent" feature
	("root", "fluent", "AGENT_HAS_TRASH_on", False, False, [
			# ON INERTIALLY
			("and", False, False, .5, False, [
					("leaf", "prev_fluent", "AGENT_HAS_TRASH_on", False, False, False),
					("leaf", "nonevent", "[USE TRASH CAN]_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .5, False, [
					("leaf", "prev_fluent", "AGENT_HAS_TRASH_off", False, False, False),
					("leaf", "event", "[REMOVE TRASH]_START", False, 1, False),
				]
			)
		]
	),
	# AGENT DOESN"T HAVE TRASH (AGENT_TRASH_OFF)
	("root", "fluent", "AGENT_HAS_TRASH_off", False, False, [
			# OFF INERTIALLY
			("and", False, False, .5, False, [
					("leaf", "prev_fluent", "AGENT_HAS_TRASH_off", False, False, False),
					("leaf", "nonevent", "[REMOVE TRASH]_START", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .5, False, [
					("leaf", "prev_fluent", "AGENT_HAS_TRASH_on", False, False, False),
					("leaf", "event", "[USE TRASH CAN]_END", False, 1, False)
				]
			)
		]
	),
]
"""
	### NOT INCLUDED ###
	# ELEVATOR DOOR OPEN # TODO
	# ELEVATOR DOOR CLOSED # TODO
	# PHONE RINGING #
	# PHONE NOT RINGING (PHONE_RINGING_OFF)
	# AGENT HAS PHONE/NOT
"""

import causal_grammar
causal_forest = causal_grammar.generate_causal_forest_from_abbreviated_forest(abbreviated_hallway_grammar)
