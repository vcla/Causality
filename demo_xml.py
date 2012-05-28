# dict keys are frame numbers
# frames are only reported when a fluent changes, and only for the fluent(s) that changed; fluents are considered to be on or off ("light" is treated as "light_on", and then "light_off" is calculated from that internally, for instance)

import causal_grammar

# our causal forest:
causal_forest = [
{
	"node_type": "root",
	"symbol_type": "fluent",
	"symbol": "light_on",
	"children": [
		{ "node_type": "leaf", "probability": .3, "symbol": "light_on", "symbol_type": "prev_fluent" },
		{ "node_type": "and", "probability": .7, "children": [
				{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_off" },
				{ "node_type": "leaf", "symbol_type": "event", "symbol": "E1", "timeout": 10 },
			]
		},
	],
}, {
	"node_type": "root",
	"symbol_type": "fluent",
	"symbol": "light_off",
	"children": [
		{ "node_type": "leaf", "probability": .3, "symbol_type":"prev_fluent", "symbol": "light_off" },
		{ "node_type": "and", "probability": .7, "children": [
				{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_on" },
				{ "node_type": "leaf", "symbol_type": "event", "symbol": "E1", "timeout": 10 },
			]
		},
	],
},
{
	"node_type": "root",
	"symbol_type": "fluent",
	"symbol": "dooropen_on",
	"children": [
		{ "node_type": "leaf", "probability": .6, "symbol": "dooropen_on", "symbol_type": "prev_fluent" },
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
		{ "node_type": "leaf", "probability": .6, "symbol_type":"prev_fluent", "symbol": "dooropen_off" },
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

fluent_parses, temporal_parses = causal_grammar.import_xml("pt.xml") #, causal_forest)
print fluent_parses
print temporal_parses
causal_grammar.process_events_and_fluents(causal_forest, fluent_parses, temporal_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy)