# NOTE: the following is run using Amy's computer on 2016-05-09 16:05, which includes the following
# Action Detection Folder: CVPR2012_reverse_slidingwindow_10_action_detection_logspace
# grammar is in commit id 0966247f7272f058145ea0cef63a4610d1845be7

#TODO: not sure how...  should maybe regenerate the csv files also...

import unittest
import csv
import os
#import causal_grammar
#import evaluateCausalGrammar as evaluateXML
#import xml.etree.ElementTree as ET
#import dealWithDBResults

kDebug = True

def extractRows(fileName):
	fileName = 'results/cvpr_db_results/'+fileName+'.csv'
	with open(fileName, 'r') as csvfile:
		lines = csv.reader(csvfile)
		for row in lines:
			if row[0] != "name":
				retval = [int(x) if x != "" else -100 for x in row[1:-2] ]
			else:
				nameRow = row[1:-2]
			if row[0] == "causalgrammar":
				causalRow = retval
			elif row[0] == "origdata":
				origRow =  retval
			elif row[0] == "random":
				randomRow =  retval
		return {"nameRow": nameRow, "causalRow": causalRow, "origRow": origRow, "randomRow": randomRow}

def getDiffIndices(list1, list2):
	diffList = []
	if len(list1) != len(list2):
		raise InputError("Mismatched list lengths")
	for ind in range(0,len(list1)-1):
		if list1[ind] != list2[ind]:
			diffList.append(ind)
	return diffList

class Test_Screen_45_Trash_8(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		# regenerate the CSV
		os.system("python dealWithDBResults.py -o screen_45_trash_8_9404 -s upanddown")
		cls.fileName = "screen_45_trash_8"
		cls.answers = extractRows(cls.fileName)

	def testCausal(self):
		amyCausalAnswer = [0,0,100,0, 0,0,100,0, 0,100, 0,100, 0,0,100, 100,0,0, 100,0, 0,100]
		dbCausalAnswer = self.answers["causalRow"]
		indices = getDiffIndices(amyCausalAnswer, dbCausalAnswer)
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t{}: Amy = {}, causalgrammar = {}\n".format(self.answers["nameRow"][ind], amyCausalAnswer[ind], dbCausalAnswer[ind])
		assert not len(indices), "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, len(indices), printText)

	def testRandom(self):
		amyRandomAnswer = [25,25,25,25, 25,25,25,25, 50,50, 50,50, 33,33,33, 33,33,33, 50,50, 50,50]
		dbRandomAnswer = self.answers["randomRow"]
		indices = getDiffIndices(amyRandomAnswer, dbRandomAnswer)
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t{}: Amy = {}, random = {}\n".format(self.answers["nameRow"][ind], amyRandomAnswer[ind], dbRandomAnswer[ind])
		nErrors = len(indices)
		assert not nErrors, "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, nErrors, printText)

	def testOrig(self):
		amyOrigAnswer = [0,200,0,0, 0,0,50,50, 100,0, 100,0, 33,33,33, 33,33,33, 100,0, 100,0]
		dbOrigAnswer = self.answers["origRow"]
		indices = getDiffIndices(amyOrigAnswer, dbOrigAnswer)
		nIgnoring = 0
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t"
				if (ind in [8,10,18]) and (amyOrigAnswer[ind] == 100) and (dbOrigAnswer[ind] >= 100):
					printText += "IGNORE BECAUSE AMY DIDN'T COUNT ACTIONS (AND IS SUFFICIENTLY OK FOR NOW) "
					nIgnoring += 1
				printText += "{}: Amy = {}, orig = {}".format(self.answers["nameRow"][ind], amyOrigAnswer[ind], dbOrigAnswer[ind])
				printText += "\n"
		nErrors = len(indices)-nIgnoring
		assert not nErrors, "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, nErrors, printText)


class Test_Waterstream_3_Water_5_8145(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		# regenerate the CSV
		os.system("python dealWithDBResults.py -o waterstream_3_water_5_8145 -s upanddown")
		cls.fileName = "waterstream_3_water_5"
		cls.answers = extractRows(cls.fileName)

	def testRandom(self):
		amyRandomAnswer = [50,50, 50,50, 25,25,25,25, 25,25,25,25, 33,33,33, 33,33,33, 50,50, 50,50, 50,50, 50,50]
		dbRandomAnswer = self.answers["randomRow"]
		indices = getDiffIndices(amyRandomAnswer, dbRandomAnswer)
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t{}: Amy = {}, random = {}\n".format(self.answers["nameRow"][ind], amyRandomAnswer[ind], dbRandomAnswer[ind])
		nErrors = len(indices)
		assert not nErrors, "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, nErrors, printText)

	def testCausal(self):
		amyCausalAnswer = [100,0, 0,100, 0,0,100,0, 0,0,100,0, 100,0,0, 0,0,100, 100,0, 0,100, 0,100, 0,100]
		dbCausalAnswer = self.answers["causalRow"]
		indices = getDiffIndices(amyCausalAnswer, dbCausalAnswer)
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t{}: Amy = {}, causalgrammar = {}\n".format(self.answers["nameRow"][ind], amyCausalAnswer[ind], dbCausalAnswer[ind])
		assert not len(indices), "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, len(indices), printText)

	def testOrig(self):
		amyOrigAnswer = [50,50, 50,50, 25,25,25,25, 25,25,25,25, 33,33,33, 33,33,33, 100,0, 100,0, 0,100, 0,100]
		dbOrigAnswer = self.answers["origRow"]
		indices = getDiffIndices(amyOrigAnswer, dbOrigAnswer)
		nIgnoring = 0
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t"
				if (ind in [18, 20, 22, 24]) and (amyOrigAnswer[ind] == 100) and (dbOrigAnswer[ind] >= 100):
					printText += "IGNORE BECAUSE AMY DIDN'T COUNT ACTIONS (AND IS SUFFICIENTLY OK FOR NOW) "
					nIgnoring += 1
				printText += "{}: Amy = {}, orig = {}".format(self.answers["nameRow"][ind], amyOrigAnswer[ind], dbOrigAnswer[ind])
				printText += "\n"
		nErrors = len(indices)-nIgnoring
		assert not nErrors, "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, nErrors, printText)


class Test_Water_4_8145(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		# regenerate the CSV
		os.system("python dealWithDBResults.py -o water_4_8145 -s upanddown")
		cls.fileName = "water_4"
		cls.answers = extractRows(cls.fileName)

	def testRandom(self):
		amyRandomAnswer = [25,25,25,25, 25,25,25,25, 33,33,33, 33,33,33, 50,50, 50,50]
		dbRandomAnswer = self.answers["randomRow"]
		indices = getDiffIndices(amyRandomAnswer, dbRandomAnswer)
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t{}: Amy = {}, random = {}\n".format(self.answers["nameRow"][ind], amyRandomAnswer[ind], dbRandomAnswer[ind])
		nErrors = len(indices)
		assert not nErrors, "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, nErrors, printText)

	def testCausal(self):
		amyCausalAnswer = [0,0,100,0, 0,0,100,0, 0,0,100, 0,100,0, 0,100, 100,0]
		dbCausalAnswer = self.answers["causalRow"]
		indices = getDiffIndices(amyCausalAnswer, dbCausalAnswer)
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t{}: Amy = {}, causalgrammar = {}\n".format(self.answers["nameRow"][ind], amyCausalAnswer[ind], dbCausalAnswer[ind])
		assert not len(indices), "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, len(indices), printText)

	def testOrig(self):
		amyOrigAnswer = [25,25,25,25, 25,25,25,25, 33,33,33, 33,33,33, 100,0, 100,0]
		dbOrigAnswer = self.answers["origRow"]
		indices = getDiffIndices(amyOrigAnswer, dbOrigAnswer)
		nIgnoring = 0
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t"
				if (ind in [14, 16]) and (amyOrigAnswer[ind] == 100) and (dbOrigAnswer[ind] >= 100):
					printText += "IGNORE BECAUSE AMY DIDN'T COUNT ACTIONS (AND IS SUFFICIENTLY OK FOR NOW) "
					nIgnoring += 1
				printText += "{}: Amy = {}, orig = {}".format(self.answers["nameRow"][ind], amyOrigAnswer[ind], dbOrigAnswer[ind])
				printText += "\n"
		nErrors = len(indices)-nIgnoring
		assert not nErrors, "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, nErrors, printText)


class Test_Screen_37_door_14_light_4_9406(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		# regenerate the CSV
		os.system("python dealWithDBResults.py -o screen_37_door_14_light_4_9406 -s upanddown")
		cls.fileName = "screen_37_door_14_light_4"
		cls.answers = extractRows(cls.fileName)

	def testRandom(self):
		amyRandomAnswer = [25,25,25,25, 25,25,25,25, 25,25,25,25, 50,50, 50,50, 50,50, 25,25,25,25, 25,25,25,25, 25,25,25,25, 33,33,33, 33,33,33, 33,33,33, 25,25,25,25, 25,25,25,25, 25,25,25,25, 50,50, 50,50, 50,50]
		dbRandomAnswer = self.answers["randomRow"]
		indices = getDiffIndices(amyRandomAnswer, dbRandomAnswer)
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t{}: Amy = {}, random = {}\n".format(self.answers["nameRow"][ind], amyRandomAnswer[ind], dbRandomAnswer[ind])
		nErrors = len(indices)
		assert not nErrors, "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, nErrors, printText)

	def testCausal(self):
		amyCausalAnswer = [0,0,100,0, 0,0,100,0, 0,0,100,0, 0,100, 0,100, 0,100, 0,0,100,0, 0,0,100,0, 0,0,100,0, 0,0,100, 0,0,100, 0,0,100, 0,0,100,0, 0,0,100,0, 0,0,100,0, 0,100, 0,100, 0,100]
		dbCausalAnswer = self.answers["causalRow"]
		indices = getDiffIndices(amyCausalAnswer, dbCausalAnswer)
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t{}: Amy = {}, causalgrammar = {}\n".format(self.answers["nameRow"][ind], amyCausalAnswer[ind], dbCausalAnswer[ind])
		assert not len(indices), "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, len(indices), printText)

	def testOrig(self):
		amyOrigAnswer = [0,100,0,0, 100,100,0,0, 0,0,50,50, 0,100, 0,100, 0,100, 0,0,50,50, 0,0,50,50, 0,100,0,0, 0,0,100, 0,0,100, 0,0,100, 0,200,0,0, 0,0,50,50, 0,0,50,50, 0,100, 0,100, 0,100]
		dbOrigAnswer = self.answers["origRow"]
		indices = getDiffIndices(amyOrigAnswer, dbOrigAnswer)
		nIgnoring = 0
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t"
				if (ind in []) and (amyOrigAnswer[ind] == 100) and (dbOrigAnswer[ind] >= 100):
					printText += "IGNORE BECAUSE AMY DIDN'T COUNT ACTIONS (AND IS SUFFICIENTLY OK FOR NOW) "
					nIgnoring += 1
				printText += "{}: Amy = {}, orig = {}".format(self.answers["nameRow"][ind], amyOrigAnswer[ind], dbOrigAnswer[ind])
				printText += "\n"
		nErrors = len(indices)-nIgnoring
		assert not nErrors, "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, nErrors, printText)


class Test_light_8_screen_50_9404(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		# regenerate the CSV
		os.system("python dealWithDBResults.py -o light_8_screen_50_9404 -s upanddown")
		cls.fileName = "light_8_screen_50"
		cls.answers = extractRows(cls.fileName)

	def testRandom(self):
		amyRandomAnswer = [25,25,25,25, 25,25,25,25, 50,50, 50,50, 25,25,25,25, 25,25,25,25, 50,50, 50,50]
		dbRandomAnswer = self.answers["randomRow"]
		indices = getDiffIndices(amyRandomAnswer, dbRandomAnswer)
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t{}: Amy = {}, random = {}\n".format(self.answers["nameRow"][ind], amyRandomAnswer[ind], dbRandomAnswer[ind])
		nErrors = len(indices)
		assert not nErrors, "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, nErrors, printText)

	def testCausal(self):
		amyCausalAnswer = [100,100,0,0, 0,0,100,0, 200,0, 0,100, 0,0,100,0, 0,0,100,0, 0,100, 0,100]
		dbCausalAnswer = self.answers["causalRow"]
		indices = getDiffIndices(amyCausalAnswer, dbCausalAnswer)
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t{}: Amy = {}, causalgrammar = {}\n".format(self.answers["nameRow"][ind], amyCausalAnswer[ind], dbCausalAnswer[ind])
		assert not len(indices), "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, len(indices), printText)

	def testOrig(self):
		amyOrigAnswer = [200,100,0,0, 0,0,50,50, 100,0, 0,100, 100,0,0,0, 0,100,0,0, 0,100, 0,100]
		dbOrigAnswer = self.answers["origRow"]
		indices = getDiffIndices(amyOrigAnswer, dbOrigAnswer)
		nIgnoring = 0
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t"
				if (ind in [8]) and (amyOrigAnswer[ind] == 100) and (dbOrigAnswer[ind] >= 100):
					printText += "IGNORE BECAUSE AMY DIDN'T COUNT ACTIONS (AND IS SUFFICIENTLY OK FOR NOW) "
					nIgnoring += 1
				printText += "{}: Amy = {}, orig = {}".format(self.answers["nameRow"][ind], amyOrigAnswer[ind], dbOrigAnswer[ind])
				printText += "\n"
		nErrors = len(indices)-nIgnoring
		assert not nErrors, "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, nErrors, printText)


class Test_door_4_trash_1_8145(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		# regenerate the CSV
		os.system("python dealWithDBResults.py -o door_4_trash_1_8145 -s upanddown")
		cls.fileName = "door_4_trash_1"
		cls.answers = extractRows(cls.fileName)

	def testRandom(self):
		amyRandomAnswer = [25,25,25,25, 25,25,25,25, 25,25,25,25, 33,33,33, 33,33,33, 33,33,33, 33,33,33, 33,33,33, 33,33,33, 50,50, 50,50, 50,50]
		dbRandomAnswer = self.answers["randomRow"]
		indices = getDiffIndices(amyRandomAnswer, dbRandomAnswer)
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t{}: Amy = {}, random = {}\n".format(self.answers["nameRow"][ind], amyRandomAnswer[ind], dbRandomAnswer[ind])
		nErrors = len(indices)
		assert not nErrors, "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, nErrors, printText)

	def testCausal(self):
		amyCausalAnswer = [100,100,0,0, 0,0,100,0, 0,100,0,0, 100,100,0, 0,0,100, 0,100,0, 0,0,100, 0,0,100, 0,0,100, 0,100, 0,100, 0,100]
		dbCausalAnswer = self.answers["causalRow"]
		indices = getDiffIndices(amyCausalAnswer, dbCausalAnswer)
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t{}: Amy = {}, causalgrammar = {}\n".format(self.answers["nameRow"][ind], amyCausalAnswer[ind], dbCausalAnswer[ind])
		assert not len(indices), "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, len(indices), printText)

	def testOrig(self):
		amyOrigAnswer = [100,100,0,0, 0,100,0,0, 0,100,0,0, 100,0,0, 100,100,0, 0,100,0, 33,33,33, 33,33,33, 33,33,33, 0,100, 0,100, 0,100]
		dbOrigAnswer = self.answers["origRow"]
		indices = getDiffIndices(amyOrigAnswer, dbOrigAnswer)
		nIgnoring = 0
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t"
				if (ind in [12,13,15,16,18,19]) and (amyOrigAnswer[ind] == 100) and (dbOrigAnswer[ind] >= 100):
					printText += "IGNORE BECAUSE AMY DIDN'T COUNT ACTIONS (AND IS SUFFICIENTLY OK FOR NOW) "
					nIgnoring += 1
				printText += "{}: Amy = {}, orig = {}".format(self.answers["nameRow"][ind], amyOrigAnswer[ind], dbOrigAnswer[ind])
				printText += "\n"
		nErrors = len(indices)-nIgnoring
		assert not nErrors, "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, nErrors, printText)


class Test_trash_10_phone_19_9404(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		# regenerate the CSV
		os.system("python dealWithDBResults.py -o trash_10_phone_19_9404 -s upanddown")
		cls.fileName = "trash_10_phone_19"
		cls.answers = extractRows(cls.fileName)

	def testRandom(self):
		amyRandomAnswer = [33,33,33, 33,33,33, 33,33,33, 50,50, 50,50, 50,50, 25,25,25,25, 25,25,25,25, 25,25,25,25, -100,-100, -100,-100, -100,-100, 50,50, 50,50, 50,50]
		dbRandomAnswer = self.answers["randomRow"]
		indices = getDiffIndices(amyRandomAnswer, dbRandomAnswer)
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t{}: Amy = {}, random = {}\n".format(self.answers["nameRow"][ind], amyRandomAnswer[ind], dbRandomAnswer[ind])
		nErrors = len(indices)
		assert not nErrors, "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, nErrors, printText)

	def testCausal(self):
		amyCausalAnswer = [0,0,100, 0,0,100, 0,0,100, 0,100, 0,100, 0,100, 0,0,0,100, 0,0,0,100, 100,100,0,0, -100,-100, -100,-100, -100,-100, 100,0, 0,100, 0,100]
		dbCausalAnswer = self.answers["causalRow"]
		indices = getDiffIndices(amyCausalAnswer, dbCausalAnswer)
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t{}: Amy = {}, causalgrammar = {}\n".format(self.answers["nameRow"][ind], amyCausalAnswer[ind], dbCausalAnswer[ind])
		assert not len(indices), "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, len(indices), printText)

	def testOrig(self):
		amyOrigAnswer = [33,33,33, 33,33,33, 33,33,33, 0,100, 0,100, 100,0, 25,25,25,25, 25,25,25,25, 25,25,25,25, -100,-100, -100,-100, -100,-100, 100,0, 100,0, 100,0]
		dbOrigAnswer = self.answers["origRow"]
		indices = getDiffIndices(amyOrigAnswer, dbOrigAnswer)
		nIgnoring = 0
		if len(indices) > 0:
			printText = ""
			for ind in indices:
				printText += "\t"
				if (ind in [9,11,13,33,35,37]) and (amyOrigAnswer[ind] == 100) and (dbOrigAnswer[ind] >= 100):
					printText += "IGNORE BECAUSE AMY DIDN'T COUNT ACTIONS (AND IS SUFFICIENTLY OK FOR NOW) "
					nIgnoring += 1
				printText += "{}: Amy = {}, orig = {}".format(self.answers["nameRow"][ind], amyOrigAnswer[ind], dbOrigAnswer[ind])
				printText += "\n"
		nErrors = len(indices)-nIgnoring
		assert not nErrors, "{} -- Amy doesn't agree with the DB in the following {} spots:\n{}".format(self.fileName, nErrors, printText)
#TODO add tests for hitrates...



"""
class TestDBOriginalReponses(unittest.TestCase):
	def testDoor2(self):
		fileName = "door_2"
		answer = extractOrigDataRow(fileName)
		print answer
		assert answer == [200,100,0,0,0,100,0,0,0,0,100,0,0,100]
		#TODO: should answer be fractioned?
"""


if __name__ == "__main__":
	unittest.main() # run all tests


