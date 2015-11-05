#GOAL: for each video clip, find the best human and report how far off the causalgrammar and origdata are from them
#QUESTION: how should these costs aggregate across video clips?

#NOTE: 'besthuman' is really 'nearesthuman' in this one.

import json
import pprint as pp
import os
import hashlib
from collections import defaultdict
from causal_grammar import TYPE_FLUENT, TYPE_ACTION
from summerdata import getPrefixType, getMasterFluentsForPrefix, getFluentsForMasterFluent, getActionsForMasterFluent
from summerdata import groupings
kCSVDir = 'results/cvpr_db_results' # from the 'export' option in dealWithDBResults.py
kComputerTypes = ['causalgrammar', 'origsmrt', 'origdata', 'causalsmrt']
#kComputerTypes = ['causalgrammar', 'origdata']
kDebugOn = False
import re
kPrefixMatch = r'([a-zA-Z_]+)_([0-9]+)_(.*)'

class MissingDataException(Exception):
	pass

def test_hit(computer, human, field_lookup, field_group):
	diff = 0
	key = field_group.keys()[0]
	As = list()
	Bs = list()
	AsD = list()
	BsD = list()
	for value in field_group[key]:
		column = field_lookup["_".join((key[0], key[1], value,))]
		Ai = computer[column]
		Bi = human[column]
		try:
			Ai = int(Ai)
		except ValueError:
			Ai = 0
		try:
			Bi = int(Bi)
		except ValueError:
			Bi = 0
		As.append(Ai)
		Bs.append(Bi)
		AsD.append(computer[column])
		BsD.append(human[column])
	if sum(As) == 0:
		As = [100, ] * len(Bs)
	if sum(Bs) == 0:
		Bs = [100, ] * len(Bs)
	sumAs = sum(As) / 100.
	sumBs = sum(Bs) / 100.
	try:
		As = [a / sumAs for a in As] # normalizing to 100
		Bs = [b / sumBs for b in Bs] # normalizing to 100
	except ZeroDivisionError:
		raise MissingDataException("no data for {}: computer {} vs human {} FROM computer {} vs human {}".format(key, As, Bs, AsD, BsD))
	diff = sum([abs(z[0]-z[1]) for z in zip(As,Bs)]) / len(field_group[key])
	return diff < 25

def splitColumnName(column_name):
	m = re.match(kPrefixMatch,column_name)
	return [m.group(1), m.group(2), m.group(3), ]

def getPrefixForColumnName(column_name):
	return re.match(kPrefixMatch,column_name).group(1)

def isFluent(fieldname):
	return not isAction(fieldname)

def isAction(fieldname):
	prefix, frame, selection = splitColumnName(field)
	return selection.startswith("act_")

def findDistanceBetweenTwoVectors(A, B):
	distance = 0
	for i in range(len(A)):
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
		distance += diff
	return distance

def emboldenWinningLine(fluentResult, winningValue):
	returnLine = " & "
	if fluentResult == winningValue:
		returnLine += "\\textbf{" + str(fluentResult) + "}"
	else:
		returnLine += str(fluentResult)
	return returnLine

def printLaTeXSummary(dictToPrint):
	#print dictToPrint
	causalLine = "Causal"
	detectionsLine = "Detection"
	headerLine = "Object"
	#tableTransposed = "Object & Detection & Causal \\\\ \n \\midrule \n"
	for singleFluent in dictToPrint:
		if dictToPrint[singleFluent]:
			winningLine = max(dictToPrint[singleFluent], key=dictToPrint[singleFluent].get)
			winningValue = dictToPrint[singleFluent][winningLine]
			if singleFluent == "total":
				winningTotalValue = winningValue
			else:
				headerLine += " & " + singleFluent
				causalLine += emboldenWinningLine(dictToPrint[singleFluent]["causalgrammar"], winningValue)
				detectionsLine += emboldenWinningLine(dictToPrint[singleFluent]["origdata"], winningValue)
				#tableTransposed += "{} & {} & {} \\\\ \n".format(singleFluent, str(dictToPrint[singleFluent]["origsmrt"]), str(dictToPrint[singleFluent]["causalsmrt"]))
		else:
			headerLine += " & " + singleFluent
			causalLine += " & N/A "
			detectionsLine += " & N/A "
	causalLine += emboldenWinningLine(dictToPrint["total"]["causalgrammar"], winningTotalValue)
	detectionsLine += emboldenWinningLine(dictToPrint["total"]["origdata"], winningTotalValue)
	headerLine += " & Average"
	causalLine += ' \\\\'
	headerLine += ' \\\\'
	detectionsLine += ' \\\\'
	print headerLine
	print "\\midrule"
	print detectionsLine
	print causalLine


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-s","--summary", action="store_true", required=False, help="just print the summary results")
parser.add_argument("-e", "--example", action="append", required=False, dest='examples_only', help="specific example[s] to run, such as screen_1, light_5, or door_11")
parser.add_argument("-d","--debug", action="store_true", required=False, help="print out extra debug info")
parser.add_argument("-t","--latex", action="store_true", required=False, help="print out summary as LaTeX")
parser.add_argument("-m","--smart", action="store_true", required=False, help="include 'smart' computers")
args = parser.parse_args()

kJustTheSummary = args.summary
kDebugOn = args.debug
kLaTeXSummary = args.latex

exceptions = []

## for storing which field prefixes are actions and which are fluents
type_actions = set()
type_fluents = set()

overall_hitrates = dict()
## for each file in our csvs directory, find the smallest "human" distance for each "computer" vector
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
				# should probably have used a csv dictreader here for simplicity but that's okay....
				if args.debug:
					print("\n\n\nREADING {}\n=========\n".format(filename))
				header = csv.readline()
				_, fields = header.rstrip().split(",",1) # chop "name" from the beginning
				fields = fields.rsplit(",",2)[0].split(",") # chop "stamp" and "hash" from the end
				field_groups = defaultdict(list)
				# step 1 -- loop through all fields to get all of the unique prefixes
				field_lookup = dict()
				i = 0
				for field in fields:
					prefix, frame, selection = splitColumnName(field)
					if isFluent(field):
						type_fluents.add(prefix)
					else:
						type_actions.add(prefix)
					field_groups[(prefix, frame, )].append(selection)
					field_lookup[field] = i
					i += 1
				lines = csv.readlines()
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
				bestdistance = {}
				besthumans = {}
				for computerType in kComputerTypes:
					bestdistance[computerType] = 0
					besthumans[computerType] = []
					for human in humans:
						score = findDistanceBetweenTwoVectors(computers[computerType],humans[human])
						if not besthumans[computerType] or score < bestdistance[computerType]:
							besthumans[computerType] = [human]
							bestdistance[computerType] = score
						elif bestdistance[computerType] == score:
							besthumans[computerType].append(human)
				clip_hits = defaultdict(lambda: defaultdict(int))
				clip_misses = defaultdict(lambda: defaultdict(int))
				clip_hitrate = defaultdict(dict)
				# clip_fluent_pr = defaultdict(lambda: defaultdict(int))
				# clip_action_pr = defaultdict(lambda: defaultdict(int))
				for computerType in kComputerTypes:
					if not args.smart and computerType in ["causalsmrt", "origsmrt", ]:
						continue
					computer = computers[computerType]
					human = humans[besthumans[computerType][0]] # TODO: for now we will always take the "first" of the best humans. in the future, maybe we want to average the human beliefs? should that always give us an equal or better score?
					for field_group in field_groups:
						try:
							hit = test_hit(computer, human, field_lookup, {field_group: field_groups[field_group]}) # there has to be a better way to do this than this silly re-dicting, right?
						except MissingDataException as bar:
							# skip this questionable column
							print("MISSING DATA {}".format([filename, computerType, bar,]))
							exceptions.append([filename, computerType, bar,])
							continue
						# adding 0 just to ensure the field exists in both hits and misses, to make reading/debugging the data easier
						if hit:
							clip_hits[computerType][field_group[0]] += 1
							clip_misses[computerType][field_group[0]] += 0
						else:
							clip_hits[computerType][field_group[0]] += 0
							clip_misses[computerType][field_group[0]] += 1
					for key in clip_hits[computerType]:
						clip_hitrate[computerType][key] = float(clip_hits[computerType][key]) / (clip_hits[computerType][key] + clip_misses[computerType][key])
				overall_hitrates[filename] = clip_hitrate
			except MissingDataException as foo:
				exceptions.append(foo)

# pp.pprint(json.dumps(overall_hitrates))
# now we sum/average our hitrates per prefix (fluent or action)
prefix_hitsum = defaultdict(lambda: defaultdict(int))
prefix_hitN = defaultdict(lambda: defaultdict(int))
prefix_hitrate = defaultdict(lambda: defaultdict(int))
for filename in overall_hitrates:
	for computer in overall_hitrates[filename]:
		if not args.smart and computer in ["causalsmrt", "origsmrt", ]:
			continue
		for prefix in overall_hitrates[filename][computer]:
			prefix_hitsum[prefix][computer] += overall_hitrates[filename][computer][prefix]
			prefix_hitN[prefix][computer] += 1
for prefix in prefix_hitsum:
	for computer in prefix_hitsum[prefix]:
		prefix_hitrate[prefix][computer] = prefix_hitsum[prefix][computer] / prefix_hitN[prefix][computer]

# now we print out our carefully crafted table :)
print("\t".join(("prefix","N","computer","hitrate",)))
summary = defaultdict(float)
if kLaTeXSummary:
	actionSummary = {"total": {}}
	fluentSummary = {"total": {}}
summary_N = defaultdict(int)
sum_fluents = defaultdict(float)
sum_fluents_N = defaultdict(int)
sum_actions = defaultdict(float)
sum_actions_N = defaultdict(int)
for prefix in prefix_hitsum:
	for computer in prefix_hitsum[prefix]:
		if not args.smart and computer in ["causalsmrt", "origsmrt", ]:
			continue
		if not args.summary:
			print("\t".join((prefix, str(prefix_hitN[prefix][computer]), computer, "{:.2f}".format(prefix_hitrate[prefix][computer]),)))
			if kLaTeXSummary:
				#print "----------------------"
				latexPrefix = prefix.split('_')[0]
				if latexPrefix in ['water']:
					latexPrefix = 'cup'
				elif latexPrefix in ['dispense']:
					latexPrefix = 'waterstream'
				if latexPrefix not in actionSummary:
					actionSummary[latexPrefix] = {}
					fluentSummary[latexPrefix] = {}
				#print "{} {} {}".format(latexPrefix, computer, prefix_hitrate[prefix][computer])
				if prefix in type_fluents:
					fluentSummary[latexPrefix][computer] = "{:.2f}".format(prefix_hitrate[prefix][computer])
					#print "FLUENT"
					#print fluentSummary
				else:
					actionSummary[latexPrefix][computer] = "{:.2f}".format(prefix_hitrate[prefix][computer])
					#print "ACTION"
					#print fluentSummary
		hitrate = prefix_hitrate[prefix][computer]
		summary[computer] += hitrate
		summary_N[computer] += 1
		if prefix in type_fluents:
			sum_fluents[computer] += hitrate
			sum_fluents_N[computer] += 1
		else:
			sum_actions[computer] += hitrate
			sum_actions_N[computer] += 1

for computer in summary:
	if kLaTeXSummary:
		fluentSummary["total"][computer] = "{:.2f}".format(sum_fluents[computer] / sum_fluents_N[computer])
	print("\t".join(("FLUENTS",str(sum_fluents_N[computer]), computer, "{:.2f}".format(sum_fluents[computer] / sum_fluents_N[computer], ))))

for computer in summary:
	if kLaTeXSummary:
		actionSummary["total"][computer] = "{:.2f}".format(sum_actions[computer] / sum_actions_N[computer])
	print("\t".join(("ACTIONS",str(sum_actions_N[computer]), computer, "{:.2f}".format(sum_actions[computer] / sum_actions_N[computer], ))))

for computer in summary:
	print("\t".join(("SUM",str(summary_N[computer]), computer, "{:.2f}".format(summary[computer] / summary_N[computer], ))))

if kLaTeXSummary:
	print "------ ACTION TABLE ------"
	printLaTeXSummary(actionSummary)
	print "------ FLUENT TABLE -------"
	printLaTeXSummary(fluentSummary)

if kDebugOn:
	pp.pprint(exceptions)
