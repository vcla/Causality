# for easier writing of the causal grammar
def write_causal_forest_for_python():
	pass

# xml formatted causal grammar
def write_xml_for_forest(causal_forest):
	print '<causal>'
	for tree in causal_forest:
		write_xml_for_tree(tree)
	print '</causal>'

def write_xml_for_tree(tree):
	#print "***{}".format(tree)
	if tree["node_type"] in ("root", "or"):
		for child in tree["children"]:
			print '\t<production_rule id=\"\" fluent=\"{}\" probability=\"{}\">'.format(tree["symbol"], 0)#tree["probability"])
			write_xml_for_tree(child)
			print '\t</production_rule>'
	elif tree["node_type"] == "and":
		for child in tree["children"]:
			#print "*** CHILD: {}".format(child)
			write_xml_for_tree(child)
	elif tree["node_type"] == "leaf":
		if tree["symbol_type"] == "prev_fluent":
			print '\t\t\t<fluent symbol=\"{}\" />'.format(tree["symbol"])
		elif tree["symbol_type"] == "event":
			print '\t\t\t<action symbol=\"{}\" />'.format(tree["symbol"])
		else:
			raise Exception("unknown symbol type: {}".format(tree["symbol_type"]))
	elif tree["node_type"] == "or":
		print "OR"


	
	#    <causal>
	#        <production_rule id="5e73a424-7ab9-4451-949e-998b2293d9ac" fluent_change="DOOR,DOOR_STATUS,OPEN,CLOSED">
	#            <actions>
	#                <action symbol="TOUCH_DOOR" />
	#            </actions>
	#        </production_rule>
	#        <production_rule id="19aa751e-adfe-4292-aaab-edb3d0156585" fluent_change="ROOM,LIGHT_STATUS,ON,OFF">
	#            <actions>
	#                <action symbol="TOUCH_LIGHT_SWITCH" />
	#            </actions>
	#        </production_rule>
	#        <production_rule id="10c26e5d-d6e0-4aec-a070-46a3d88d54c0" fluent_change="ROOM,LIGHT_STATUS,OFF,ON">
	#            <actions>
	#                <action symbol="TOUCH_LIGHT_SWITCH" />
	#            </actions>
	#        </production_rule>
	#    </causal>



def write_xml_for_parse_tree(completed_parse_tree):
	#xml_string = '<relation id=\"' + ***ID 
	#        <causal>
	#            <relation id="f775d305-8abb-4744-9986-eee9588e1f04" production_rule="5e73a424-7ab9-4451-949e-998b2293d9ac">
	#                <instance fluent_change="9236e488-e050-4362-8c29-c0f78a3fd911">
	#                    <action id="637b9b66-ac48-4071-98b8-406c55ba47af" />
	#                </instance>
	#            </relation>
	#            <relation id="fa517b00-30b0-4615-bc56-e73a47afd500" production_rule="19aa751e-adfe-4292-aaab-edb3d0156585">
	#                <instance fluent_change="72e4c44d-9b90-4aaf-ac65-82c41fdac99f">
	#                    <action id="f50742cf-cc9d-4610-83bb-d34b43e9c599" />
	#                </instance>
	#            </relation>
	#        </causal>
	#    </interpretation>
	pass

def fluentXMLToString(elem):
	# energy, fluent, new_value, old_value (optional)
	frame = elem.attrib['frame']
	value = elem.attrib['new_value']
	if 'old_value' in elem.attrib:
		value = elem.attrib['old_value'] + ' -> ' + value
	fluent = elem.attrib['fluent']
	energy = elem.attrib['energy']
	return "{}: {} {} [{}]".format(frame,fluent,value,energy)

def actionXMLToString(elem):
	# action, energy, frame
	frame = elem.attrib['frame']
	action = elem.attrib['action']
	energy = elem.attrib['energy']
	return "{}: {} [{}]".format(frame,action,energy)

def printXMLFluent(xml):
	print(fluentXMLToString(xml))

def printXMLFluents(xml):
	fluents = xml.findall('.//fluent_change')
	print("--fluents")
	print("\n".join(fluentXMLToString(elem) for elem in sorted(fluents, key=lambda elem: int(elem.attrib['frame']))))

def printXMLAction(xml):
	print(actionXMLToString(xml))

def printXMLActions(xml):
	actions = xml.findall('.//event')
	print("--actions")
	print("\n".join(actionXMLToString(elem) for elem in sorted(actions, key=lambda elem: int(elem.attrib['frame']))))

def printXMLActionsAndFluents(xml):
	print("vvvvvvvvv")
	printXMLFluents(xml)
	printXMLActions(xml)
	print("^^^^^^^^^")

import xml.etree.ElementTree as ET
from xml.dom import minidom

def munge_parses_to_xml(fluent_parses,action_parses,suppress_output=False):
	import causal_grammar
	import math
	temporal = ET.Element('temporal')
	fluent_changes = ET.SubElement(temporal,'fluent_changes')
	actions_el = ET.SubElement(temporal,'actions')
	# avoiding cleverness. step 1: get all actions and fluents.
	fluents = set()
	actions = set()
	for frame in fluent_parses:
		fluents = fluents.union(fluent_parses[frame].keys())
	for frame in action_parses:
		actions = actions.union(action_parses[frame].keys())
	# continuing to avoid cleverness, now for each fluent in all frames, build our xml
	for fluent in sorted(fluents):
		for frame in sorted(fluent_parses):
			if fluent in fluent_parses[frame]:
				fluent_value = fluent_parses[frame][fluent]
				fluent_on_probability = math.exp(-fluent_value)
				fluent_off_probability = 1 - fluent_on_probability
				if 0 == fluent_off_probability:
					fluent_off_energy = causal_grammar.kZeroProbabilityEnergy
				else:
					fluent_off_energy = -math.log(fluent_off_probability)
				fluent_status = None
				if fluent_value < causal_grammar.kFluentThresholdOnEnergy:
					fluent_status = "on"
				elif fluent_off_energy < causal_grammar.kFluentThresholdOnEnergy:
					fluent_status = "off"
					fluent_value = fluent_off_energy
				else:
					continue
				fluent_attributes = {
					'fluent': fluent,
					'new_value': fluent_status,
					'frame': str(frame),
					'energy': str(fluent_value),
				}
				if fluent_status == "on":
					fluent_attributes['old_value'] = "off"
				else:
					fluent_attributes['old_value'] = "on"
				fluent_parse = ET.SubElement(fluent_changes,'fluent_change', fluent_attributes)
	# continuing to avoid cleverness, now for each action in all frames, build our xml
	for action in sorted(actions):
		prev_value = None
		for frame in sorted(action_parses):
			if action in action_parses[frame]:
				event_value = action_parses[frame][action]
				event_attributes = {
					'action': action,
					'energy': str(event_value['energy']), # ignore 'agent'
					'frame': str(frame),
				}
				event = ET.SubElement(actions_el, "event", event_attributes)
	return ET.tostring(temporal, method='xml', encoding='utf-8')

"""
<?xml version="1.0" ?>
<temporal>
        <fluent_changes>
                <fluent_change energy="20.6285569309" fluent="door" frame="0" new_value="off"/>
                <fluent_change energy="20.6285569309" fluent="door" frame="322" new_value="on" old_value="off"/>
                <fluent_change energy="20.6285569309" fluent="door" frame="347" new_value="off" old_value="on"/>
                <fluent_change energy="20.6285569309" fluent="door" frame="396" new_value="on" old_value="off"/>
                <fluent_change energy="2.42169664849" fluent="PHONE_ACTIVE" frame="0" new_value="off"/>
                <fluent_change energy="4.16467029398" fluent="cup_MORE" frame="0" new_value="off"/>
                <fluent_change energy="5.6543235132" fluent="screen" frame="0" new_value="off"/>
                <fluent_change energy="1.91087102473" fluent="cup_LESS" frame="0" new_value="off"/>
                <fluent_change energy="3.00948331339" fluent="thirst" frame="0" new_value="on"/>
                <fluent_change energy="7.60801819001" fluent="water" frame="0" new_value="off"/>
                <fluent_change energy="1.91087102473" fluent="trash_MORE" frame="0" new_value="off"/>
                <fluent_change energy="2.42169664849" fluent="light" frame="0" new_value="on"/>
                <fluent_change energy="1.91087102473" fluent="TRASH_LESS" frame="0" new_value="off"/>
        </fluent_changes>
        <actions>
                <event action="standing_START" energy="20.6285569309" frame="322"/>
                <event action="standing_END" energy="20.6285569309" frame="347"/>
                <event action="standing_START" energy="20.6285569309" frame="396"/>
        </actions>
</temporal>
"""

# NOTE: this assumes there is at most one action change between frame1 and frame2
# THERE IS A DISTINCT LACK OF CHECKING THINGS TO BE SURE HERE
# NOTE: we're now penalizing multiple counts of the same action...
# NOTE: does not pair START and END together???
def queryXMLForActionBetweenFrames(xml,action,frame1,frame2):
	debugOn = True
	count = 0
	for event in sorted(xml.findall('actions/event'), key=lambda elem: int(elem.attrib['frame'])):
		if event.attrib['action'] == action:
			frame = int(event.attrib['frame'])
			if frame > frame1 and frame < frame2:
				#return {"frame":frame, "energy": float(event.attrib['energy']}
				count += 1
			elif frame >= frame2:
				break
	return count

# AS ABOVE BUT PAIRS START AND END, so it knows if an action is "ongoing" into the frameslice you care about
# TODO: does not know how multiple action pairings turn into different actions, or how to handle fake action pairings ala door ... 
def queryXMLForActionsBetweenFrames(xml,actions,frame1,frame2):
	debugOn = False
	count = 0
	if len(actions) > 1:
		raise ValueError("DOES NOT KNOW HOW TO HANDLE multiple action pairings yet: {}".format(actions))
	actions = actions[0]
	if debugOn:
		print("HUNTING FOR {} BETWEEN {} AND {}".format(actions[0],frame1,frame2))
		printXMLActions(xml)
	is_happening = False
	for event in sorted(xml.findall('actions/event'), key=lambda elem: int(elem.attrib['frame'])):
		frame = int(event.attrib['frame'])
		if event.attrib['action'] == actions[0]:
			if frame < frame1:
				is_happening = True
			elif frame > frame1 and frame < frame2:
				is_happening = False
				count += 1
			elif frame >= frame2:
				break
		elif event.attrib['action'] == actions[1]:
			if frame < frame1:
				is_happening = False
			elif frame > frame1 and frame < frame2:
				is_happening = False
				count += 1
			elif frame >= frame2:
				break
	if is_happening:
		count += 1
	return count

"""
This tried to be smart and see whether fluent changes were conflicting and
what that really meant in terms of whether and how fluents changed between frames...
which was a kind of bad approach because that was looking at maybe pre-fixing stuff
unintelligently as compared to handing the raw-ish fluent data to the grammar
### DO NOT USE ###
"""
def buildDictForFluentBetweenFramesIntoResults(xml,fluent,onsoffs,frame1,frame2):
	debugQuery = False
	if debugQuery:
		print("SEARCHING {} between {} and {}".format(fluent,frame1,frame2))
		printXMLFluents(xml)
	prefix = "{}_{}_".format(fluent,frame1)
	frame1 = int(frame1)
	frame2 = int(frame2)
	onstring = onsoffs[0]
	offstring = onsoffs[1]
	on_off = 0
	off_on = 0
	on = 0
	off = 0
	start_value = None
	end_value = None
	fluent_changes = sorted(xml.findall('.//fluent_change'), key=lambda elem: int(elem.attrib['frame']))
	for fluent_change in fluent_changes:
		if fluent_change.attrib['fluent'] == fluent:
			frame = int(fluent_change.attrib['frame'])
			if not start_value:
				if frame < frame1:
					start_value = str(fluent_change.attrib['new_value'])
					if debugQuery:
						print("- frame {}: storing 'old' value of {}".format(frame,start_value))
				else: # frame >= frame1, but didn't have a start value
					end_value = str(fluent_change.attrib['new_value'])
					if 'old_value' in fluent_change.attrib:
						start_value = str(fluent_change.attrib['old_value'])
					if start_value and start_value != end_value:
						if debugQuery:
							print("+ frame {}: start: {}; now: {}".format(frame,start_value,end_value))
						if start_value == "on":
							on_off += 100
						else:
							off_on += 100
					elif not start_value:
						if end_value == "on":
							if debugQuery:
								print(". setting start_value to off")
							start_value = "off"
							off_on += 100
						else:
							start_value = "on"
							if debugQuery:
								print(". setting start_value to on")
							on_off += 100
					if debugQuery:
						print("+ frame {}: start: {}; now: {}".format(frame,start_value,end_value))
					start_value = end_value
			else:
				if frame < frame1:
					start_value = str(fluent_change.attrib['new_value'])
					if debugQuery:
						print("- frame {}: storing 'old' value of {}".format(frame,start_value))
				elif frame >= frame2:
					break
				else:
					end_value = str(fluent_change.attrib['new_value'])
					if 'old_value' in fluent_change.attrib:
						next_start_value = str(fluent_change.attrib['old_value'])
						# there may be a conflict here
						if start_value and next_start_value != start_value:
							if start_value == "on":
								on_off += 100
							else:
								off_on += 100
						start_value = next_start_value
						# and now to see if we changed /in/ this fluent change, given the old_value
						if end_value != start_value:
							if start_value == "on":
								on_off += 100
							else:
								off_on += 100
					else:
						# we don't know what our previous value is, all we know is we have a fluent change, assume it's a change
						if start_value == "on":
							off_on += 100
						else:
							on_off += 100
					if debugQuery:
						print("+ frame {}: start: {}; now: {}".format(frame,start_value,end_value))
					start_value = end_value
	if not on_off and not off_on:
		if start_value:
			if start_value == "on":
				on = 100
			else:
				off = 100
		else:
			pass
	retval = {
		"{}{}_{}".format(prefix,onstring,offstring): on_off,
		"{}{}_{}".format(prefix,offstring,onstring): off_on,
		"{}{}".format(prefix,onstring): on,
		"{}{}".format(prefix,offstring): off,
	}
	if debugQuery:
		print("RETVAL FOR FRAME {} to {}:\n{}".format(frame1,frame2,"\n".join(key + ": " + str(retval[key]) for key in retval)))
	return retval

# NOTE: THIS IS THE ONE TO USE. IT IS SIMPLE AND DOES ITS BEST TO MAINTAIN THE RAW
# FLUENT DATA UP TO THE GRAMMAR/WHATNOT
# NOTE: this doesn't care how many fluent changes there are, only where things start and where they end up
# NOTE: this appears to fail to fill in "stayed on" or "stayed off" appropriately,
# doesn't look back to see what the value was BEFORE the frame range
# THERE IS A DISTINCT LACK OF CHECKING THINGS TO BE SURE HERE
def buildDictForDumbFluentBetweenFramesIntoResults(xml,fluent,onsoffs,frame1,frame2):
	debugQuery = False
	if debugQuery:
		print("SEARCHING DUMB {} between {} and {}".format(fluent,frame1,frame2))
		printXMLFluents(xml)
	prefix = "{}_{}_".format(fluent,frame1)
	onstring = onsoffs[0]
	offstring = onsoffs[1]
	on_off = 0
	off_on = 0
	on = 0
	off = 0
	frame1 = int(frame1)
	frame2 = int(frame2)
	fluent_changes = sorted(xml.findall('.//fluent_change'), key=lambda elem: int(elem.attrib['frame']))
	old_value = False
	for fluent_change in fluent_changes:
		if fluent_change.attrib['fluent'] == fluent:
			frame = int(fluent_change.attrib['frame'])
			if frame <= frame1:
				old_value = fluent_change.attrib['new_value']
			if frame > frame1 and frame <= frame2:
				# we're only counting "changes" because that's all that was ever really detected, despite what our xml might look like
				# TODO: penalize conflicts somehow. I think that will require a complete reorg of all the things wrapping this
				# and technically we're counting /everything/ as a change
				# but we should listen to and trust 'old_value' if we have it. and okay, we'll listen to our previous value a little
				# just not penalize things for not matching!
				new_value = fluent_change.attrib['new_value']
				""" removed some smart 'if it hasn't changed' code, because it was being too smart? """
				#if 'old_value' in fluent_change.attrib:
				#	if fluent_change.attrib['old_value'] == new_value:
				#		old_value = new_value
				#		continue
				#	if debugQuery:
				#		print("+ frame {}: now: {} was: {}".format(frame,new_value,fluent_change.attrib['old_value']))
				#else:
				#	if debugQuery:
				#		print("+ frame {}: now: {} was: {}".format(frame,new_value,old_value))
				#if old_value and old_value == new_value:
				#	if debugQuery:
				#		print("+ frame {}: still: {}".format(frame,new_value))
				#	continue
				if new_value == "on": #NOT "onsoffs".
					off_on += 100
				else:
					on_off += 100
				old_value = new_value
			if frame >= frame2:
				break
	#return {"start": {"energy":start_energy, "value":start_value}, "end": {"energy":end_energy, "value":end_value}, "changed": start_value != end_value }
	if not on_off and not off_on:
		if old_value == "on":
			on = 100
		elif old_value == "off":
			off = 100
		else:
			#on = 50
			#off = 50
			on = 25
			off = 25
			on_off = 25
			off_on = 25
	retval = {
		"{}{}_{}".format(prefix,onstring,offstring): on_off,
		"{}{}_{}".format(prefix,offstring,onstring): off_on,
		"{}{}".format(prefix,onstring): on,
		"{}{}".format(prefix,offstring): off,
	}
	if debugQuery:
		print("RETVAL FOR FRAME {} to {}:\n{}".format(frame1,frame2,"\n".join(key + ": " + str(retval[key]) for key in retval)))
	return retval

def buildDictForActionPossibilities(fluent,frame,actions):
	prefix = "{}_action_{}_".format(fluent,frame)
	retval = {}
	for key in actions:
		keykey = "{}{}".format(prefix,key)
		retval[keykey] = actions[key]
		#if actions[key] > 100:
		#	print fluent
		#	print frame
		#	print actions
		#	raise SystemExit(0)
	return retval
	
def buildDictForFluentChangePossibilities(fluent,frame,onstring,offstring,prev,now):
	prefix = "{}_{}_".format(fluent,frame)
	changed = prev != now
	on_off = off_on = on = off = 0
	if changed:
		if prev == "on":
			on_off = 100
		else:
			off_on = 100
	else:
		if now == "on":
			on = 100
		else:
			off = 100
	return {
		"{}{}_{}".format(prefix,onstring,offstring): on_off,
		"{}{}_{}".format(prefix,offstring,onstring): off_on,
		"{}{}".format(prefix,onstring): on,
		"{}{}".format(prefix,offstring): off,
	}
	
def queryXMLForAnswersBetweenFrames(xml,oject,frame1,frame2,source,dumb=False):
	# get actions and fluents for the oject
	retval = {}
	import summerdata
	onsoffs = summerdata.onsoffs # dispense, thirst, waterstream, cup
	if not oject in onsoffs.keys():
		raise ValueError("unknown object type in queryXMLForAnswersBetweenFrames: {} not found in {}".format(oject, onsoffs.keys()))
	if oject == "ringer":
		#nothing to do with this
		return retval
	if oject == "doorlock":
		#nothing to do with this
		return retval
	#fluents
	onsoffs = onsoffs[oject]
	if oject in summerdata.actionPairings:
		actionpairings = summerdata.actionPairings[oject]
	else:
		print("WARNING: missing actionpairing: {} (queryXMLForAnswersBetweenFrames)".format(oject))
	oject2 = False
	tmpoject = None
	if oject == "trash":
		tmpoject = "trash"
		oject = "trash_MORE"
	elif oject == "cup":
		tmpoject = oject
		oject = "_".join((tmpoject,"MORE"))
		oject2 = "_".join((tmpoject,"LESS"))
	elif oject == "phone":
		tmpoject = oject
		oject = "PHONE_ACTIVE"
	if dumb:
		result = buildDictForDumbFluentBetweenFramesIntoResults(xml,oject,onsoffs,frame1,frame2)
		if oject2:
			result2 = buildDictForDumbFluentBetweenFramesIntoResults(xml,oject2,onsoffs,frame1,frame2)
	else:
		result = buildDictForFluentBetweenFramesIntoResults(xml,oject,onsoffs,frame1,frame2)
		if oject2:
			result2 = buildDictForFluentBetweenFramesIntoResults(xml,oject2,onsoffs,frame1,frame2)
	if tmpoject == "phone":
		result = {k.replace(oject,tmpoject):result[k] for k in result}
		oject = tmpoject
	if tmpoject == "trash":
		resultkeys = result.keys()
		tmpresult = result
		result = {}
		result[tmpoject + "_" + str(frame1) + "_less"] = 0
		result[tmpoject + "_" + str(frame1) + "_more"] = 0
		result[tmpoject + "_" + str(frame1) + "_same"] = 0
		if source.startswith('causal'):
			#result[tmpoject + "_" + str(frame1) + "_more"] = tmpresult[oject + "_" + str(frame1) + "_off_on"] + tmpresult[oject + "_" + str(frame1) + "_on"]
			#result[tmpoject + "_" + str(frame1) + "_same"] = tmpresult[oject + "_" + str(frame1) + "_on_off"] + tmpresult[oject + "_" + str(frame1) + "_off"]
			result[tmpoject + "_" + str(frame1) + "_more"] = tmpresult[oject + "_" + str(frame1) + "_off_on"]
			result[tmpoject + "_" + str(frame1) + "_same"] = 100 - tmpresult[oject + "_" + str(frame1) + "_off_on"]
		oject = tmpoject
	elif oject == "waterstream":
		# we only did "on" and "off" with waterstream
		for key in result.keys():
			if key.endswith("water_on_water_off") or key.endswith("water_off_water_on"):
				result.pop(key,None)
	elif tmpoject == "cup":
		#turn "off", "on_off", "on", "off_on" into "_same", "_less", "_more"
		MORE_off = result["_".join((oject,str(frame1),"off"))]
		MORE_onoff = result["_".join((oject,str(frame1),"on","off"))]
		MORE_offon = result["_".join((oject,str(frame1),"off","on"))]
		MORE_on = result["_".join((oject,str(frame1),"on"))]
		LESS_off = result2["_".join((oject2,str(frame1),"off"))]
		LESS_onoff = result2["_".join((oject2,str(frame1),"on","off"))]
		LESS_offon = result2["_".join((oject2,str(frame1),"off","on"))]
		LESS_on = result2["_".join((oject2,str(frame1),"on"))]
		oject = tmpoject
		## NO BAD WRONG
		#result = {
		#	"_".join((oject,str(frame1),"more")): MORE_on + MORE_offon,
		#	"_".join((oject,str(frame1),"less")): LESS_on + LESS_offon,
		#	"_".join((oject,str(frame1),"same")): max(0,100-(MORE_on+MORE_offon)-(LESS_on+LESS_offon)),
		#}
		result = {
			"_".join((oject,str(frame1),"more")): MORE_offon,
			"_".join((oject,str(frame1),"less")): LESS_offon,
			"_".join((oject,str(frame1),"same")): max(0,100-(MORE_offon)-(LESS_offon)),
		}
	if oject != "water": # just ... don't even ... yeah.
		retval.update(result)
	#actions
	if oject == "door":
		result = {"act_opened":0, "act_closed":0, "act_not_opened_closed":0}
		if source.startswith('orig'):
			count = queryXMLForActionBetweenFrames(xml,"standing_START",frame1,frame2)
			noaction = True
			if count:
				noaction = False
				result['act_opened'] = 100 * count
			count = queryXMLForActionBetweenFrames(xml,"standing_END",frame1,frame2)
			if count:
				noaction = False
				result['act_closed'] = 100 * count
			if noaction:
				result['act_not_opened_closed'] = 100
		else:
			# causal grammar answers mirror the fluent change
			result['act_closed'] = retval[oject+'_'+str(frame1)+'_'+'open_closed']
			result['act_opened'] = retval[oject+'_'+str(frame1)+'_'+'closed_open']
			result['act_not_opened_closed'] = retval[oject+'_'+str(frame1)+'_'+'closed'] + retval[oject+'_'+str(frame1)+'_'+'open'] 
			# JUST GOT AN IDEA OF QUERYING FOR ANY INSTANCE OF STANDING -- BUT SINCE WE'RE WINNING ON ACTIONS, MAYBE NOT RIGHT NOW
		#print("retval: {}".format(retval))
		#print("result: {}".format(result))
	elif oject == "light":
		result = {"act_pushbutton":0, "act_no_pushbutton":0}
		count = queryXMLForActionBetweenFrames(xml,"pressbutton_START",frame1,frame2)
		if count:
			result['act_pushbutton'] = 100 * count
		else:
			result['act_no_pushbutton'] = 100
	elif oject == "screen":
		result = {"act_mousekeyboard":0, "act_no_mousekeyboard":0}
		count = queryXMLForActionsBetweenFrames(xml,actionpairings,frame1,frame2)
		if count:
			result['act_mousekeyboard'] = 100 * count
		else:
			result['act_no_mousekeyboard'] = 100
	elif oject == "phone":
		# act_no_call, act_received_call 
		result = {"act_no_call":0, "act_received_call":0}
		# don't need to worry about end
		count = queryXMLForActionBetweenFrames(xml,"makecall_START",frame1,frame2)
		if count:
			result['act_received_call'] = 100 * count
		else:
			result['act_no_call'] = 100
	elif oject == "cup": # (water)
		result = [] # the action for this frame will be handled by thirst
		pass
	elif oject == "thirst":
		result = [] # nope nope nope not here
		pass
	elif oject == "water":
		result = {"act_drink": 0, "act_no_drink": 0}
		count = queryXMLForActionBetweenFrames(xml,"drink_START",frame1,frame2)
		if not count:
			count = queryXMLForActionBetweenFrames(xml,"drink_END",frame1,frame2)
		if count:
			result["act_drink"] = 100 * count
		else:
			result["act_no_drink"] = 100
	elif oject == "waterstream":
		result = {"act_dispensed": 0, "act_no_dispense": 0}
		count = queryXMLForActionBetweenFrames(xml,"benddown_START",frame1,frame2)
		if count:
			result["act_dispensed"] = 100 * count
		else:
			result["act_no_dispense"] = 100
	elif oject == "trash":
		result = {"act_benddown": 0, "act_no_benddown": 0}
		count = queryXMLForActionBetweenFrames(xml,"throwtrash_END",frame1,frame2)
		if count:
			result["act_benddown"] = 100 * count
		else:
			result["act_no_benddown"] = 100
	else:
		raise ValueError("Unknown object type in queryXMLForAnswersBetweenFrames: {}".format(oject))
	result = buildDictForActionPossibilities(oject,frame1,result)
	if oject == "waterstream":
		# more kludging for irregular names
		result_tmp = {}
		for key in result.keys():
			result_tmp[key.replace("waterstream_action","dispense")] = result[key]
		result = result_tmp
	# print("retval: {}".format(retval))
	# print("result: {}".format(result))
	retval.update(result)
	return retval

# this is used by getFluentChangesForFluentBetweenFrames only?
def getFluentChangesForFluent(xml, fluent):
	return xml.findall("./fluent_changes/fluent_change[@fluent='{}'][@old_value]".format(fluent))

# this is used for base_unittests validation, not for actual dealwithdbresults
def getFluentChangesForFluentBetweenFrames(xml, fluent, frame1, frame2):
	assert(frame1 <= frame2)
	changes = getFluentChangesForFluent(xml, fluent)
	retval = []
	for change in changes:
		if int(change.attrib['frame']) >= frame1 and int(change.attrib['frame']) < frame2:
			retval.append(change)
	return retval
