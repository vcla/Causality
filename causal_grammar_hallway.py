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

# TODO: unsure of what to put in for probabilities -- using mostly False for now
### GRAMMAR FOR MINGTIAN'S HALLWAY -- NIPS 2012###
abbreviated_hallway_grammar = [
	# DOOR OPEN 
	("root", "fluent", "DOOR_OPEN_on", False, False, [
			# inertially ON
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "DOOR_OPEN_on", False, False, False),
					("leaf", "nonevent", "@TODO@", False, (0,10), False), # TODO: non-action
				]
			),
			# causally ON (open door inside)  # TODO
		]
	),
	# DOOR CLOSED (DOOR OPEN OFF) # TODO
	# ELEVATOR DOOR OPEN # TODO
	# ELEVATOR DOOR CLOSED # TODO
	# LIGHT ON 
	("root", "fluent", "[LIGHT_ON]_on", False, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_on", False, False, False),
					("leaf", "nonevent", "TOUCH_SWITCH_START",  False, (0,10), False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_off", False, False, False),
					("leaf", "event", "TOUCH_SWITCH_START",  False, (0,10), False),
				]
			)
		]
	),
	# LIGHT OFF	(LIGHT_ON_OFF)
	("root", "fluent", "[LIGHT_ON]_off", False, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_off", False, False, False),
					("leaf", "nonevent", "TOUCH_SWITCH_START",  False, (0,10), False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_on", False, False, False),
					("leaf", "event", "TOUCH_SWITCH_START",  False, (0,10), False),
				]
			)
		]
	),
	# WATER STREAM ON
	("root", "fluent", "WATER_STREAM_on", False, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "WATER_STREAM_on", False, False, False),
					("leaf", "nonevent", "[USE FOUNTAIN]_END", False, (0,1), False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "WATER_STREAM_off", False, False, False),
					("leaf", "event", "[USE FOUNTAIN]_START", False, (0,1), False),
				]
			)
		]
	),
	# WATER STREAM OFF (WATERSTREAM_ON_OFF)
	("root", "fluent", "WATER_STREAM_off", False, False, [
			# OFF INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "WATER_STREAM_off", False, False, False),
					("leaf", "nonevent", "[USE FOUNTAIN]_START", False, (0,1), False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "WATER_STREAM_on", False, False, False),
					("leaf", "event", "[USE FOUNTAIN]_END", False, (0,1), False)
				]
			)
		]
	),
	# TRASH MORE
	("root", "fluent", "TRASH_MORE_on", False, False, [
			# ON CAUSALLY (NEVER ON INERTIALLY)
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "TRASH_MORE_on", False, False, False),
					("leaf", "event", "[DROP TRASH]_END", False, (0,1), False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "TRASH_MORE_off", False, False, False),
					("leaf", "event", "[DROP TRASH]_END", False, (0,1), False)
				]
			)
		]
	),
	# TRASH MORE OFF (STAYS)
	("root", "fluent", "TRASH_MORE_off", False, False, [
			# OFF INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "TRASH_MORE_off", False, False, False),
					("leaf", "nonevent", "[DROP TRASH]_END", False, (0,1), False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "TRASH_MORE_on", False, False, False),
					("leaf", "nonevent", "[DROP TRASH]_END", False, (0,1), False),
				]
			)
		]
	),
	# TRASH LESS # TODO: unsure of causal remove trash action
	# TRASH LESS OFF 
	# PHONE RINGING # TODO
	# PHONE NOT RINGING (PHONE_RINGING_OFF)
	# PHONE ACTIVE # TODO
	# PHONE STANDBY (PHONE_ACTIVE_OFF)
	# AGENT THIRSTY
	("root", "fluent", "AGENT_THIRST_on", False, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "AGENT_THIRST_on", False, False, False),
					("leaf", "nonevent", "[USE FOUNTAIN]_END", False, (0,1), False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "AGENT_THIRST_off", False, False, False),
					# TODO: this is the timer one...  unsure of how to put it...  (not an action, but...)
				]
			)
		]
	),
	# AGENT SATIATED (AGENT_THIRSTY_OFF)
	("root", "fluent", "AGENT_THIRST_off", False, False, [
			# OFF INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "AGENT_THIRST_off", False, False, False),
					# TODO: Timer for on causally
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "AGENT_THIRST_on", False, False, False),
					("leaf", "event", "[USE FOUNTAIN]_END", False, (0,1), False)
				]
			)
		]
	),
	# AGENT HAS TRASH # TODO
	# AGENT DOESN"T HAVE TRASH (AGENT_TRASH_OFF)
]

import causal_grammar
causal_forest = causal_grammar.generate_causal_forest_from_abbreviated_forest(abbreviated_hallway_grammar)
