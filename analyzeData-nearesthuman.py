#GOAL: for each video clip, find the best human and report how far off the causalgrammar and origdata are from them
#QUESTION: how should these costs aggregate across video clips?

import os
import hashlib
from causal_grammar import TYPE_FLUENT, TYPE_ACTION
from summerdata import getPrefixType, getMasterFluentsForPrefix, getFluentsForMasterFluent, getActionsForMasterFluent
from summerdata import groupings
kCSVDir = 'results/cvpr_db_results' # from the 'export' option in dealWithDBResults.py
kComputerTypes = ['causalgrammar', 'origsmrt', 'origdata', 'causalsmrt']
kDebugOn = False
kJustSMRT = True
import re
kPrefixMatch = r'([a-zA-Z_]+)_[0-9]+_'

class MissingDataException(Exception):
	pass

def getPrefixForColumnName(column_name):
	return re.match(kPrefixMatch,column_name).group(1)

def findDistanceBetweenTwoVectors(A, B, fields, fluent):
	distance = {TYPE_ACTION: 0, TYPE_FLUENT: 0}
	fluent_actions = getActionsForMasterFluent(groupings, fluent)
	fluent_fluents = getFluentsForMasterFluent(groupings, fluent)
	for i in range(len(A)):
		prefix = getPrefixForColumnName(fields[i])
		if prefix in fluent_actions or prefix in fluent_fluents:
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
			if prefix in fluent_actions:
				distance[TYPE_ACTION] += diff
			else:
				distance[TYPE_FLUENT] += diff
	return distance

def printLaTeXSummary(dictToPrint):
	causalLine = "Causal"
	detectionsLine = "Detection"
	headerLine = "Object"
	tableTransposed = "Object & Detection & Causal \\\\ \n \\midrule \n"
	for singleFluent in dictToPrint:
		headerLine += " & " + singleFluent
		winningLine = min(dictToPrint[singleFluent], key=dictToPrint[singleFluent].get)
		dictToPrint[singleFluent][winningLine] = "\\textbf{" + str(dictToPrint[singleFluent][winningLine]) + "}"
		causalLine += " & " + str(dictToPrint[singleFluent]["causalsmrt"])
		detectionsLine += " & " + str(dictToPrint[singleFluent]["origsmrt"])
		tableTransposed += "{} & {} & {} \\\\ \n".format(singleFluent, str(dictToPrint[singleFluent]["origsmrt"]), str(dictToPrint[singleFluent]["causalsmrt"]))
	causalLine += ' \\\\'
	headerLine += ' \\\\'
	detectionsLine += ' \\\\'
	print headerLine
	print "\\midrule"
	print detectionsLine
	print causalLine
	print tableTransposed

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-s","--summary", action="store_true", required=False, help="just print the summary results")
parser.add_argument("-e", "--example", action="append", required=False, dest='examples_only', help="specific example[s] to run, such as screen_1, light_5, or door_11")
parser.add_argument("-d","--debug", action="store_true", required=False, help="print out extra debug info")
parser.add_argument("-t","--latex", action="store_true", required=False, help="print out summary as LaTeX")
args = parser.parse_args()

kJustTheSummary = args.summary
kDebugOn = args.debug
kLaTeXSummary = args.latex

## for each file in our csvs directory, find the smallest "human" distance for each "computer" vector
if not kJustTheSummary:
	print("FILENAME\tFLUENT\tHASH\tORIGDATA [action]\t[fluent]\tORIGSMRT [action]\t[fluent]\tCAUSALGRAMMAR [action]\t[fluent]\tCAUSALSMRT [action]\t[fluent]\tORIGHUMANS\tSMRTHUMANS\tCAUSALHUMANS\tCAUSSMRTHUMANS")
exceptions = []
fluentDiffSums = {}

for filename in os.listdir (kCSVDir):
	if args.examples_only:
		found = False
		for example in args.examples_only:
			if filename.startswith(example):
				found = True
				break
		if not found:
			continue
	if filename.endswith(".csv"):
		with open(os.path.join(kCSVDir,filename),"r") as csv:
			try:
				header = csv.readline()
				_, fields = header.rstrip().split(",",1)
				fields = fields.rsplit(",",2)[0].split(",")
				prefixes = set()
				# step 1 -- loop through all fields to get all of the unique prefixes
				for field in fields:
					prefixes.add(getPrefixForColumnName(field))
				fluents = set()
				# step 2 -- turn the reduced set of prefixes into master (aka "reportable") fluents
				for prefix in prefixes:
					for fluent in getMasterFluentsForPrefix(groupings, prefix):
						fluents.add(fluent)
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
						bestscores[computerType] = {'sum':0, TYPE_FLUENT: 0, TYPE_ACTION: 0}
						besthumans[computerType] = []
						for human in humans:
							score = findDistanceBetweenTwoVectors(computers[computerType],humans[human],fields,fluent)
							score['sum'] = score[TYPE_FLUENT] + score[TYPE_ACTION]
							if not besthumans[computerType] or score['sum'] < bestscores[computerType]['sum']:
								besthumans[computerType] = [human]
								bestscores[computerType] = score
							elif bestscores[computerType]['sum'] == score['sum']:
								besthumans[computerType].append(human)
					## FILENAME, FLUENT, HASH, ORIGDATA SCORE, ORIGSMRT SCORE, CAUSALGRAMMAR SCORE, ORIGDATA HUMANS, ORIGSMRT HUMANS, CAUSALGRAMMAR HUMANS
					exampleName, room = filename.rsplit('.',1)
					exampleNameForDB = exampleName.replace("_","")
					if not kJustTheSummary:
						print("\t".join((filename,fluent,hashlib.md5(exampleNameForDB).hexdigest(),
							str(bestscores['origdata'][TYPE_ACTION]), 
							str(bestscores['origdata'][TYPE_FLUENT]), 
							str(bestscores['origsmrt'][TYPE_ACTION]), 
							str(bestscores['origsmrt'][TYPE_FLUENT]), 
							str(bestscores['causalgrammar'][TYPE_ACTION]), 
							str(bestscores['causalgrammar'][TYPE_FLUENT]), 
							str(bestscores['causalsmrt'][TYPE_ACTION]), 
							str(bestscores['causalsmrt'][TYPE_FLUENT]), 
							",".join(besthumans['origdata']), ",".join(besthumans['origsmrt']), ",".join(besthumans['causalgrammar']), ",".join(besthumans['causalsmrt']))))
					# summing for later
					if not fluent in fluentDiffSums:
						fluentDiffSums[fluent] = dict()
						for computer_type in kComputerTypes:
							fluentDiffSums[fluent][computer_type] = {TYPE_ACTION: 0, TYPE_FLUENT: 0}
						fluentDiffSums[fluent]['_count'] = 0
					fluentDiffSums[fluent]['_count'] += 1
					for computer in kComputerTypes:
						fluentDiffSums[fluent][computer][TYPE_ACTION] += bestscores[computer][TYPE_ACTION]
						fluentDiffSums[fluent][computer][TYPE_FLUENT] += bestscores[computer][TYPE_FLUENT]
			except MissingDataException as foo:
				exceptions.append(foo)

#if not N:
#	N = 1

#if not kJustTheSummary:
#print("-\t-\t-\t-\t-\t-\t-\t-\t-\t-")
#print("{}\t{}\t{}\t{}\t{}".format("AVERAGE",total_origdata_score / N,total_causalgrammar_score / N,"",""))
if kJustTheSummary:
	if kLaTeXSummary:
		actionSummary = {}
		fluentSummary = {}
	else:
		print("\t".join(('fluent','N','computer','distA','distF',u'dist\u2211','avgA','avgF',u'avg\u2211')))
	totals = {"_count":0}
	for fluent in fluentDiffSums.keys():
		for computer_type in kComputerTypes:
			if kJustSMRT and not computer_type.endswith("smrt"):
				fluentDiffSums[fluent].pop(computer_type,None)
				continue
			clipsN = fluentDiffSums[fluent]["_count"]
			diff_action = fluentDiffSums[fluent][computer_type][TYPE_ACTION]
			diff_fluent = fluentDiffSums[fluent][computer_type][TYPE_FLUENT]
			diff_total = diff_action + diff_fluent
			fluentDiffSums[fluent][computer_type]["sum"] = diff_total
			fluentDiffSums[fluent][computer_type]["action_avg"] = diff_action / clipsN
			fluentDiffSums[fluent][computer_type]["fluent_avg"] = diff_fluent / clipsN
			fluentDiffSums[fluent][computer_type]["sum_avg"] = diff_total / clipsN
			if computer_type.startswith('causal'):
				computer_words = "Causal"
			elif computer_type.startswith('orig'):
				computer_words= "Detections"
			if kLaTeXSummary:
				if fluent not in actionSummary:
					actionSummary[fluent] = {}
					fluentSummary[fluent] = {}
				actionSummary[fluent][computer_type] = diff_action/clipsN
				fluentSummary[fluent][computer_type] = diff_fluent/clipsN
			else:
				print("\t".join(str(x) for x in (fluent,clipsN,computer_type,diff_action,diff_fluent,diff_total,diff_action/clipsN,diff_fluent/clipsN,diff_total/clipsN)))
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
		if kLaTeXSummary:
			pass
			# TODO: put in totals/All
		else:
			print("\t".join(str(x) for x in ("SUM",fluentsN,computer_type,diff_action,diff_fluent,diff_total,diff_action/fluentsN,diff_fluent/fluentsN,diff_total/fluentsN)))
	if kLaTeXSummary:
		print "ACTION"
		printLaTeXSummary(actionSummary)
		print "FLUENT"
		printLaTeXSummary(fluentSummary)
if kDebugOn:
	print exceptions
