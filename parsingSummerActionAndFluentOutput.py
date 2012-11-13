fluent_dir = "CVPR2012_fluent_result/"
fluent_types = ["door_open_closed", "door_closed_open", "light_on_off", "light_off_on", "screen_on_off", "screen_off_on"]
objectInitials = ["d", "l", "t", "s", "w", "p", "e"]

import math

# takes Bruce's detections
def readFluentResults(exampleName):
	#fluent_parses = {"initial":{}}
	#initial_fluents = fluent_parses['initial']
	fluent_parses = {}
	for fluent_type in fluent_types:
		[fluent, old_value, new_value] = fluent_type.split("_")
		fluent_file = fluent_dir + fluent_type + "_fluent_results.txt"
		#print("READING {}".format(fluent_file))
		#print("opening {}".format(fluent_file))
		#print("looking for {}".format(exampleName))
		thefile = open(fluent_file, 'r')
		results = thefile.readlines()
		i = 0
		resultsN = len(results)
		while i < resultsN:
			result = results[i].strip()
			skip = int(results[i+1].strip())
			if result == exampleName:
				#print "FOUND EXAMPLE NAME {} on line {} with {} results".format(result,i,skip)
				for j in range(i+2,i+2+skip):
					# then there are detections, and this is one of them
					[start_frame, end_frame, probability] = results[j].strip().split(" ");
					start_frame = int(start_frame)
					end_frame = int(end_frame)
					probability = float(probability)
					# TODO: we were dealing with "instantaneous" changes before.  which frame do i take?  or average????
					frame_number = min(start_frame + 4, int(round((start_frame + end_frame)/2))) # TODO: maybe???!?!? and put buffer around it on the other side???
					if frame_number not in fluent_parses:
						fluent_parses[frame_number] = {}
					frame = fluent_parses[frame_number]
					# TODO: no idea how to handle what energy becomes/ how to put in file (loooking at import_xml in causal_grammar.py)...  like why does new value == 0 go to zero probability?
					if new_value in ["open", "on"]:
						fluent_value = -math.log(probability)
					elif new_value in ["closed", "off"]:
						fluent_value = -math.log(1-probability)
					if fluent in frame:
						# if we've already got a value, let's see which one is "more" likely (further from .5)
						old_value = frame[fluent]
						old_diff = abs(.5 - math.exp(-old_value))
						new_diff = abs(.5 - math.exp(-fluent_value))
						if new_diff > old_diff:
							frame[fluent] = fluent_value
					else:
						frame[fluent] = fluent_value
					#if fluent not in initial_fluents:
					#	if new_value in ["open", "on"]:
					#		prev_value = -math.log(1-probability)
					#	elif new_value in ["closed", "off"]:
					#		prev_value = -math.log(probability)
					#	initial_fluents[fluent] = prev_value
					#	print("{}: {} -> {}".format(frame_number,prev_value,fluent_value))
					# initial_fluents[fluent] = .001 # 500 # .301 # let's try probability 1/5 for this for now
				break
			else:
				i += skip + 2
		if i == resultsN:
			print "BUMMER; not found. Try more dinosaur."
		thefile.close()
	return fluent_parses

# dict keys are frame numbers
# frames are only reported when a fluent changes, and only for the fluent(s) that changed; fluents are considered to be on or off ("light" is treated as "light_on", and then "light_off" is calculated from that internally, for instance)

def returnExampleNames():
	# each fluent detection file seems to contain all examples, so only need one...
	fluent_file = fluent_dir + fluent_types[0] + "_fluent_results.txt"
	results = open(fluent_file, 'r');
	example_names = []
	for line in results:
		line = line.strip()
		if line[0] in objectInitials:
			example_names.append(line)
	results.close()
	return example_names


def add_event(events, agent, frame, name, energy):
	if frame not in events:
		events[frame] = {}
	frame = events[frame]
	frame[name] = {'energy': energy, 'agent': agent}

def convertActionNumberToText(actionNumber):
	pass


# BELOW WAS FOR MINGTIAN'S CODE FOR SMOOTHING PING'S RESULTS WITH THE POTTS MODEL
# dict keys are frame numbers
# frames are only reported when an event begins
# events have energy and agents
# it is assumed that the same event /can/ happen multiple times at the same time (multiple people talking on different cell phones, for example)
"""
def readActionResults(exampleName, action_dir, resultNumber):
	# resultNumber is 1 to ?.  represents the nth highest probability result
	temporal_parses = {}
	#TODO: issue...  what about activities that are "on going" like using the computer?  maybe this was why i removed the computer from nips experiments?
	actionFile = action_dir + "/" + exampleName + ".txt"
	theFile = open(actionFile, 'r')
	results = theFile.readlines()
	[hashMark, title, exampleStartFrame, dash, exampleEndFrame] = results[1].strip().split(" ")
	exampleStartFrame = int(exampleStartFrame)
	exampleEndFrame = int(exampleEndFrame)
	# we skip the first 4 lines, the next 10 are highest probability outputs
	try:
		result = results[3+resultNumber].strip().split(" ")
	except IndexError:
		print "you requested a result number that exceeds the number available"
		raise
 # if error on this line, not enough outs
	energy = float(result.pop(0))
	agent = ("a1",) # TODO: unsure of data type for agent -- see form below of temporal_parses
	# 455: { "E1_END": {"energy": .916, "agent": ("uuid3") } },
	effectiveFrame = exampleStartFrame
	for frame in result:
		action_name = frame[0]
		try:
			if action_name != currentAction:
				# then this is a new Action, start a new action/complete the old one
				add_event(temporal_parses, agent, (effectiveFrame-1), "{}_END".format(currentAction),energy)
				currentAction = action_name
				add_event(temporal_parses, agent, effectiveFrame, "{}_START".format(currentAction),energy)
		except NameError:
			# then need to create first action
			currentAction = action_name
			add_event(temporal_parses, agent, effectiveFrame, "{}_START".format(currentAction),energy)
		effectiveFrame = effectiveFrame + 1
	# then complete the last one
	add_event(temporal_parses, agent, (effectiveFrame-1), "{}_END".format(currentAction),energy)
	theFile.close()
	import pprint
	pp = pprint.PrettyPrinter(depth=6)
	pp.pprint(temporal_parses)
	return temporal_parses
"""

def readActionResults(module):
	module = __import__(module,fromlist=['temporal_parses'])
	action_parses = module.temporal_parses[0]
	# we don't trust the action parses as much as they want us to
	for frame in action_parses:
		for action in action_parses[frame]:
			action_parses[frame][action]['energy'] = action_parses[frame][action]['energy'] # + 0.69 # + 0.69314718056;
	return action_parses

##########################


if __name__ == '__main__':
	#print returnExampleNames()
	readFluentResults('door_10_phone_14_light_1_screen_29_9406')
	#readActionResults('door_11_9406', 'CVPR2012_smoothed_action_detections', 10)
	#readActionResults('door_11_9406', 'CVPR2012_smoothed_action_detections', 12)
	readActionResults('CVPR2012_slidingwindow_action_detection.door_11_9406')
