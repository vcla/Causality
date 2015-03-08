import unittest
import causal_grammar
import evaluateCausalGrammar as evaluateXML
import xml.etree.ElementTree as ET
import dealWithDBResults

kDebug = True

# our causal forest:
causal_forest_light = [
{
	"node_type": "root",
	"symbol_type": "fluent",
	"symbol": "light_on",
	"children": [
		{ "node_type": "and", "probability": .6, "children": [ #on inertially -- higher chance of occurrence?
				{ "node_type": "leaf", "symbol": "light_on", "symbol_type": "prev_fluent" },
				{ "node_type": "leaf", "symbol": "E1_START", "symbol_type": "nonevent", "timeout": 10 },
		]},
		{ "node_type": "and", "probability": .4, "children": [ #on by causing action E1_START
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
		{ "node_type": "and", "probability": .6, "children": [ #off inertially
				{ "node_type": "leaf", "symbol": "light_off", "symbol_type": "prev_fluent" },
				{ "node_type": "leaf", "symbol": "E1_START", "symbol_type": "nonevent", "timeout": 10 },
		]},
		{ "node_type": "and", "probability": .4, "children": [ #off by causing action E1_START
				{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_on" },
				{ "node_type": "leaf", "symbol_type": "event", "symbol": "E1_START", "timeout": 10 },
			]
		},
	],
},
]

######################## NEW TEST CLASS: 2 FLUENTS, 2nd IS CORRECT ###################
# the ideal result: action at 5, light changes to on at 8
class LightingTestCaseSecondOfTwoFluents(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		fluents_simple_light = {
			6:  { "light": causal_grammar.probability_to_energy(.6)}, #light turns on at 6
			8:  { "light": causal_grammar.probability_to_energy(.9)}, #light turns on at 8
		}
		actions_simple_light = {
			5:  { "E1_START": {"energy": causal_grammar.probability_to_energy(.9), "agent": ("uuid4")} },
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest_light, fluents_simple_light, actions_simple_light, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug) # !kDebug: suppress output
		cls.root = ET.fromstring(xml_string)
		if kDebug:
			print(xml_string)

	def setUp(self):
		"""Call before every test case."""
		pass

	def tearDown(self):
		"""Call after every test case."""
		pass

	def testFluentZeroState(self):
		light_0 = self.root.findall("./fluent_changes/fluent_change[@frame='0']")
		assert light_0[0].attrib['new_value'] == 'off', "should have decided light started out as off; was: {}".format(light_0[0].attrib['new_value'])

	def testFluentTrueChangeState(self):
		light_8 = self.root.findall("./fluent_changes/fluent_change[@frame='8']")
		assert light_8[0].attrib['new_value'] == 'on', "should have decided light changed to on at 8; was: {}".format(light_8[0].attrib['new_value'])

	def testFluentMisdetectedChangeState(self):
		light_6 = self.root.findall("./fluent_changes/fluent_change[@frame='6']")
		assert (not light_6), "should have shown no change at 6; changed to: {}".format(light_6[0].attrib['new_value'])

	def testFluentTooEarly(self):
		frame = 7
		light_changes = evaluateXML.getFluentChangesForFluentBetweenFrames(self.root, 'light', 0, frame)
		assert not len(light_changes), "found {} unexpected changes before frame {}".format(len(light_changes),frame)

	def testFluentTooEarlyToo(self):
		frame = 7
		# only returns valid results for changed-on or changed-off, not stayed-on, stayed-off
		fluentDict = dealWithDBResults.buildDictForDumbFluentBetweenFramesIntoResults(self.root, "light", ('light_on','light_off'), 0, frame)
		assert not fluentDict['light_0_light_on_light_off'] and not fluentDict['light_0_light_off_light_on'], "should have had no light status change before {}".format(frame)

	def testFluentTooLate(self):
		frame = 9
		light_changes = evaluateXML.getFluentChangesForFluentBetweenFrames(self.root,'light',frame, 15)
		assert not len(light_changes), "found {} unexpected changes after frame {}".format(len(light_changes),frame)

	def testActionTooEarly(self):
		#queryXMLForActionBetweenFrames(xml,action,frame1,frame2)
		action_occurrences = dealWithDBResults.queryXMLForActionBetweenFrames(self.root,"E1_START",0,5)
		assert (not action_occurrences), "should have had no action before 5; n times action occurred: {}".format(action_occurrences)

	def testActionJustRight(self):
		action_occurrences = dealWithDBResults.queryXMLForActionBetweenFrames(self.root,"E1_START",4,6)
		assert (action_occurrences), "should have had action at 5; n times action occurred: {}".format(action_occurrences)

	def testActionTooLate(self):
		action_occurrences = dealWithDBResults.queryXMLForActionBetweenFrames(self.root,"E1_START",5,15)
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
			5:  { "E1_START": {"energy": causal_grammar.probability_to_energy(.9), "agent": ("uuid4")} },
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest_light, fluents_simple_light, actions_simple_light, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug) # !kDebug: suppress output
		cls.root = ET.fromstring(xml_string)
		if kDebug:
			print(xml_string)

	def setUp(self):
		"""Call before every test case."""
		pass

	def tearDown(self):
		"""Call after every test case."""
		pass

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
		light_changes = evaluateXML.getFluentChangesForFluentBetweenFrames(self.root,'light',0, frame)
		assert not len(light_changes), "found {} unexpected changes before frame {}".format(len(light_changes),frame)

	def testFluentTooEarlyToo(self):
		frame = 5
		# only returns valid results for changed-on or changed-off, not stayed-on, stayed-off
		fluentDict = dealWithDBResults.buildDictForDumbFluentBetweenFramesIntoResults(self.root, "light", ('light_on','light_off'), 0, frame)
		assert not fluentDict['light_0_light_on_light_off'] and not fluentDict['light_0_light_off_light_on'], "should have had no light status change before {}".format(frame)

	def testFluentTooLate(self):
		frame = 7
		light_changes = evaluateXML.getFluentChangesForFluentBetweenFrames(self.root,'light',frame, 15)
		assert not len(light_changes), "found {} unexpected changes after frame {}".format(len(light_changes),frame)

	def testActionTooEarly(self):
		#queryXMLForActionBetweenFrames(xml,action,frame1,frame2)
		action_occurrences = dealWithDBResults.queryXMLForActionBetweenFrames(self.root,"E1_START",0,5)
		assert (not action_occurrences), "should have had no action before 5; n times action occurred: {}".format(action_occurrences)

	def testActionJustRight(self):
		action_occurrences = dealWithDBResults.queryXMLForActionBetweenFrames(self.root,"E1_START",4,6)
		assert (action_occurrences), "should have had action at 5; n times action occurred: {}".format(action_occurrences)

	def testActionTooLate(self):
		action_occurrences = dealWithDBResults.queryXMLForActionBetweenFrames(self.root,"E1_START",5,15)
		assert (not action_occurrences), "should have had no action after 5; n times action occurred: {}".format(action_occurrences)


#class OtherTestCase(unittest.TestCase):
#
#	def setUp(self):
#		blah_blah_blah()
#
#	def tearDown(self):
#		blah_blah_blah()
#
#	def testBlah(self):
#		assert self.blahblah == "blah", "blah isn't blahing blahing correctly"


if __name__ == "__main__":
	unittest.main() # run all tests
