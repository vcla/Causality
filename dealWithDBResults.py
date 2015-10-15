import csv
import hashlib
import MySQLdb
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import videoCutpoints
import summerdata

DBNAME = "amy_cvpr2012"
DBUSER = "amycvpr2012"
DBHOST = "127.0.0.1" # forwarding 3306
DBPASS = "rC2xfLQFDMUZqJxf"
TBLPFX = "cvpr2012_"
kKnownObjects = ["screen","door","light","phone","ringer","trash","dispense","thirst","waterstream","cup","water"]
kInsertionHash = "1234567890"

globalDryRun = None # commandline argument

# managing human responses for comparison - note upload versus download

def getExampleFromDB(exampleName, conn=False):
	resultStorageFolder = "results/cvpr_db_results/"
	exampleNameForDB = exampleName.replace("_","")
	m = hashlib.md5(exampleNameForDB)
	tableName = TBLPFX + m.hexdigest()
	leaveconn = True
	if not conn:
		leaveconn = False
		conn = MySQLdb.connect (host = DBHOST, user = DBUSER, passwd = DBPASS, db = DBNAME)
	cursor = conn.cursor ()
	try:
		cursor.execute("SHOW COLUMNS FROM {}".format(tableName))
	except (MySQLdb.ProgrammingError):
		print "TABLE {} not found for example {}".format(tableName,exampleNameForDB)
		return
	allColumns = cursor.fetchall()
	sqlStatement = "SELECT "
	for singleColumn in allColumns:
		if "act_made_call" not in singleColumn[0] and "act_unlock" not in singleColumn[0]:
			sqlStatement += singleColumn[0] + ", "
		else:
			pass #print singleColumn
	notNullColumn = allColumns[len(allColumns)-3] # the last data column (hopefully)
	#cursor.execute("SELECT data.* FROM {} data, cvpr2012complete tally WHERE data.name = tally.name AND data.stamp = tally.stamp and tally.hash = %s".format(tableName), m.hexdigest())
	#cursor.execute("SELECT * FROM {} WHERE {} IS NOT NULL".format(tableName, notNullColumn[0]))
	sqlStatement = sqlStatement[:-2]
	sqlStatement += " FROM " + tableName + " WHERE " + notNullColumn[0] + " IS NOT NULL"
	cursor.execute(sqlStatement)
	if not globalDryRun:
		csv_filename = resultStorageFolder + exampleName + ".csv"
		print(" as {}".format(csv_filename))
		csv_writer = csv.writer(open(csv_filename, "wt"))
		csv_writer.writerow([i[0] for i in cursor.description]) # write headers
		csv_writer.writerows(cursor)
		del csv_writer # this will close the CSV file
	cursor.close()
	if not leaveconn:
		conn.close()

#def getAllExamplesFromDB()
#	fileWithExampleNames = 'testingCutPoints.txt'
#	f = open(fileWithExampleNames, 'r')
#	for line in f:
#		line = line.split(

"""
fluent_parses
{3113: {'door': 0.6043252768966678},
 3127: {'door': 0.6546979187448962, 'screen': 2.1738928903851895}}

temporal_parses
{3097: {'throwtrash_START': {'agent': 'uuid1', 'energy': 1.20098}},
 3101: {'throwtrash_END': {'agent': 'uuid1', 'energy': 1.20098}},
 3103: {'standing_START': {'agent': 'uuid1', 'energy': 0.551687}},
 3111: {'standing_END': {'agent': 'uuid1', 'energy': 0.551687}},
 3115: {'makecall_START': {'agent': 'uuid1', 'energy': 1.429988}},
 3119: {'makecall_END': {'agent': 'uuid1', 'energy': 1.429988}}}
"""

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
		prev_value = None
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
				if prev_value:
					fluent_attributes['old_value'] = prev_value
				fluent_parse = ET.SubElement(fluent_changes,'fluent_change', fluent_attributes)
				prev_value = fluent_status
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
		xml_stuff.printXMLActions(xml)
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
	debugQuery = True
	if debugQuery:
		print("SEARCHING {} between {} and {}".format(fluent,frame1,frame2))
		xml_stuff.printXMLFluents(xml)
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
		xml_stuff.printXMLFluents(xml)
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
			if frame < frame1:
				old_value = fluent_change.attrib['new_value']
			if frame >= frame1 and frame <= frame2:
				# we're only counting "changes" because that's all that was ever really detected, despite what our xml might look like
				# TODO: penalize conflicts somehow. I think that will require a complete reorg of all the things wrapping this
				# and technically we're counting /everything/ as a change
				# but we should listen to and trust 'old_value' if we have it. and okay, we'll listen to our previous value a little
				# just not penalize things for not matching!
				new_value = fluent_change.attrib['new_value']
				if 'old_value' in fluent_change.attrib:
					if fluent_change.attrib['old_value'] == new_value:
						old_value = new_value
						continue
					if debugQuery:
						print("+ frame {}: now: {} was: {}".format(frame,new_value,fluent_change.attrib['old_value']))
				else:
					if debugQuery:
						print("+ frame {}: now: {} was: {}".format(frame,new_value,old_value))
				if old_value and old_value == new_value:
					if debugQuery:
						print("+ frame {}: still: {}".format(frame,new_value))
					continue
				if new_value == 'on':
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
			on = 50
			off = 50
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
	onsoffs = summerdata.onsoffs # dispense, thirst, waterstream, cup
	if not oject in onsoffs.keys():
		raise ValueError("unknown object type in queryXMLForAnswersBetweenFrames: {}".format(oject))
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
		print("WARNING: missing actionpairing: {}".format(oject))
	oject2 = False
	tmpoject = None
	if oject == "trash":
		tmpoject = "trash"
		oject = "trash_MORE"
	elif oject == "cup":
		tmpoject = oject
		oject = "_".join((tmpoject,"MORE"))
		oject2 = "_".join((tmpoject,"LESS"))
	if dumb:
		result = buildDictForDumbFluentBetweenFramesIntoResults(xml,oject,onsoffs,frame1,frame2)
		if oject2:
			result2 = buildDictForDumbFluentBetweenFramesIntoResults(xml,oject2,onsoffs,frame1,frame2)
	else:
		result = buildDictForFluentBetweenFramesIntoResults(xml,oject,onsoffs,frame1,frame2)
		if oject2:
			result2 = buildDictForFluentBetweenFramesIntoResults(xml,oject2,onsoffs,frame1,frame2)
	if tmpoject == "trash":
		resultkeys = result.keys()
		tmpresult = result
		result = {}
		result[tmpoject + "_" + str(frame1) + "_less"] = 0
		result[tmpoject + "_" + str(frame1) + "_more"] = 0
		result[tmpoject + "_" + str(frame1) + "_same"] = 0
		if source.startswith('causal'):
			result[tmpoject + "_" + str(frame1) + "_more"] = tmpresult[oject + "_" + str(frame1) + "_off_on"] + tmpresult[oject + "_" + str(frame1) + "_on"]
			result[tmpoject + "_" + str(frame1) + "_same"] = tmpresult[oject + "_" + str(frame1) + "_on_off"] + tmpresult[oject + "_" + str(frame1) + "_off"]
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
		result = {
			"_".join((oject,str(frame1),"more")): MORE_on + MORE_offon,
			"_".join((oject,str(frame1),"less")): LESS_on + LESS_offon,
			"_".join((oject,str(frame1),"same")): max(0,100-(MORE_on+MORE_offon)-(LESS_on+LESS_offon)),
		}
	if oject != "water": # just ... don't even ... yeah.
		retval.update(result)
	#actions
	if oject == "door":
		result = {"act_opened":0, "act_closed":0, "act_not_opened_closed":0}
		if source.startswith('orig'):
			result = {"act_opened":0, "act_closed":0, "act_not_opened_closed":0}
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
	print("retval: {}".format(retval))
	print("result: {}".format(result))
	retval.update(result)
	return retval

def uploadComputerResponseToDB(example, fluent_and_action_xml, source, conn = False):
	debugQuery = False
	parsedExampleName = example.split('_')
	# for db lookup, remove "room" at end, and munge _'s away
	exampleNameForDB = "".join(parsedExampleName[:-1])
	# for cutpoints, just remove "room" at end
	exampleNameForCutpoints = "_".join(parsedExampleName[:-1])
	m = hashlib.md5(exampleNameForDB)
	tableName = TBLPFX + m.hexdigest()
	leaveconn = True
	if not conn:
		leaveconn = False
		conn = MySQLdb.connect (host = DBHOST, user = DBUSER, passwd = DBPASS, db = DBNAME)
	cursor = conn.cursor ()
	try:
		cursor.execute("SHOW COLUMNS FROM {}".format(tableName))
	except (MySQLdb.ProgrammingError):
		print "TABLE {} not found for example {}".format(tableName,exampleNameForDB)
		return False
	allColumns = cursor.fetchall()
	# get cutpoints and objects from our columns; we'll build the actions and fluents back up manually from lookups
	print("{}".format(tableName))
	cutpoint_lookup = videoCutpoints.cutpoints[exampleNameForCutpoints]
	cutpoints = []
	ojects = []
	sqlStatement = "SELECT "
	for singleColumn in allColumns:
		column = singleColumn[0]
		if column not in ("act_made_call", "act_unlock", "name", "stamp", "hash"):
			# sqlStatement += singleColumn[0] + ", "
			# print("COLUMN: {}".format(column))
			if column.count("_") < 3:
				oject, frame, tmp = singleColumn[0].split("_",2)
			else:
				oject, frame, tmp, rest = singleColumn[0].split("_",3)
			if frame == "action":
				frame = tmp
			if oject == "dispense":
				continue
			ojects.append(oject,)
			cutpoints.append(int(frame))
	ojects = list(set(ojects))
	cutpoints = sorted(list(set(cutpoints)))
	if str(cutpoints[-1]) in cutpoint_lookup:
		cutpoints.append(cutpoint_lookup[str(cutpoints[-1])])
	else:
		print("WARNING: {} failed to be found in cutpoints for {}".format(str(cutpoints[-1]),exampleNameForCutpoints))
		last_cutpoint = sorted(int(x) for x in cutpoint_lookup)[-1]
		cutpoints.append(cutpoint_lookup[str(last_cutpoint)])

	# let's make sure we know how to work on all of these objects
	known_ojects = kKnownObjects
	if not all(map(lambda x: x in known_ojects,ojects)):
		difference = set(ojects).difference(known_ojects)
		print("skipping {} due to unknown: {}".format(example,", ".join(difference)))
		return
	print("WORKING ON------{}".format(ojects))
	# for each of our objects, figure out what we think went on at each cutpoint
	#print("objects: {}".format(ojects))
	#print("frames: {}".format(cutpoints))
	insertion_object = {"name": source, "hash": kInsertionHash}
	if debugQuery:
		print minidom.parseString(fluent_and_action_xml).toprettyxml(indent="\t")
	fluent_and_action_xml_xml = ET.fromstring(fluent_and_action_xml)
	for oject in ojects:
		prev_frame = cutpoints[0]
		for frame in cutpoints[1:]:
			#print("{} - {}".format(oject, frame))
			insertion_object.update(queryXMLForAnswersBetweenFrames(fluent_and_action_xml_xml,oject,prev_frame,frame,source,not source.endswith('smrt')))
			prev_frame = frame
	print("INSERT: {}".format(insertion_object))
	# http://stackoverflow.com/a/9336427/856925
	for key in insertion_object.keys():
		if type(insertion_object[key]) is str:
			insertion_object[key] = "'{}'".format(insertion_object[key])
	qry = "INSERT INTO %s (%s) VALUES (%s)" % (tableName, ", ".join(insertion_object.keys()), ", ".join(map(str,insertion_object.values())))
	if not globalDryRun:
		cursor.execute("DELETE FROM %s WHERE name IN ('%s')" % (tableName,source))
		cursor.execute(qry)
		conn.commit()
	cursor.close()
	if not leaveconn:
		conn.close()
	return True


##########################

import xml_stuff

if __name__ == '__main__':
	debugQuery = False
	import argparse
	kSummerDataPythonDir="results/CVPR2012_reverse_slidingwindow_action_detection_logspace";
	parser = argparse.ArgumentParser()
	parser.add_argument("mode", choices=["upload","download","upanddown","list"])
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-d','--dry-run', action='store_true', dest='dryrun', required=False, help='Do not actually upload data to the db or save downloaded data; only valid for "upload" or "download", does not make sense for "upanddown" or "list"')
	group.add_argument('-o','--only', action='append', dest='examples_only', required=False, help='specific examples to run, versus all found examples')
	group.add_argument('-x','--exclude', action='append', dest='examples_exclude', required=False, help='specific examples to exclude, out of all found examples', default=[])
	parser.add_argument("-s","--simplify", action="store_true", required=False, help="simplify the summerdata grammar to only include fluents that start with the example name[s]")
	# parser.add_argument("--dry-run",required=False,action="store_true") #TODO: would be nie
	args = parser.parse_args()
	examples = []
	globalDryRun = args.dryrun
	if args.mode in ("list","upanddown",) and globalDryRun:
		raise ValueError("dryrun is only valid for 'download' or 'upload', not 'upanddown' or 'list'")
	if args.examples_only:
		examples = args.examples_only
	else:
		for filename in os.listdir (kSummerDataPythonDir):
			if filename.endswith(".py") and filename != "__init__.py":
				example = filename[:-3]
				if example not in args.examples_exclude:
					examples.append(filename[:-3])
	conn = MySQLdb.connect (host = DBHOST, user = DBUSER, passwd = DBPASS, db = DBNAME)
	if args.mode in ("list",):
		for filename in os.listdir (kSummerDataPythonDir):
			if filename.endswith(".py") and filename != "__init__.py":
				example = filename[:-3]
				exampleNameForDB, room = example.rsplit('_',1)
				exampleNameForDB = exampleNameForDB.replace("_","")
				m = hashlib.md5(exampleNameForDB)
				print("{}	{}".format(example,m.hexdigest()))
	if args.mode in ("upload","upanddown",):
		print("===========")
		print("UPLOADING")
		print("===========")
		completed = []
		also_completed = []
		oject_failed = []
		also_oject_failed = []
		import_failed = []
		import causal_grammar
		import causal_grammar_summerdata # sets up causal_forest
		causal_forest_orig = causal_grammar_summerdata.causal_forest
		# These thresholds tuned for this fluent data because it's not "flipping between on and off", it's 
		# flipping "did transition closed to on" and "didn't transition closed to on"
		causal_grammar.kFluentThresholdOnEnergy = 0.6892
		causal_grammar.kFluentThresholdOffEnergy = 0.6972
		#raise("MAYBE DELETE 'computer' FROM RESULTS BEFORE RE-RUNNING")
		for example in examples:
			print("---------\nEXAMPLE: {}\n-------".format(example))
			if args.simplify:
				causal_grammar_summerdata.causal_forest = causal_grammar.get_simplified_forest_for_example(causal_forest_orig, example)
				print("... simplified to {}".format(", ".join(x['symbol'] for x in causal_grammar_summerdata.causal_forest)))
			try:
				fluent_parses, temporal_parses = causal_grammar.import_summerdata(example,kSummerDataPythonDir)
				import pprint
				pp = pprint.PrettyPrinter(indent=1)
				print" fluent parses "
				pp.pprint(fluent_parses)
				print("")
				print" action parses "
				pp.pprint(temporal_parses)
				print("")
			except ImportError as ie:
				print("IMPORT FAILED: {}".format(ie))
				import_failed.append(example)
				continue
			orig_xml = munge_parses_to_xml(fluent_parses,temporal_parses)
			fluent_and_action_xml = causal_grammar.process_events_and_fluents(causal_grammar_summerdata.causal_forest, fluent_parses, temporal_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy, True) # last true: suppress the xml output
			if debugQuery:
				print("_____ ORIG FLUENT AND ACTION PARSES _____")
				#print minidom.parseString(orig_xml).toprettyxml(indent="\t")
				xml_stuff.printXMLActionsAndFluents(ET.fromstring(orig_xml))
				print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
				print("_____ AFTER CAUSAL GRAMMAR _____")
				#print minidom.parseString(fluent_and_action_xml).toprettyxml(indent="\t")
				xml_stuff.printXMLActionsAndFluents(ET.fromstring(fluent_and_action_xml))
				print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
			print("------> causalgrammar <------")
			if uploadComputerResponseToDB(example, fluent_and_action_xml, 'causalgrammar', conn):
				completed.append("{}-{}".format(example,'causalgrammar'))
			else:
				oject_failed.append("{}-{}".format(example,'causalgrammar'))
			print("------> causalsmrt <------")
			if uploadComputerResponseToDB(example, fluent_and_action_xml, 'causalsmrt', conn):
				completed.append("{}-{}".format(example,'causalsmrt'))
			else:
				oject_failed.append("{}-{}".format(example,'causalsmrt'))
			print("------> origdata <------")
			if uploadComputerResponseToDB(example, orig_xml, 'origdata', conn):
				completed.append("{}-{}".format(example,'origdata'))
			else:
				oject_failed.append("{}-{}".format(example,'origdata'))
			print("------> origsmrt <------")
			if uploadComputerResponseToDB(example, orig_xml, 'origsmrt', conn):
				completed.append("{}-{}".format(example,'origsmrt'))
			else:
				oject_failed.append("{}-{}".format(example,'origsmrt'))
		print("COMPLETED: {}".format(completed))
		if oject_failed:
			print("SKIPPED DUE TO OBJECT: {}".format(oject_failed))
		if import_failed:
			print("SKIPPED DUE TO IMPORT: {}".format(import_failed))
		print("....................")
		print("....................")
	if args.mode in ("download","upanddown"):
		print("===========")
		print("DOWNLOADING")
		print("===========")
		for example in examples:
			print("---------\nEXAMPLE: {}\n-------".format(example))
			example, room = example.rsplit('_',1)
			getExampleFromDB(example, conn)
	conn.close()
