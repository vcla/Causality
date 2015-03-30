# used with analyze_results.R (which is tied to analyze_results.go somehow?)
fluentList = ['screen', 'door', 'light']
fluentComputerTypes = ['causalgrammar', 'origdata', 'origsmrt', 'causalsmrt']#, 'fluent']
actionList = ['screen_action', 'door_action', 'light_action']
actionComputerTypes = ['causalgrammar', 'origdata', 'origsmrt', 'causalsmrt']#, 'action']
dbcsv = 'results/cvpr_db_results.csv' # TODO: R < analyze_results.R --vanilla to run mingtians code to toss the DB results together
thresh = 50

def readMingtiansDBCompilation(dbcsv, oject, computerType):
	# cup,cvprdbresults/screen47water8phone18@1952,amy,more,0
	# object,exampleAndTime,human,fluentValue,humanAssignment
	f = open(dbcsv, 'r')
	ojectDict = {}
	for line in f:
		line = line.strip().split(',')
		if line[0] == oject:
			# then we have an object we're looking for
			exampleNameAndTime = line[1].split("/")[1]
			humanName = line[2]
			fluentValue = line[3]
			assignedValue = line[4]
			if exampleNameAndTime not in ojectDict:
				ojectDict[exampleNameAndTime] = {}
			if humanName not in ojectDict[exampleNameAndTime]:
				ojectDict[exampleNameAndTime][humanName] = {}
			if fluentValue not in ojectDict[exampleNameAndTime][humanName]:
				ojectDict[exampleNameAndTime][humanName][fluentValue] = {}
			ojectDict[exampleNameAndTime][humanName][fluentValue] = assignedValue
	# now collect all the winners (closest results)
	winningPairs = {}
	tablesNeedingInvestigating = []  # TODO: MAJOR TODO...  some of the tables were created incorrectly (meaning they have the wrong column names).  need to investigate why, how many, any other issues? (like ardid tables upload to wrong ones?
	for example in ojectDict.keys():
		#print 'example: {}'.format(example)
		#print 'objectDict[example]: {}'.format(ojectDict[example])
		bestDistance = 100000
		try:
			computerResult = ojectDict[example][computerType]
			for tmpType in fluentComputerTypes:
				del ojectDict[example][tmpType]
		except KeyError:
			print 'Missing Result for {}: {}'.format(computerType, example) # there is no computer output for this one
			continue
		humans = ojectDict[example]
		#print 'humans: {}'.format(humans)
		for human in humans:
			#print 'human {}'.format(human)
			tmpDist = findDistanceBetweenTwoDictsOfNumbers(humans[human], computerResult)
			if tmpDist < bestDistance:
				bestDistance = tmpDist
				closestHuman = human
		try:
			winningPairs[example] = {'computer': computerResult, 'human': humans[closestHuman], 'distance': bestDistance}
		except KeyError:
			print '****** TABLE PROBABLY WRONG FOR {}******'.format(example) # same database issue listed in the MAJOR TODO above
			tablesNeedingInvestigating.append(example)
			continue
		#print bestDistance
	#import pprint
	#pp = pprint.PrettyPrinter(depth=6)
	#pp.pprint(winningPairs)
	#print winningPairs
	print '-----------------------------'
	print 'TABLES NEEDING INVESTIGATING: {}'.format(tablesNeedingInvestigating) # same database issue listed in the MAJOR TODO above
	print '-----------------------------'
	return winningPairs


# Entity: screen Instance: cvprdbresults/screen58@192 causalgrammar: map[on_off:0 on:0 off:100 off_on:0] NearestHuman: map[on:0 off:100 off_on:0 on_off:0]

# obsolete function -- not using mingtian's go code anymore
def findDistanceGivenLineOfGoOutput(line, oject, computerType):
	line = line.strip().split('[')
	if len(line) > 3:
		raise Exception('line had more than expected parts')
	wordyChunk = line[0]
	wordyChunk = wordyChunk.split(' ')
	ojectInLine = wordyChunk[1]
	computerTypeInLine = wordyChunk[4].split(':')[0]
	if ojectInLine == oject and computerTypeInLine == computerType:
		computerChunk = line[1]
		humanChunk = line[2]
		humanResult = getSingleVectorResultAsDict(humanChunk)
		computerResult = getSingleVectorResultAsDict(computerChunk)
		dist = findDistanceBetweenTwoDictsOfNumbers(humanResult, computerResult)
	else:
		dist = 10000  # large so definitely not a hit
	return dist

# obsolete function -- not using mingtian's go code anymore
def getSingleVectorResultAsDict(outputChunk):
	outputChunk = outputChunk.split(']')[0]
	outputChunk = outputChunk.split(' ')
	dictOfResult = {}
	for individualResult in outputChunk:
		tmp = individualResult.split(':')
		dictOfResult[tmp[0]] = tmp[1]
	return dictOfResult

def findDistanceBetweenTwoDictsOfNumbers(humanResult, computerResult):
	dist = 0
	for key in humanResult.keys():
		dist += abs(int(humanResult[key]) - int(computerResult[key]))
	# TODO: should i be taking average, or aggregating over all timestamps for an example?
	#print dist
	return dist

# TODO: what the hell is a false positive?  what limits me from taking threshold to 100000?!?!?
def findOptimalThreshold(lines, ojects, computerType): # untested
	for thresh in range(1, 400):
		percent = tallyHitsForSingleComputerType(lines, oject, computerType, thresh)

def tallyHitsForWinningPairs(winningPairs, thresh):
	hits = 0
	count = 0
	PRDict = {}
	print 'length of winningPairs: {}'.format(len(winningPairs))
	for winningPair in winningPairs:
		#print winningPair
		#print winningPairs[winningPair]['distance']
		output = lookupHits(winningPairs[winningPair], thresh)
		if not output['ambiguous']:
			for key in output.keys():
				if key is not 'ambiguous':
					if key not in PRDict.keys():
						PRDict[key] = {'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0}
					humanScore = output[key]['human']
					computerScore = output[key]['computer']
					PRDict[key]['tp'] += (humanScore and computerScore)
					PRDict[key]['fp'] += (computerScore and not humanScore)
					PRDict[key]['tn'] += (not humanScore and not computerScore)
					PRDict[key]['fn'] += (not computerScore and humanScore)
		#print '----PR DICT'
		#print PRDict
		if winningPairs[winningPair]['distance'] <= thresh:
			# then it's possibly a hit -- TODO -- more sophisticated way of measuring "hit"
			hits += 1
		count += 1
		#print hits
	print 'hits: {}   count: {} '.format(hits, count)
	print '--PR DICT--'
	print PRDict
	percent = hits/count
	return percent

def lookupHits(winningPair,thresh):
	actionHitKeys = ['act_pushbutton', 'act_opened', 'act_closed', 'act_mousekeyboard'] # TODO: might need to worry if a "non-hit" key is in hit keys
	fluentHitKeys = ['off_on', 'on_off', 'open_closed', 'closed_open']
	hitKeys = actionHitKeys + fluentHitKeys
	#import pprint
	#pp = pprint.PrettyPrinter(depth=6)
	#pp.pprint(winningPair)
	#print hitKeys
	#print 'thresh: {}'.format(thresh)
	output = {'ambiguous': 1}
	for key in winningPair['computer'].keys():
		#print key
		judgments = {'human': 0, 'computer': 0}
		if int(winningPair['human'][key]) > thresh:
			# then human had higher than threshold assigned to something -- not ambiguous.  TODO later: incorporate matching on ambiguity
			output['ambiguous'] = 0
		if key in hitKeys:
			# then we need to record both judgments (for sorting out false positive/etcs)
			#print key
			if int(winningPair['human'][key]) > thresh:
				#print winningPair['human'][key]
				judgments['human'] = 1
			if int(winningPair['computer'][key]) > thresh:
				#print winningPair['computer'][key]
				judgments['computer'] = 1
			output[key] = judgments
		#print judgments
	#pp.pprint(output)
	#raw_input()
	return output

def tallyHitsForAllComputerTypes(thresh): # untested
	# go through the fluents
	for oject in fluentList:
		for computerType in fluentComputerTypes:
			winningPairs = readMingtiansDBCompilation(dbcsv, oject, computerType)
			print 'COMPUTER: {}    OBJECT: {}'.format(computerType,oject)
			tallyHitsForWinningPairs(winningPairs, thresh)
		#raw_input()
	# go through the actions
	for oject in actionList:
		for computerType in actionComputerTypes:
			winningPairs = readMingtiansDBCompilation(dbcsv, oject, computerType)
			print 'COMPUTER: {}    OBJECT: {}'.format(computerType,oject)
			tallyHitsForWinningPairs(winningPairs, thresh)

#readMingtiansDBCompilation(dbcsv, 'door', 'causalgrammar')
#readMingtiansDBCompilation(dbcsv, 'screen', 'causalgrammar')
#readMingtiansDBCompilation(dbcsv, 'light', 'causalgrammar')
#readMingtiansDBCompilation(dbcsv, 'light_action', 'causalgrammar')
#readMingtiansDBCompilation(dbcsv, 'door_action', 'causalgrammar')
#readMingtiansDBCompilation(dbcsv, 'screen_action', 'causalgrammar')

tallyHitsForAllComputerTypes(thresh)

#line = 'Entity: screen Instance: cvprdbresults/screen58@192 causalgrammar: map[on_off:0 on:0 off:100 off_on:0] NearestHuman: map[on:0 off:100 off_on:0 on_off:0]'
#findDistanceGivenLineOfGoOutput(line, 'screen', 'causalgrammar')
#tallyHitsForSingleComputerType([line,], 'screen', 'causalgrammar', 10)
