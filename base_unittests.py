import unittest
import causal_grammar
import xml_stuff
import xml.etree.ElementTree as ET

kDebug = True

# our causal forest:
causal_forest_light = [
{
	"node_type": "root",
	"symbol_type": "fluent",
	"symbol": "light_on",
	"children": [
		{ "node_type": "and", "probability": .6, "children": [ #on inertially -- higher chance of occurrence? #energy = .51
				{ "node_type": "leaf", "symbol": "light_on", "symbol_type": "prev_fluent" },
				{ "node_type": "leaf", "symbol": "FLIPSWITCH", "symbol_type": "nonevent", "timeout": 10 },
		]},
		{ "node_type": "and", "probability": .4, "children": [ #on by causing action FLIPSWITCH#energy = .92
				{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_off" },
				{ "node_type": "leaf", "symbol_type": "event", "symbol": "FLIPSWITCH", "timeout": 10 },
			]
		},
	],
}, {
	"node_type": "root",
	"symbol_type": "fluent",
	"symbol": "light_off",
	"children": [
		{ "node_type": "and", "probability": .6, "children": [ #off inertially #energy = .51
				{ "node_type": "leaf", "symbol": "light_off", "symbol_type": "prev_fluent" },
				{ "node_type": "leaf", "symbol": "FLIPSWITCH", "symbol_type": "nonevent", "timeout": 10 },
		]},
		{ "node_type": "and", "probability": .4, "children": [ #off by causing action FLIPSWITCH#energy = .92
				{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_on" },
				{ "node_type": "leaf", "symbol_type": "event", "symbol": "FLIPSWITCH", "timeout": 10 },
			]
		},
	],
},
]


######################## TEST CLASS: 2 FLUENTS, 2nd IS CORRECT ###################
# the ideal result: action at 5, light changes to on at 8
class LightingTestCaseSecondOfTwoFluents(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		fluents_simple_light = {
			6:  { "light": causal_grammar.probability_to_energy(.6)}, #light turns on at 6 -- energy = .51
			8:  { "light": causal_grammar.probability_to_energy(.9)}, #light turns on at 8 -- energy = .11
		}
		actions_simple_light = {
			5:  { "FLIPSWITCH": {"energy": causal_grammar.probability_to_energy(.9), "agent": ("uuid4")} }, #energy = .11
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest_light, fluents_simple_light, actions_simple_light, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug, handle_overlapping_events = True) # !kDebug: suppress output
		cls.root = ET.fromstring(xml_string)
		if kDebug:
			print(xml_string)

	def testFluentZeroState(self):
		light_0 = self.root.findall("./fluent_changes/fluent_change[@frame='0']")
		assert light_0[0].attrib['new_value'] == 'off', "should have decided light started out as off; was: {}".format(light_0[0].attrib['new_value'])

	def testFluentTrueChangeState(self):
		light_8 = self.root.findall("./fluent_changes/fluent_change[@frame='8']")
		assert len(light_8) > 0, "should have decided light changed to on at 8; no change detected"
		assert light_8[0].attrib['new_value'] == 'on', "should have decided light changed to on at 8; was: {}".format(light_8[0].attrib['new_value'])

	def testFluentMisdetectedChangeState(self):
		light_6 = self.root.findall("./fluent_changes/fluent_change[@frame='6']")
		assert (not light_6), "should have shown no change at 6; changed to: {}".format(light_6[0].attrib['new_value'])

	def testFluentTooEarly(self):
		frame = 7
		light_changes = xml_stuff.getFluentChangesForFluentBetweenFrames(self.root, 'light', 0, frame)
		assert not len(light_changes), "found {} unexpected changes before frame {}".format(len(light_changes),frame)

	def testFluentTooEarlyToo(self):
		frame = 7
		# only returns valid results for changed-on or changed-off, not stayed-on, stayed-off
		fluentDict = xml_stuff.buildDictForDumbFluentBetweenFramesIntoResults(self.root, "light", ('light_on','light_off'), 1, frame)
		assert not fluentDict['light_1_light_on_light_off'] and not fluentDict['light_1_light_off_light_on'], "should have had no light status change before {}".format(frame)

	def testFluentTooLate(self):
		frame = 9
		light_changes = xml_stuff.getFluentChangesForFluentBetweenFrames(self.root,'light',frame, 15)
		assert not len(light_changes), "found {} unexpected changes after frame {}".format(len(light_changes),frame)


################## NEW TEST CLASS: ACTION TIME SHOULD BE WHEN ACTION OCCURS ##############
# Answer: action at 5 only (fluent change at 8)
class LightingTestCaseExactActionTime2ndOf2Fluents(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		fluents_simple_light = {
			6:  { "light": causal_grammar.probability_to_energy(.6)}, #light turns on at 6
			8:  { "light": causal_grammar.probability_to_energy(.9)}, #light turns on at 8
		}
		actions_simple_light = {
			5:  { "FLIPSWITCH": {"energy": causal_grammar.probability_to_energy(.9), "agent": ("uuid4")} },
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest_light, fluents_simple_light, actions_simple_light, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug, handle_overlapping_events = True) # !kDebug: suppress output
		cls.root = ET.fromstring(xml_string)
		if kDebug:
			print(xml_string)

	def testActionTooEarly(self):
		#queryXMLForActionBetweenFrames(xml,action,frame1,frame2)
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root,"FLIPSWITCH",0,5)
		assert (not action_occurrences), "should have had no action before 5; n times action occurred: {}".format(action_occurrences)

	def testActionJustRight(self):
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root,"FLIPSWITCH",4,6)
		assert (action_occurrences), "should have had action at 5; n times action occurred: {}".format(action_occurrences)

	def testActionTooLate(self):
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root,"FLIPSWITCH",5,15)
		assert (not action_occurrences), "should have had no action after 5; n times action occurred: {}".format(action_occurrences)


######################## NEW TEST CLASS: 2 FLUENTS, 1st IS CORRECT ###################
# the ideal result: action at 5, light changes to on at 6
class LightingTestCaseFirstOfTwoFluents(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		fluents_simple_light = {
			6:  { "light": causal_grammar.probability_to_energy(.9)}, #light turns on at 6
			8:  { "light": causal_grammar.probability_to_energy(.6)}, #light turns on at 8
		}
		actions_simple_light = {
			5:  { "FLIPSWITCH": {"energy": causal_grammar.probability_to_energy(.9), "agent": ("uuid4")} },
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest_light, fluents_simple_light, actions_simple_light, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug, handle_overlapping_events = True) # !kDebug: suppress output
		cls.root = ET.fromstring(xml_string)
		if kDebug:
			print(xml_string)

	def testFluentZeroState(self):
		light_0 = self.root.findall("./fluent_changes/fluent_change[@frame='0']")
		assert light_0[0].attrib['new_value'] == 'off', "should have decided light started out as off; was: {}".format(light_0[0].attrib['new_value'])

	def testFluentTrueChangeState(self):
		light_6 = self.root.findall("./fluent_changes/fluent_change[@frame='6']")
		assert light_6[0].attrib['new_value'] == 'on', "should have decided light changed to on at 6; was: {}".format(light_6[0].attrib['new_value'])

	def testFluentMisdetectedChangeState(self):
		light_8 = self.root.findall("./fluent_changes/fluent_change[@frame='8']")
		assert (not light_8), "should have shown no change at 8; changed to: {}".format(light_8[0].attrib['new_value'])

	def testFluentTooEarly(self):
		frame = 5
		light_changes = xml_stuff.getFluentChangesForFluentBetweenFrames(self.root,'light',0, frame)
		assert not len(light_changes), "found {} unexpected changes before frame {}".format(len(light_changes),frame)

	def testFluentTooLate(self):
		frame = 7
		light_changes = xml_stuff.getFluentChangesForFluentBetweenFrames(self.root,'light',frame, 15)
		assert not len(light_changes), "found {} unexpected changes after frame {}".format(len(light_changes),frame)


######################## NEW TEST CLASS: ACTION TIME EXACT
# the ideal result: action at 5, light changes to on at 6
class LightingTestCaseExactActionTime1stOf2Fluents(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		fluents_simple_light = {
			6:  { "light": causal_grammar.probability_to_energy(.9)}, #light turns on at 6
			8:  { "light": causal_grammar.probability_to_energy(.6)}, #light turns on at 8
		}
		actions_simple_light = {
			5:  { "FLIPSWITCH": {"energy": causal_grammar.probability_to_energy(.9), "agent": ("uuid4")} },
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest_light, fluents_simple_light, actions_simple_light, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug, handle_overlapping_events = True) # !kDebug: suppress output
		cls.root = ET.fromstring(xml_string)
		if kDebug:
			print(xml_string)

	def testActionTooEarly(self):
		#queryXMLForActionBetweenFrames(xml,action,frame1,frame2)
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root,"FLIPSWITCH",0,5)
		assert (not action_occurrences), "should have had no action before 5; n times action occurred: {}".format(action_occurrences)

	def testActionJustRight(self):
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root,"FLIPSWITCH",4,6)
		assert (action_occurrences), "should have had action at 5; n times action occurred: {}".format(action_occurrences)

	def testActionTooLate(self):
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root,"FLIPSWITCH",5,15)
		assert (not action_occurrences), "should have had no action after 5; n times action occurred: {}".format(action_occurrences)


######################## NEW TEST CLASS: TWO ACTIONS, FIRST BEST
# the ideal result: 
class LightingTestCase1stOf2Actions(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		causal_forest_modified = [
		{
			"node_type": "root",
			"symbol_type": "fluent",
			"symbol": "light_on",
			"children": [
				{ "node_type": "and", "probability": .25, "children": [ #on inertially -- higher chance of occurrence?
						{ "node_type": "leaf", "symbol": "light_on", "symbol_type": "prev_fluent" },
						{ "node_type": "leaf", "symbol": "A3", "symbol_type": "nonevent", "timeout": 10 },
						{ "node_type": "leaf", "symbol": "A4", "symbol_type": "nonevent", "timeout": 10 },
				]},
				{ "node_type": "and", "probability": .375, "children": [ #on by causing action
						{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_off" },
						{ "node_type": "leaf", "symbol_type": "event", "symbol": "FLIPSWITCH", "timeout": 10 },
					]
				},
				{ "node_type": "and", "probability": .375, "children": [ #on by causing action
						{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_off" },
						{ "node_type": "leaf", "symbol_type": "event", "symbol": "A2", "timeout": 10 },
					]
				},
			],
		}, {
			"node_type": "root",
			"symbol_type": "fluent",
			"symbol": "light_off",
			"children": [
				{ "node_type": "and", "probability": .25, "children": [ #off inertially
						{ "node_type": "leaf", "symbol": "light_off", "symbol_type": "prev_fluent" },
						{ "node_type": "leaf", "symbol": "FLIPSWITCH", "symbol_type": "nonevent", "timeout": 10 },
						{ "node_type": "leaf", "symbol": "A2", "symbol_type": "nonevent", "timeout": 10 },
				]},
				{ "node_type": "and", "probability": .375, "children": [ #off by causing action
						{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_on" },
						{ "node_type": "leaf", "symbol_type": "event", "symbol": "A3", "timeout": 10 },
					]
				},
				{ "node_type": "and", "probability": .375, "children": [ #off by causing action
						{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_on" },
						{ "node_type": "leaf", "symbol_type": "event", "symbol": "A4", "timeout": 10 },
					]
				},
			],
		},
		]
		fluents_simple_light = {
			8:  { "light": causal_grammar.probability_to_energy(.9)}, #light turns on at 8
		}
		actions_simple_light = {
			5:  { "FLIPSWITCH": {"energy": causal_grammar.probability_to_energy(.9), "agent": ("uuid4")} },
			6:  { "A2": {"energy": causal_grammar.probability_to_energy(.6), "agent": ("uuid4")} },
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest_modified, fluents_simple_light, actions_simple_light, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug, handle_overlapping_events = True) # !kDebug: suppress output
		cls.root = ET.fromstring(xml_string)
		if kDebug:
			print(xml_string)

	def testCorrectAction(self):
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root,"FLIPSWITCH",0,15)
		assert (action_occurrences == 1), "should have had action FLIPSWITCH; n times action occurred: {}".format(action_occurrences)

	def testNotIncorrectAction(self):
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root,"A2",0,15)
		action_occurrences += xml_stuff.queryXMLForActionBetweenFrames(self.root,"A3",0,15)
		action_occurrences += xml_stuff.queryXMLForActionBetweenFrames(self.root,"A4",0,15)
		assert (not action_occurrences), "should not have had action A2; n times action occurred: {}".format(action_occurrences)


######################## NEW TEST CLASS: TWO ACTIONS, SECOND BEST
# the ideal result:  action 
class LightingTestCase2ndOf2Actions(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		causal_forest_modified = [
		{
			"node_type": "root",
			"symbol_type": "fluent",
			"symbol": "light_on",
			"children": [
				{ "node_type": "and", "probability": .4, "children": [ #on inertially -- higher chance of occurrence?
						{ "node_type": "leaf", "symbol": "light_on", "symbol_type": "prev_fluent" },
						{ "node_type": "leaf", "symbol": "FLIPSWITCH", "symbol_type": "nonevent", "timeout": 10 },
						{ "node_type": "leaf", "symbol": "A2", "symbol_type": "nonevent", "timeout": 10 },
				]},
				{ "node_type": "and", "probability": .3, "children": [ #on by causing action
						{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_off" },
						{ "node_type": "leaf", "symbol_type": "event", "symbol": "FLIPSWITCH", "timeout": 10 },
					]
				},
				{ "node_type": "and", "probability": .3, "children": [ #on by causing action
						{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_off" },
						{ "node_type": "leaf", "symbol_type": "event", "symbol": "A2", "timeout": 10 },
					]
				},
			],
		}, {
			"node_type": "root",
			"symbol_type": "fluent",
			"symbol": "light_off",
			"children": [
				{ "node_type": "and", "probability": .4, "children": [ #off inertially
						{ "node_type": "leaf", "symbol": "light_off", "symbol_type": "prev_fluent" },
						{ "node_type": "leaf", "symbol": "FLIPSWITCH", "symbol_type": "nonevent", "timeout": 10 },
				]},
				{ "node_type": "and", "probability": .3, "children": [ #off by causing action
						{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_on" },
						{ "node_type": "leaf", "symbol_type": "event", "symbol": "A3", "timeout": 10 },
					]
				},
				{ "node_type": "and", "probability": .3, "children": [ #off by causing action
						{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_on" },
						{ "node_type": "leaf", "symbol_type": "event", "symbol": "A4", "timeout": 10 },
					]
				},
			],
		},
		]
		fluents_simple_light = {
			8:  { "light": causal_grammar.probability_to_energy(.9)}, #light turns on at 8
		}
		actions_simple_light = {
			5:  { "FLIPSWITCH": {"energy": causal_grammar.probability_to_energy(.6), "agent": ("uuid4")} },
			6:  { "A2": {"energy": causal_grammar.probability_to_energy(.9), "agent": ("uuid4")} },
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest_modified, fluents_simple_light, actions_simple_light, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug, handle_overlapping_events = True) # !kDebug: suppress output
		cls.root = ET.fromstring(xml_string)
		if kDebug:
			print(xml_string)

	def testCorrectAction(self):
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root,"A2",0,15)
		assert (action_occurrences == 1), "should have had action A2; n times action occurred: {}".format(action_occurrences)

	def testNotIncorrectAction(self):
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root,"FLIPSWITCH",0,15)
		action_occurrences += xml_stuff.queryXMLForActionBetweenFrames(self.root,"A3",0,15)
		action_occurrences += xml_stuff.queryXMLForActionBetweenFrames(self.root,"A4",0,15)
		assert (not action_occurrences), "should not have had action FLIPSWITCH, A3, A4; n times action occurred: {}".format(action_occurrences)

######################## NEW TEST CLASS: TWO ACTIONS, FIRST GETS LOST
# the ideal result:  action 
class TrampledMonitorAction(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		import causal_grammar_summerdata
		causal_forest = []
		for root in causal_grammar_summerdata.causal_forest:
			if root['symbol'].startswith('screen' + "_"):
				causal_forest.append(root)
		causal_forest_modified = causal_forest
		fluents = {
			550:  { "screen": 0.969968},
		}
		actions = {
			528:  { "usecomputer_END": {"energy": 0, "agent": ("uuid4")} },
			529:  { "usecomputer_START": {"energy": 0, "agent": ("uuid4")} },
			558:  { "usecomputer_END": {"energy": 0, "agent": ("uuid4")} },
			#559:  { "usecomputer_START": {"energy": 0.183661, "agent": ("uuid4")} },
			#567:  { "usecomputer_END": {"energy": 0.183661, "agent": ("uuid4")} },
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest_modified, fluents, actions, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug, handle_overlapping_events = True) # !kDebug: suppress output
		cls.root = ET.fromstring(xml_string)
		if kDebug:
			print(xml_string)

	def testCorrectAction(self):
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root,"usecomputer_END",528,559)
		assert (action_occurrences == 1), "should have had action usecomputer_END; n times action occurred: {}".format(action_occurrences)

# TODO: test "nonevent" does what i really want
# TODO: make sure not averaging to calculate mismatched number of nodes -- need the probabilities to appropriately compensate for that


if __name__ == "__main__":
	unittest.main() # run all tests


