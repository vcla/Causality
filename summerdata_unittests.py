import unittest
import causal_grammar
import causal_grammar_summerdata
causal_forest_orig = causal_grammar_summerdata.causal_forest

import summerdata
from summerdata import kActionDetections
import evaluateCausalGrammar as evaluateXML
import xml.etree.ElementTree as ET
import xml_stuff

kDebug = False

class SummerdataTestCases(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		causal_forest_orig = causal_grammar_summerdata.causal_forest
		ignoreoverlaps = True #these really need less-confusing names =/
		withoutoverlaps = not ignoreoverlaps
		suppress_output = not kDebug
		simplify = True # TODO: I should have a unit test that just makes sure simplifying doesn't break anything
		example = 'door_1_8145'
		"""
		Clip:
		annotation: 261 - 314: opens, standing; 314 - 349: closes, standing
		detection: 261 - 314: opens 297, shuts 301; 314-349: closes 322, closes 338, standing
		origdb: 261 - 314: opens, shuts; 314-349: shuts x 2, stand_start, stand_end
		causal: 261 - 314: stays open; 314-349: shuts, stand_start
		"""
		if simplify:
			causal_grammar_summerdata.causal_forest = causal_grammar.get_simplified_forest_for_example(causal_forest_orig, example)
		# fluent_parses, action_parses = causal_grammar.import_summerdata(example,kActionDetections)
		fluent_parses = {297: {'door': 0.13272600275231877}, 338: {'door': 1.4261894413473993}, 322: {'door': 1.0789008419993453}, 301: {'door': 1.1634100434038068}, 313: {'screen': 3.203371638332235}}
		action_parses = {
				320: { "standing_START": {"energy": 0.240229, "agent": "uuid1"} },
				346: { "standing_END": {"energy": 0.240229, "agent": "uuid1"} },
				347: { "benddown_START": {"energy": 1.236692, "agent": "uuid1"} },
				349: { "benddown_END": {"energy": 1.236692, "agent": "uuid1"} },
				}
		orig_xml = xml_stuff.munge_parses_to_xml(fluent_parses, action_parses)
		causal_xml = causal_grammar.process_events_and_fluents(causal_grammar_summerdata.causal_forest, fluent_parses, action_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy, suppress_output = suppress_output, handle_overlapping_events = withoutoverlaps)
		#uploadComputerResponseToDB(example, fluent_and_action_xml, 'causalgrammar', connType, conn)
		#uploadComputerResponseToDB(example, orig_xml, 'origdata', connType, conn)
		#cls.root = ET.fromstring(xml_string)
		cls.orig_xml = ET.fromstring(orig_xml)
		cls.causal_xml = ET.fromstring(causal_xml)
		if kDebug:
			print(orig_xml)
			print(causal_xml)

	def testFrame1Door(self):
		start_frame = 261
		end_frame = 314
		fluent = 'door'

		source = 'origdata'
		orig_dict = xml_stuff.queryXMLForAnswersBetweenFrames(self.orig_xml, fluent, start_frame, end_frame, source, not source.endswith('smrt') )
		desired_dict = {'door_261_closed': 0, 'door_261_closed_open': 100, 'door_261_open_closed': 100, 'door_action_261_act_opened': 0, 'door_261_open': 0, 'door_action_261_act_not_opened_closed': 100, 'door_action_261_act_closed': 0}
		assert orig_dict == desired_dict, "{} != {}".format(orig_dict, desired_dict)

		source = 'causaldata'
		causal_dict = xml_stuff.queryXMLForAnswersBetweenFrames(self.causal_xml, fluent, start_frame, end_frame, source, not source.endswith('smrt') )
		desired_dict = {'door_261_closed': 0, 'door_261_closed_open': 0, 'door_261_open_closed': 0, 'door_action_261_act_opened': 0, 'door_261_open': 100, 'door_action_261_act_not_opened_closed': 100, 'door_action_261_act_closed': 0}
		assert causal_dict == desired_dict, "{} != {}".format(causal_dict, desired_dict)

	def testFrame2Door(self):
		start_frame = 314
		end_frame = 349
		fluent = 'door'

		"""
		origdb: 314-349: shuts x 2, stand_start, stand_end
		causal: 314-349: shuts, stand_start
		"""
		source = 'origdata'
		orig_dict = xml_stuff.queryXMLForAnswersBetweenFrames(self.orig_xml, fluent, start_frame, end_frame, source, not source.endswith('smrt') )
		desired_dict = {'door_314_closed': 0, 'door_314_closed_open': 0, 'door_314_open_closed': 200, 'door_action_314_act_opened': 100, 'door_314_open': 0, 'door_action_314_act_not_opened_closed': 0, 'door_action_314_act_closed': 100}
		assert orig_dict == desired_dict, "\ntest:  {}\ntruth: {}".format(orig_dict, desired_dict)
		source = 'causaldata'
		causal_dict = xml_stuff.queryXMLForAnswersBetweenFrames(self.causal_xml, fluent, start_frame, end_frame, source, not source.endswith('smrt') )
		desired_dict = {'door_314_closed': 0, 'door_314_closed_open': 0, 'door_314_open_closed': 100, 'door_action_314_act_opened': 100, 'door_314_open': 0, 'door_action_314_act_not_opened_closed': 0, 'door_action_314_act_closed': 0}
		assert causal_dict == desired_dict, "\n{}\n{}".format(causal_dict, desired_dict)

if __name__ == "__main__":
	unittest.main() # run all tests
