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

# the ideal result: takes the first action because it has lower energy
class LightingTestCaseFirstOfTwoActions(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		fluents_simple_light = {
			6:  { "light": causal_grammar.probability_to_energy(.6)}, #light turns on at 6 -- energy = .51
		}
		actions_simple_light = {
			4:  { "FLIPSWITCH": {"energy": causal_grammar.probability_to_energy(.9), "agent": ("uuid4")} }, #energy = .11
			5:  { "FLIPSWITCH": {"energy": causal_grammar.probability_to_energy(.6), "agent": ("uuid4")} }, #energy = .51
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest_light, fluents_simple_light, actions_simple_light, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug, handle_overlapping_events = True) # !kDebug: suppress output
		cls.root = ET.fromstring(xml_string)
		cls.xml_string = xml_string
		if kDebug:
			print(xml_string)

	def testAction(self):
		# known 'failure': we can't trust just getting the event at frame 4 because we play around with when we want the event to actually happen (for instance, causing it to happen when the fluent happens)
		#action = self.root.findall("./actions/event[@frame='4']")
		#assert action, "should have found action at frame 4; instead got {}".format(self.xml_string)
		#TODO: we don't xml out the individual energies, just the whole energy, so we're going to leave this a little fragile for now
		#energy = causal_grammar.probability_to_energy(.9)
		energy = 19.365
		action = self.root.findall("./actions/event")
		assert action, "did not complete with /any/ action"
		assert len(action) == 1, "found multiple actions ~ {}".format(cls.xml_string)
		action = action[0]
		assert action.attrib['action'] == 'FLIPSWITCH', "found wrong action, how did that happen!? ~ {}".format(cls.xml_string)
		assert abs(float(action.attrib['energy'])-energy) < .000001, "wrong energy ~ {} != expected {}".format(action.attrib['energy'],energy)

	def testFluentChangeAt6(self):
		light_6 = self.root.findall("./fluent_changes/fluent_change[@frame='6']")
		assert light_6, "should have decided light change off to on at 6, no change decided"
		assert light_6[0].attrib['new_value'] == 'on', "should have decided light change to on at 6; was: {}".format(light_6[0].attrib['new_value'])



# the ideal result: takes the second action because it has lower energy
class LightingTestCaseSecondOfTwoActions(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		fluents_simple_light = {
			6:  { "light": causal_grammar.probability_to_energy(.6)}, #light turns on at 6 -- energy = .51
		}
		actions_simple_light = {
			4:  { "FLIPSWITCH": {"energy": causal_grammar.probability_to_energy(.6), "agent": ("uuid4")} }, #energy = .51
			5:  { "FLIPSWITCH": {"energy": causal_grammar.probability_to_energy(.9), "agent": ("uuid4")} }, #energy = .11
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest_light, fluents_simple_light, actions_simple_light, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug, handle_overlapping_events = True) # !kDebug: suppress output
		cls.root = ET.fromstring(xml_string)
		cls.xml_string = xml_string
		if kDebug:
			print(xml_string)

	def testAction(self):
		# known failure: we can't trust just getting the event at frame 5 because we play around with when we want the event to actually happen (for instance, causing it to happen when the fluent happens)
		#action = self.root.findall("./actions/event[@frame='5']")
		#assert action, "should have found action at frame 5; instead got {}".format(self.xml_string)
		#TODO: we don't xml out the individual energies, just the whole energy, so we're going to leave this a little fragile for now
		#energy = causal_grammar.probability_to_energy(.9)
		energy = 19.365
		action = self.root.findall("./actions/event")
		assert action, "did not complete with /any/ action"
		assert len(action) == 1, "found multiple actions ~ {}".format(cls.xml_string)
		action = action[0]
		assert action.attrib['action'] == 'FLIPSWITCH', "found wrong action, how did that happen!? ~ {}".format(cls.xml_string)
		assert abs(float(action.attrib['energy'])-energy) < .000001, "wrong energy ~ {} != expected {}".format(action.attrib['energy'],energy)


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

######################## NEW TEST CLASS: TESTING NONEVENT
class NoneventTimeouts(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		causal_forest = [
		{
			"node_type": "root",
			"symbol_type": "fluent",
			"symbol": "fluent_on",
			"children": [
				{ "node_type": "and", "probability": .6, "children": [ #on inertially - not turned off
						{ "node_type": "leaf", "symbol": "fluent_on", "symbol_type": "prev_fluent" },
						{ "node_type": "leaf", "symbol": "OFFACTION", "symbol_type": "nonevent", "timeout": 3 },
				]},
				{ "node_type": "and", "probability": .4, "children": [ #on by causing action
						{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "fluent_off" },
						{ "node_type": "leaf", "symbol_type": "event", "symbol": "ONACTION", "timeout": 1 },
					]
				},
			],
		}, {
			"node_type": "root",
			"symbol_type": "fluent",
			"symbol": "fluent_off",
			"children": [
				{ "node_type": "and", "probability": .6, "children": [ #off inertially #energy = .51
						{ "node_type": "leaf", "symbol": "fluent_off", "symbol_type": "prev_fluent" },
						{ "node_type": "leaf", "symbol": "OFFACTION", "symbol_type": "nonevent", "timeout": 3 },
				]},
				{ "node_type": "and", "probability": .4, "children": [ #off by causing action A1
						{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "fluent_on" },
						{ "node_type": "leaf", "symbol_type": "event", "symbol": "OFFACTION", "timeout": 1 },
					]
				},
			],
		},
		]
		fluents_simple = {
			5:  { "fluent": causal_grammar.probability_to_energy(.9)}, #light turns off at 5 -- energy = .51
		}
		actions_simple = {
			1:  { "OFFACTION": {"energy": causal_grammar.probability_to_energy(.9), "agent": ("uuid4")} }, #energy = .11
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest, fluents_simple, actions_simple, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug, handle_overlapping_events = True) # !kDebug: suppress output
		cls.root = ET.fromstring(xml_string)
		if kDebug:
			print(xml_string)

	def testFluentNonEvent(self):
		assert 0

######################## NEW TEST CLASS: TWO ACTIONS, FIRST GETS LOST
# the ideal result:  action 
class TrampledMonitorAction(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		causal_forest_abbreviated = [ #NOTE: this was yanked from causal_grammar_summerdata.py on 2016-04-24
			("root", "fluent", "screen_on", .5, False, [ #SCREEN ON
				("and", False, False, .35, False, [ #ON INERTIALLY
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "nonevent", "usecomputer_END", False, 1, False), ]
				),
				("and", False, False, .3, False, [ #ON CAUSALLY
					("leaf", "prev_fluent", "screen_off", False, False, False),
					("leaf", "event", "usecomputer_START", False, 100, False), ]
				),
				("and", False, False, .35, False, [ #ON CONTINUOUSLY
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "event", "usecomputer_START", False, 100, False), ]
				), ]
			),
			("root", "fluent", "screen_off", .5, False, [ #SCREEN OFF
				("and", False, False, .3, False, [ #OFF CAUSALLY
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "event", "usecomputer_END", False, 30, False) ]
				),
				("and", False, False, .4, False, [ # OFF INERTIALLY - due to the screensaver kicking on (so causally changed because of non-action)
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "nonevent", "usecomputer_START", False, 100, False),
					("leaf", "nonevent", "usecomputer_END", False, 1000, False) ]
				),
				("and", False, False, .3, False, [ # OFF INERTIALLY - no change because didn't start using the computer
					("leaf", "prev_fluent", "screen_off", False, False, False),
					("leaf", "nonevent", "usecomputer_START", False, 200, False) ]
				) ]
			)
		]
		causal_forest_modified = causal_grammar.generate_causal_forest_from_abbreviated_forest(causal_forest_abbreviated)
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
		cls.xml_string = xml_string
		if kDebug:
			print(xml_string)

	def testCorrectAction(self):
		start = 527
		end = 551
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root,"usecomputer_END",start,end)
		assert (action_occurrences == 1), "should have had action usecomputer_END between {} and {}; n times action occurred: {} [{}]".format(start,end,action_occurrences,self.xml_string)


######################## NEW TEST CLASS: Two timeouts for a single action. First fluent is answer: so person turned off computer.
class MutlipleTimeoutsShorterTimeoutWins(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		causal_forest_abbreviated = [ #NOTE: this was yanked from causal_grammar_summerdata.py on 2016-04-24
			("root", "fluent", "screen_on", .5, False, [ #SCREEN ON
				("and", False, False, .4, False, [ #ON INERTIALLY
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "nonevent", "usecomputer_END", False, 1, False), ]
				),
				("and", False, False, .3, False, [ #ON CONTINUOUSLY
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "event", "usecomputer_START", False, 100, False), ]
				), ]
			),
			("root", "fluent", "screen_off", .5, False, [ #SCREEN OFF
				("and", False, False, .33, False, [ #OFF CAUSALLY
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "event", "usecomputer_END", False, 30, False) ]
				),
				("and", False, False, .34, False, [ # OFF INERTIALLY - due to the screensaver kicking on (so causally changed because of non-action)
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "nonevent", "usecomputer_START", False, 100, False),
					("leaf", "event", "usecomputer_END", False, 1000, False) ]
				),
				("and", False, False, .33, False, [ # OFF INERTIALLY - no change because didn't start using the computer
					("leaf", "prev_fluent", "screen_off", False, False, False),
					("leaf", "nonevent", "usecomputer_START", False, 200, False) ]
				) ]
			)
		]
		causal_forest_modified = causal_grammar.generate_causal_forest_from_abbreviated_forest(causal_forest_abbreviated)
		fluents = {
			20:  { "screen": 0.9},
			600: { "screen": 0.8},
		}
		actions = {
			5:  { "usecomputer_END": {"energy": 0, "agent": ("uuid4")} },
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest_modified, fluents, actions, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug, handle_overlapping_events = True) # !kDebug: suppress output
		cls.root = ET.fromstring(xml_string)
		cls.xml_string = xml_string
		if kDebug:
			print(xml_string)

	def testActionOccursOnce(self):
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root,"usecomputer_END",0,1000)
		assert (action_occurrences == 1), "should have had action usecomputer_END once; n times action occurred: {} [{}]".format(action_occurrences,self.xml_string)

	def testFluentChangeAt20(self):
		screen_20 = self.root.findall("./fluent_changes/fluent_change[@frame='20']")
		assert screen_20[0].attrib['new_value'] == 'off', "should have decided screen change to off at 20; was: {}".format(screen_20[0].attrib['new_value'])

	def testTooManyFluentChanges(self):
		screen_changes = xml_stuff.getFluentChangesForFluentBetweenFrames(self.root, 'screen', 0, 1000)
		assert (len(screen_changes) == 1), "found {} unexpected fluent changes".format(len(screen_changes)-1)


######################## NEW TEST CLASS: Two timeouts for a single action. 2nd fluent is answer: so screensaver turned off computer.
class MultipleTimeoutsLongerTimeoutWins(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		causal_forest_abbreviated = [ #NOTE: this was yanked from causal_grammar_summerdata.py on 2016-04-24
			("root", "fluent", "screen_on", .5, False, [ #SCREEN ON
				("and", False, False, .4, False, [ #ON INERTIALLY
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "nonevent", "usecomputer_END", False, 1, False), ]
				),
				("and", False, False, .3, False, [ #ON CONTINUOUSLY
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "event", "usecomputer_START", False, 100, False), ]
				), ]
			),
			("root", "fluent", "screen_off", .5, False, [ #SCREEN OFF
				("and", False, False, .33, False, [ #OFF CAUSALLY
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "event", "usecomputer_END", False, 30, False) ]
				),
				("and", False, False, .34, False, [ # OFF INERTIALLY - due to the screensaver kicking on (so causally changed because of non-action)
					("leaf", "prev_fluent", "screen_on", False, False, False),
					("leaf", "nonevent", "usecomputer_START", False, 100, False),
					("leaf", "event", "usecomputer_END", False, 1000, False) ]
				),
				("and", False, False, .33, False, [ # OFF INERTIALLY - no change because didn't start using the computer
					("leaf", "prev_fluent", "screen_off", False, False, False),
					("leaf", "nonevent", "usecomputer_START", False, 200, False) ]
				) ]
			)
		]
		causal_forest_modified = causal_grammar.generate_causal_forest_from_abbreviated_forest(causal_forest_abbreviated)
		fluents = {
			20:  { "screen": 0.8},
			600: { "screen": 0.9},
		}
		actions = {
			5:  { "usecomputer_END": {"energy": 0, "agent": ("uuid4")} },
		}
		xml_string = causal_grammar.process_events_and_fluents(causal_forest_modified, fluents, actions, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy,not kDebug, handle_overlapping_events = False) # !kDebug: suppress output
		cls.root = ET.fromstring(xml_string)
		cls.xml_string = xml_string
		if kDebug:
			print(xml_string)

	def testActionOccursOnce(self):
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.root,"usecomputer_END",0,1000)
		assert (action_occurrences == 1), "should have had action usecomputer_END once; n times action occurred: {} [{}]".format(action_occurrences,self.xml_string)

	def testFluentChangeAt600(self):
		screen_600 = self.root.findall("./fluent_changes/fluent_change[@frame='600']")
		if (len(screen_600) > 0):
			assert screen_600[0].attrib['new_value'] == 'off', "should have decided screen changed to off once; was: {}".format(screen_600[0].attrib['new_value'])
		else:
			assert 0, "should have decided screen changed to off once; didn't even make it to 600"

	def testTooManyFluentChanges(self):
		screen_changes = xml_stuff.getFluentChangesForFluentBetweenFrames(self.root, 'screen', 0, 1000)
		assert (len(screen_changes) == 1), "found {} unexpected fluent changes".format(len(screen_changes) - 1)


class SummerdataDoor1TestCases(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		import causal_grammar_summerdata
		causal_forest_orig = causal_grammar_summerdata.causal_forest
		ignoreoverlaps = False #these really need less-confusing names =/
		suppress_output = not kDebug
		#suppress_output = True
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
		#fluent_parses = {297: {'door': 0.13272600275231877}, 338: {'door': 1.4261894413473993}, 322: {'door': 1.0789008419993453}, 301: {'door': 1.1634100434038068}, 313: {'screen': 3.203371638332235}}
		withoutoverlaps = False
		fluent_parses = {297: {'door': 0.13272600275231877} }
		action_parses = {
				296: { "standing_START": {"energy": 0.279449, "agent": "uuid1"} },
				#297: { "standing_START": {"energy": 0.240229, "agent": "uuid1"} },
				#326: { "standing_END": {"energy": 0.257439, "agent": "uuid1"} },
				##328: { "standing_END": {"energy": 0.338959, "agent": "uuid1"} },
				##320: { "standing_START": {"energy": 0.240229, "agent": "uuid1"} },
				##346: { "standing_END": {"energy": 0.240229, "agent": "uuid1"} },
				##347: { "benddown_START": {"energy": 1.236692, "agent": "uuid1"} },
				##349: { "benddown_END": {"energy": 1.236692, "agent": "uuid1"} },
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
			print("ORIG XML")
			xml_stuff.printXMLActionsAndFluents(cls.orig_xml)
			print("CAUSAL XML")
			xml_stuff.printXMLActionsAndFluents(cls.causal_xml)

	def testFluentChangeAt297(self):
		door_297 = self.causal_xml.findall("./fluent_changes/fluent_change[@frame='297']")
		# off (closed) to on (open) at 297 because of a standing start: parse 1
		# 0: ('door_on', [('?', ['PREV door_on', 'NOT standing_END'])])
		# 1: ('door_on', [('?', ['PREV door_off', 'standing_START'])])
		# 2: ('door_on', [('?', ['PREV door_off', 'NOT standing_END'])])
		# 3: ('door_off', [('?', ['PREV door_off', 'NOT standing_START'])])
		# 4: ('door_off', [('?', ['PREV door_on', 'standing_END'])])
		# 5: ('door_off', [('?', ['PREV door_on', 'standing_START'])])
		### WRONG TOP ENERGY CHOICES CURRENTLY
		# [[[[(0, 0, {}), (297, 0, {}), (338, 5, {'standing_START': set([297])})], 38.136]]]
		# [[[[(0, 0, {}), (297, 0, {}), (338, 5, {'standing_START': set([297])})], 38.136]]]
		# [[[[(0, 0, {}), (299, 0, {}), (338, 5, {'standing_START': set([297])})], 38.136]]]
		# [[[[(0, 0, {}), (301, 0, {}), (338, 5, {'standing_START': set([297])})], 38.136]]]
		# [[[[(0, 0, {}), (307, 0, {}), (338, 5, {'standing_START': set([297])})], 38.136]]]
		### WANT SOMETHING LIKE:
		# 0: 3, 297: [1,2]
		# [[[[0, 3

		assert door_297, "should have decided door change off to on at 297, no change decided"
		assert door_297[0].attrib['new_value'] == 'on', "should have decided door change to on at 297; was: {}".format(door_297[0].attrib['new_value'])

	def testFluentTooEarly(self):
		door_changes = xml_stuff.getFluentChangesForFluentBetweenFrames(self.causal_xml, 'door', 0, 350)
		assert len(door_changes)==1, "found {} unexpected changes before frame {}".format(len(door_changes),frame)

	def testActionJustRight(self):
		action_occurrences = xml_stuff.queryXMLForActionBetweenFrames(self.causal_xml,"standing_START",295,297)
		assert (action_occurrences), "should have had action at 295; n times action occurred: {}".format(action_occurrences)

# TODO: test "nonevent" does what i really want
# TODO: make sure not averaging to calculate mismatched number of nodes -- need the probabilities to appropriately compensate for that


if __name__ == "__main__":
	unittest.main() # run all tests


