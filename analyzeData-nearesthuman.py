#GOAL: for each video clip, find the best human and report how far off the causalgrammar and origdata are from them
#QUESTION: how should these costs aggregate across video clips?

import os
import hashlib
kCSVDir = 'cvpr_db_results' # from the 'export' option in dealWithDBResults.py
kComputerTypes = ['causalgrammar', 'origsmrt', 'origdata']

def findDistanceBetweenTwoVectors(A, B, fields, fluent):
	dist = 0
	for i in range(len(A)):
		if fields[i].startswith(fluent):
			dist += abs(int(A[i]) - int(B[i]))
	return dist

## for each file in our csvs directory, find the smallest "human" distance for each "computer" vector
print("FILENAME\tFLUENT\tHASH\tORIGDATA\tORIGSMRT\tCAUSALGRAMMAR\tORIGHUMANS\tSMRTHUMANS\tCAUSALHUMANS")
exceptions = []
kAllFluentsConstant="all"
fluentDiffSums = {}

for filename in os.listdir (kCSVDir):
	if filename.endswith(".csv"):
		with open(os.path.join(kCSVDir,filename),"r") as csv:
			try:
				header = csv.readline()
				_, fields = header.rstrip().split(",",1)
				fields = fields.rsplit(",",2)[0].split(",")
				fluents = set()
				for field in fields:
					fluents.add(field.split("_",1)[0])
				fluents.add("") # empty string ~ all fluents
				lines = csv.readlines()
				for fluent in fluents:
					humans = {}
					computers = {}
					for line in lines:
						# first column is name; last two columns are timestamp and ... a hash? of ... something?
						# changing it to a map of name -> values, dropping timestamp and hash
						name, values = line.rstrip().split(",",1)
						values = values.rsplit(",",2)[0].split(",")
						if name in kComputerTypes:
							computers[name] = values
						else:
							humans[name] = values
					if not humans:
						raise Exception("NO HUMANS FOR {}".format(filename))
					if not 'origdata' in computers:
						raise Exception("NO ORIGDATA FOR {}".format(filename))
					if not 'causalgrammar' in computers:
						raise Exception("NO CAUSALGRAMMAR FOR {}".format(filename))
					humansN = len(humans)
					bestscores = {}
					besthumans = {}
					for computerType in kComputerTypes:
						bestscores[computerType] = 0
						besthumans[computerType] = []
						for human in humans:
							currentscore = findDistanceBetweenTwoVectors(computers[computerType],humans[human],fields,fluent)
							if not besthumans[computerType] or currentscore < bestscores[computerType]:
								besthumans[computerType] = [human]
								bestscores[computerType] = currentscore
							elif bestscores[computerType] == currentscore:
								besthumans[computerType].append(human)
					## FILENAME, FLUENT, HASH, ORIGDATA SCORE, ORIGSMRT SCORE, CAUSALGRAMMAR SCORE, ORIGDATA HUMANS, ORIGSMRT HUMANS, CAUSALGRAMMAR HUMANS
					exampleName, room = filename.rsplit('.',1)
					exampleNameForDB = exampleName.replace("_","")
					fluent = fluent if fluent else kAllFluentsConstant
					print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(filename,fluent,hashlib.md5(exampleNameForDB).hexdigest(),bestscores['origdata'], bestscores['origsmrt'], bestscores['causalgrammar'], besthumans['origdata'], besthumans['origsmrt'], besthumans['causalgrammar']))
					# summing for later
					if not fluent in fluentDiffSums:
						fluentDiffSums[fluent] = {'origdata': [0, 0], 'origsmrt': [0, 0], 'causalgrammar': [0, 0], '_count': 0}
					fluentDiffSums[fluent]['_count'] += 1
					for computer in kComputerTypes:
						fluentDiffSums[fluent][computer][0] += bestscores[computer]
						fluentDiffSums[fluent][computer][1] = "{} avg".format(fluentDiffSums[fluent][computer][0] / fluentDiffSums[fluent]['_count'])
			except Exception as foo:
				exceptions.append(foo)

#if not N:
#	N = 1

print("-\t-\t-\t-\t-\t-\t-\t-")
#print("{}\t{}\t{}\t{}\t{}".format("AVERAGE",total_origdata_score / N,total_causalgrammar_score / N,"",""))
import pprint
pp = pprint.PrettyPrinter(depth=6)
pp.pprint(fluentDiffSums)

#print exceptions
