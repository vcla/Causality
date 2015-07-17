#GOAL: for each video clip, compute the stddev of each computer method against all of the humans

import os
import hashlib
from causal_grammar import TYPE_FLUENT, TYPE_ACTION
from summerdata import getPrefixType, getMasterFluentsForPrefix, getFluentsForMasterFluent, getActionsForMasterFluent
from summerdata import groupings
import numpy as np
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

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--example", action="append", required=False, dest='examples_only', help="specific example[s] to run, such as screen_1, light_5, or door_11")
parser.add_argument("-d","--debug", action="store_true", required=False, help="print out extra debug info")
parser.add_argument("-t","--latex", action="store_true", required=False, help="print out summary as LaTeX")
args = parser.parse_args()

kDebugOn = args.debug
kLaTeX = args.latex

exceptions = []
scores = {}

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
					if not fluent in scores:
						scores[fluent] = dict()
						scores[fluent]['_count'] = 1
					else:
						scores[fluent]['_count'] += 1
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
					for computerType in kComputerTypes:
						scores[fluent][computerType] = {TYPE_FLUENT: [], TYPE_ACTION: []}
						for human in humans:
							score = findDistanceBetweenTwoVectors(computers[computerType],humans[human],fields,fluent)
							scores[fluent][computerType][TYPE_FLUENT].append(score[TYPE_FLUENT])
							scores[fluent][computerType][TYPE_ACTION].append(score[TYPE_ACTION])
					fluent = fluent if fluent else kAllFluentsConstant
			except MissingDataException as foo:
				exceptions.append(foo)

if kLaTeX:
	print(" & ".join(('Object','Computer','Action','Fluent','All'))+' \\\\')
	print("\\midrule")
else:
	print("\t".join(('fluent','N','computer','stddevA','stddevF',u'stddevSUM')))
totals = {"_count":0}
#import pprint
#pp = pprint.PrettyPrinter(indent=1)
#pp.pprint(scores)
for fluent in scores.keys():
	for computer_type in kComputerTypes:
		if kJustSMRT and not computer_type.endswith("smrt"):
			scores[fluent].pop(computer_type,None)
			continue
		if not computer_type in scores[fluent]:
			continue
		clipsN = scores[fluent]['_count']
		stddev_action = np.std(scores[fluent][computer_type][TYPE_ACTION])
		stddev_fluent = np.std(scores[fluent][computer_type][TYPE_FLUENT])
		stddev_total = np.std(scores[fluent][computer_type][TYPE_ACTION] + scores[fluent][computer_type][TYPE_FLUENT])
		scores[fluent][computer_type]["stddev_total"] = stddev_total
		scores[fluent][computer_type]["stddev_action"] = stddev_action
		scores[fluent][computer_type]["stddev_fluent"] = stddev_fluent
		if computer_type.startswith('causal'):
			computer_words = "Causal"
		elif computer_type.startswith('orig'):
			computer_words= "Detections"
		if kLaTeX:
			#print(" & ".join(str(x) for x in (fluent,computer_words,diff_action/clipsN,diff_fluent/clipsN,diff_total/clipsN))+' \\\\')
			raise "TODO"
		else:
			print("\t".join(str(x) for x in (fluent,clipsN,computer_type,stddev_action,stddev_fluent,stddev_total)))
		if not computer_type in totals:
			totals[computer_type] = {"stddev_action": 0, 'stddev_fluent': 0, 'stddev_total': 0}
		totals[computer_type]["stddev_action"] += stddev_action
		totals[computer_type]["stddev_fluent"] += stddev_fluent
		totals[computer_type]["stddev_total"] += stddev_total
	totals["_count"] += 1
for computer_type in kComputerTypes:
	if computer_type.startswith('causal'):
		computer_words = "Causal"
	elif computer_type.startswith('orig'):
		computer_words= "Detections"
	if kJustSMRT and not computer_type.endswith("smrt"):
		continue
	fluentsN = totals["_count"]
	stddev_action = totals[computer_type]['stddev_action'] / fluentsN
	stddev_fluent = totals[computer_type]['stddev_fluent'] / fluentsN
	stddev_total = totals[computer_type]['stddev_total'] / fluentsN
	if kLaTeX:
		#print(" & ".join(str(x) for x in ("ALL",computer_words,diff_action/fluentsN,diff_fluent/fluentsN,diff_total/fluentsN))+' \\\\')
		raise "TODO"
	else:
		print("\t".join(str(x) for x in ("AVG",fluentsN,computer_type,stddev_action,stddev_fluent,stddev_total)))
if kDebugOn:
	print exceptions
