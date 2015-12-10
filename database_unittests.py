import unittest
import csv
#import causal_grammar
#import evaluateCausalGrammar as evaluateXML
#import xml.etree.ElementTree as ET
#import dealWithDBResults

kDebug = True

def extractOrigDataRow(fileName):
	fileName = 'results/cvpr_db_results/'+fileName+'.csv'
	print fileName
	with open(fileName, 'r') as csvfile:
		lines = csv.reader(csvfile)
		for row in lines:
			if row[0] == "origdata":
				retval = row[1:-2]
				print retval
				return map(int, retval)

class TestDBOriginalReponses(unittest.TestCase):
	def testDoor2(self):
		fileName = "door_2"
		answer = extractOrigDataRow(fileName)
		print answer
		assert answer == [200,100,0,0,0,100,0,0,0,0,100,0,0,100]
		#TODO: should answer be fractioned?

	def testDoor5(self):
		pass



if __name__ == "__main__":
	unittest.main() # run all tests


