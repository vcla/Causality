import unittest
import csv
import os
import xml.etree.ElementTree as ET
import xml_stuff

def runDBResults(fileName,room,simplify=True):
		os.system("python dealWithDBResults.py -o {}_{} {}upanddown >& /dev/null".format(fileName,room,"-s " if simplify else ""))
		return extractRows(fileName)

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
	for ind in range(0,len(list1)):
		if list1[ind] != list2[ind]:
			diffList.append(ind)
	return diffList

class TestTrash10Phone19_9404Directly(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		xml = """
<temporal>
        <fluent_changes>
                <fluent_change energy="60.281" fluent="PHONE_ACTIVE" frame="0" new_value="off"/>
                <fluent_change energy="60.281" fluent="PHONE_ACTIVE" frame="3890" new_value="on" old_value="off"/>
                <fluent_change energy="60.281" fluent="PHONE_ACTIVE" frame="3990" new_value="off" old_value="on"/>
        </fluent_changes>
        <actions>
                <event action="makecall_START" energy="60.281" frame="3718"/>
                <event action="makecall_END" energy="60.281" frame="3767"/>
        </actions>
</temporal>"""
		cls.parsexml = ET.fromstring(xml)
	
	def innertestAnswers(self,expected,answers):
		returned = {k:answers[k] for k in expected}
		assert expected == returned, "{} [returned] != {} [expected]".format(returned,expected)

	def getAnswersForFrames(self,frame1,frame2):
		return xml_stuff.queryXMLForAnswersBetweenFrames(self.parsexml, "phone", frame1, frame2, "causalgrammar", dumb=True)

	def test3663(self):
		answers = self.getAnswersForFrames(3663,3764)
		self.innertestAnswers({'phone_3663_off_active':0, 'phone_3663_active_off':0, 'phone_3663_active':0,'phone_3663_off':100},answers)

	def test3764(self):
		answers = self.getAnswersForFrames(3764,3858)
		self.innertestAnswers({'phone_3764_off_active':0, 'phone_3764_active_off':0, 'phone_3764_active':0,'phone_3764_off':100},answers)

	def test3858(self):
		answers = self.getAnswersForFrames(3858,10000)
		self.innertestAnswers({'phone_3858_off_active':100, 'phone_3858_active_off':100, 'phone_3858_active':0,'phone_3858_off':0},answers)




class TestScreen45Trash8_9404Directly(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		xml = """
<temporal>
	<fluent_changes>
		<fluent_change energy="37.43" fluent="trash_MORE" frame="0" new_value="off"/>
		<fluent_change energy="37.43" fluent="trash_MORE" frame="1659" new_value="on" old_value="off"/>
		<fluent_change energy="16.511" fluent="TRASH_LESS" frame="0" new_value="off"/>
	</fluent_changes>
	<actions>
		<event action="throwtrash_END" energy="37.43" frame="1652"/>
	</actions>
</temporal>"""
		cls.parsexml = ET.fromstring(xml)
	
	def innertestAnswers(self,expected,answers):
		returned = {k:answers[k] for k in expected}
		assert expected == returned, "{} [returned] != {} [expected]".format(returned,expected)

	def getAnswersForFrames(self,frame1,frame2):
		return xml_stuff.queryXMLForAnswersBetweenFrames(self.parsexml, "trash", frame1, frame2, "causalgrammar", dumb=True)

	def test1490(self):
		# fluent change to trash_more happens at 1659; human query points are at 1490 and 1659. this should not happen at cutpoint 1490, only cutpoint 1659. ... and 1707???
		answers = self.getAnswersForFrames(0,1490)
		self.innertestAnswers({'trash_0_less':0, 'trash_0_more':0, 'trash_0_same':100},answers)

	def test1659(self):
		answers = self.getAnswersForFrames(1490,1659)
		self.innertestAnswers({'trash_1490_less':0, 'trash_1490_more':0, 'trash_1490_same':100},answers)

	def test1707(self):
		answers = self.getAnswersForFrames(1659,1707)
		self.innertestAnswers({'trash_1659_less':0, 'trash_1659_more':100, 'trash_1659_same':0},answers)

def innertest(answerSets, name, expected, excluding = list()):
	answers = answerSets[name]
	indices = getDiffIndices(expected, answers)
	#raise Exception("INDICES ~ {}\nEXCLUDING ~ {}\n{}\n{}".format(indices,excluding,answers,expected))
	nIgnoring = 0
	if len(indices) > 0:
		printText = ""
		for ind in indices:
			printText += "\t"
			if (ind in excluding) and (expected[ind] == 100) and (answers[ind] >= 100):
				printText += "IGNORE BECAUSE AMY DIDN'T COUNT ACTIONS (AND IS SUFFICIENTLY OK FOR NOW) "
				nIgnoring += 1
			printText += "{}: Amy = {}, {} = {}".format(answerSets["nameRow"][ind], expected[ind], name, answers[ind])
			printText += "\n"
	nErrors = len(indices)-nIgnoring
	assert not nErrors, " -- Amy doesn't agree with the DB in the following {} spot{}:\n{}".format(nErrors, "s" if nErrors != 1 else "",printText)

class Test_Screen_45_Trash_8(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.fileName = "screen_45_trash_8"
		cls.answers = runDBResults(cls.fileName,"9404")

	def testCausal(self):
		innertest(self.answers, "causalRow", [0,0,100,0, 0,0,100,0, 0,100, 0,100, 0,0,100, 100,0,0, 100,0, 0,100])

	def testRandom(self):
		innertest(self.answers, "randomRow", [25,25,25,25, 25,25,25,25, 50,50, 50,50, 33,33,33, 33,33,33, 50,50, 50,50])

	def testOrig(self):
		innertest(self.answers, "origRow", [0,200,0,0, 0,0,50,50, 100,0, 100,0, 33,33,33, 33,33,33, 100,0, 100,0], excluding=[8,10,18])


class Test_Waterstream_3_Water_5_8145(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.fileName = "waterstream_3_water_5"
		cls.answers = runDBResults(cls.fileName,"8145")

	def testRandom(self):
		innertest(self.answers,"randomRow", [50] * 4 + [25] * 8 + [33] * 6 + [50] * 8)

	def testCausal(self):
		innertest(self.answers,"causalRow", [100,0, 0,100, 0,0,100,0, 0,0,100,0, 100,0,0, 0,0,100, 100,0, 0,100, 0,100, 0,100])

	def testOrig(self):
		innertest(self.answers,"origRow", [50,50, 50,50, 25,25,25,25, 25,25,25,25, 33,33,33, 33,33,33, 100,0, 100,0, 0,100, 0,100], excluding = [18,20,22,24])

class Test_Water_4_8145(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.fileName = "water_4"
		cls.answers = runDBResults(cls.fileName,"8145")

	def testRandom(self):
		innertest(self.answers,"randomRow", [25,25,25,25, 25,25,25,25, 33,33,33, 33,33,33, 50,50, 50,50])

	def testCausal(self):
		innertest(self.answers,"causalRow", [0,0,100,0, 0,0,100,0, 0,0,100, 0,100,0, 0,100, 100,0])

	def testOrig(self):
		innertest(self.answers,"origRow", [25,25,25,25, 25,25,25,25, 33,33,33, 33,33,33, 100,0, 100,0], excluding = [14,16])

class Test_Screen_37_door_14_light_4_9406(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.fileName = "screen_37_door_14_light_4"
		cls.answers = runDBResults(cls.fileName,"9406")

	def testRandom(self):
		innertest(self.answers,"randomRow", [25,25,25,25, 25,25,25,25, 25,25,25,25, 50,50, 50,50, 50,50, 25,25,25,25, 25,25,25,25, 25,25,25,25, 33,33,33, 33,33,33, 33,33,33, 25,25,25,25, 25,25,25,25, 25,25,25,25, 50,50, 50,50, 50,50])

	def testCausal(self):
		innertest(self.answers,"causalRow", [0,0,100,0, 0,0,100,0, 0,0,100,0, 0,100, 0,100, 0,100, 0,0,100,0, 0,0,100,0, 0,0,100,0, 0,0,100, 0,0,100, 0,0,100, 0,0,100,0, 0,0,100,0, 0,0,100,0, 0,100, 0,100, 0,100])

	def testOrig(self):
		innertest(self.answers,"origRow", [0,100,0,0, 100,100,0,0, 0,0,50,50, 0,100, 0,100, 0,100, 0,0,50,50, 0,0,50,50, 0,100,0,0, 0,0,100, 0,0,100, 0,0,100, 0,200,0,0, 0,0,50,50, 0,0,50,50, 0,100, 0,100, 0,100])

class Test_light_8_screen_50_9404(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.fileName = "light_8_screen_50"
		cls.answers = runDBResults(cls.fileName,"9404")

	def testRandom(self):
		innertest(self.answers,"randomRow",[25,25,25,25, 25,25,25,25, 50,50, 50,50, 25,25,25,25, 25,25,25,25, 50,50, 50,50])

	def testCausal(self):
		innertest(self.answers,"causalRow",[100,100,0,0, 0,0,100,0, 200,0, 0,100, 0,0,100,0, 0,0,100,0, 0,100, 0,100])

	def testOrig(self):
		innertest(self.answers,"origRow", [200,100,0,0, 0,0,50,50, 100,0, 0,100, 100,0,0,0, 0,100,0,0, 0,100, 0,100],excluding=[8])

class Test_door_4_trash_1_8145(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.fileName = "door_4_trash_1"
		cls.answers = runDBResults(cls.fileName,"8145")

	def testRandom(self):
		innertest(self.answers,"randomRow",[25,25,25,25, 25,25,25,25, 25,25,25,25, 33,33,33, 33,33,33, 33,33,33, 33,33,33, 33,33,33, 33,33,33, 50,50, 50,50, 50,50])

	def testCausal(self):
		innertest(self.answers,"causalRow",[100,100,0,0, 0,0,100,0, 0,100,0,0, 100,100,0, 0,0,100, 0,100,0, 0,0,100, 0,0,100, 0,0,100, 0,100, 0,100, 0,100])

	def testOrig(self):
		innertest(self.answers,"origRow",[100,100,0,0, 0,100,0,0, 0,100,0,0, 100,0,0, 100,100,0, 0,100,0, 33,33,33, 33,33,33, 33,33,33, 0,100, 0,100, 0,100],excluding=[12,13,15,16,18,19])

class Test_trash_10_phone_19_9404(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.fileName = "trash_10_phone_19"
		cls.answers = runDBResults(cls.fileName,"9404",simplify=False)

	def testRandom(self):
		innertest(self.answers,"randomRow", [33,33,33, 33,33,33, 33,33,33, 50,50, 50,50, 50,50, 25,25,25,25, 25,25,25,25, 25,25,25,25, -100,-100, -100,-100, -100,-100, 50,50, 50,50, 50,50])

	def testCausal(self):
		innertest(self.answers,"causalRow", [0,0,100, 0,0,100, 0,0,100, 0,100, 0,100, 0,100, 0,0,0,100, 0,0,0,100, 100,100,0,0, -100,-100, -100,-100, -100,-100, 100,0, 0,100, 0,100])

	def testOrig(self):
		innertest(self.answers,"origRow", [33,33,33, 33,33,33, 33,33,33, 0,100, 0,100, 100,0, 25,25,25,25, 25,25,25,25, 25,25,25,25, -100,-100, -100,-100, -100,-100, 100,0, 100,0, 100,0],excluding=[9,11,13,33,35,37])

#TODO add tests for hitrates...

if __name__ == "__main__":
	unittest.main() # run all tests
