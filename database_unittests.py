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

class TestWaterstream3Water5_8145Directly(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		causal_xml = """
<temporal>
        <fluent_changes>
                <fluent_change energy="54.701" fluent="cup_MORE" frame="0" new_value="off"/>
                <fluent_change energy="54.701" fluent="cup_MORE" frame="498" new_value="on" old_value="off"/>
                <fluent_change energy="16.511" fluent="cup_LESS" frame="0" new_value="off"/>
                <fluent_change energy="17.609" fluent="thirst" frame="0" new_value="on"/>
                <fluent_change energy="74.961" fluent="waterstream" frame="0" new_value="on"/>
                <fluent_change energy="74.961" fluent="waterstream" frame="551" new_value="off" old_value="on"/>
        </fluent_changes>
        <actions>
                <event action="benddown_END" energy="54.701" frame="548"/>
                <event action="benddown_END" energy="74.961" frame="548"/>
        </actions>
</temporal>
"""
		orig_xml = """<temporal><fluent_changes><fluent_change energy="0.0989533079441" fluent="door" frame="443" new_value="off" old_value="on" /><fluent_change energy="0.0110478028553" fluent="screen" frame="419" new_value="off" old_value="on" /><fluent_change energy="0.0513722448725" fluent="screen" frame="512" new_value="on" old_value="off" /></fluent_changes><actions>
	<event action="benddown_END" energy="0.348902" frame="496" />
	<event action="benddown_END" energy="0.342847" frame="497" />
	<event action="benddown_END" energy="0.35301" frame="498" />
	<event action="benddown_END" energy="0.226075" frame="536" />
	<event action="benddown_END" energy="0.153823" frame="537" />
	<event action="benddown_END" energy="0.137256" frame="538" />
	<event action="benddown_END" energy="0.11994" frame="539" />
	<event action="benddown_END" energy="0.087058" frame="540" />
	<event action="benddown_END" energy="0.065782" frame="541" />
	<event action="benddown_END" energy="0.055857" frame="542" />
	<event action="benddown_END" energy="0.05185" frame="543" />
	<event action="benddown_END" energy="0.041464" frame="544" />
	<event action="benddown_END" energy="0.030577" frame="545" />
	<event action="benddown_END" energy="0.024335" frame="546" />
	<event action="benddown_END" energy="0.018087" frame="547" />
	<event action="benddown_END" energy="0.015182" frame="548" />
	<event action="benddown_END" energy="0.024462" frame="549" />
	<event action="benddown_END" energy="0.055768" frame="550" />
	<event action="benddown_END" energy="0.151598" frame="551" />
	<event action="benddown_START" energy="0.226075" frame="437" />
	<event action="benddown_START" energy="0.153823" frame="438" />
	<event action="benddown_START" energy="0.137256" frame="439" />
	<event action="benddown_START" energy="0.11994" frame="440" />
	<event action="benddown_START" energy="0.087058" frame="441" />
	<event action="benddown_START" energy="0.065782" frame="442" />
	<event action="benddown_START" energy="0.055857" frame="443" />
	<event action="benddown_START" energy="0.05185" frame="444" />
	<event action="benddown_START" energy="0.041464" frame="445" />
	<event action="benddown_START" energy="0.030577" frame="446" />
	<event action="benddown_START" energy="0.348902" frame="447" />
	<event action="benddown_START" energy="0.342847" frame="448" />
	<event action="benddown_START" energy="0.35301" frame="449" />
	<event action="benddown_START" energy="0.024462" frame="450" />
	<event action="benddown_START" energy="0.055768" frame="451" />
	<event action="benddown_START" energy="0.151598" frame="452" />
	<event action="standing_END" energy="0.172683" frame="464" />
	<event action="standing_END" energy="0.172683" frame="465" />
	<event action="standing_END" energy="0.172683" frame="466" />
	<event action="standing_END" energy="0.172683" frame="467" />
	<event action="standing_END" energy="0.172683" frame="468" />
	<event action="standing_END" energy="0.172683" frame="469" />
	<event action="standing_END" energy="0.172683" frame="470" />
	<event action="standing_END" energy="0.172683" frame="471" />
	<event action="standing_END" energy="0.172683" frame="472" />
	<event action="standing_END" energy="0.172683" frame="473" />
	<event action="standing_END" energy="0.172683" frame="474" />
	<event action="standing_END" energy="0.172683" frame="475" />
	<event action="standing_END" energy="0.172683" frame="476" />
	<event action="standing_END" energy="0.172683" frame="477" />
	<event action="standing_END" energy="0.172683" frame="478" />
	<event action="standing_END" energy="0.217847" frame="479" />
	<event action="standing_END" energy="0.288565" frame="480" />
	<event action="standing_END" energy="0.181479" frame="514" />
	<event action="standing_END" energy="0.181479" frame="515" />
	<event action="standing_END" energy="0.181479" frame="516" />
	<event action="standing_END" energy="0.181479" frame="517" />
	<event action="standing_END" energy="0.181479" frame="518" />
	<event action="standing_END" energy="0.181479" frame="519" />
	<event action="standing_END" energy="0.148166" frame="520" />
	<event action="standing_END" energy="0.148166" frame="521" />
	<event action="standing_END" energy="0.148166" frame="522" />
	<event action="standing_END" energy="0.148166" frame="523" />
	<event action="standing_END" energy="0.148166" frame="524" />
	<event action="standing_END" energy="0.148166" frame="525" />
	<event action="standing_END" energy="0.174606" frame="526" />
	<event action="standing_END" energy="0.193928" frame="527" />
	<event action="standing_END" energy="0.195351" frame="528" />
	<event action="standing_END" energy="0.220305" frame="529" />
	<event action="standing_END" energy="0.250518" frame="530" />
	<event action="standing_END" energy="0.323485" frame="531" />
	<event action="standing_START" energy="0.172683" frame="415" />
	<event action="standing_START" energy="0.172683" frame="416" />
	<event action="standing_START" energy="0.172683" frame="417" />
	<event action="standing_START" energy="0.172683" frame="418" />
	<event action="standing_START" energy="0.172683" frame="419" />
	<event action="standing_START" energy="0.172683" frame="420" />
	<event action="standing_START" energy="0.172683" frame="421" />
	<event action="standing_START" energy="0.172683" frame="422" />
	<event action="standing_START" energy="0.172683" frame="423" />
	<event action="standing_START" energy="0.172683" frame="424" />
	<event action="standing_START" energy="0.172683" frame="425" />
	<event action="standing_START" energy="0.172683" frame="426" />
	<event action="standing_START" energy="0.172683" frame="427" />
	<event action="standing_START" energy="0.172683" frame="428" />
	<event action="standing_START" energy="0.172683" frame="429" />
	<event action="standing_START" energy="0.217847" frame="430" />
	<event action="standing_START" energy="0.288565" frame="431" />
	<event action="standing_START" energy="0.323485" frame="432" />
	<event action="throwtrash_END" energy="0.243814" frame="544" />
	<event action="throwtrash_END" energy="0.152309" frame="545" />
	<event action="throwtrash_END" energy="0.10544" frame="546" />
	<event action="throwtrash_END" energy="0.073304" frame="547" />
	<event action="throwtrash_END" energy="0.051397" frame="548" />
	<event action="throwtrash_END" energy="0.036254" frame="549" />
	<event action="throwtrash_END" energy="0.025449" frame="550" />
	<event action="throwtrash_END" energy="0.01712" frame="551" />
	<event action="throwtrash_END" energy="0.011286" frame="552" />
	<event action="throwtrash_END" energy="0.007226" frame="553" />
	<event action="throwtrash_END" energy="0.004424" frame="554" />
	<event action="throwtrash_END" energy="0.002565" frame="555" />
	<event action="throwtrash_END" energy="0.001344" frame="556" />
	<event action="throwtrash_END" energy="0.000753" frame="557" />
	<event action="throwtrash_END" energy="0.000445" frame="558" />
	<event action="throwtrash_END" energy="0.000258" frame="559" />
	<event action="throwtrash_END" energy="0.000152" frame="560" />
	<event action="throwtrash_END" energy="8.9e-05" frame="561" />
	<event action="throwtrash_END" energy="5.6e-05" frame="562" />
	<event action="throwtrash_END" energy="3.5e-05" frame="563" />
	<event action="throwtrash_END" energy="2.3e-05" frame="564" />
	<event action="throwtrash_END" energy="1.7e-05" frame="565" />
	<event action="throwtrash_END" energy="1.2e-05" frame="566" />
	<event action="throwtrash_END" energy="8e-06" frame="567" />
	<event action="throwtrash_END" energy="5e-06" frame="568" />
	<event action="throwtrash_END" energy="3e-06" frame="569" />
	<event action="throwtrash_END" energy="3e-06" frame="570" />
	<event action="throwtrash_END" energy="3e-06" frame="571" />
	<event action="throwtrash_END" energy="3e-06" frame="572" />
	<event action="throwtrash_END" energy="2e-06" frame="573" />
	<event action="throwtrash_END" energy="1e-06" frame="574" />
	<event action="throwtrash_END" energy="0.0" frame="575" />
	<event action="throwtrash_END" energy="0.0" frame="576" />
	<event action="throwtrash_END" energy="0.0" frame="577" />
	<event action="throwtrash_END" energy="0.0" frame="578" />
	<event action="throwtrash_END" energy="0.0" frame="579" />
	<event action="throwtrash_END" energy="0.0" frame="580" />
	<event action="throwtrash_END" energy="0.0" frame="581" />
	<event action="throwtrash_END" energy="0.0" frame="582" />
	<event action="throwtrash_END" energy="0.0" frame="583" />
	<event action="throwtrash_END" energy="0.0" frame="584" />
	<event action="throwtrash_END" energy="0.0" frame="585" />
	<event action="throwtrash_END" energy="0.0" frame="586" />
	<event action="throwtrash_END" energy="0.0" frame="587" />
	<event action="throwtrash_END" energy="0.0" frame="588" />
	<event action="throwtrash_END" energy="0.0" frame="589" />
	<event action="throwtrash_END" energy="0.0" frame="590" />
	<event action="throwtrash_END" energy="1e-06" frame="591" />
	<event action="throwtrash_END" energy="1e-06" frame="592" />
	<event action="throwtrash_END" energy="5e-06" frame="593" />
	<event action="throwtrash_START" energy="0.017983" frame="415" />
	<event action="throwtrash_START" energy="0.012056" frame="416" />
	<event action="throwtrash_START" energy="0.007721" frame="417" />
	<event action="throwtrash_START" energy="0.004248" frame="418" />
	<event action="throwtrash_START" energy="0.002312" frame="419" />
	<event action="throwtrash_START" energy="0.001267" frame="420" />
	<event action="throwtrash_START" energy="0.000806" frame="421" />
	<event action="throwtrash_START" energy="0.000581" frame="422" />
	<event action="throwtrash_START" energy="0.000452" frame="423" />
	<event action="throwtrash_START" energy="0.000257" frame="424" />
	<event action="throwtrash_START" energy="0.000128" frame="425" />
	<event action="throwtrash_START" energy="6.3e-05" frame="426" />
	<event action="throwtrash_START" energy="3.3e-05" frame="427" />
	<event action="throwtrash_START" energy="1.9e-05" frame="428" />
	<event action="throwtrash_START" energy="1.2e-05" frame="429" />
	<event action="throwtrash_START" energy="7e-06" frame="430" />
	<event action="throwtrash_START" energy="4e-06" frame="431" />
	<event action="throwtrash_START" energy="3e-06" frame="432" />
	<event action="throwtrash_START" energy="2e-06" frame="433" />
	<event action="throwtrash_START" energy="2e-06" frame="434" />
	<event action="throwtrash_START" energy="3e-06" frame="435" />
	<event action="throwtrash_START" energy="4e-06" frame="436" />
	<event action="throwtrash_START" energy="7e-06" frame="437" />
	<event action="throwtrash_START" energy="1.3e-05" frame="438" />
	<event action="throwtrash_START" energy="3.1e-05" frame="439" />
	<event action="throwtrash_START" energy="8e-05" frame="440" />
	<event action="throwtrash_START" energy="0.000215" frame="441" />
	<event action="throwtrash_START" energy="0.000575" frame="442" />
	<event action="throwtrash_START" energy="0.001358" frame="443" />
	<event action="throwtrash_START" energy="0.003026" frame="444" />
	<event action="throwtrash_START" energy="0.129106" frame="455" />
	<event action="throwtrash_START" energy="0.047578" frame="456" />
	<event action="throwtrash_START" energy="0.016216" frame="457" />
	<event action="throwtrash_START" energy="0.005947" frame="458" />
	<event action="throwtrash_START" energy="0.002211" frame="459" />
	<event action="throwtrash_START" energy="0.000773" frame="460" />
	<event action="throwtrash_START" energy="0.000267" frame="461" />
	<event action="throwtrash_START" energy="8.9e-05" frame="462" />
	<event action="throwtrash_START" energy="5.3e-05" frame="463" />
	<event action="throwtrash_START" energy="3.4e-05" frame="464" />
	<event action="throwtrash_START" energy="2.3e-05" frame="465" />
	<event action="throwtrash_START" energy="1.6e-05" frame="466" />
	<event action="throwtrash_START" energy="1.1e-05" frame="467" />
	<event action="throwtrash_START" energy="7e-06" frame="468" />
	<event action="throwtrash_START" energy="5e-06" frame="469" />
	<event action="throwtrash_START" energy="3e-06" frame="470" />
	<event action="throwtrash_START" energy="3e-06" frame="471" />
	<event action="throwtrash_START" energy="3e-06" frame="472" />
	<event action="throwtrash_START" energy="2e-06" frame="473" />
	<event action="throwtrash_START" energy="2e-06" frame="474" />
	<event action="throwtrash_START" energy="1e-06" frame="475" />
	<event action="throwtrash_START" energy="0.0" frame="476" />
	<event action="throwtrash_START" energy="0.0" frame="477" />
	<event action="throwtrash_START" energy="0.0" frame="478" />
	<event action="throwtrash_START" energy="0.0" frame="479" />
	<event action="throwtrash_START" energy="0.0" frame="480" />
	<event action="throwtrash_START" energy="0.0" frame="481" />
	<event action="throwtrash_START" energy="0.0" frame="482" />
	<event action="throwtrash_START" energy="0.0" frame="483" />
	<event action="throwtrash_START" energy="0.0" frame="484" />
	<event action="throwtrash_START" energy="0.0" frame="485" />
	<event action="throwtrash_START" energy="0.0" frame="486" />
	<event action="throwtrash_START" energy="0.0" frame="487" />
	<event action="throwtrash_START" energy="0.0" frame="488" />
	<event action="throwtrash_START" energy="0.0" frame="489" />
	<event action="throwtrash_START" energy="0.0" frame="490" />
	<event action="throwtrash_START" energy="0.0" frame="491" />
	<event action="throwtrash_START" energy="0.0" frame="492" />
	<event action="throwtrash_START" energy="0.0" frame="493" />
	<event action="throwtrash_START" energy="0.0" frame="494" />
	<event action="throwtrash_START" energy="0.243814" frame="495" />
	<event action="throwtrash_START" energy="0.152309" frame="496" />
	<event action="throwtrash_START" energy="0.10544" frame="497" />
	<event action="throwtrash_START" energy="0.073304" frame="498" />
	<event action="throwtrash_START" energy="0.051397" frame="499" />
	<event action="throwtrash_START" energy="0.036254" frame="500" />
	<event action="throwtrash_START" energy="0.025449" frame="501" />
	<event action="throwtrash_START" energy="0.01712" frame="502" />
	<event action="throwtrash_START" energy="0.011286" frame="503" />
	<event action="throwtrash_START" energy="0.007226" frame="504" />
	<event action="throwtrash_START" energy="0.004424" frame="505" />
	<event action="throwtrash_START" energy="0.002565" frame="506" />
	<event action="throwtrash_START" energy="0.001344" frame="507" />
	<event action="throwtrash_START" energy="0.000753" frame="508" />
	<event action="throwtrash_START" energy="0.000445" frame="509" />
	<event action="throwtrash_START" energy="0.000258" frame="510" />
	<event action="throwtrash_START" energy="0.000152" frame="511" />
	<event action="throwtrash_START" energy="8.9e-05" frame="512" />
	<event action="throwtrash_START" energy="5.6e-05" frame="513" />
	<event action="throwtrash_START" energy="3.5e-05" frame="514" />
	<event action="throwtrash_START" energy="2.3e-05" frame="515" />
	<event action="throwtrash_START" energy="1.7e-05" frame="516" />
	<event action="throwtrash_START" energy="1.2e-05" frame="517" />
	<event action="throwtrash_START" energy="8e-06" frame="518" />
	<event action="throwtrash_START" energy="5e-06" frame="519" />
	<event action="throwtrash_START" energy="3e-06" frame="520" />
	<event action="throwtrash_START" energy="3e-06" frame="521" />
	<event action="throwtrash_START" energy="3e-06" frame="522" />
	<event action="throwtrash_START" energy="3e-06" frame="523" />
	<event action="throwtrash_START" energy="2e-06" frame="524" />
	<event action="throwtrash_START" energy="1e-06" frame="525" />
	<event action="throwtrash_START" energy="0.0" frame="526" />
	<event action="throwtrash_START" energy="0.0" frame="527" />
	<event action="throwtrash_START" energy="0.0" frame="528" />
	<event action="throwtrash_START" energy="0.0" frame="529" />
	<event action="throwtrash_START" energy="0.0" frame="530" />
	<event action="throwtrash_START" energy="0.0" frame="531" />
	<event action="throwtrash_START" energy="0.0" frame="532" />
	<event action="throwtrash_START" energy="0.0" frame="533" />
	<event action="throwtrash_START" energy="0.0" frame="534" />
	<event action="throwtrash_START" energy="0.0" frame="535" />
	<event action="throwtrash_START" energy="0.0" frame="536" />
	<event action="throwtrash_START" energy="0.0" frame="537" />
	<event action="throwtrash_START" energy="0.0" frame="538" />
	<event action="throwtrash_START" energy="0.0" frame="539" />
	<event action="throwtrash_START" energy="0.0" frame="540" />
	<event action="throwtrash_START" energy="0.0" frame="541" />
	<event action="throwtrash_START" energy="1e-06" frame="542" />
	<event action="throwtrash_START" energy="1e-06" frame="543" />
	<event action="throwtrash_START" energy="5e-06" frame="544" /></actions></temporal>"""
		cls.parse_causalxml = ET.fromstring(causal_xml)
		cls.parse_origxml = ET.fromstring(orig_xml)
	
	def innertestAnswers(self,expected,answers):
		returned = {k:answers[k] for k in expected}
		assert expected == returned, "{} [returned] != {} [expected]".format(returned,expected)

	def getAnswersForFrames(self,xml,name,oject,frame1,frame2):
		return xml_stuff.queryXMLForAnswersBetweenFrames(xml, oject, frame1, frame2, name, dumb=True)

	#cutpoints: 415, 515, ...
	def test515(self):
		answers = self.getAnswersForFrames(self.parse_origxml,"origdata","waterstream",515,10000)
		self.innertestAnswers({'dispense_515_act_dispensed':0, 'dispense_515_act_no_dispense':100},answers)

	def test515_cup_causal(self):
		answers = self.getAnswersForFrames(self.parse_causalxml,"causalgrammar","cup",515,10000)
		self.innertestAnswers({'cup_515_more': 0, 'cup_515_less': 0, 'cup_515_same': 100}, answers)

	def test515_waterstream_causal(self):
		answers = self.getAnswersForFrames(self.parse_causalxml,"causalgrammar","waterstream",515,10000)
		self.innertestAnswers({'waterstream_515_water_off': 100, 'waterstream_515_water_on': 0}, answers)

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
		innertest(self.answers,"causalRow", [100,0, 0,100, 0,0,100,0, 0,0,100,0, 100,0,0, 0,0,100, 0,100, 0,100, 0,100, 0,100])

	def testOrig(self):
		innertest(self.answers,"origRow", [50,50, 50,50, 25,25,25,25, 25,25,25,25, 33,33,33, 33,33,33, 100,0, 0,100, 0,100, 0,100], excluding = [18,20,22,24])

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
