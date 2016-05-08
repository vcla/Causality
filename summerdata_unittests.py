import unittest
import causal_grammar
import causal_grammar_summerdata
causal_forest_orig = causal_grammar_summerdata.causal_forest

import summerdata
from summerdata import kActionDetections
import xml.etree.ElementTree as ET
import xml_stuff

kDebug = True


#### door_1_8145 unittest #####
# amy annotate: 1st clip: door opens/agent appears in doorway.  2nd clip: agent enters the room, closes door.
# annotated_causal_dict_261 = {'door_261_closed': 0, 'door_261_closed_open': 100, 'door_261_open_closed': 0, 'door_action_261_act_opened': 100, 'door_261_open': 100, 'door_action_261_act_not_opened_closed': 0, 'door_action_261_act_closed': 0}
# annotated_causal_dict_314 = {'door_314_closed': 0, 'door_314_closed_open': 0, 'door_314_open_closed': 100, 'door_action_314_act_opened': 0, 'door_314_open': 0, 'door_action_314_act_not_opened_closed': 0, 'door_action_314_act_closed': 100}
# TODO NOTE: when running causal grammar on this example, the leading solution completely misses 297, but the 2nd and 3rd get it.. . BUG!@!!!
class SummerdataDoor1TestCases(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		causal_forest_orig = causal_grammar_summerdata.causal_forest
		ignoreoverlaps = True #these really need less-confusing names =/
		withoutoverlaps = not ignoreoverlaps
		suppress_output = not kDebug
		simplify = False # TODO: I should have a unit test that just makes sure simplifying doesn't break anything
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
				326: { "standing_END": {"energy": 0.257439, "agent": "uuid1"} },
				#320: { "standing_START": {"energy": 0.240229, "agent": "uuid1"} },
				#346: { "standing_END": {"energy": 0.240229, "agent": "uuid1"} },
				#347: { "benddown_START": {"energy": 1.236692, "agent": "uuid1"} },
				#349: { "benddown_END": {"energy": 1.236692, "agent": "uuid1"} },
				}
		orig_xml = xml_stuff.munge_parses_to_xml(fluent_parses, action_parses)
		sorted_keys = sorted(fluent_parses.keys())
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
		desired_orig_dict = {'door_261_closed': 0, 'door_261_closed_open': 100, 'door_261_open_closed': 100, 'door_action_261_act_opened': 0, 'door_261_open': 0, 'door_action_261_act_not_opened_closed': 100, 'door_action_261_act_closed': 0}
		assert orig_dict == desired_orig_dict, "{} != {}".format(orig_dict, desired_orig_dict)

		source = 'causaldata'
		causal_dict = xml_stuff.queryXMLForAnswersBetweenFrames(self.causal_xml, fluent, start_frame, end_frame, source, not source.endswith('smrt') )
		desired_causal_dict = {'door_261_closed': 0, 'door_261_closed_open': 0, 'door_261_open_closed': 0, 'door_action_261_act_opened': 0, 'door_261_open': 100, 'door_action_261_act_not_opened_closed': 100, 'door_action_261_act_closed': 0}
		assert causal_dict == desired_causal_dict, "{} != {}".format(causal_dict, desired_causal_dict)

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
		desired_orig_dict = {'door_314_closed': 0, 'door_314_closed_open': 0, 'door_314_open_closed': 200, 'door_action_314_act_opened': 100, 'door_314_open': 0, 'door_action_314_act_not_opened_closed': 0, 'door_action_314_act_closed': 100}
		assert orig_dict == desired_orig_dict, "\ntest:  {}\ntruth: {}".format(orig_dict, desired_orig_dict)
		source = 'causaldata'
		causal_dict = xml_stuff.queryXMLForAnswersBetweenFrames(self.causal_xml, fluent, start_frame, end_frame, source, not source.endswith('smrt') )
		desired_causal_dict = {'door_314_closed': 0, 'door_314_closed_open': 0, 'door_314_open_closed': 100, 'door_action_314_act_opened': 0, 'door_314_open': 0, 'door_action_314_act_not_opened_closed': 0, 'door_action_314_act_closed': 100}
		assert causal_dict == desired_causal_dict, "\n{}\n{}".format(causal_dict, desired_causal_dict)


##### light_9_screen_57_9404 #####
# 1 clip, 2 fluents
# amy annotate the clip: agent 1 at keyboard, typing.  then agent 2 walks across scene.  then agent 1 gets up.  then agent 2 turns off light.
# annotated_screen = {'screen_2311_off_on': 0, 'screen_action_2311_act_no_mousekeyboard': 0, 'screen_action_2311_act_mousekeyboard': 100, 'screen_2311_on_off': 0, 'screen_2311_on': 100, 'screen_2311_off': 0}
# annotated_light = {'light_action_2311_act_pushbutton': 100, 'light_2311_off_on': 0, 'light_action_2311_act_no_pushbutton': 0, 'light_2311_on': 0, 'light_2311_on_off': 100, 'light_2311_off': 0}

class SummerdataLight9Screen57TestCases(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		causal_forest_orig = causal_grammar_summerdata.causal_forest
		ignoreoverlaps = True #these really need less-confusing names =/
		withoutoverlaps = not ignoreoverlaps
		suppress_output = not kDebug
		simplify = False # TODO: I should have a unit test that just makes sure simplifying doesn't break anything
		example = 'light_9_screen_57_9404'
		if simplify:
			causal_grammar_summerdata.causal_forest = causal_grammar.get_simplified_forest_for_example(causal_forest_orig, example)
		print kActionDetections
		#fluent_parses, action_parses = causal_grammar.import_summerdata(example,kActionDetections)
		fluent_parses = {2336: {'door': 0.06674041018366039}, 2350: {'door': 4.511042523263396}, 2333: {'light': 1.2432023175179374}, 2322: {'screen': 4.511042523263396}, 2425: {'light': 4.111633152359644}, 2364: {'screen': 0.015513717831387925}, 2429: {'light': 4.111633152359644}}
		action_parses = {
			2361: {'standing_START': {'energy': 1.6e-05, 'agent': 'uuid1'}},
			2442: {'standing_END': {'energy': 1.6e-05, 'agent': 'uuid1'}},
			2341: {'usecomputer_END': {'energy': 0.300451, 'agent': 'uuid1'}},
			2342: {'drink_START': {'energy': 1.787062, 'agent': 'uuid1'}, 'drink_END': {'energy': 1.787062, 'agent': 'uuid1'}},
			2311: {'usecomputer_START': {'energy': 0.300451, 'agent': 'uuid1'}}
		}
		orig_xml = xml_stuff.munge_parses_to_xml(fluent_parses, action_parses)
		sorted_keys = sorted(fluent_parses.keys())
		causal_xml = causal_grammar.process_events_and_fluents(causal_grammar_summerdata.causal_forest, fluent_parses, action_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy, suppress_output = suppress_output, handle_overlapping_events = withoutoverlaps)
		#uploadComputerResponseToDB(example, fluent_and_action_xml, 'causalgrammar', connType, conn)
		#uploadComputerResponseToDB(example, orig_xml, 'origdata', connType, conn)
		#cls.root = ET.fromstring(xml_string)
		cls.orig_xml = ET.fromstring(orig_xml)
		cls.causal_xml = ET.fromstring(causal_xml)
		if kDebug:
			print(orig_xml)
			print(causal_xml)

	def testFrame1Screen(self):
		start_frame = 2311
		end_frame = 2442
		fluent = 'screen'

		source = 'origdata'
		orig_dict = xml_stuff.queryXMLForAnswersBetweenFrames(self.orig_xml, fluent, start_frame, end_frame, source, not source.endswith('smrt') )
		desired_orig_dict = {'screen_2311_off_on': 100, 'screen_action_2311_act_no_mousekeyboard': 0, 'screen_action_2311_act_mousekeyboard': 100, 'screen_2311_on_off': 100, 'screen_2311_on': 0, 'screen_2311_off': 0}
		assert orig_dict == desired_orig_dict, "{} != {}".format(orig_dict, desired_orig_dict)

		source = 'causaldata'
		causal_dict = xml_stuff.queryXMLForAnswersBetweenFrames(self.causal_xml, fluent, start_frame, end_frame, source, not source.endswith('smrt') )
		desired_causal_dict = {'screen_2311_off_on': 0, 'screen_action_2311_act_no_mousekeyboard': 0, 'screen_action_2311_act_mousekeyboard': 100, 'screen_2311_on_off': 0, 'screen_2311_on': 100, 'screen_2311_off': 0}
		assert causal_dict == desired_causal_dict, "{} != {}".format(causal_dict, desired_causal_dict)

	def testFrame1Light(self):
		start_frame = 2311
		end_frame = 2442
		fluent = 'light'

		source = 'origdata'
		orig_dict = xml_stuff.queryXMLForAnswersBetweenFrames(self.orig_xml, fluent, start_frame, end_frame, source, not source.endswith('smrt') )
		desired_orig_dict = {'light_action_2311_act_pushbutton': 0, 'light_2311_off_on': 0, 'light_action_2311_act_no_pushbutton': 100, 'light_2311_on': 0, 'light_2311_on_off': 300, 'light_2311_off': 0}
		assert orig_dict == desired_orig_dict, "\ntest:  {}\ntruth: {}".format(orig_dict, desired_orig_dict)
		source = 'causaldata'
		causal_dict = xml_stuff.queryXMLForAnswersBetweenFrames(self.causal_xml, fluent, start_frame, end_frame, source, not source.endswith('smrt') )
		desired_causal_dict = {'light_action_2311_act_pushbutton': 0, 'light_2311_off_on': 0, 'light_action_2311_act_no_pushbutton': 100, 'light_2311_on': 100, 'light_2311_on_off': 0, 'light_2311_off': 0}
		assert causal_dict == desired_causal_dict, "\n{}\n{}".format(causal_dict, desired_causal_dict)

if __name__ == "__main__":
	unittest.main() # run all tests
