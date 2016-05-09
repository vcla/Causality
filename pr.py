#GOAL: for each video clip, find the best human and report how far off the causalgrammar and origdata are from them
#still weird for precision and recall because the way we've defined things, FP's tend to pair with FN's (on binary choice), and be 1/3 to 2/3 (either direction) on trinary choices, etc....

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
kComputerTypes = ['causalgrammar', 'origsmrt', 'origdata', 'causalsmrt', 'random']
kDebugOn = False
import re
kPrefixMatch = r'([a-zA-Z_]+)_([0-9]+)_(.*)'

class MissingDataException(Exception):
	pass

"""
Here's how it's going to go down:

for each single query (ie: single text entry field from the quiz):
	truth positive = (nearest human's response > 50)
	truth negative = (nearest human's response <= 50)

	true positive = (truth positive && |nearest - computer| < 25)
	false negative = (truth positive && !(true positive))

	true negative = (truth negative && |nearest - computer| < 25)
	false positive = (truth negative && !(true negative))
"""
# returns [TP, TN, FP, FN] instead of just HIT
def test_hit(computer, human, field_lookup, field_group):
	retval = {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0}
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
	for z in zip(As,Bs):
		diff = abs(z[0] - z[1])
		if z[1] > 50: # ground truth positive
			if diff < 12:
				selection = 'TP'
			else:
				selection = 'FN'
		else: # ground truth negative
			if diff < 25:
				selection = 'TN'
			else:
				selection = 'FP'
		retval[selection] += 1
	return retval

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

overall_scores = dict()
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
				clip_scores = defaultdict(lambda: defaultdict(lambda: {'TP':0, 'FP':0, 'TN':0, 'FN':0}))
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
						for key in hit:
							clip_scores[computerType][field_group[0]][key] += hit[key]
				overall_scores[filename] = clip_scores
			except MissingDataException as foo:
				exceptions.append(foo)

# now we sum/average our hitrates per prefix (fluent or action)
prefix_scores = defaultdict(lambda: defaultdict(lambda: {'TP':0, 'FP':0, 'TN':0, 'FN':0, 'precision': 0., 'recall': 0., 'f1score': 0.}))
for filename in overall_scores:
	for computer in overall_scores[filename]:
		if not args.smart and computer in ["causalsmrt", "origsmrt", ]:
			continue
		for prefix in overall_scores[filename][computer]:
			for key in overall_scores[filename][computer][prefix]:
				prefix_scores[prefix][computer][key] += overall_scores[filename][computer][prefix][key]
for prefix in prefix_scores:
	for computer in prefix_scores[prefix]:
		TP = prefix_scores[prefix][computer]["TP"]
		FP = prefix_scores[prefix][computer]["FP"]
		TN = prefix_scores[prefix][computer]["TN"]
		FN = prefix_scores[prefix][computer]["FN"]
		try:
			prefix_scores[prefix][computer]["precision"] = float(TP) / (TP + FP)
		except ZeroDivisionError:
			pass
		try:
			prefix_scores[prefix][computer]["recall"] = float(TP) / (TP + FN)
		except ZeroDivisionError:
			pass
		try:
			prefix_scores[prefix][computer]["f1score"] = 2. * TP / (2 * TP + FP + FN)
		except ZeroDivisionError:
			pass

# now we print out our carefully crafted table :)
print("\t".join(("prefix","computer","TP","TN","FP","FN","precision","recall","f1score",)))
summary = defaultdict(lambda: {"precision": 0., "recall": 0., "f1score": 0.})
summary_N = defaultdict(int)
sum_fluents = defaultdict(lambda: {"precision": 0., "recall": 0., "f1score": 0.})
sum_fluents_N = defaultdict(int)
sum_actions = defaultdict(lambda: {"precision": 0., "recall": 0., "f1score": 0.})
sum_actions_N = defaultdict(int)
for prefix in prefix_scores:
	for computer in prefix_scores[prefix]:
		if not args.smart and computer in ["causalsmrt", "origsmrt", ]:
			continue
		TP = prefix_scores[prefix][computer]['TP']
		TN = prefix_scores[prefix][computer]['TN']
		FP = prefix_scores[prefix][computer]['FP']
		FN = prefix_scores[prefix][computer]['FN']
		precision = prefix_scores[prefix][computer]['precision']
		recall = prefix_scores[prefix][computer]['recall']
		f1score = prefix_scores[prefix][computer]['f1score']
		if not args.summary:
			print("\t".join((prefix, computer, str(TP), str(TN), str(FP), str(FN), "{:.2f}".format(precision), "{:.2f}".format(recall), "{:.2f}".format(f1score))))
		summary[computer]["precision"] += precision
		summary[computer]["recall"] += recall
		summary[computer]["f1score"] += f1score
		summary_N[computer] += 1
		if prefix in type_fluents:
			sum_fluents[computer]["precision"] += precision
			sum_fluents[computer]["recall"] += recall
			sum_fluents[computer]["f1score"] += f1score
			sum_fluents_N[computer] += 1
		else:
			sum_actions[computer]["precision"] += precision
			sum_actions[computer]["recall"] += recall
			sum_actions[computer]["f1score"] += f1score
			sum_actions_N[computer] += 1

for computer in sum_fluents:
	precision = sum_fluents[computer]["precision"] / sum_fluents_N[computer]
	recall = sum_fluents[computer]["recall"] / sum_fluents_N[computer]
	f1score = sum_fluents[computer]["f1score"] / sum_fluents_N[computer]
	print("\t".join(("FLUENTS", computer, "", "", "", "", "{:.2f}".format(precision), "{:.2f}".format(recall), "{:.2f}".format(f1score))))

for computer in sum_actions:
	precision = sum_actions[computer]["precision"] / sum_actions_N[computer]
	recall = sum_actions[computer]["recall"] / sum_actions_N[computer]
	f1score = sum_actions[computer]["f1score"] / sum_actions_N[computer]
	print("\t".join(("ACTIONS", computer, "", "", "", "", "{:.2f}".format(precision), "{:.2f}".format(recall), "{:.2f}".format(f1score))))

for computer in summary:
	precision = summary[computer]["precision"] / summary_N[computer]
	recall = summary[computer]["recall"] / summary_N[computer]
	f1score = summary[computer]["f1score"] / summary_N[computer]
	print("\t".join(("SUM", computer, "", "", "", "", "{:.2f}".format(precision), "{:.2f}".format(recall), "{:.2f}".format(f1score))))

if kDebugOn:
	pp.pprint(exceptions)
