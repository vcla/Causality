### HALLWAY GRAMMAR ###
#("node_type", "symbol_type", "symbol", probability, timeout, [children])
"""
abbreviated_hallway_grammar = [
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
### GRAMMAR FOR MINGTIAN'S HALLWAY -- NIPS 2012###
abbreviated_hallway_grammar = [
	# LIGHT ON
	("root", "fluent", "[LIGHT_ON]_on", .6, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_on", False, False, False),
					("leaf", "nonevent", "TOUCH_SWITCH_START",  False, 10, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_off", False, False, False),
					("leaf", "event", "TOUCH_SWITCH_START",  False, 10, False),
				]
			)
		]
	),
	# LIGHT OFF	(LIGHT_ON_OFF)
	("root", "fluent", "[LIGHT_ON]_off", .4, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_off", False, False, False),
					("leaf", "nonevent", "TOUCH_SWITCH_START",  False, 10, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_on", False, False, False),
					("leaf", "event", "TOUCH_SWITCH_START",  False, 10, False),
				]
			)
		]
	),
	# WATER STREAM ON
	("root", "fluent", "WATER_STREAM_on", .4, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "WATER_STREAM_on", False, False, False),
					("leaf", "nonevent", "[USE FOUNTAIN]_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "WATER_STREAM_off", False, False, False),
					("leaf", "event", "[USE FOUNTAIN]_START", False, 1, False),
				]
			)
		]
	),
	# WATER STREAM OFF (WATERSTREAM_ON_OFF)
	("root", "fluent", "WATER_STREAM_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "WATER_STREAM_off", False, False, False),
					("leaf", "nonevent", "[USE FOUNTAIN]_START", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "WATER_STREAM_on", False, False, False),
					("leaf", "event", "[USE FOUNTAIN]_END", False, 1, False)
				]
			)
		]
	),
	# TRASH MORE
	("root", "fluent", "TRASH_MORE_on", .4, False, [
			# ON CAUSALLY (NEVER ON INERTIALLY)
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "TRASH_MORE_on", False, False, False),
					("leaf", "event", "[DROP TRASH]_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "TRASH_MORE_off", False, False, False),
					("leaf", "event", "[DROP TRASH]_END", False, 1, False)
				]
			)
		]
	),
	# TRASH MORE OFF (STAYS)
	("root", "fluent", "TRASH_MORE_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "TRASH_MORE_off", False, False, False),
					("leaf", "nonevent", "[DROP TRASH]_END", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "TRASH_MORE_on", False, False, False),
					("leaf", "nonevent", "[DROP TRASH]_END", False, 1, False),
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
	# AGENT THIRSTY
	("root", "fluent", "AGENT_THIRST_on", .4, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "AGENT_THIRST_on", False, False, False),
					("leaf", "nonevent", "[USE FOUNTAIN]_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "AGENT_THIRST_off", False, False, False),
					("leaf", "event", "[USE FOUNTAIN]_START", False, 1, False), # added to force the issue
					# TODO: this is the timer one...  unsure of how to put it...  (not an action, but...)
				]
			)
		]
	),
	# AGENT SATIATED (AGENT_THIRSTY_OFF)
	("root", "fluent", "AGENT_THIRST_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "AGENT_THIRST_off", False, False, False),
					# TODO: Timer for on causally
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "AGENT_THIRST_on", False, False, False),
					("leaf", "event", "[USE FOUNTAIN]_END", False, 1, False)
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
	# DOOR OPEN
	("root", "fluent", "DOOR_OPEN_on", False, False, [
			# inertially ON
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "DOOR_OPEN_on", False, False, False),
					("leaf", "nonevent", "@TODO@", False, 10, False), # TODO: non-action
				]
			),
			# causally ON (open door inside)  # TODO
		]
	),
	# DOOR CLOSED (DOOR OPEN OFF) # TODO
	# ELEVATOR DOOR OPEN # TODO
	# ELEVATOR DOOR CLOSED # TODO
	# PHONE RINGING #
	# PHONE NOT RINGING (PHONE_RINGING_OFF)
	# AGENT HAS PHONE/NOT
"""

import causal_grammar
causal_forest = causal_grammar.generate_causal_forest_from_abbreviated_forest(abbreviated_hallway_grammar)
