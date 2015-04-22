#GOAL: for each video clip, find the best human and report how far off the causalgrammar and origdata are from them
#QUESTION: how should these costs aggregate across video clips?

import os
import hashlib
kCSVDir = 'results/cvpr_db_results' # from the 'export' option in dealWithDBResults.py
kComputerTypes = ['causalgrammar', 'origsmrt', 'origdata', 'causalsmrt']
kJustTheSummary = False
kDebugOn = False
kJustSMRT = True

class MissingDataException(Exception):
	pass

def findDistanceBetweenTwoVectors(A, B, fields, fluent):
	distance = {"action": 0, "fluent": 0}
	fluent_action = "{}_action".format(fluent)
	for i in range(len(A)):
		if fields[i].startswith(fluent) or fields[i].startswith(fluent_action):
			Ai = A[i]
			Bi = B[i]
			try:
				Ai = int(Ai)
			except ValueError:
				Ai = 0
			try:
				Bi = int(Bi)
			except ValueError:
				Bi = 0
			diff = abs(Ai - Bi)
			if fields[i].startswith(fluent_action):
				distance['action'] += diff
			else:
				distance['fluent'] += diff
	return distance

## for each file in our csvs directory, find the smallest "human" distance for each "computer" vector
if not kJustTheSummary:
	print("FILENAME\tFLUENT\tHASH\tORIGDATA\tORIGSMRT\tCAUSALGRAMMAR\tCAUSALSMRT\tORIGHUMANS\tSMRTHUMANS\tCAUSALHUMANS\tCAUSSMRTHUMANS")
exceptions = []
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
						raise MissingDataException("NO HUMANS FOR {}".format(filename))
					if not 'origdata' in computers:
						raise MissingDataException("NO ORIGDATA FOR {}".format(filename))
					if not 'origsmrt' in computers:
						raise MissingDataException("NO ORIGSMRT FOR {}".format(filename))
					if not 'causalgrammar' in computers:
						raise MissingDataException("NO CAUSALGRAMMAR FOR {}".format(filename))
					if not 'causalsmrt' in computers:
						raise MissingDataException("NO CAUSALSMRT FOR {}".format(filename))
					humansN = len(humans)
					bestscores = {}
					besthumans = {}
					for computerType in kComputerTypes:
						bestscores[computerType] = {'sum':0, 'fluent': 0, 'action': 0}
						besthumans[computerType] = []
						for human in humans:
							score = findDistanceBetweenTwoVectors(computers[computerType],humans[human],fields,fluent)
							score['sum'] = score['fluent'] + score['action']
							if not besthumans[computerType] or score['sum'] < bestscores[computerType]['sum']:
								besthumans[computerType] = [human]
								bestscores[computerType] = score
							elif bestscores[computerType]['sum'] == score['sum']:
								besthumans[computerType].append(human)
					## FILENAME, FLUENT, HASH, ORIGDATA SCORE, ORIGSMRT SCORE, CAUSALGRAMMAR SCORE, ORIGDATA HUMANS, ORIGSMRT HUMANS, CAUSALGRAMMAR HUMANS
					exampleName, room = filename.rsplit('.',1)
					exampleNameForDB = exampleName.replace("_","")
					fluent = fluent if fluent else kAllFluentsConstant
					if not kJustTheSummary:
						print("\t".join((filename,fluent,hashlib.md5(exampleNameForDB).hexdigest(),str(bestscores['origdata']['sum']), str(bestscores['origsmrt']['sum']), str(bestscores['causalgrammar']['sum']), str(bestscores['causalsmrt']['sum']), ",".join(besthumans['origdata']), ",".join(besthumans['origsmrt']), ",".join(besthumans['causalgrammar']), ",".join(besthumans['causalsmrt']))))
					# summing for later
					if not fluent in fluentDiffSums:
						fluentDiffSums[fluent] = dict()
						for computer_type in kComputerTypes:
							fluentDiffSums[fluent][computer_type] = {"action": 0, "fluent": 0}
						fluentDiffSums[fluent]['_count'] = 0
					fluentDiffSums[fluent]['_count'] += 1
					for computer in kComputerTypes:
						fluentDiffSums[fluent][computer]["action"] += bestscores[computer]["action"]
						fluentDiffSums[fluent][computer]["fluent"] += bestscores[computer]["fluent"]
			except MissingDataException as foo:
				exceptions.append(foo)

#if not N:
#	N = 1

#if not kJustTheSummary:
#print("-\t-\t-\t-\t-\t-\t-\t-\t-\t-")
#print("{}\t{}\t{}\t{}\t{}".format("AVERAGE",total_origdata_score / N,total_causalgrammar_score / N,"",""))
if kJustTheSummary:
	#print("&".join(('fluent','N','computer','distA','distF','dist=','avgA','avgF','avg=')))
	print(" & ".join(('Object','Computer','N','Action','Fluent','All'))+'\\\\')
	print("\\midrule")
	totals = {"_count":0}
	for fluent in fluentDiffSums.keys():
		for computer_type in kComputerTypes:
			if kJustSMRT and not computer_type.endswith("smrt"):
				fluentDiffSums[fluent].pop(computer_type,None)
				continue
			clipsN = fluentDiffSums[fluent]["_count"]
			diff_action = fluentDiffSums[fluent][computer_type]["action"]
			diff_fluent = fluentDiffSums[fluent][computer_type]["fluent"]
			diff_total = diff_action + diff_fluent
			fluentDiffSums[fluent][computer_type]["sum"] = diff_total
			fluentDiffSums[fluent][computer_type]["action_avg"] = diff_action / clipsN
			fluentDiffSums[fluent][computer_type]["fluent_avg"] = diff_fluent / clipsN
			fluentDiffSums[fluent][computer_type]["sum_avg"] = diff_total / clipsN
			if computer_type.startswith('causal'):
				computer_words = "Causal"
			elif computer_type.startswith('orig'):
				computer_words= "Detections"
			#print("&".join(str(x) for x in (fluent,clipsN,computer_type,diff_action,diff_fluent,diff_total,diff_action/clipsN,diff_fluent/clipsN,diff_total/clipsN)))
			print(" & ".join(str(x) for x in (fluent,computer_words,clipsN,diff_action/clipsN,diff_fluent/clipsN,diff_total/clipsN))+'\\\\')
			if not computer_type in totals:
				totals[computer_type] = {"action_avg_sum": 0, 'fluent_avg_sum': 0}
			totals[computer_type]["action_avg_sum"] += diff_action / clipsN
			totals[computer_type]["fluent_avg_sum"] += diff_fluent / clipsN
		totals["_count"] += 1
	for computer_type in kComputerTypes:
		if computer_type.startswith('causal'):
			computer_words = "Causal"
		elif computer_type.startswith('orig'):
			computer_words= "Detections"
		if kJustSMRT and not computer_type.endswith("smrt"):
			continue
		diff_action = totals[computer_type]['action_avg_sum']
		diff_fluent = totals[computer_type]['fluent_avg_sum']
		diff_total = diff_action + diff_fluent
		fluentsN = totals["_count"]
		print("&".join(str(x) for x in ("SUM",fluentsN,computer_type,diff_action,diff_fluent,diff_total,diff_action/fluentsN,diff_fluent/fluentsN,diff_total/fluentsN)))
		print(" & ".join(str(x) for x in ("ALL",computer_words,fluentsN,diff_action/fluentsN,diff_fluent/fluentsN,diff_total/fluentsN))+'\\\\')
if kDebugOn:
	print exceptions
