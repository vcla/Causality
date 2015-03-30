import csv
import hashlib
import MySQLdb
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

DBNAME = "amy_cvpr2012"
DBUSER = "amycvpr2012"
DBHOST = "127.0.0.1" # forwarding 3306
DBPASS = "rC2xfLQFDMUZqJxf"
TBLPFX = "cvpr2012_"
kInfinityCutpoint = 1000000000000000 # close enough to infinity, anyway; working on an off-by-one issue
kKnownObjects = ["screen","door","light","phone","ringer"]
kInsertionHash = "1234567890"

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
	csv_writer = csv.writer(open((resultStorageFolder + exampleName + ".csv"), "wt"))
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
	count = 0
	for event in xml.findall('actions/event'):
		if event.attrib['action'] == action:
			frame = int(event.attrib['frame'])
			if frame > frame1 and frame < frame2:
				#return {"frame":frame, "energy": float(event.attrib['energy']}
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
	prefix = "{}_{}_".format(fluent,frame1)
	onstring = onsoffs[0]
	offstring = onsoffs[1]
	on_off = 0
	off_on = 0
	on = 0
	off = 0
	start_value = None
	end_value = None
	fluent_changes = xml.findall('.//fluent_change')
	for fluent_change in fluent_changes:
		if fluent_change.attrib['fluent'] == fluent:
			frame = int(fluent_change.attrib['frame'])
			if not start_value:
				if frame < frame1:
					start_value = str(fluent_change.attrib['new_value'])
					if debugQuery:
						print("- frame {}: storing 'old' value of {}".format(frame,start_value))
				else: #frame >= frame1
					# let's just get these ducks lined up....
					end_value = str(fluent_change.attrib['new_value'])
					# trust 'old_value' over what we had before ...  TODO: penalize if it doesn't agree?
					if 'old_value' in fluent_change.attrib.keys():
						start_value = str(fluent_change.attrib['old_value'])
						if end_value != start_value:
							if start_value == "on":
								on_off += 100
							else:
								off_on += 100
					else:
						# assume we're staying steady and just reporting it because of some other reason?
						start_value = end_value
					if debugQuery:
						print("+ frame {}: start: {}; now: {}".format(frame,start_value,start_value))
					continue
			else:
				if frame >= frame2:
					break
				else:
					next_end_value = str(fluent_change.attrib['new_value'])
					if 'old_value' in fluent_change.attrib.keys():
						next_old_value = str(fluent_change.attrib['old_value'])
					else:
						next_old_value = None
					if end_value and next_old_value != end_value:
						#conflict! we need to add a transition from next_old to end_value
						if next_old_value == "on":
							off_on += 100
						else:
							on_off += 100
					end_value = next_end_value
					if end_value == "on":
						off_on += 100
					else:
						on_off += 100
					if debugQuery:
						print("+ frame {}: start: {}; now: {}".format(frame,start_value,end_value))
	#if debugQuery:
	#	print("query results: {}".format({"start": {"energy":start_energy, "value":start_value}, "end": {"energy":end_energy, "value":end_value}, "changed": start_value != end_value }))
	#return {"start": {"energy":start_energy, "value":start_value}, "end": {"energy":end_energy, "value":end_value}, "changed": start_value != end_value }
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
		print("DUMB SEARCHING {} between {} and {}".format(fluent,frame1,frame2))
	prefix = "{}_{}_".format(fluent,frame1)
	onstring = onsoffs[0]
	offstring = onsoffs[1]
	on_off = 0
	off_on = 0
	on = 0
	off = 0
	fluent_changes = xml.findall('.//fluent_change')
	for fluent_change in fluent_changes:
		if fluent_change.attrib['fluent'] == fluent:
			frame = int(fluent_change.attrib['frame'])
			if (frame >= frame1 or frame <= frame2):
				# we're only counting "changes" because that's all that was ever really detected, despite what our xml might look like
				# TODO: penalize conflicts somehow. I think that will require a complete reorg of all the things wrapping this
				# and technically we're counting /everything/ as a change
				if str(fluent_change.attrib['new_value']) == "on":
					off_on += 100
				else:
					on_off += 100
			if frame >= frame2:
				break
	#if debugQuery:
	#	print("query results: {}".format({"start": {"energy":start_energy, "value":start_value}, "end": {"energy":end_energy, "value":end_value}, "changed": start_value != end_value }))
	#return {"start": {"energy":start_energy, "value":start_value}, "end": {"energy":end_energy, "value":end_value}, "changed": start_value != end_value }
	if not on_off and not off_on:
		on = 0
		off = 0
	retval = {
		"{}{}_{}".format(prefix,onstring,offstring): on_off,
		"{}{}_{}".format(prefix,offstring,onstring): off_on,
		"{}{}".format(prefix,onstring): on,
		"{}{}".format(prefix,offstring): off,
	}
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
	
def queryXMLForAnswersBetweenFrames(xml,oject,frame1,frame2,dumb=False):
	# get actions and fluents for the oject
	retval = {}
	onsoffs = { "door": ["open","closed"], "light": ["on","off"], "screen": ["on","off"], "phone": ["active","off"], "ringer": ["ring","no_ring"] }
	if not oject in onsoffs.keys():
		raise ValueError("unknown object type in queryXMLForAnswersBetweenFrames: {}".format(oject))
	if oject == "ringer":
		#nothing to do with this
		return retval
	#fluents
	onsoffs = onsoffs[oject]
	if dumb:
		result = buildDictForDumbFluentBetweenFramesIntoResults(xml,oject,onsoffs,frame1,frame2)
	else:
		result = buildDictForFluentBetweenFramesIntoResults(xml,oject,onsoffs,frame1,frame2)
	retval.update(result)
	#actions
	if oject == "door":
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
	elif oject == "light":
		result = {"act_pushbutton":0, "act_no_pushbutton":0}
		# don't need to worry about end
		count = queryXMLForActionBetweenFrames(xml,"pressbutton_START",frame1,frame2)
		if count:
			result['act_pushbutton'] = 100 * count
		else:
			result['act_no_pushbutton'] = 100
	elif oject == "screen":
		result = {"act_mousekeyboard":0, "act_no_mousekeyboard":0}
		# don't need to worry about end
		count = queryXMLForActionBetweenFrames(xml,"usecomputer_START",frame1,frame2)
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
	else:
		raise ValueError("Unknown object type in queryXMLForAnswersBetweenFrames: {}".format(oject))
	result = buildDictForActionPossibilities(oject,frame1,result)
	retval.update(result)
	return retval

def uploadComputerResponseToDB(example, fluent_and_action_xml, source, conn = False):
	exampleNameForDB, room = example.rsplit('_',1)
	exampleNameForDB = exampleNameForDB.replace("_","")
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
			ojects.append(oject,)
			cutpoints.append(int(frame))
	cutpoints.append(kInfinityCutpoint) # close enough to infinity, anyway; working on an off-by-one issue
	ojects = list(set(ojects))
	cutpoints = sorted(list(set(cutpoints)))
	# let's make sure we know how to work on all of these objects
	known_ojects = kKnownObjects
	if not all(map(lambda x: x in known_ojects,ojects)):
		print("skipping {} due to an un unknown object (one of {})".format(example,ojects))
		return
	# for each of our objects, figure out what we think went on at each cutpoint
	#print("objects: {}".format(ojects))
	#print("frames: {}".format(cutpoints))
	insertion_object = {"name": source, "hash": kInsertionHash}
	print minidom.parseString(fluent_and_action_xml) #.toprettyxml(indent="\t")
	fluent_and_action_xml_xml = ET.fromstring(fluent_and_action_xml)
	for oject in ojects:
		prev_frame = cutpoints[0]
		for frame in cutpoints[1:]:
			#print("{} - {}".format(oject, frame))
			insertion_object.update(queryXMLForAnswersBetweenFrames(fluent_and_action_xml_xml,oject,prev_frame,frame,not source.endswith('smrt')))
			prev_frame = frame
	print("INSERT: {}".format(insertion_object))
	# http://stackoverflow.com/a/9336427/856925
	for key in insertion_object.keys():
		if type(insertion_object[key]) is str:
			insertion_object[key] = "'{}'".format(insertion_object[key])
	qry = "INSERT INTO %s (%s) VALUES (%s)" % (tableName, ", ".join(insertion_object.keys()), ", ".join(map(str,insertion_object.values())))
	cursor.execute("DELETE FROM %s WHERE name IN ('%s')" % (tableName,source))
	cursor.execute(qry)
	conn.commit()
	cursor.close()
	if not leaveconn:
		conn.close()
	return True


##########################


if __name__ == '__main__':
	import argparse
	kSummerDataPythonDir="results/CVPR2012_reverse_slidingwindow_action_detection_logspace";
	parser = argparse.ArgumentParser()
	parser.add_argument("mode", choices=["upload","download","upanddown","list"])
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-o','--only', action='append', dest='examples_only', required=False, help='specific examples to run, versus all found examples')
	group.add_argument('-x','--exclude', action='append', dest='examples_exclude', required=False, help='specific examples to exclude, out of all found examples', default=[])
	parser.add_argument("-s","--simplify", action="store_true", required=False, help="simplify the summerdata grammar to only include fluents that start with the example name[s]")
	# parser.add_argument("--dry-run",required=False,action="store_true") #TODO: would be nie
	args = parser.parse_args()
	examples = []
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
		#raise("MAYBE DELETE 'computer' FROM RESULTS BEFORE RERUNNING")
		for example in examples:
			print("---------\nEXAMPLE: {}\n-------".format(example))
			if args.simplify:
				if len(example.split("_")) == 3:
					#TODO: does not work on door_13_light_3_roomname, for instance. could/should split
					# prune causal forest to 'screen' events
					causal_forest = []
					fluent = example.split("_",1)[0]
					for root in causal_forest_orig:
						if root['symbol'].startswith(fluent + "_"):
							causal_forest.append(root)
					causal_grammar_summerdata.causal_forest = causal_forest
				else:
					causal_grammar_summerdata.causal_forest = causal_forest_orig
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
				#print("IMPORT FAILED: {}".format(ie))
				import_failed.append(example)
				continue
			orig_xml = munge_parses_to_xml(fluent_parses,temporal_parses)
			fluent_and_action_xml = causal_grammar.process_events_and_fluents(causal_grammar_summerdata.causal_forest, fluent_parses, temporal_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy, True) # last true: suppress the xml output
			print minidom.parseString(orig_xml).toprettyxml(indent="\t")
			print minidom.parseString(fluent_and_action_xml).toprettyxml(indent="\t")
			#print fluent_and_action_xml.toprettyxml(indent="\t")
			if uploadComputerResponseToDB(example, fluent_and_action_xml, 'causalgrammar', conn):
				completed.append(example)
			else:
				oject_failed.append(example)
			if uploadComputerResponseToDB(example, fluent_and_action_xml, 'causalsmrt', conn):
				completed.append(example)
			else:
				oject_failed.append(example)
			if uploadComputerResponseToDB(example, orig_xml, 'origdata', conn):
				also_completed.append(example)
			else:
				also_oject_failed.append(example)
			if uploadComputerResponseToDB(example, orig_xml, 'origsmrt', conn):
				also_completed.append(example)
			else:
				also_oject_failed.append(example)
		print("COMPLETED: {}".format(completed))
		print("ALSO COMPLETED: {}".format(also_completed))
		print("SKIPPED DUE TO OBJECT: {}".format(oject_failed))
		print("ALSO SKIPPED DUE TO OBJECT: {}".format(also_oject_failed))
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
