import csv
import hashlib
import MySQLdb
DBNAME = "amy_cvpr2012"
DBUSER = "amy"
DBHOST = "alethe.net"
DBPASS = "bB3s5tT"

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

def uploadComputerResponseToDB(fluent, queryPoints, exampleName):
	# TODO
	# what does computer output look like exactly?
	# maybe list of (frame, parse_id).  need to convert parses into when actions happened, and what fluent values are throughout based on those.  triggers will likely get handled differently than top-level fluents
	# get column names from DB, find times that we need
	# insert into DB 
	pass



##########################


if __name__ == '__main__':
	conn = MySQLdb.connect (host = DBHOST, user = DBUSER, passwd = DBPASS, db = DBNAME)
	getExampleFromDB("door_1",conn)
	getExampleFromDB("waterstream_1",conn)
	getExampleFromDB("water_1",conn)
	getExampleFromDB("water_2",conn)
	getExampleFromDB("phone_1",conn)
	getExampleFromDB("door_2",conn)
	getExampleFromDB("waterstream_2_water_3",conn)
	getExampleFromDB("water_4",conn)
	getExampleFromDB("doorlock_1_door_3",conn)
	getExampleFromDB("door_4_trash_1",conn)
	getExampleFromDB("phone_2",conn)
	getExampleFromDB("door_5",conn)
	getExampleFromDB("doorlock_2",conn)
	getExampleFromDB("waterstream_3_water_5",conn)
	getExampleFromDB("phone_3",conn)
	getExampleFromDB("waterstream_4",conn)
	getExampleFromDB("door_6",conn)
	getExampleFromDB("door_7",conn)
	getExampleFromDB("water_6_waterstream_5",conn)
	getExampleFromDB("door_8_doorlock_3",conn)
	getExampleFromDB("door_9",conn)
	getExampleFromDB("phone_4",conn)
	getExampleFromDB("trash_2",conn)
	getExampleFromDB("screen_1",conn)
	getExampleFromDB("screen_2",conn)
	getExampleFromDB("screen_3_phone_5",conn)
	getExampleFromDB("screen_4_phone_6",conn)
	getExampleFromDB("screen_5",conn)
	getExampleFromDB("screen_6",conn)
	getExampleFromDB("trash_3",conn)
	getExampleFromDB("screen_7",conn)
	getExampleFromDB("screen_8",conn)
	getExampleFromDB("screen_9_phone_7",conn)
	getExampleFromDB("screen_10",conn)
	getExampleFromDB("trash_4_screen_11",conn)
	getExampleFromDB("screen_12",conn)
	getExampleFromDB("screen_13",conn)
	getExampleFromDB("screen_14_phone_8",conn)
	getExampleFromDB("screen_15",conn)
	getExampleFromDB("screen_16_phone_9",conn)
	getExampleFromDB("screen_17_trash_5",conn)
	getExampleFromDB("screen_18",conn)
	getExampleFromDB("screen_19",conn)
	getExampleFromDB("screen_20",conn)
	getExampleFromDB("screen_21_phone_10",conn)
	getExampleFromDB("trash_6_phone_11_screen_22",conn)
	getExampleFromDB("screen_23",conn)
	getExampleFromDB("screen_24",conn)
	getExampleFromDB("screen_25",conn)
	getExampleFromDB("screen_26_phone_12",conn)
	getExampleFromDB("phone_13_screen_27",conn)
	getExampleFromDB("screen_28",conn)
	getExampleFromDB("door_10_phone_14_light_1_screen_29",conn)
	getExampleFromDB("screen_30",conn)
	getExampleFromDB("screen_31",conn)
	getExampleFromDB("screen_32",conn)
	getExampleFromDB("screen_33",conn)
	getExampleFromDB("screen_34_phone_15",conn)
	getExampleFromDB("door_11",conn)
	getExampleFromDB("door_12_light_2",conn)
	getExampleFromDB("door_13_light_3",conn)
	getExampleFromDB("screen_35",conn)
	getExampleFromDB("screen_36",conn)
	getExampleFromDB("screen_37_door_14_light_4",conn)
	getExampleFromDB("door_15",conn)
	getExampleFromDB("light_5",conn)
	getExampleFromDB("screen_38",conn)
	getExampleFromDB("screen_39",conn)
	getExampleFromDB("screen_40",conn)
	getExampleFromDB("phone_16",conn)
	getExampleFromDB("trash_7",conn)
	getExampleFromDB("screen_41",conn)
	getExampleFromDB("light_6",conn)
	getExampleFromDB("screen_42",conn)
	getExampleFromDB("waterstream_6_water_7_phone_17_screen_43",conn)
	getExampleFromDB("screen_44",conn)
	getExampleFromDB("screen_45_trash_8",conn)
	getExampleFromDB("screen_46",conn)
	getExampleFromDB("screen_47_water_8_phone_18",conn)
	getExampleFromDB("water_9_screen_48_trash_9",conn)
	getExampleFromDB("waterstream_7",conn)
	getExampleFromDB("trash_10_phone_19",conn)
	getExampleFromDB("screen_49",conn)
	getExampleFromDB("light_7",conn)
	getExampleFromDB("light_8_screen_50",conn)
	getExampleFromDB("screen_51",conn)
	getExampleFromDB("water_10_screen_52",conn)
	getExampleFromDB("phone_20_screen_53",conn)
	getExampleFromDB("water_11_screen_54",conn)
	getExampleFromDB("waterstream_8_screen_55",conn)
	getExampleFromDB("trash_11_screen_56",conn)
	getExampleFromDB("light_9_screen_57",conn)
	getExampleFromDB("light_10",conn)
	getExampleFromDB("screen_58",conn)
	getExampleFromDB("water_12_phone_21_screen_59",conn)
	getExampleFromDB("waterstream_9_water_13_phone_22_screen_60",conn)
	getExampleFromDB("screen_61",conn)
	getExampleFromDB("waterstream_10_water_14_phone_23_screen_62",conn)
	getExampleFromDB("screen_63",conn)
	getExampleFromDB("water_15_screen_64",conn)
	getExampleFromDB("phone_24_screen_65",conn)
	getExampleFromDB("water_16_screen_66",conn)
	getExampleFromDB("waterstream_11",conn)
	getExampleFromDB("water_17",conn)
	getExampleFromDB("phone_25_screen_67",conn)
	getExampleFromDB("water_18_screen_68",conn)
	getExampleFromDB("water_19_screen_69",conn)
	getExampleFromDB("waterstream_12_water_20_screen_70",conn)
	conn.close()
