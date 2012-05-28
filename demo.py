# dict keys are frame numbers
# frames are only reported when a fluent changes, and only for the fluent(s) that changed; fluents are considered to be on or off ("light" is treated as "light_on", and then "light_off" is calculated from that internally, for instance)

import causal_grammar

fluent_parses = {
	1:  { "light": .105, "fluent_3": .511, "fluent_4": .916, "fluent_5": 1.61, "fluent_6": .105 },
	6:  { "light": causal_grammar.kZeroProbabilityEnergy, "fluent_6": causal_grammar.kZeroProbabilityEnergy},
	16:  { "light": causal_grammar.kZeroProbabilityEnergy, "fluent_4": 1.20},
	17: { "fluent_3": causal_grammar.kZeroProbabilityEnergy, "fluent_4": 2.30},
	400: { "fluent_5": .223, "light": .105},
}

# dict keys are frame numbers
# frames are only reported when an event begins
# events have energy and agents
# it is assumed that the same event /can/ happen multiple times at the same time (multiple people talking on different cell phones, for example)
temporal_parses = {
	5:  { "E1_START": {"energy": .105, "agent": ("uuid4")} },
	6:  { "E1_END": {"energy": .105, "agent": ("uuid4")}, "E5_START": {"energy": 1.20, "agent": ("uuid2") } },
	7:  { "E2_START": {"energy": .511, "agent": ("uuid1") }, "E5_END": {"energy": 1.20, "agent": ("uuid2") } },
	10: { "E3_START": {"energy": .916, "agent": ("uuid3") } },
	15: { "E1_START": {"energy": .223, "agent": ("uuid9") } },
	19: { "E1_END": {"energy": .223, "agent": ("uuid9") } },
	45: { "E3_END": {"energy": .916, "agent": ("uuid3") } },
}

# our causal forest:
causal_forest = [
{
	"node_type": "root",
	"symbol_type": "fluent",
	"symbol": "light_on",
	"children": [
		{ "node_type": "and", "probability": .3, "children": [
				{ "node_type": "leaf", "symbol": "light_on", "symbol_type": "prev_fluent" },
				{ "node_type": "leaf", "symbol": "E1_START", "symbol_type": "nonevent", "timeout": 10 },
		]},
		{ "node_type": "and", "probability": .7, "children": [
				{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_off" },
				{ "node_type": "leaf", "symbol_type": "event", "symbol": "E1_START", "timeout": 10 },
			]
		},
	],
}, {
	"node_type": "root",
	"symbol_type": "fluent",
	"symbol": "light_off",
	"children": [
		{ "node_type": "and", "probability": .3, "children": [
				{ "node_type": "leaf", "symbol": "light_off", "symbol_type": "prev_fluent" },
				{ "node_type": "leaf", "symbol": "E1_START", "symbol_type": "nonevent", "timeout": 10 },
		]},
		{ "node_type": "and", "probability": .7, "children": [
				{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_on" },
				{ "node_type": "leaf", "symbol_type": "event", "symbol": "E1_START", "timeout": 10 },
			]
		},
	],
},
{
	"node_type": "root",
	"symbol_type": "fluent",
	"symbol": "dooropen_on",
	"children": [
		{ "node_type": "inertial", "probability": .6, "symbol": "dooropen_on", "symbol_type": "prev_fluent" },
		{ "node_type": "and", "probability": .2, "children": [
				{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "dooropen_off" },
				{ "node_type": "leaf", "symbol_type": "event", "symbol": "door_open_outside", "timeout": 20 },
			]
		},
		{ "node_type": "and", "probability": .2, "children": [
				{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "dooropen_off" },
				{ "node_type": "leaf", "symbol_type": "event", "symbol": "door_open_inside", "timeout": 20 },
			]
		},
	],
}, {
	"node_type": "root",
	"symbol_type": "fluent",
	"symbol": "dooropen_off",
	"children": [
		{ "node_type": "inertial", "probability": .6, "symbol_type":"prev_fluent", "symbol": "dooropen_off" },
		{ "node_type": "and", "probability": .2, "children": [
				{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "dooropen_on" },
				{ "node_type": "leaf", "symbol_type": "event", "symbol": "door_close_outside", "timeout": 20 },
			]
		},
		{ "node_type": "and", "probability": .2, "children": [
				{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "dooropen_on" },
				{ "node_type": "leaf", "symbol_type": "event", "symbol": "door_close_inside", "timeout": 20 },
			]
		},
	],
},
]

# TRUE NEXT LINE TO LOAD ORIGINAL MATLAB CSV FILE FOR OFFICE SCENE, JUST PULLING LIGHT SWITCH AND DOOR INFO, OVERRIDING TRIVIAL fluent_parses AND temporal_parses ABOVE
if False:
	fluent_maps = {"Light_Status": "light", "Door_Status": "dooropen"}
	event_maps = {"Touch_Switch":"E1", "Close_Door_Inside": "door_close_inside", "Close_Door_Outside": "door_close_outside", "Open_Door_Inside":"door_open_inside", "Open_Door_Outside":"door_open_outside"}
	fluent_parses, temporal_parses = causal_grammar.import_csv("Exp2_output_data.txt",fluent_maps,event_maps)

causal_grammar.process_events_and_fluents(causal_forest, fluent_parses, temporal_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy)
print "BOY HOWDY!"
