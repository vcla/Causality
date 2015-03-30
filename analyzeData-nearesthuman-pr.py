#GOAL: for each video clip, find the best human and report how far off the causalgrammar and origdata are from them
#QUESTION: how should these costs aggregate across video clips?

import pprint
pp = pprint.PrettyPrinter(depth=6)

import os
import hashlib
kCSVDir = 'results/cvpr_db_results' # from the 'export' option in dealWithDBResults.py
kComputerTypes = ['origdata', 'origsmrt', 'causalgrammar', 'causalsmrt' ]

# note that "negative" action must be the last one specified for proper P/R and there must be only one "no action"
kFluentToFieldMapping = {
		#door_95_closed_open door_95_open_closed door_95_open door_95_closed
		#door_action_1_act_opened door_action_1_act_closed door_action_1_act_not_opened_closed
	"door": { "fluents": ["open","closed","open_closed","closed_open"], "actions": ["act_opened","act_closed","act_not_opened_closed"] },
		#light_95_off_on light_95_on_off light_95_on light_95_off
		#light_action_1_act_pushbutton light_action_1_act_no_pushbutton
	"light": { "fluents": ["on","off","on_off","off_on"], "actions": ["act_pushbutton","act_nopushbutton"] },
		#phone_2300_active phone_2300_off phone_2498_off_active phone_2498_active_off
		#phone_action_2300_act_received_call phone_action_2300_act_no_call
	"phone": { "fluents": ["active","off","off_active","active_off"], "actions": ["act_received_call","act_no_call"] },
		#ringer_2498_ring ringer_2498_no_ring
	"ringer": {"fluents": ["ring","no_ring"], "actions": [] },
		#screen_2300_off_on screen_2300_on_off screen_2300_on screen_2300_off
		#screen_action_1784_act_mousekeyboard screen_action_1784_act_no_mousekeyboard
	"screen": {"fluents": ["off_on","on_off","on","off"], "actions": ["act_mousekeyboard","act_no_mousekeyboard"]},
}

def findDistanceBetweenTwoVectors(A, B, fields, fluent):
	dist = 0
	for i in range(len(A)):
		if fields[i].startswith(fluent):
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
			dist += abs(Ai - Bi)
	return dist

def pr_from_hitsandmisses(hitsandmisses):
	# coming in as actions: TP, FP, TN, FN and fluents: TP, FP, TN, FN
	retval = {
		"actions": {},
		"fluents": {}
	}
	for key in retval:
		TP = float(hitsandmisses[key]["TP"])
		FP = float(hitsandmisses[key]["FP"])
		TN = float(hitsandmisses[key]["TN"])
		FN = float(hitsandmisses[key]["FN"])
		if TP + FP > 0:
			retval[key]["precision"] = TP / (TP + FP)
		else:
			retval[key]["precision"] = 0
		if TP + FN > 0:
			retval[key]["recall"] =  TP / (TP + FN)
		else:
			retval[key]["recall"] =  0
		if TP + FP + FN > 0:
			retval[key]["f1score"] = 2 * TP / (2 * TP + FP + FN)
		else:
			retval[key]["f1score"] = 0
	return retval

def getHitsAndMisses(truth, test, fields, filterfluent):
	retval = {
		"actions": {"TP":0,"FP":0,"TN":0,"FN":0},
		"fluents": {"TP":0,"FP":0,"TN":0,"FN":0}
	}
	keyframes = set()
	for field in fields:
		fluent, frame, _ = field.split("_",2)
		if frame == "action":
			fluent, _, frame, _ = field.split("_",3)
		keyframes.add(frame)
	truth_lookup = {}
	test_lookup = {}
	for i in range(len(fields)):
		field = fields[i]
		truth_lookup[field] = truth[i]
		test_lookup[field] = test[i]
	for frame in keyframes:
		for fluent in kFluentToFieldMapping:
			if not filterfluent or filterfluent == fluent:
				fluent_options = kFluentToFieldMapping[fluent]['fluents']
				action_options = kFluentToFieldMapping[fluent]['actions']
				real_value = ""
				#FLUENTS
				for option in fluent_options:
					column = "{}_{}_{}".format(fluent,frame,option)
					if not column in truth_lookup:
						continue
					if int(truth_lookup[column]) > 50:
						real_value = option
						break
				for option in fluent_options:
					column = "{}_{}_{}".format(fluent,frame,option)
					if not column in truth_lookup:
						continue
					testvalue = 0 if test_lookup[column] == '' else int(test_lookup[column])
					truthvalue = 0 if truth_lookup[column] == '' else int(truth_lookup[column])
					if option == real_value:
						if testvalue <= 50:
							retval["fluents"]["FN"] += 1
						else:
							retval["fluents"]["TP"] += 1
							if testvalue > 100:
								# + 49 to deal with not-rounding and that we're using 50 as threshold for yea/nay
								retval["fluents"]["FP"] += int(((testvalue-100)+49) / 100)
					else:
						if testvalue > 50:
							# + 49 to deal with not-rounding and that we're using 50 as threshold for yea/nay
							retval["fluents"]["FP"] += int((testvalue+49) / 100)
				#ACTIONS
				last_option = action_options[-1:]
				for option in action_options:
					#phone_action_2300_act_received_call phone_action_2300_act_no_call
					column = "{}_action_{}_{}".format(fluent,frame,option)
					if not column in truth_lookup:
						continue
					testvalue = 0 if test_lookup[column] == '' else int(test_lookup[column])
					truthvalue = 0 if truth_lookup[column] == '' else int(truth_lookup[column])
					truth_on = truthvalue > 50
					test_on = testvalue > 50
					if option != last_option:
						if truth_on and test_on:
							# + 49 to deal with not-rounding and that we're using 50 as threshold for yea/nay
							retval["actions"]["TP"] += 1
							if testvalue > 100:
								retval["actions"]["FP"] += int(((testvalue-100)+49) / 100)
						elif truth_on and not test_on:
							retval["actions"]["FN"] += 1
						elif not truth_on and test_on:
							retval["actions"]["FP"] += int((testvalue+49) / 100)
						else:
							# truth_off and test_off: so far so good
							pass
					else: # option == last_option, which is "no action", so things are a little different
						if truth_on and test_on:
							retval["actions"]["TN"] += 1
						elif truth_on and not test_on:
							pass # this should have been handled elsewhere
						elif not truth_on and test_on:
							# 'negative' detections really don't make any sense stacking-wise....
							retval["actions"]["FN"] += 1
						else:
							#truth_off and test_off: good, handled elsewhere
							pass
	return retval


## for each file in our csvs directory, find the smallest "human" distance for each "computer" vector
print("FILENAME\tFLUENT\tHASH\tORIGDATA\tORIGSMRT\tCAUSALGRAMMAR\tCAUSALSMRT\tORIGHUMANS\tSMRTHUMANS\tCAUSALHUMANS\tCAUSSMRTHUMANS")
exceptions = []
kAllFluentsConstant="all"
fluentDiffSums = {}
PR = {}

for filename in os.listdir (kCSVDir):
	if filename.endswith(".csv"):
		with open(os.path.join(kCSVDir,filename),"r") as csv:
			try:
				header = csv.readline()
				_, fields = header.rstrip().split(",",1)
				fields = fields.rsplit(",",2)[0].split(",")
				fluents = set()
				for field in fields:
					fluent = field.split("_",1)[0]
					if fluent not in ("ringer",):
						fluents.add(fluent)
				fluents.add("") # empty string ~ all fluents
				lines = csv.readlines()
				example = filename[:-3]
				PR[example] = {}
				for fluent in fluents:
					humans = {}
					computers = {}
					PR[example][fluent if fluent else "all"] = {}
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
					if not 'origsmrt' in computers:
						raise Exception("NO ORIGSMRT FOR {}".format(filename))
					if not 'causalgrammar' in computers:
						raise Exception("NO CAUSALGRAMMAR FOR {}".format(filename))
					if not 'causalsmrt' in computers:
						raise Exception("NO CAUSALSMRT FOR {}".format(filename))
					humansN = len(humans)
					bestscores = {}
					besthumans = {}
					hitsandmisses = {}
					for computerType in kComputerTypes:
						bestscores[computerType] = 0
						besthumans[computerType] = []
						for human in humans:
							currentscore = findDistanceBetweenTwoVectors(computers[computerType],humans[human],fields,fluent)
							if not besthumans[computerType] or currentscore < bestscores[computerType]:
								besthumans[computerType] = [human]
								bestscores[computerType] = currentscore
								hitsandmisses[computerType] = getHitsAndMisses(humans[human], computers[computerType], fields, fluent)
								PR[example][fluent if fluent else "all"][computerType] = pr_from_hitsandmisses(hitsandmisses[computerType])
							elif bestscores[computerType] == currentscore:
								besthumans[computerType].append(human)
					## FILENAME, FLUENT, HASH, ORIGDATA SCORE, ORIGSMRT SCORE, CAUSALGRAMMAR SCORE, ORIGDATA HUMANS, ORIGSMRT HUMANS, CAUSALGRAMMAR HUMANS
					exampleName, room = filename.rsplit('.',1)
					exampleNameForDB = exampleName.replace("_","")
					fluent = fluent if fluent else kAllFluentsConstant
					print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(filename,fluent,hashlib.md5(exampleNameForDB).hexdigest(),bestscores['origdata'], bestscores['origsmrt'], bestscores['causalgrammar'], bestscores['causalsmrt'], besthumans['origdata'], besthumans['origsmrt'], besthumans['causalgrammar'], besthumans['causalsmrt']))
					print("HITS AND MISSES: ")
					pp.pprint(hitsandmisses)
					# summing for later
					if not fluent in fluentDiffSums:
						fluentDiffSums[fluent] = {'origdata': [0, 0], 'origsmrt': [0, 0], 'causalgrammar': [0, 0], 'causalsmrt': [0, 0], '_count': 0}
					fluentDiffSums[fluent]['_count'] += 1
					for computer in kComputerTypes:
						fluentDiffSums[fluent][computer][0] += bestscores[computer]
						fluentDiffSums[fluent][computer][1] = "{} avg".format(fluentDiffSums[fluent][computer][0] / fluentDiffSums[fluent]['_count'])
			except KeyError as hmm:
				import traceback
				print traceback.format_exc()
			except ValueError as hmm:
				import traceback
				print traceback.format_exc()
			except NameError as hmm:
				import traceback
				print traceback.format_exc()
			except ZeroDivisionError as hmm:
				import traceback
				print traceback.format_exc()
			except TypeError as hmm:
				import traceback
				print traceback.format_exc()
			except Exception as foo:
				exceptions.append(foo)

#if not N:
#	N = 1

print("-\t-\t-\t-\t-\t-\t-\t-")
#print("{}\t{}\t{}\t{}\t{}".format("AVERAGE",total_origdata_score / N,total_causalgrammar_score / N,"",""))
pp.pprint(fluentDiffSums)

pp.pprint(PR)

PR_SUMMARY = {}
"""
 'screen_9_phone_7.': {'all': {'causalgrammar': {'actions': {'f1score': 0.2222222222222222,
                                                             'precision': 0.2,
                                                             'recall': 0.25},
                                                 'fluents': {'f1score': 0.2,
                                                             'precision': 0.25,
                                                             'recall': 0.16666666666666666}},
"""
for example in PR:
	for fluent in PR[example]:
		if not fluent in PR_SUMMARY:
			PR_SUMMARY[fluent] = {}
		for computertype in PR[example][fluent]:
			if not computertype in PR_SUMMARY[fluent]:
				PR_SUMMARY[fluent][computertype] = {}
			for subtype in PR[example][fluent][computertype]:
				if not subtype in PR_SUMMARY[fluent][computertype]:
					PR_SUMMARY[fluent][computertype][subtype] = {'f1score_sum':0, 'precision_sum':0, 'recall_sum':0, 'N': 0, 'f1score':0, 'precision':0, 'recall':0 }
				PR_SUMMARY[fluent][computertype][subtype]['f1score_sum'] += PR[example][fluent][computertype][subtype]['f1score']
				PR_SUMMARY[fluent][computertype][subtype]['precision_sum'] += PR[example][fluent][computertype][subtype]['precision']
				PR_SUMMARY[fluent][computertype][subtype]['recall_sum'] += PR[example][fluent][computertype][subtype]['recall']
				PR_SUMMARY[fluent][computertype][subtype]['N'] += 1
				PR_SUMMARY[fluent][computertype][subtype]['f1score'] = PR_SUMMARY[fluent][computertype][subtype]['f1score_sum'] / PR_SUMMARY[fluent][computertype][subtype]['N']
				PR_SUMMARY[fluent][computertype][subtype]['precision'] = PR_SUMMARY[fluent][computertype][subtype]['precision_sum'] / PR_SUMMARY[fluent][computertype][subtype]['N']
				PR_SUMMARY[fluent][computertype][subtype]['recall'] = PR_SUMMARY[fluent][computertype][subtype]['recall_sum'] / PR_SUMMARY[fluent][computertype][subtype]['N']
		
print("-\t-\t-\t-\t-\t-\t-\t-")
print("-\t-\t-\t-\t-\t-\t-\t-")

#pp.pprint(PR_SUMMARY)
for fluent in PR_SUMMARY:
	for computertype in PR_SUMMARY[fluent]:
		#if computertype == "origsmrt":
		#	continue
		for foo in ["actions","fluents"]:
			print("{} {} {}: P: {}, R: {}".format(computertype, fluent, foo, PR_SUMMARY[fluent][computertype][foo]["precision"], PR_SUMMARY[fluent][computertype][foo]["recall"]))
#print exceptions
	print("-\t-\t-\t-\t-\t-\t-\t-")
