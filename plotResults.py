import csv
import hashlib
import MySQLdb
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import pprint

DBNAME = "amy_cvpr2012"
DBUSER = "amycvpr2012"
DBHOST = "127.0.0.1" # forwarding 3306
DBPASS = "rC2xfLQFDMUZqJxf"
TBLPFX = "cvpr2012_"

kSummerDataPythonDir="results/CVPR2012_reverse_slidingwindow_action_detection_logspace";
kResultStorageFolder = "results/cvpr_db_results/"
kHumanAnnotationClippoints = "results/CVPR2012_humanTestAnnotation.txt"

import causal_grammar
import causal_grammar_summerdata
causal_forest = causal_grammar_summerdata.causal_forest

def buildHeatmapForExample(exampleName, prefix, conn=False):
	parsedExampleName = exampleName.split('_')
	# -------------------- STAGE 1: READ FROM DB --------------------------
	# for db lookup, remove "room" at end, and munge _'s away
	exampleNameForDB = "".join(parsedExampleName[:-1])
	# for clippoints, just remove "room" at end
	exampleNameForClippoints = "_".join(parsedExampleName[:-1])
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
	action_width = 20
	frames_sorted = sorted(video_clippoints[exampleNameForClippoints].keys())
	start_of_frames = int(frames_sorted[0])
	end_of_frames = int(video_clippoints[exampleNameForClippoints][frames_sorted[-1]])
	for row in cursor:
		fluent_matrix = []
		action_matrix = []
		fluents = False
		actions = False
		name = row[0]
		xindex = 1
		while xindex < len(row):
			(root, actiontest, rest) = headers[xindex].split("_",2)
			if actiontest == "action":
				actions = True
				# a yes action at this point means we "trigger" it for 1 frame in the middle of our framecount, give or take
				(start_frame, _, action) = rest.split("_") # assumes "act" before "act_no"; assumes only "act" and "act_no"; TODO: what else exists in the database???
				start_frame = int(start_frame)
				end_frame = int(video_clippoints[exampleNameForClippoints][str(start_frame)])
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
				end_frame = int(video_clippoints[exampleNameForClippoints][str(start_frame)])
				frame_diff = end_frame-start_frame
				# note this throws preference to on, then off, then onoff, then offon
				# just because we need some simple tie-breaking way
				# TODO: -1 class to represent unknown/unsure?
				choices = row[xindex:xindex+4]
				sum_choices = float(sum(choices))
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
	last_frame = start_of_frames
	last_index = 0
	last_energy = 0
	fluent_matrix = []
	fluents = False
	last_probability = 0
	for key in sorted(x for x in fluent_parses.keys() if x < end_of_frames):
		# prefix is, for example, 'screen', the root of the tree we are looking at
		if prefix in fluent_parses[key]:
			energy = fluent_parses[key][prefix]
			probability = causal_grammar.energy_to_probability(energy)
			frame_diff = key - last_frame
			last_frame = key
			if key == 0:
				# we'll just set this here to be picked up by the next loop
				last_probability = probability
			else:
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
		result = [0.5,]*last_db_frame
		fluent_matrix.extend(result)
	elif last_frame < end_of_frames:
		result = [last_probability,]*(end_of_frames-last_frame)
		fluent_matrix.extend(result)
	row = ['ORIG' + " " + prefix + " on",]
	row.extend([str(x) for x in fluent_matrix])
	csv_rows.append(",".join(row))

	last_frame = start_of_frames
	last_index = 0
	last_energy = 0
	action_matrix = []
	actions = False
	last_probability = 0
	#{1016: {'usecomputer_END': {'energy': 0.0, 'agent': 'uuid1'}}, 733: {'usecomputer_END': {'energy': 0.0, 'agent': 'uuid1'}}, 388: {'usecomputer_END': {'energy': 0.0, 'agent': 'uuid1'}}, 389: {'usecomputer_START': {'energy': 0.0, 'agent': 'uuid1'}}, 582: {'usecomputer_START': {'energy': 0.001096, 'agent': 'uuid1'}}, 650: {'usecomputer_END': {'energy': 0.0, 'agent': 'uuid1'}}, 651: {'usecomputer_START': {'energy': 6e-06, 'agent': 'uuid1'}}, 525: {'usecomputer_END': {'energy': 3e-06, 'agent': 'uuid1'}}, 526: {'usecomputer_START': {'energy': -0.0, 'agent': 'uuid1'}}, 889: {'usecomputer_START': {'energy': 0.0, 'agent': 'uuid1'}}, 791: {'usecomputer_END': {'energy': -0.0, 'agent': 'uuid1'}}, 593: {'usecomputer_END': {'energy': 0.001096, 'agent': 'uuid1'}}, 594: {'usecomputer_START': {'en
	thingies = {"screen":["usecomputer_START","usecomputer_END"]}
	thingy = thingies[prefix]
	last_state = 0
	for key in sorted(x for x in action_parses.keys() if x < end_of_frames):
		# prefix is, for example, 'screen', the root of the tree we are looking at
		if thingy[0] in action_parses[key]:
			energy = action_parses[key][thingy[0]]['energy']
			last_probability = causal_grammar.energy_to_probability(energy)
			frame_diff = key - last_frame
			result = [0.,]*frame_diff
			action_matrix.extend(result)
			actions = True
			last_frame = key
		elif thingy[1] in action_parses[key]:
			frame_diff = key - last_frame
			result = [last_probability,]*frame_diff # we know start and stop are symmetric
			action_matrix.extend(result)
			last_probability = 0
			actions = True
			last_frame = key
	if not actions:
		# we've never seen anything! 0% all the way!
		result = [0.,]*(end_of_frames - start_of_frames)
		action_matrix.extend(result)
	elif key < end_of_frames:
		result = [last_probability,]*(end_of_frames-key)
		action_matrix.extend(result)
	row = ['ORIG' + " " + thingies[prefix][0].split("_")[0],]
	row.extend([str(x) for x in action_matrix])
	csv_rows.append(",".join(row))

	print("\n".join(csv_rows))


#TODO: run on all videos
#for filename in os.listdir(kSummerDataPythonDir):
#	if filename.endswith(".py") and filename != "__init__.py":
#		example = filename[:-3]
#TODO: for each video, run on all relevant trees, not having to specify

video_clippoints = dict()
with open(kHumanAnnotationClippoints, 'ra') as file:
	import re
	clip_frames_regexp = re.compile(r"Frame: (\d+).*End: (\d+)")
	newlines = (line.rstrip() for line in file)
	nextexample = dict()
	example_key = False
	for line in newlines:
		if line.startswith("Testing Data Name:"):
			example_key = line[19:]
		elif line.startswith("Clip Start Frame:"):
			match = re.findall(clip_frames_regexp, line)[0]
			nextexample[match[0]] = match[1]
		elif line.startswith("****"):
			video_clippoints[example_key] = nextexample
			nextexample = dict()

buildHeatmapForExample('screen_1_lounge','screen')
