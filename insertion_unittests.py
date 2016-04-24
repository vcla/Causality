import unittest
import causal_grammar
import xml.etree.ElementTree as ET
import xml_stuff

kDebug = True

# our causal forest:
abbreviated_forest = [
	("root", "fluent", "thirst_on", .5, False, [
			("and", False, False, .5, False, [
					("leaf", "prev_fluent", "thirst_on", False, False, False),
					("leaf", "nonevent", "DRINK", False, 1, False)
				]
			),
			("and", False, False, .5, False, [
					("leaf", "prev_fluent", "thirst_off", False, False, False),
					("leaf", "event", "GETTHIRSTY", False, 10, False)
				]
			),
		]
	),
	("root", "fluent", "thirst_off", .5, False, [
			("and", False, False, .5, False, [
					("leaf", "prev_fluent", "thirst_off", False, False, False),
					("leaf", "nonevent", "GETTHIRSTY", False, 1, False)
				]
			),
			("and", False, False, .5, False, [
					("leaf", "prev_fluent", "thirst_on", False, False, False),
					("leaf", "event", "DRINK", False, 10, False)
				]
			),
		]
	),
]

causal_forest_thirst = causal_grammar.generate_causal_forest_from_abbreviated_forest(abbreviated_forest)

"""
causal_forest_thirst = [
{
	"node_type": "root",
	"symbol_type": "fluent",
	"symbol": "thirst_on",
	"children": [
		{ "node_type": "and", "probability": .5, "children": [ #on inertially (NO DRINK)
				{ "node_type": "leaf", "symbol": "thirst_on", "symbol_type": "prev_fluent" },
				{ "node_type": "leaf", "symbol": "DRINK", "symbol_type": "nonevent", "timeout": 1 },
		]},
		{ "node_type": "and", "probability": .5, "children": [ #on by causing action GETTHIRSTY
				{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "thirst_off" },
				{ "node_type": "leaf", "symbol_type": "event", "symbol": "GETTHIRSTY", "timeout": 1 },
			]
		},
	],
}, {
	"node_type": "root",
	"symbol_type": "fluent",
	"symbol": "thirst_off",
	"children": [
		{ "node_type": "and", "probability": .5, "children": [ #off inertially (no GETTHIRSTY)
				{ "node_type": "leaf", "symbol": "thirst_off", "symbol_type": "prev_fluent" },
				{ "node_type": "leaf", "symbol": "GETTHIRSTY", "symbol_type": "nonevent", "timeout": 1 },
		]},
		{ "node_type": "and", "probability": .5, "children": [ #off by causing action DRINK
				{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "thirst_on" },
				{ "node_type": "leaf", "symbol_type": "event", "symbol": "DRINK", "timeout": 1 },
			]
		},
	],
},
]
"""


######################## TEST CLASS: NEED INSERTION ###################
# the ideal result: both thirst on->off's are true, there are thirst off->on's ahead of them
class thirst(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		fluents_simple_thirst = {
			5:  { "thirst": causal_grammar.probability_to_energy(.1)}, #thirst turns off at 5
			20:  { "thirst": causal_grammar.probability_to_energy(.1)}, #thirst turns off at 20
		}
		actions_simple_thirst = {
			4:  { "DRINK": {"energy": causal_grammar.probability_to_energy(.9), "agent": ("uuid4")} }, #energy = .11
			19:  { "DRINK": {"energy": causal_grammar.probability_to_energy(.9), "agent": ("uuid4")} }, #energy = .11
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest_thirst, fluents_simple_thirst, actions_simple_thirst, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,suppress_output = not kDebug, handle_overlapping_events = False)
		cls.root = ET.fromstring(xml_string)
		if kDebug:
			print(xml_string)

	def testThirstyBetweenDrinks(self):
		startframe = 6
		endframe = 19
		thirst_changes = xml_stuff.getFluentChangesForFluentBetweenFrames(self.root, 'thirst', startframe, endframe)
		assert len(thirst_changes) == 1, "found {} changes of thirst between frames {} and {}".format(len(thirst_changes),startframe,endframe)

	def testGetThirstyAction(self):
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root, "GETTHIRSTY", 4, 19)
		assert (action_occurrences == 1), "should have had GETTHIRSTY between 4 and 19, but occurred {}".format(action_occurrences)

"""
	def testFluentTrueChangeState(self):
		light_8 = self.root.findall("./fluent_changes/fluent_change[@frame='8']")
		assert len(light_8) > 0, "should have decided light changed to on at 8; no change detected"
		assert light_8[0].attrib['new_value'] == 'on', "should have decided light changed to on at 8; was: {}".format(light_8[0].attrib['new_value'])

	def testFluentMisdetectedChangeState(self):
		light_6 = self.root.findall("./fluent_changes/fluent_change[@frame='6']")
		assert (not light_6), "should have shown no change at 6; changed to: {}".format(light_6[0].attrib['new_value'])

	def testFluentTooEarlyToo(self):
		frame = 7
		# only returns valid results for changed-on or changed-off, not stayed-on, stayed-off
		fluentDict = dealWithDBResults.buildDictForDumbFluentBetweenFramesIntoResults(self.root, "light", ('light_on','light_off'), 1, frame)
		assert not fluentDict['light_1_light_on_light_off'] and not fluentDict['light_1_light_off_light_on'], "should have had no light status change before {}".format(frame)

	def testFluentTooLate(self):
		frame = 9
		light_changes = xml_stuff.getFluentChangesForFluentBetweenFrames(self.root,'light',frame, 15)
		assert not len(light_changes), "found {} unexpected changes after frame {}".format(len(light_changes),frame)

	def testActionJustRight(self):
		action_occurrences = dealWithDBResults.queryXMLForActionBetweenFrames(self.root,"A1",4,6)
		assert (action_occurrences), "should have had action at 5; n times action occurred: {}".format(action_occurrences)
"""


if __name__ == "__main__":
	unittest.main() # run all tests


