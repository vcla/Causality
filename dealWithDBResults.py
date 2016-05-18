import csv
import hashlib
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import videoCutpoints
import xml_stuff
import summerdata
import gc

import sqlite3
DBTYPE_MYSQL = "mysql"
DBTYPE_SQLITE = "sqlite"

DBNAME = "amy_cvpr2012"
DBUSER = "amycvpr2012"
DBHOST = "127.0.0.1" # forwarding 3306
DBPASS = "rC2xfLQFDMUZqJxf"
TBLPFX = "cvpr2012_"
kKnownObjects = ["screen","door","light","phone","ringer","trash","dispense","thirst","waterstream","cup","water"]
kInsertionHash = "1234567890"

globalDryRun = None # commandline argument

# managing human responses for comparison - note upload versus download

def getDB(connType):
	if connType == DBTYPE_MYSQL:
		conn = MySQLdb.connect (host = DBHOST, user = DBUSER, passwd = DBPASS, db = DBNAME)
	else:
		conn = sqlite3.connect ("{}.db".format(DBNAME))
	return conn

def getColumns(conn, connType, tableName, exampleNameForDB):
	retval = False
	if connType == DBTYPE_MYSQL:
		query = "SHOW COLUMNS FROM {}".format(tableName)
	else:
		query = "PRAGMA table_info({})".format(tableName)
	try:
		cursor = conn.cursor()
		cursor.execute(query)
		retval = cursor.fetchall()
		cursor.close()
	except (MySQLdb.ProgrammingError, sqlite3.Error,) as e:
		print "TABLE {} not found for example {}: {}".format(tableName,exampleNameForDB, e.args)
	if connType == DBTYPE_SQLITE:
		retval = [(x[1],) for x in retval] # weird unSELECTable tuple retval
	return retval

def getExampleFromDB(exampleName, connType, conn=False):
	resultStorageFolder = "results/cvpr_db_results/"
	exampleNameForDB = exampleName.replace("_","")
	m = hashlib.md5(exampleNameForDB)
	tableName = TBLPFX + m.hexdigest()
	leaveconn = True
	if not conn:
		leaveconn = False
		conn = getDB(connType)
	allColumns = getColumns(conn, connType, tableName, exampleNameForDB)
	if not allColumns:
		return
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
	cursor = conn.cursor()
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

def uploadComputerResponseToDB(example, fluent_and_action_xml, source, connType, conn = False):
	import causal_grammar_summerdata # sets up causal_forest
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
		conn = getDB(connType)
	allColumns = getColumns(conn, connType, tableName, exampleNameForDB)
	if not allColumns:
		return
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
			answers = xml_stuff.queryXMLForAnswersBetweenFrames(fluent_and_action_xml_xml,oject,prev_frame,frame,source,not source.endswith('smrt'))
			if source in ("random","origdata",):
				framestr = "{}".format(prev_frame)
				things = dict()
				for key in answers:
					thing, choice = key.split(framestr)
					if not thing in things:
						things[thing] = 1
					else:
						things[thing] += 1
				for key in answers:
					thing, choice = key.split(framestr)
					# {door, light, screen} are only detectable fluents. So if it's not door, light, screen, it should be "random" for origdata. which means (tested) ~ we're setting to "random": trash {same, less, more}; phone {off_active, active_off, off, active}; cup {same, less, more}; thirst {not, thirsty, thirsty_not, not_thirsty}; waterstream {water_on, water_off};
					if source in ("origdata",):
						if choice.startswith("_act_"):
							continue
						elif thing in (x+"_" for x in causal_grammar_summerdata.detectable_fluents):
							# this is horribly, horribly hardcoded here....
							# if there's no detection but it's detectable, choice is herein split:
							# when no detection:
							# door_{}_closed_open: 0, door_{}_open_closed: 0, door_{}_closed: 50, door_{}_open: 50
							# light_{}_off_on: 0, light_{}_on_off: 0, light_{}_off: 50, light_{}_on: 50
							# screen_{}_off_on: 0, screen_{}_on_off: 0, screen_{}_off: 50, screen_{}_on: 50
							dothisthing = False
							if thing == "door_" and choice == "_closed_open":
								dothisthing = True
								off_on = "_".join(("door",str(prev_frame),"closed_open"))
								on_off = "_".join(("door",str(prev_frame),"open_closed"))
								on = "_".join(("door",str(prev_frame),"open"))
								off = "_".join(("door",str(prev_frame),"closed"))
							elif thing == "light_" and choice == "_off_on":
								dothisthing = True
								off_on = "_".join(("light",str(prev_frame),"off_on"))
								on_off = "_".join(("light",str(prev_frame),"on_off"))
								on = "_".join(("light",str(prev_frame),"on"))
								off = "_".join(("light",str(prev_frame),"off"))
							elif thing == "screen_" and choice == "_off_on":
								dothisthing = True
								off_on = "_".join(("screen",str(prev_frame),"off_on"))
								on_off = "_".join(("screen",str(prev_frame),"on_off"))
								on = "_".join(("screen",str(prev_frame),"on"))
								off = "_".join(("screen",str(prev_frame),"off"))
							if dothisthing:
								keys = [off_on, on_off, on, off]
								# we say there's no detection if everything is even, or if we've got 0 for off_on and on_off
								if len(set(answers[k] for k in keys)) == 1 or (answers[off_on] == 0 and answers[on_off] == 0):
									answers[off_on] = 0
									answers[on_off] = 0
									answers[on] = 50
									answers[off] = 50
									print("FOO+ {} {}".format(example, {k:answers[k] for k in keys}))
								else:
									print("FOO- {} {}".format(example, {k:answers[k] for k in keys}))
							continue
					answers[key] = int(100 / things[thing])
			insertion_object.update(answers)
			prev_frame = frame
	print("INSERT: {}".format(insertion_object))
	# http://stackoverflow.com/a/9336427/856925
	for key in insertion_object.keys():
		if type(insertion_object[key]) is str:
			insertion_object[key] = "'{}'".format(insertion_object[key])
	qry = "INSERT INTO %s (%s) VALUES (%s)" % (tableName, ", ".join(insertion_object.keys()), ", ".join(map(str,insertion_object.values())))
	if not globalDryRun:
		cursor = conn.cursor()
		cursor.execute("DELETE FROM %s WHERE name IN ('%s')" % (tableName,source))
		cursor.execute(qry)
		conn.commit()
		cursor.close()
	if not leaveconn:
		conn.close()
	return True

def processAndUploadExamples(directory,examples,conn,simplify=False):
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
	#raise("MAYBE DELETE 'computer' FROM RESULTS BEFORE RE-RUNNING")
	for example in examples:
		print("---------\nEXAMPLE: {}\n-------".format(example))
		""" -s (simplify) is broken at the moment, on the below example, so ... this can help """
		#if example == "doorlock_2_8145":
		#	suppress_output = False
		if simplify:
			causal_grammar_summerdata.causal_forest = causal_grammar.get_simplified_forest_for_example(causal_forest_orig, example)
			print("... simplified to {}".format(", ".join(x['symbol'] for x in causal_grammar_summerdata.causal_forest)))
		try:
			fluent_parses, temporal_parses = causal_grammar.import_summerdata(example,directory)
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
		orig_xml = xml_stuff.munge_parses_to_xml(fluent_parses,temporal_parses)
		fluent_and_action_xml = causal_grammar.process_events_and_fluents(causal_grammar_summerdata.causal_forest, fluent_parses, temporal_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy, suppress_output = suppress_output, handle_overlapping_events = withoutoverlaps)
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
		if uploadComputerResponseToDB(example, fluent_and_action_xml, 'causalgrammar', connType, conn):
			completed.append("{}-{}".format(example,'causalgrammar'))
		else:
			oject_failed.append("{}-{}".format(example,'causalgrammar'))
		print("------> causalsmrt <------")
		if uploadComputerResponseToDB(example, fluent_and_action_xml, 'causalsmrt', connType, conn):
			completed.append("{}-{}".format(example,'causalsmrt'))
		else:
			oject_failed.append("{}-{}".format(example,'causalsmrt'))
		print("------> origdata <------")
		if uploadComputerResponseToDB(example, orig_xml, 'origdata', connType, conn):
			completed.append("{}-{}".format(example,'origdata'))
		else:
			oject_failed.append("{}-{}".format(example,'origdata'))
		print("------> origsmrt <------")
		if uploadComputerResponseToDB(example, orig_xml, 'origsmrt', connType, conn):
			completed.append("{}-{}".format(example,'origsmrt'))
		else:
			oject_failed.append("{}-{}".format(example,'origsmrt'))
		print("------> random <------")
		if uploadComputerResponseToDB(example, orig_xml, 'random', connType, conn):
			completed.append("{}-{}".format(example,'random'))
		else:
			oject_failed.append("{}-{}".format(example,'random'))
		gc.collect()
	print("COMPLETED: {}".format(completed))
	if oject_failed:
		print("SKIPPED DUE TO OBJECT: {}".format(oject_failed))
	if import_failed:
		print("SKIPPED DUE TO IMPORT: {}".format(import_failed))
	print("....................")
	print("....................")

def downloadExamples(examples,connType,conn=False):
	print("===========")
	print("DOWNLOADING")
	print("===========")
	leaveconn = True
	if not conn:
		leaveconn = False
		conn = getDB(connType)
	for example in examples:
		print("---------\nEXAMPLE: {}\n-------".format(example))
		example, room = example.rsplit('_',1)
		getExampleFromDB(example, connType, conn)
	if not leaveconn:
		conn.close()


def getExamples(directory, exclude=list(), require=list(), grep=list(), mode=None):
	print("===========")
	print("LOADING EXAMPLES FROM")
	print("===========")
	print("> {}".format(directory))
	examples = list()
	for filename in os.listdir (directory):
		if filename.endswith(".py") and filename != "__init__.py":
			example = filename[:-3]
			ok = False
			if grep and example.startswith(grep):
				ok = True
			elif require:
				if example in require:
					ok = True
			elif not grep and example not in exclude:
				ok = True
			if ok:
				examples.append(example)
				if mode and mode in ("list",):
					exampleNameForDB, room = example.rsplit('_',1)
					exampleNameForDB = exampleNameForDB.replace("_","")
					m = hashlib.md5(exampleNameForDB)
					print("{}	{}".format(example,m.hexdigest()))
	return examples

##########################

if __name__ == '__main__':
	import xml_stuff
	debugQuery = False
	import argparse
	from summerdata import kActionDetections
	parser = argparse.ArgumentParser()
	parser.add_argument("mode", choices=["upload","download","upanddown","list"])
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-d','--dry-run', action='store_true', dest='dryrun', required=False, help='Do not actually upload data to the db or save downloaded data; only valid for "upload" or "download", does not make sense for "upanddown" or "list"')
	group.add_argument('-o','--only', action='append', dest='examples_only', required=False, help='specific examples to run, versus all found examples')
	group.add_argument('-x','--exclude', action='append', dest='examples_exclude', required=False, help='specific examples to exclude, out of all found examples', default=[])
	group.add_argument('-g','--grep', action='store', dest='examples_grep', required=False, help='class of examples to include', default=[])
	parser.add_argument("-s","--simplify", action="store_true", required=False, help="simplify the summerdata grammar to only include fluents that start with the example name[s]")
	parser.add_argument('-i','--ignoreoverlaps', action='store_true', required=False, help='skip the "without overlaps" code')
	parser.add_argument('--debug', action='store_true', required=False, help='Spit out a lot more context information during processing')
	parser.add_argument('--database', choices=["mysql","sqlite"],default = "sqlite")
	# parser.add_argument("--dry-run",required=False,action="store_true") #TODO: would be nie
	args = parser.parse_args()
	connType = args.database
	withoutoverlaps = not args.ignoreoverlaps
	suppress_output = not args.debug
	examples = []
	globalDryRun = args.dryrun
	if globalDryRun and args.mode in ("upanddown","download"):
		raise ValueError("dryrun is not actually valid for download/upanddown")
	if args.database in ("mysql",):
		# sometimes MySQLdb just doesn't want to work....
		try:
			import MySQLdb
		except ImportError:
			import pymysql
			pymysql.install_as_MySQLdb()
			class MySQLdb:
				ProgrammingError = pymysql.MySQLError
	examples = getExamples(kActionDetections,exclude=args.examples_exclude,require=args.examples_only, grep = args.examples_grep, mode=args.mode)
	if globalDryRun:
		conn = None
	else:
		conn = getDB(connType)
	if args.mode in ("upload","upanddown",):
		processAndUploadExamples(kActionDetections,examples,conn,args.simplify)
	if args.mode in ("download","upanddown"):
		downloadExamples(examples,connType,conn)
	if conn:
		conn.close()
