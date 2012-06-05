### GRAMMAR FOR ZHU OFFICE -- NIPS 2012 ###
#("node_type", "symbol_type", "symbol", probability, timeout, [children])
abbreviated_office_grammar = [
	# actions: "walk on floor" "press switch" "drink with cup" "use dispenser" "watch monitor" "use keyboard" "use mouse" "call with phone"
	# LIGHT ON
	("root", "fluent", "[LIGHT_ON]_on", .6, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_on", False, False, False),
					("leaf", "nonevent", "press switch_START",  False, 10, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_off", False, False, False),
					("leaf", "event", "press switch_START",  False, 10, False),
				]
			)
		]
	),
	# LIGHT OFF	(LIGHT_ON_OFF)
	("root", "fluent", "[LIGHT_ON]_off", .4, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_off", False, False, False),
					("leaf", "nonevent", "press switch_START",  False, 10, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_on", False, False, False),
					("leaf", "event", "press switch_START",  False, 10, False),
				]
			)
		]
	),
	# CUP MORE -- NOTE if implementation fails for some reason, i moved probabilities around on this one
	("root", "fluent", "[cup_MORE]_on", .4, False, [
			# ON CAUSALLY (NEVER ON INERTIALLY)
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "[cup_MORE]_on", False, False, False),
					("leaf", "event", "use dispenser_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "[cup_MORE]_off", False, False, False),
					("leaf", "event", "use dispenser_END", False, 1, False),
				]
			)
		]
	),
	# CUP MORE OFF (STAYS)
	("root", "fluent", "[cup_MORE]_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "[cup_MORE]_off", False, False, False),
					("leaf", "nonevent", "use dispenser_END", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "[cup_MORE]_on", False, False, False),
					("leaf", "nonevent", "use dispenser_END", False, 1, False),
				]
			)
		]
	),
	# CUP LESS -- NOTE if implementation fails for some reason, i moved probabilities around on this one
	("root", "fluent", "[cup_LESS]_on", .4, False, [
			# ON CAUSALLY (NEVER ON INERTIALLY)
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "[cup_LESS]_on", False, False, False),
					("leaf", "event", "drink with cup_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "[cup_LESS]_off", False, False, False),
					("leaf", "event", "drink with cup_END", False, 1, False),
				]
			)
		]
	),
	# CUP LESS OFF (STAYS)
	("root", "fluent", "[cup_LESS]_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "[cup_LESS]_off", False, False, False),
					("leaf", "nonevent", "drink with cup_END", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, False, False, [
					("leaf", "prev_fluent", "[cup_LESS]_on", False, False, False),
					("leaf", "nonevent", "drink with cup_END", False, 1, False),
				]
			)
		]
	),
	# WATER STREAM ON 
	("root", "fluent", "WATER_STREAM_on", .4, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "WATER_STREAM_on", False, False, False),
					("leaf", "nonevent", "use dispenser_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "WATER_STREAM_off", False, False, False),
					("leaf", "event", "use dispenser_START", False, 1, False),
				]
			)
		]
	),
	# WATER STREAM OFF (WATERSTREAM_ON_OFF)
	("root", "fluent", "WATER_STREAM_off", .6, False, [
			# OFF INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "WATER_STREAM_off", False, False, False),
					("leaf", "nonevent", "use dispenser_START", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "WATER_STREAM_on", False, False, False),
					("leaf", "event", "use dispenser_END", False, 1, False)
				]
			)
		]
	),
	# AGENT THIRSTY
	("root", "fluent", "AGENT_THIRST_on", .4, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "AGENT_THIRST_on", False, False, False),
					("leaf", "nonevent", "drink with cup_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "AGENT_THIRST_off", False, False, False),
					("leaf", "event", "drink with cup_START", False, 1, False),
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
					("leaf", "nonevent", "drink with cup_START", False, 1, False),
					# TODO: Timer for on causally
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "AGENT_THIRST_on", False, False, False),
					("leaf", "event", "drink with cup_END", False, 1, False)
				]
			)
		]
	),
	# PHONE ACTIVE
	("root", "fluent", "PHONE_ACTIVE_on", False, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "PHONE_ACTIVE_on", False, False, False),
					("leaf", "nonevent", "call with phone_END", False, 1, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "PHONE_ACTIVE_off", False, False, False),
					("leaf", "event", "call with phone_START", False, 1, False),
				]
			)
		]
	),
	# PHONE STANDBY
	("root", "fluent", "PHONE_ACTIVE_off", False, False, [
			# OFF INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "PHONE_ACTIVE_off", False, False, False),
					("leaf", "nonevent", "call with phone_START", False, 1, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "PHONE_ACTIVE_on", False, False, False),
					("leaf", "event", "call with phone_END", False, 1, False)
				]
			)
		]
	),
]
"""



	### IGNORING ONES BELOW HERE ###
	# TRASH MORE # NOT INCLUDED
	# TRASH LESS # NOT INCLUDED
	# AGENT HAS TRASH # NOT INCLUDED
	# AGENT DOESN"T HAVE TRASH (AGENT_TRASH_OFF) # NOT INCLUDED
	# PHONE RINGING # NOT INCLUDED
	# PHONE RINGING OFF # NOT INCLUDED


TODO: BROKEN!!!!
	# MONITOR DISPLAY ON TODO
	("root", "fluent", "[monitor_display]_on", .5, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "[monitor_display]_on", False, False, False),
					#("leaf", "nonevent", "use keyboard_END",  False, 10, False),
				]
			),
			# ON CAUSALLY - KEYBOARD
			("and", False, False, .4, False, [
					#("leaf", "prev_fluent", "[monitor_display]_off", False, False, False),
					("leaf", "event", "use keyboard_START",  False, 1, False),
				]
			),
			# ON CAUSALLY - MOUSE
			("and", False, False, .4, False, [
					#("leaf", "prev_fluent", "[monitor_display]_off", False, False, False),
					("leaf", "event", "use mouse_START",  False, 1, False),
				]
			)
		]
	),
	# MONITOR DISPLAY OFF TODO
	("root", "fluent", "[monitor_display]_off", .5, False, [
			# OFF INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "[monitor_display]_off", False, False, False),
					#("leaf", "nonevent", "use keyboard_END",  False, 10, False),
				]
			),
			# OFF CAUSALLY - KEYBOARD
			("and", False, False, .4, False, [
					#("leaf", "prev_fluent", "[monitor_display]_on", False, False, False),
					("leaf", "nonevent", "use keyboard_START",  False, 1, False),
				]
			),
			# ON CAUSALLY - MOUSE
			("and", False, False, .4, False, [
					#("leaf", "prev_fluent", "[monitor_display]_on", False, False, False),
					("leaf", "nonevent", "use mouse_START",  False, 1, False),
				]
			)
		]
	),
	# MONITOR POWER ON TODO

"""
"""	("root", "fluent", "[LIGHT_ON]_on", False, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_on", False, False, False),
					("leaf", "nonevent", "press switch_START",  False, 10, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_off", False, False, False),
					("leaf", "event", "press switch_START",  False, 10, False),
				]
			)
		]
	),
	# LIGHT OFF	(LIGHT_ON_OFF)
	("root", "fluent", "[LIGHT_ON]_off", False, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_off", False, False, False),
					("leaf", "nonevent", "press switch_START",  False, 10, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_on", False, False, False),
					("leaf", "event", "press switch_START",  False, 10, False),
				]
			)
		]
	),
	# MONITOR POWER OFF TODO
	# COMPUTER AWAKE ON TODO
	("root", "fluent", "[LIGHT_ON]_on", False, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_on", False, False, False),
					("leaf", "nonevent", "press switch_START",  False, 10, False),
				]
			),
			# ON CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_off", False, False, False),
					("leaf", "event", "press switch_START",  False, 10, False),
				]
			)
		]
	),
	# LIGHT OFF	(LIGHT_ON_OFF)
	("root", "fluent", "[LIGHT_ON]_off", False, False, [
			# ON INERTIALLY
			("and", False, False, .6, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_off", False, False, False),
					("leaf", "nonevent", "press switch_START",  False, 10, False),
				]
			),
			# OFF CAUSALLY
			("and", False, False, .4, False, [
					("leaf", "prev_fluent", "[LIGHT_ON]_on", False, False, False),
					("leaf", "event", "press switch_START",  False, 10, False),
				]
			)
		]
	),
	# COMPUTER AWAKE OFF TODO
"""


import causal_grammar
causal_forest = causal_grammar.generate_causal_forest_from_abbreviated_forest(abbreviated_office_grammar)
