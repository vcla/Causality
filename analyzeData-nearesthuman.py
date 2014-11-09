#GOAL: for each video clip, find the best human and report how far off the causalgrammar and origdata are from them
#QUESTION: how should these costs aggregate across video clips?

import os
import hashlib
kCSVDir = 'cvpr_db_results' # from the 'export' option in dealWithDBResults.py
kComputerTypes = ['causalgrammar', 'origdata']

def findDistanceBetweenTwoVectors(A, B):
	dist = 0
	for i in range(len(A)):
		dist += abs(int(A[i]) - int(B[i]))
	return dist


## for each file in our csvs directory, find the smallest "human" distance for each "computer" vector
print("FILENAME\tHASH\tORIGDATA\tCAUSALGRAMMAR\tORIGHUMANS\tCAUSALHUMANS")
exceptions = []
total_origdata_score = 0
total_causalgrammar_score = 0
N = 0
for filename in os.listdir (kCSVDir):
	if filename.endswith(".csv"):
		with open(os.path.join(kCSVDir,filename),"r") as csv:
			try:
				header = csv.readline()
				humans = {}
				computers = {}
				for line in csv:
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
						currentscore = findDistanceBetweenTwoVectors(computers[computerType],humans[human])
						if not besthumans[computerType] or currentscore < bestscores[computerType]:
							besthumans[computerType] = [human]
							bestscores[computerType] = currentscore
						elif bestscores[computerType] == currentscore:
							besthumans[computerType].append(human)
				#print bestscores
				#print besthumans
				## FILE, ORIGDATA SCORE, CAUSALGRAMMAR SCORE, ORIGDATA HUMANS, CAUSALGRAMMAR HUMANS
				exampleName, room = filename.rsplit('.',1)
				exampleNameForDB = exampleName.replace("_","")
				print("{}\t{}\t{}\t{}\t{}\t{}".format(filename,hashlib.md5(exampleNameForDB).hexdigest(),bestscores['origdata'], bestscores['causalgrammar'], besthumans['origdata'],besthumans['causalgrammar']))
				N += 1
				total_origdata_score += bestscores['origdata']
				total_causalgrammar_score += bestscores['causalgrammar']
			except Exception as foo:
				exceptions.append(foo)

if not N:
	N = 1

print("{}\t{}\t{}\t{}\t{}".format("AVERAGE",total_origdata_score / N,total_causalgrammar_score / N,"",""))

print exceptions
