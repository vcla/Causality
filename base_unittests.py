import unittest
import causal_grammar
import xml.etree.ElementTree as ET
import dealWithDBResults

kDebug = True

fluents_simple_light = {
	6:  { "light": causal_grammar.probability_to_energy(.6)}, #light turns on at 6
	8:  { "light": causal_grammar.probability_to_energy(.9)}, #light turns on at 8
}

actions_simple_light = {
	5:  { "E1_START": {"energy": causal_grammar.probability_to_energy(.9), "agent": ("uuid4")} },
}

### desired solution: light off to start.  then "turned on" at 5 for "on" at 8.

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

xml_string = causal_grammar.process_events_and_fluents(causal_forest_light, fluents_simple_light, actions_simple_light, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug) # !kDebug: suppress output
root = ET.fromstring(xml_string)
if kDebug:
	print(xml_string)

class LightingTestCase(unittest.TestCase):

	def setUp(self):
		"""Call before every test case."""
		pass

	def tearDown(self):
		"""Call after every test case."""
		pass


	def testFluentZeroState(self):
		light_0 = root.findall("./fluent_changes/fluent_change[@frame='0']")
		assert light_0[0].attrib['new_value'] == 'off', "should have decided light started out as off; was: {}".format(light_0[0].attrib['new_value'])

	def testFluentTrueChangeState(self):
		light_8 = root.findall("./fluent_changes/fluent_change[@frame='8']")
		assert light_8[0].attrib['new_value'] == 'on', "should have decided light changed to on at 8; was: {}".format(light_8[0].attrib['new_value'])

	def testFluentMisdetectedChangeState(self):
		light_6 = root.findall("./fluent_changes/fluent_change[@frame='6']")
		assert (not light_6), "should have shown no change at 6; changed to: {}".format(light_6[0].attrib['new_value'])

	def getFluentChangesForFluent(self, fluent):
		return root.findall("./fluent_changes/fluent_change[@fluent='{}'][@old_value]".format(fluent))

	def getFluentChangesForFluentBetweenFrames(self, fluent, frame1, frame2):
		assert(frame1 <= frame2)
		changes = self.getFluentChangesForFluent(fluent)
		retval = []
		for change in changes:
			if change.attrib['frame'] >= frame1 and change.attrib['frame'] <= frame2:
				retval.append(change)
		return retval

	def testFluentTooEarly(self):
		frame = 9
		light_changes = self.getFluentChangesForFluentBetweenFrames('light',0, frame)
		light_changes = root.findall("./fluent_changes/fluent_change[@fluent='light'][@old_value]")
		assert not len(light_changes), "found {} unexpected changes before frame {}".format(len(light_changes),frame)

	def testFluentTooEarlyToo(self):
		frame = 9
		# only returns valid results for changed-on or changed-off, not stayed-on, stayed-off
		fluentDict = dealWithDBResults.buildDictForDumbFluentBetweenFramesIntoResults(root, "light", ('light_on','light_off'), 0, frame)
		assert not fluentDict['light_0_light_on_light_off'] and not fluentDict['light_0_light_off_light_on'], "should have had no light status change before {}".format(frame)

	def testActionTooEarly(self):
		#queryXMLForActionBetweenFrames(xml,action,frame1,frame2)
		action_occurrences = dealWithDBResults.queryXMLForActionBetweenFrames(root,"E1_START",0,8)
		assert (not action_occurrences), "should have had no action before 7; n times action occurred: {}".format(action_occurrences)

	def testActionJustRight(self):
		action_occurrences = dealWithDBResults.queryXMLForActionBetweenFrames(root,"E1_START",7,9)
		assert (action_occurrences), "should have had action at 8; n times action occurred: {}".format(action_occurrences)

	def testActionTooLate(self):
		action_occurrences = dealWithDBResults.queryXMLForActionBetweenFrames(root,"E1_START",8,15)
		assert (not action_occurrences), "should have had no action after 8; n times action occurred: {}".format(action_occurrences)

	def testBetterAction(self):
		"""Test case A. note that all test method names must begin with 'test.'"""
		#assert foo.bar() == 543, "bar() not calculating values correctly"
		pass

	#def testB(self):
	#	"""test case B"""
	#	assert foo+foo == 34, "can't add Foo instances"

	#def testC(self):
	#	"""test case C"""
	#	assert foo.baz() == "blah", "baz() not returning blah correctly"


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
