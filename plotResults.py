import csv
import hashlib
import MySQLdb
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import pprint
import xml_stuff
import videoCutpoints
import summerdata
from causal_grammar import TYPE_ACTION, TYPE_FLUENT

#TODO: this really shouldn't require the database, should it? everything's already dumped to cvpr_db_results.... but kResultStorageFolder is unused! BAH! DOH! Yes. So ideally before this "python dealWithDBResults.py upanddown" to create those.

DBNAME = "amy_cvpr2012"
DBUSER = "amycvpr2012"
DBHOST = "127.0.0.1" # forwarding 3306
DBPASS = "rC2xfLQFDMUZqJxf"
TBLPFX = "cvpr2012_"

kSummerDataPythonDir="results/CVPR2012_reverse_slidingwindow_action_detection_logspace";
kResultStorageFolder = "results/cvpr_db_results/"
kActionPairings = summerdata.actionPairings
kOnsOffs = summerdata.onsoffs

kTruthDir = "results/truth/"
kImpulseDivision = 100 # "number of frames" divided by this gives a the full impulse width

#TODO: how to manage more complicated fluents, such as cup_MORE_on, cup_MORE_off, cup_LESS_on, cup_LESS_off, TRASH_LESS_on, TRASH_LESS_OFF, trash_MORE_on, trash_MORE_off? these should each get a new line, simplest answer. but then our alternating rows thing DIES.
#TODO: water and trash above
#TODO: how to manage timers: become_thirsty?

import causal_grammar
import causal_grammar_summerdata
causal_forest = causal_grammar_summerdata.causal_forest

def buildHeatmapForExample(exampleName, prefix, conn=False):
	debugOn = False
	parsedExampleName = exampleName.split('_')
	# -------------------- STAGE 1: READ FROM DB --------------------------
	# for db lookup, remove "room" at end, and munge _'s away
	exampleNameForDB = "".join(parsedExampleName[:-1])
	# for cutpoints, just remove "room" at end
	exampleNameForCutpoints = "_".join(parsedExampleName[:-1])
	m = hashlib.md5(exampleNameForDB)
	tableName = TBLPFX + m.hexdigest()
	leaveconn = True
	human_dups = dict()
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
	sqlStatement = "SELECT name, "
	for singleColumn in allColumns:
		columnName = singleColumn[0]
		if "act_made_call" not in columnName and "act_unlock" not in columnName and columnName.startswith(prefix):
			sqlStatement += columnName + ", "
		else:
			pass #print singleColumn
	notNullColumn = allColumns[len(allColumns)-3] # the last data column (hopefully)
	sqlStatement = sqlStatement[:-2]
	sqlStatement += " FROM " + tableName + " WHERE " + notNullColumn[0] + " IS NOT NULL"
	cursor.execute(sqlStatement)
	headers = [i[0] for i in cursor.description]
	# SELECT name, screen_192_off_on, screen_192_on_off, screen_192_on, screen_192_off, screen_348_off_on, screen_348_on_off, screen_348_on, screen_348_off, screen_action_192_act_mousekeyboard, screen_action_192_act_no_mousekeyboard, screen_action_348_act_mousekeyboard, screen_action_348_act_no_mousekeyboard FROM cvpr2012_7f05529dec6a03d3a459fc2ee1969f7f WHERE screen_action_348_act_no_mousekeyboard IS NOT NULL
	csv_rows = []
	first = True
	frames_sorted = sorted(int(x) for x in videoCutpoints.cutpoints[exampleNameForCutpoints].keys())
	start_of_frames = frames_sorted[0]
	end_of_frames = int(videoCutpoints.cutpoints[exampleNameForCutpoints][str(frames_sorted[-1])])
	impulse_width_2 = (end_of_frames - start_of_frames) / (kImpulseDivision / 2)# width / 2
	action_width = impulse_width_2 * 2
	for row in cursor:
		fluent_matrix = []
		action_matrix = []
		fluents = False
		actions = False
		name = row[0]
		if name in human_dups:
			human_dups[name] += 1
			name = "{}_{}".format(name, human_dups[name])
		else:
			human_dups[name] = 1
		xindex = 1
		while xindex < len(row):
			(root, actiontest, rest) = headers[xindex].split("_",2)
			if actiontest == TYPE_ACTION:
				actions = True
				# a yes action at this point means we "trigger" it for 1 frame in the middle of our framecount, give or take
				(start_frame, _, action) = rest.split("_") # assumes "act" before "act_no"; assumes only "act" and "act_no"; TODO: what else exists in the database???
				start_frame = int(start_frame)
				end_frame = int(videoCutpoints.cutpoints[exampleNameForCutpoints][str(start_frame)])
				frame_diff = end_frame - start_frame
				zeros = ['0',]*(frame_diff)
				choices = row[xindex:xindex+2]
				sum_choices = float(sum(choices))
				choices = [a/sum_choices for a in choices]
				triggered = choices[0] >= choices[1]
				if triggered:
					trigger_start = int(frame_diff / 2) - int(action_width / 2)
					zeros[trigger_start:trigger_start+action_width] = [choices[0],] * action_width
				action_matrix.extend(zeros)
				xindex += 2
			else:
				fluents = True
				start_frame = int(actiontest)
				end_frame = int(videoCutpoints.cutpoints[exampleNameForCutpoints][str(start_frame)])
				frame_diff = end_frame-start_frame
				# note this throws preference to on, then off, then onoff, then offon
				# just because we need some simple tie-breaking way
				# TODO: -1 class to represent unknown/unsure?
				choices = row[xindex:xindex+4]
				sum_choices = float(sum(choices))
				if sum_choices == 0:
					choices = [.25, .25, .25, .25] # TODO: is this a valid something? or a sign of a bug?
				else:
					choices = [a/sum_choices for a in choices]
				offon = choices[0]
				onoff = choices[1]
				on = choices[2]
				off = choices[3]
				if on == max(offon,onoff,on,off):
					result = [on,]*(frame_diff)
				elif off == max(offon,onoff,on,off):
					result = [1-off,]*(frame_diff)
				elif onoff == max(offon,onoff,on,off):
					diff_2 = frame_diff / 2
					result = [onoff,]*(diff_2) + [1-onoff,]*(frame_diff-diff_2)
				else: # it's offon, then
					diff_2 = frame_diff / 2
					result = [1-offon,]*(diff_2) + [offon,]*(frame_diff-diff_2)
				fluent_matrix.extend(result)
				xindex += 4
		if first:
			row = ["NAME",]
			row.extend(xrange(start_of_frames,end_of_frames))
			csv_rows.append(",".join([str(x) for x in row]))
			first = False
		if fluents:
			row = [name + " " + prefix + " on",]
			row.extend([str(x) for x in fluent_matrix])
			csv_rows.append(",".join(row))
		if actions:
			row = [name + " " + action,]
			row.extend([str(x) for x in action_matrix])
			csv_rows.append(",".join(row))
	cursor.close()
	if not leaveconn:
		conn.close()
	# -------------------- STAGE 2: READ FROM PARSE --------------------------
	# for screen_1_lounge, that's CVPR2012_fluent_result/screen_on_off_fluent_results.txt, CVPR2012_fluent_result/screen_off_on_fluent_results.txt, and results/CVPR2012_reverse_slidingwindow_action_detection_logspace/screen_1_lounge.py
	# thankfully, import_summerdata uses parsingSummerActionAndFluentOutput's readFluentResults and readActionResults
	fluent_parses, action_parses = causal_grammar.import_summerdata(exampleName, kSummerDataPythonDir)
	# displaying fluent changes as _impulses_ around their detection,
	# and 50% everywhere else
	fluent_matrix = [0.5,]*(end_of_frames-start_of_frames)
	fluent_matrix_len = len(fluent_matrix)
	for frame in sorted(x for x in fluent_parses.keys() if x < end_of_frames):
		# prefix is, for example, 'screen', the root of the tree we are looking at
		if prefix in fluent_parses[frame]:
			energy = fluent_parses[frame][prefix]
			probability = causal_grammar.energy_to_probability(energy)
			offset_left = 0
			if int(frame) - start_of_frames < impulse_width_2:
				offset_left = start_of_frames - int(frame)
			offset_right = 0
			if int(frame) + impulse_width_2 > end_of_frames:
				offset_right = end_of_frames - int(frame)
			if debugOn and (offset_left != 0 or offset_right != 0):
				print("OFFSETS: {} and {} at frame {}".format(offset_left, offset_right, frame))
			result = [1-probability,] * (impulse_width_2 - offset_left) + [probability,] * (impulse_width_2 - offset_right)
			start_replacement = int(frame) - start_of_frames - impulse_width_2 - offset_left
			if debugOn:
				print("START FRAME: {}; CURRENT FRAME: {}".format(start_of_frames,int(frame)))
				print("REPLACING {} to {} with {}".format(start_replacement,start_replacement+len(result),result))
			fluent_matrix[start_replacement:start_replacement+len(result)] = result
	row = ['ORIG' + " " + prefix + " on",]
	row.extend([str(x) for x in fluent_matrix])
	csv_rows.append(",".join(row))
	if len(fluent_matrix) != fluent_matrix_len:
		print("ERROR: fluent_matrix grew in replacement")
		raise SystemExit(0)

	#{1016: {'usecomputer_END': {'energy': 0.0, 'agent': 'uuid1'}}, 733: {'usecomputer_END': {'energy': 0.0, 'agent': 'uuid1'}}, 388: {'usecomputer_END': {'energy': 0.0, 'agent': 'uuid1'}}, 389: {'usecomputer_START': {'energy': 0.0, 'agent': 'uuid1'}}, 582: {'usecomputer_START': {'energy': 0.001096, 'agent': 'uuid1'}}, 650: {'usecomputer_END': {'energy': 0.0, 'agent': 'uuid1'}}, 651: {'usecomputer_START': {'energy': 6e-06, 'agent': 'uuid1'}}, 525: {'usecomputer_END': {'energy': 3e-06, 'agent': 'uuid1'}}, 526: {'usecomputer_START': {'energy': -0.0, 'agent': 'uuid1'}}, 889: {'usecomputer_START': {'energy': 0.0, 'agent': 'uuid1'}}, 791: {'usecomputer_END': {'energy': -0.0, 'agent': 'uuid1'}}, 593: {'usecomputer_END': {'energy': 0.001096, 'agent': 'uuid1'}}, 594: {'usecomputer_START': {'en
	actionPairings = kActionPairings[prefix]
	for actionPairing in actionPairings:
		last_frame = start_of_frames
		action_matrix = []
		actions = False
		last_probability = 0
		for frame in sorted(x for x in action_parses.keys() if x < end_of_frames):
			# prefix is, for example, 'screen', the root of the tree we are looking at
			if actionPairing[0] in action_parses[frame]:
				energy = action_parses[frame][actionPairing[0]]['energy']
				last_probability = causal_grammar.energy_to_probability(energy)
				frame_diff = frame - last_frame
				result = [0.,]*frame_diff
				action_matrix.extend(result)
				actions = True
				last_frame = frame
			elif actionPairing[1] in action_parses[frame]:
				frame_diff = frame - last_frame
				result = [last_probability,]*frame_diff # we know start and stop are symmetric
				action_matrix.extend(result)
				last_probability = 0
				actions = True
				last_frame = frame
		if not actions:
			# we've never seen anything! 0% all the way!
			result = [0.,]*(end_of_frames - start_of_frames)
			action_matrix.extend(result)
		elif frame < end_of_frames:
			if debugOn:
				print("LAST FRAME BEFORE END OF FRAMES: filling {} from {} -> {}".format(last_probability,last_frame,end_of_frames))
			result = [last_probability,]*(end_of_frames-last_frame)
			action_matrix.extend(result)
		row = ['ORIG' + " " + actionPairing[0].split("_")[0],]
		row.extend([str(x) for x in action_matrix])
		csv_rows.append(",".join(row))

	# -------------------- STAGE 3: READ CAUSALGRAMMAR RESULTS  --------------------------
	fluent_and_action_xml_string = causal_grammar.process_events_and_fluents(causal_grammar_summerdata.causal_forest, fluent_parses, action_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy, True) # last True: suppress the xml output
	# <temporal><fluent_changes><fluent_change energy="17.6095287144" fluent="screen" frame="0" new_value="off" /><fluent_change energy="16.5108710247" fluent="screen" frame="328" new_value="on" old_value="off" /></fluent_changes></temporal>
	fluent_and_action_xml = ET.fromstring(fluent_and_action_xml_string)
	fluent_changes = sorted(fluent_and_action_xml.findall('.//fluent_change'), key=lambda elem: int(elem.attrib['frame']))
	events = sorted(fluent_and_action_xml.findall('.//event'), key=lambda elem: int(elem.attrib['frame']))
	last_frame = start_of_frames
	fluent_matrix = []
	fluents = False
	last_probability = 0
	thison = kOnsOffs[prefix][0]
	thisoff = kOnsOffs[prefix][1]
	for fluent in fluent_changes:
		# prefix is, for example, 'screen', the root of the tree we are looking at
		# ignoring energies at the moment because they are the sum of all the energies for this 'chain' as compared to other chains, and not for the individual nodes (oops TODO?)
		if prefix == fluent.attrib['fluent']:
			# xml_stuff.printXMLFluent(fluent)
			frame = int(fluent.attrib['frame'])
			new_value = fluent.attrib['new_value']
			if 'old_value' in fluent.attrib:
				fluents = True # this counts as having an answer if we needed one
				old_value = fluent.attrib['old_value']
				if old_value == thison:
					last_probability = 1.
				else:
					last_probability = 0.
			if new_value == thison:
				probability = 1.
			else:
				probability = 0.
			if frame <= start_of_frames:
				# we're not there yet :)
				last_probability = probability
				fluents = True # and this cements our answer
				continue
			if int(frame) > end_of_frames:
				# just wrap up our last value
				frame = end_of_frames
				frame_diff = end_of_frames - last_frame
				result = [last_probability,]*frame_diff
				fluent_matrix.extend(result)
				last_frame = end_of_frames
				break
			frame_diff = frame - last_frame
			last_frame = frame
			if not fluents:
				# let's fill in our previous state with the opposite to this one...
				# because we take in our fluents as "changes" to the fluent!
				# alternately, it might be fair to say 50/50 on this one...
				last_probability = probability
				result = [1-last_probability,]*frame_diff
			else:
				# we've seen something before, that's what we fill up to this frame
				result = [last_probability,]*frame_diff
				last_probability = probability
			fluent_matrix.extend(result)
			fluents = True
	if not fluents:
		# we've never seen anything! 50% all the way!
		result = [0.5,]*(end_of_frames-start_of_frames)
		fluent_matrix.extend(result)
	elif last_frame < end_of_frames:
		result = [last_probability,]*(end_of_frames-last_frame)
		fluent_matrix.extend(result)
	row = ['CAUSAL ' + prefix + " on",]
	row.extend([str(x) for x in fluent_matrix])
	csv_rows.append(",".join(row))

	# <temporal><actions><event action="usecomputer_START" energy="33.4413967566" frame="658" /><event action="usecomputer_START" energy="33.4271617566" frame="1000" /><event action="usecomputer_START" energy="52.6460829824" frame="1025" /><event action="usecomputer_END" energy="52.2956748688" frame="1232" /></actions></temporal>
	actionPairings = kActionPairings[prefix]
	for actionPairing in actionPairings:
		last_frame = start_of_frames
		action_matrix = []
		actions = False
		last_probability = 0
		for event in events:
			result = []
			# ignoring energies at the moment because they are the sum of all the energies for this 'chain' as compared to other chains, and not for the individual nodes (oops TODO?)
			frame = int(event.attrib['frame'])
			frame_diff = frame - last_frame
			if actionPairing[0] == event.attrib[TYPE_ACTION]:
				if debugOn:
					xml_stuff.printXMLAction(event)
				last_probability = 1.
				if frame <= start_of_frames:
					if debugOn:
						print("PRE-START, SETTING PREV_PROB: 1")
					continue
				if frame > end_of_frames:
					frame = end_of_frames
					frame_diff = frame - last_frame
				result = [0.,]*frame_diff
			elif actionPairing[1] == event.attrib[TYPE_ACTION]:
				if debugOn:
					xml_stuff.printXMLAction(event)
				last_probability = 0.
				if frame <= start_of_frames:
					if debugOn:
						print("PRE-START, SETTING PREV_PROB: 0")
					continue
				if frame > end_of_frames:
					frame = end_of_frames
					frame_diff = frame - last_frame
				result = [1.,]*frame_diff # we know start and stop are symmetric
			if len(result) > 0:
				actions = True
				action_matrix.extend(result)
				last_frame = frame
			if frame >= end_of_frames:
				break
		if not actions:
			# we've never seen anything! 0% all the way!
			result = [last_probability,]*(end_of_frames - start_of_frames)
			action_matrix.extend(result)
		elif last_frame < end_of_frames:
			if debugOn:
				print("LAST FRAME BEFORE END OF FRAMES: filling {} from {} -> {}".format(last_probability,last_frame,end_of_frames))
			result = [last_probability,]*(end_of_frames-last_frame)
			action_matrix.extend(result)
		row = ['CAUSAL' + " " + actionPairing[0].split("_")[0],]
		row.extend([str(x) for x in action_matrix])
		csv_rows.append(",".join(row))

	# -------------------- STAGE 4: READ GROUND TRUTH --------------------------
	#screen_1_lounge.csv:
	#  192, 338, screen, OFF
	#  339, 985, screen, ON
	#  986, 1298, screen, OFF
	#  284, 986, screen_act, usecomputer
	truthcsv_name = os.path.join(kTruthDir,".".join((exampleName,"csv")))
	if os.path.isdir(kTruthDir) and os.path.exists(truthcsv_name):
		# first, fluents
		result = [0.,] * (end_of_frames - start_of_frames)
		with open(truthcsv_name, 'rb') as truthcsv_file:
			truthcsv = csv.reader(truthcsv_file,skipinitialspace=True)
			for line in truthcsv:
				(start, end, key, value) = line
				if key == prefix:
					if value == "OFF":
						continue
					start = max(0,int(start) - start_of_frames)
					end = min(int(end) - start_of_frames, end_of_frames - start_of_frames)
					if end < 0:
						continue
					result[start:end] = [1.,] * (end - start)
		row = ['TRUTH ' + prefix + ' on',]
		row.extend([str(x) for x in result])
		csv_rows.append(",".join(row))

		# and then, actions!
		actionPairings = kActionPairings[prefix]
		prefix_act = "_".join((prefix,"act"))
		for actionPairing in actionPairings:
			result = [0.,] * (end_of_frames - start_of_frames)
			with open(truthcsv_name, 'rb') as truthcsv_file:
				truthcsv = csv.reader(truthcsv_file,skipinitialspace=True)
				for line in truthcsv:
					(start, end, key, value) = line
					if key == prefix_act and actionPairing[0].startswith(value):
						start = max(0,int(start) - start_of_frames)
						end = min(int(end) - start_of_frames, end_of_frames - start_of_frames)
						if end < 0:
							continue
						result[start:end] = [1.,] * (end - start)
			row = ['TRUTH ' + actionPairing[0].split("_")[0],]
			row.extend([str(x) for x in result])
			csv_rows.append(",".join(row))

	if not debugOn:
		print("\n".join(csv_rows))

import sys
if len(sys.argv) == 1:
	example = 'screen_1_lounge'
	key = 'screen'
elif len(sys.argv) == 3:
	example = sys.argv[1]
	key = sys.argv[2]
else:
	key = False
	print("requires 0 or 2 arguments: example, key")
if key:
	if key in kActionPairings.keys():
		buildHeatmapForExample(example,key)
	else:
		raise SystemExit("'{}' not handled; we only know: {}".format(key,", ".join(kActionPairings.keys())))
