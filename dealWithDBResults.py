import csv
import hashlib
import MySQLdb
DBNAME = "amy_cvpr2012"
DBUSER = "amycvpr2012"
DBHOST = "127.0.0.1" # forwarding 3306
DBPASS = "rC2xfLQFDMUZqJxf"

# managing human responses for comparison - note upload versus download

def getExampleFromDB(exampleName, conn=False):
	resultStorageFolder = "cvpr_db_results/"
	exampleNameForDB = exampleName.replace("_","")
	m = hashlib.md5(exampleNameForDB)
	tableName = "cvpr2012_" + m.hexdigest()
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
	from xml.dom.minidom import Document
	import causal_grammar
	import math
	doc = Document()
	temporal_stuff = doc.createElement("temporal")
	doc.appendChild(temporal_stuff)
	fluent_changes = doc.createElement("fluent_changes")
	temporal_stuff.appendChild(fluent_changes)
	actions_el = doc.createElement("actions")
	temporal_stuff.appendChild(actions_el)
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
				fluent_parse = doc.createElement("fluent_change")
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
				fluent_parse.setAttribute("fluent",fluent)
				fluent_parse.setAttribute("new_value",fluent_status)
				if prev_value:
					fluent_parse.setAttribute("old_value",prev_value)
				fluent_parse.setAttribute("frame",str(frame))
				fluent_parse.setAttribute("energy",str(fluent_value))
				fluent_changes.appendChild(fluent_parse)
				prev_value = fluent_status
	# continuing to avoid cleverness, now for each action in all frames, build our xml
	for action in sorted(actions):
		prev_value = None
		for frame in sorted(action_parses):
			if action in action_parses[frame]:
				event = doc.createElement("event")
				event_value = action_parses[frame][action]
				event.setAttribute("action",action)
				event.setAttribute("energy",str(event_value['energy'])) # ignore 'agent'
				event.setAttribute("frame",str(frame))
				actions_el.appendChild(event)
	return doc

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
def queryXMLForActionBetweenFrames(xml,action,frame1,frame2):
	events = xml.getElementsByTagName('event')
	found_start = False
	for event in events:
		if event.attributes['action'].nodeValue == action:
			frame = int(event.attributes['frame'].nodeValue)
			if frame > frame1 and frame < frame2:
				return {"frame":frame, "energy": float(event.attributes['energy'].nodeValue)}
	return None

# NOTE: this doesn't care how many fluent changes there are, only where things start and where they end up
# THERE IS A DISTINCT LACK OF CHECKING THINGS TO BE SURE HERE
def queryXMLForFluentBetweenFrames(xml,fluent,frame1,frame2):
	fluent_changes = xml.getElementsByTagName('fluent_change')
	prev_value = None
	prev_energy = None
	found_start = False
	start_value = None
	end_value = None
	start_energy = None
	end_energy = None
	#causal_grammar.hr()
	#print("SEARCHING {} between {} and {}".format(fluent,frame1,frame2))
	#print("{}\t{}\t{}\t{}".format('frame','prev','start','end'))
	for fluent_change in fluent_changes:
		if fluent_change.attributes['fluent'].nodeValue == fluent:
			frame = int(fluent_change.attributes['frame'].nodeValue)
			#print("comparing {}".format([frame, frame1, frame2, type(frame1),type(frame2)]))
			#print("{}\t{}\t{}\t{}".format(frame,prev_value,start_value,end_value))
			if not found_start:
				if frame > frame1:
					#print("FOUND FIRST FRAME: {}".format(frame))
					if prev_value:
						start_value = prev_value
						start_energy = prev_energy
						#print("assigning prev ({})-> start".format(start_value))
					elif 'prev_value' in fluent_change.attributes.keys():
						start_value = str(fluent_change.attributes['prev_value'].nodeValue)
						start_energy = float(fluent_change.attributes['energy'].nodeValue)
						#print("assigning now[prev] ({}) -> start".format(start_value))
					else:
						# for lack of anything better, we'll assume we've always been like this
						start_value = str(fluent_change.attributes['new_value'].nodeValue)
						start_energy = float(fluent_change.attributes['energy'].nodeValue)
						#print("assigning now ({}) -> start".format(start_value))
					if frame < frame2:
						end_value = str(fluent_change.attributes['new_value'].nodeValue)
						end_energy = float(fluent_change.attributes['energy'].nodeValue)
						#print("assigning now[new] ({}) -> end".format(end_value))
					else:
						end_value = start_value
						end_value = end_value
						#print("assigning start value ({}) -> end".format(end_value))
					found_start = True
					continue
				#print("assigning now[new] -> prev")
				#prev_value =  str(fluent_change.attributes['new_value'].nodeValue)
				#prev_energy = float(fluent_change.attributes['energy'].nodeValue)
			else:
				if frame >= frame2:
					#print("breaking")
					break
				else:
					#print("assigning now[new] -> end")
					end_value = str(fluent_change.attributes['new_value'].nodeValue)
					end_energy = float(fluent_change.attributes['energy'].nodeValue)
					#print("end set: {}, {}".format(end_value,end_energy))
	return {"start": {"energy":start_energy, "value":start_value}, "end": {"energy":end_energy, "value":end_value}, "changed": start_value != end_value }

def buildDictForActionPossibilities(fluent,frame,actions):
	prefix = "{}_action_{}_".format(fluent,frame)
	retval = {}
	for key in actions:
		retval["{}{}".format(prefix,key)] = actions[key]
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
	
def queryXMLForAnswersBetweenFrames(xml,oject,frame1,frame2):
	# get actions and fluents for the oject
	retval = {}
	onsoffs = { "door": ["open","closed"], "light": ["on","off"], "screen": ["on","off"] }
	if not oject in onsoffs.keys():
		raise "Unknown object type in queryXMLForAnswersBetweenFrames: {}".format(oject)
	#fluents
	onsoffs = onsoffs[oject]
	fluent_change = queryXMLForFluentBetweenFrames(xml,oject,frame1,frame2)
	result = buildDictForFluentChangePossibilities(oject,frame1,onsoffs[0],onsoffs[1],fluent_change['start']['value'],fluent_change['end']['value'])
	retval.update(result)
	if oject == "door":
		#actions
		result = {"act_opened":0, "act_closed":0, "act_not_opened_closed":0}
		action = queryXMLForActionBetweenFrames(xml,"standing_START",frame1,frame2)
		if action:
			result['act_opened'] = 100
		else:
			action = queryXMLForActionBetweenFrames(xml,"standing_END",frame1,frame2)
			if action:
				result['act_closed'] = 100
			else:
				result['act_not_opened_closed'] = 100
	elif oject == "light":
		result = {"act_pushbutton":0, "act_no_pushbutton":0}
		# don't need to worry about end
		if queryXMLForActionBetweenFrames(xml,"pressbutton_START",frame1,frame2):
			result['act_pushbutton'] = 100
		else:
			result['act_no_pushbutton'] = 100
	elif oject == "screen":
		result = {"act_mousekeyboard":0, "act_no_mousekeyboard":0}
		# don't need to worry about end
		if queryXMLForActionBetweenFrames(xml,"usecomputer_START",frame1,frame2):
			result['act_mousekeyboard'] = 100
		else:
			result['act_no_mousekeyboard'] = 100
	else:
		raise("unknown object type in queryXMLForAnswersBetweenFrames: {}".format(oject))
	result = buildDictForActionPossibilities(oject,frame1,result)
	retval.update(result)
	return retval

def uploadComputerResponseToDB(example, fluent_and_action_xml, source, conn = False):
	exampleNameForDB, room = example.rsplit('_',1)
	exampleNameForDB = exampleNameForDB.replace("_","")
	m = hashlib.md5(exampleNameForDB)
	tableName = "cvpr2012_" + m.hexdigest()
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
	cutpoints.append(1000000000000000) # close enough to infinity, anyway; working on an off-by-one issue
	ojects = list(set(ojects))
	cutpoints = sorted(list(set(cutpoints)))
	# let's make sure we know how to work on all of these objects
	known_ojects = ["screen","door","light"]
	if not all(map(lambda x: x in known_ojects,ojects)):
		print("skipping {} due to an un unknown object (one of {})".format(example,ojects))
		return
	# for each of our objects, figure out what we think went on at each cutpoint
	#print("objects: {}".format(ojects))
	#print("frames: {}".format(cutpoints))
	insertion_object = {"name": source, "hash": "1234567890"}
	print fluent_and_action_xml.toprettyxml(indent="\t")
	for oject in ojects:
		prev_frame = cutpoints[0]
		for frame in cutpoints[1:]:
			#print("{} - {}".format(oject, frame))
			insertion_object.update(queryXMLForAnswersBetweenFrames(fluent_and_action_xml,oject,prev_frame,frame))
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
	if False:
		mode = "upload"
	else:
		mode = "download"
	examples = ['door_11_9406', 'door_12_light_2_9406', 'door_13_light_3_9406', 'door_15_9406', 'door_1_8145', 'door_2_8145', 'door_4_trash_1_8145', 'door_5_8145', 'door_6_8145', 'door_7_8145', 'door_8_doorlock_3_8145', 'door_9_8145', 'doorlock_1_door_3_8145', 'doorlock_2_8145', 'light_10_9404', 'light_5_9406', 'light_6_9404', 'light_7_9404', 'light_8_screen_50_9404', 'light_9_screen_57_9404', 'phone_13_screen_27_lounge', 'phone_16_9406', 'phone_1_8145', 'phone_20_screen_53_9404', 'phone_24_screen_65_9404', 'phone_25_screen_67_9404', 'phone_2_8145', 'phone_3_8145', 'phone_4_8145', 'screen_10_lounge', 'screen_12_lounge', 'screen_13_lounge', 'screen_14_phone_8_lounge', 'screen_15_lounge', 'screen_16_phone_9_lounge', 'screen_17_trash_5_lounge', 'screen_18_lounge', 'screen_19_lounge', 'screen_1_lounge', 'screen_21_phone_10_lounge', 'screen_23_lounge', 'screen_24_lounge', 'screen_25_lounge', 'screen_26_phone_12_lounge', 'screen_2_lounge', 'screen_30_9406', 'screen_31_9406', 'screen_32_9406', 'screen_35_9406', 'screen_36_9406', 'screen_37_door_14_light_4_9406', 'screen_38_9406', 'screen_39_9406', 'screen_3_phone_5_lounge', 'screen_40_9406', 'screen_41_9406', 'screen_42_9404', 'screen_44_9404', 'screen_45_trash_8_9404', 'screen_46_9404', 'screen_47_water_8_phone_18_9404', 'screen_49_9404', 'screen_4_phone_6_lounge', 'screen_51_9404', 'screen_58_9404', 'screen_5_lounge', 'screen_61_9404', 'screen_63_9404', 'screen_6_lounge', 'screen_7_lounge', 'screen_8_lounge', 'screen_9_phone_7_lounge', 'trash_10_phone_19_9404', 'trash_11_screen_56_9404', 'trash_2_8145', 'trash_3_lounge', 'trash_4_screen_11_lounge', 'trash_7_9406', 'water_10_screen_52_9404', 'water_11_screen_54_9404', 'water_12_phone_21_screen_59_9404', 'water_15_screen_64_9404', 'water_16_screen_66_9404', 'water_17_9404', 'water_18_screen_68_9404', 'water_19_screen_69_9404', 'water_1_8145', 'water_2_8145', 'water_4_8145', 'water_6_waterstream_5_8145', 'water_9_screen_48_trash_9_9404', 'waterstream_11_9404', 'waterstream_1_8145', 'waterstream_2_water_3_8145', 'waterstream_3_water_5_8145', 'waterstream_4_8145', 'waterstream_7_9404', 'waterstream_8_screen_55_9404',]
	#examples = ['light_5_9406',]
	conn = MySQLdb.connect (host = DBHOST, user = DBUSER, passwd = DBPASS, db = DBNAME)
	if mode == "upload":
		completed = []
		also_completed = []
		oject_failed = []
		also_oject_failed = []
		import_failed = []
		import causal_grammar
		import causal_grammar_summerdata as causal_grammar_summerdata # sets up causal_forest
		# These thresholds tuned for this fluent data because it's not "flipping between on and off", it's 
		# flipping "did transition closed to on" and "didn't transition closed to on"
		causal_grammar.kFluentThresholdOnEnergy = 0.6892
		causal_grammar.kFluentThresholdOffEnergy = 0.6972
		#examples = [ "door_1_8145", ]
		#examples = [ "door_2_8145", "door_5_8145", "door_6_8145", "door_7_8145", "door_9_8145", ]
		#raise("MAYBE DELETE 'computer' FROM RESULTS BEFORE RERUNNING")
		for example in examples:
			try:
				fluent_parses, temporal_parses = causal_grammar.import_summerdata(example,'CVPR2012_reverse_slidingwindow_action_detection_logspace')
				import pprint
				pp = pprint.PrettyPrinter(indent=1)
				pp.pprint(fluent_parses)
				pp.pprint(temporal_parses)
			except ImportError as ie:
				print("IMPORT FAILED: {}".format(ie))
				import_failed.append(example)
				continue
			orig_xml = munge_parses_to_xml(fluent_parses,temporal_parses)
			fluent_and_action_xml = causal_grammar.process_events_and_fluents(causal_grammar_summerdata.causal_forest, fluent_parses, temporal_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy, True) # last true: suppress the xml output
			print orig_xml.toprettyxml(indent="\t")
			print fluent_and_action_xml.toprettyxml(indent="\t")
			#print fluent_and_action_xml.toprettyxml(indent="\t")
			if uploadComputerResponseToDB(example, fluent_and_action_xml, 'causalgrammar', conn):
				completed.append(example)
			else:
				also_oject_failed.append(example)
			if uploadComputerResponseToDB(example, orig_xml, 'origdata', conn):
				also_completed.append(example)
			else:
				oject_failed.append(example)
		print("COMPLETED: {}".format(completed))
		print("ALSO COMPLETED: {}".format(also_completed))
		print("SKIPPED DUE TO OBJECT: {}".format(oject_failed))
		print("ALSO SKIPPED DUE TO OBJECT: {}".format(also_oject_failed))
		print("SKIPPED DUE TO IMPORT: {}".format(import_failed))
	elif mode == "download":
		for example in examples:
			example, room = example.rsplit('_',1)
			getExampleFromDB(example, conn)
	conn.close()
