import unittest
import causal_grammar
import xml.etree.ElementTree as ET

fluents_simple_light = {
	12:  { "light": .7},
	14:  { "light": .01},
}

actions_simple_light = {
	10:  { "E1_START": {"energy": .1, "agent": ("uuid4")} },
}

# our causal forest:
causal_forest_light = [
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
]

xml_string = causal_grammar.process_events_and_fluents(causal_forest_light, fluents_simple_light, actions_simple_light, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,True) # final True: suppress output
root = ET.fromstring(xml_string)
print xml_string

class LightingTestCase(unittest.TestCase):

	def setUp(self):
		"""Call before every test case."""
		pass

	def tearDown(self):
		"""Call after every test case."""
		pass


	def testZeroState(self):
		light_0 = root.findall("./fluent_changes/fluent_change[@frame='0']")
		assert light_0[0].attrib['new_value'] == 'on', "should have decided light started out as on; was: {}".format(light_0[0].attrib['new_value'])

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
