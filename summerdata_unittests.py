import unittest
import causal_grammar
import causal_grammar_summerdata
import summerdata
from summerdata import kActionDetections
import evaluateCausalGrammar as evaluateXML
import xml.etree.ElementTree as ET
import dealWithDBResults

kDebug = True

######################## NEW TEST CLASS: 2 FLUENTS, 2nd IS CORRECT ###################
# the ideal result: action at 5, light changes to on at 8
class LightingTestCaseSecondOfTwoFluents(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		causal_forest_orig = causal_grammar_summerdata.causal_forest
		ignoreoverlaps = True #these really need less-confusing names =/
		withoutoverlaps = not ignoreoverlaps
		simplify = True # TODO: I should have a unit test that just makes sure simplifying doesn't break anything
		example = 'light_5_9406'
		if simplify:
			causal_grammar_summerdata.causal_forest = causal_grammar.get_simplified_forest_for_example(causal_forest_orig, example)
		fluent_parses, temporal_parses = causal_grammar.import_summerdata(example,kActionDetections)
		xml_string = causal_grammar.process_events_and_fluents(causal_grammar_summerdata.causal_forest, fluent_parses, temporal_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy, suppress_output = False, handle_overlapping_events = withoutoverlaps)
		cls.root = ET.fromstring(xml_string)
		if kDebug:
			print(xml_string)

	def testFluentZeroState(self):
		light_0 = self.root.findall("./fluent_changes/fluent_change[@frame='0']")
		assert light_0[0].attrib['new_value'] == 'off', "should have decided light started out as off; was: {}".format(light_0[0].attrib['new_value'])

if __name__ == "__main__":
	unittest.main() # run all tests


