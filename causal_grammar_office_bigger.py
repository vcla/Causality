### GRAMMAR FOR ZHU OFFICE -- NIPS 2012 ###
#("node_type", "symbol_type", "symbol", probability, timeout, [children])
abbreviated_office_grammar = [
	# actions: "walk on floor" "press switch" "drink with cup" "use dispenser" "watch monitor" "use keyboard" "use mouse" "call with phone"
	# LIGHT ON


	### IGNORING ONES BELOW HERE ###
	# TRASH MORE # NOT INCLUDED
	# TRASH LESS # NOT INCLUDED
	# AGENT HAS TRASH # NOT INCLUDED
	# AGENT DOESN"T HAVE TRASH (AGENT_TRASH_OFF) # NOT INCLUDED
	# PHONE RINGING # NOT INCLUDED
	# PHONE RINGING OFF # NOT INCLUDED


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
]


import causal_grammar
causal_forest = causal_grammar.generate_causal_forest_from_abbreviated_forest(abbreviated_office_grammar)
