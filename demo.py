# dict keys are frame numbers
# frames are only reported when a fluent changes, and only for the fluent(s) that changed; fluents are considered to be on or off ("light" is treated as "light_on", and then "light_off" is calculated from that internally, for instance)

import causal_grammar

fluent_parses = {
	1:  { "light": .105, "fluent_3": .511, "fluent_4": .916, "fluent_5": 1.61, "fluent_6": .105 },
	6:  { "light": causal_grammar.kUnknownEnergy, "fluent_6": causal_grammar.kUnknownEnergy},
	16:  { "light": causal_grammar.kUnknownEnergy, "fluent_4": 1.20},
	17: { "fluent_3": causal_grammar.kUnknownEnergy, "fluent_4": 2.30},
	400: { "fluent_5": .223, "light": .105},
}

# dict keys are frame numbers
# frames are only reported when an event completes
# events have energy and agents
temporal_parses = {
	5:  { "E1": {"energy": .105, "agent": "uuid4" } },
	7:  { "E2": {"energy": .511, "agent": "uuid1"}, "E5": {"energy": 1.20, "agent": "uuid2"} },
	10: { "E3": {"energy": .916, "agent": "uuid3" } },
	15: { "E1": {"energy": .223, "agent": "uuid9" } },
}

# our causal forest:
causal_forest = [ {
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
]

# UNCOMMENT NEXT LINE TO LOAD ORIGINAL MATLAB CSV FILE FOR OFFICE SCENE, JUST PULLING LIGHT SWITCH INFO, OVERRIDING TRIVIAL fluent_parses AND temporal_parses ABOVE
fluent_parses, temporal_parses = causal_grammar.import_csv("Exp2_output_data.txt",{"Light_Status": "light"},{"Touch_Switch":"E1"})
causal_grammar.process_events_and_fluents(causal_forest, fluent_parses, temporal_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy)
