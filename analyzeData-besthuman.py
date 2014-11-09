#GOAL: for each video clip, find the best human and report how far off the causalgrammar and origdata are from them
#QUESTION: how should these costs aggregate across video clips?

import os
kCSVDir = 'cvpr_db_results' # from the 'export' option in dealWithDBResults.py
kComputerTypes = ['causalgrammar', 'origdata']

def findDistanceBetweenTwoVectors(A, B):
	dist = 0
	for i in range(len(A)):
		dist += abs(int(A[i]) - int(B[i]))
	return dist


## for each file in our csvs directory, find the "mode" human, then use their values to evaluate each "computer"
print("FILENAME\tBESTHUMANSCORE\tORIGDATA\tCAUSALGRAMMAR")
exceptions = []
total_human_score = 0
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
				humansN = len(humans)
				besthumans = []
				bestscore = 0
				for humanA in humans:
					currentscore = 0
					for humanB in humans:
						currentscore += findDistanceBetweenTwoVectors(humans[humanA],humans[humanB])
					currentscore /= humansN
					if not besthumans or bestscore > currentscore:
						besthumans = [humanA]
						bestscore = currentscore
					elif bestscore == currentscore:
						besthumans.append(humanA)
					#print("{}: {}".format(humanA,currentscore))
				#print("{}\t{}\t{}\t{}\t".format(filename,besthumans,currentscore,humans[besthumans[0]]))
				## FILE, BEST HUMAN SCORE, ORIGDATA SCORE, CAUSALGRAMMAR SCORE
				if not humans:
					raise Exception("NO HUMANS FOR {}".format(filename))
				if not 'origdata' in computers:
					raise Exception("NO ORIGDATA FOR {}".format(filename))
				if not 'causalgrammar' in computers:
					raise Exception("NO CAUSALGRAMMAR FOR {}".format(filename))
				besthumansN = len(besthumans)
				origdata_score = 0
				causalgrammar_score = 0
				for i in range(besthumansN):
					origdata_score += findDistanceBetweenTwoVectors(computers['origdata'],humans[besthumans[i]])
					causalgrammar_score += findDistanceBetweenTwoVectors(computers['causalgrammar'],humans[besthumans[i]])
				origdata_score /= besthumansN
				causalgrammar_score /= besthumansN
				#print("{}\t{}\t{}\t{}\t".format(filename,besthumans,currentscore,humans[besthumans[0]]))
				print("{}\t{}\t{}\t{}\t".format(filename,bestscore,origdata_score,causalgrammar_score))
				N += 1
				total_human_score += bestscore
				total_origdata_score += origdata_score
				total_causalgrammar_score += causalgrammar_score
			except Exception as foo:
				exceptions.append(foo)

print("{}\t{}\t{}\t{}\t".format("AVERAGE",total_human_score / N,total_origdata_score / N,total_causalgrammar_score / N))

print exceptions
