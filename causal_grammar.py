"""
causal grammar parser and helper functions
"""
# TODO: filter out "competing" parse trees below thresh

import itertools
import math # for log, etc
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import copy
from collections import defaultdict

"""some helper functions"""
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

def flatten(listOfLists):
    "Flatten one level of nesting"
    return itertools.chain.from_iterable(listOfLists)

def split_fluents_into_windows(fluents):
    splits = list()
    kFluentOverlap = 10
    cluster = list()
    prev_frame = -kFluentOverlap
    for frame in sorted(fluents):
        if kFluentOverlap < (frame - prev_frame):
            splits.append(cluster)
            cluster = list()
        prev_frame = frame
        cluster.append(frame)
    splits.append(cluster)
    return splits[1:]

TYPE_FLUENT = "fluent"
TYPE_ACTION = "action"

kUnknownEnergy = 8#0.7 # TODO: may want to tune
kUnlikelyEnergy = 10.0 # TODO: may want to tune
kZeroProbabilityEnergy = 10.0 # TODO: may want to tune: 10.0 = very low
kNonActionPenaltyEnergy = 0. # TODO: need to validate; kind of matches a penalty energy in readActionResults of parsingSummerActionAndFluentOutput

# these are used to keep something that's flipping "around" 50% to not keep triggering fluent changes TODO: no they're not. but they are used in dealWithDbResults for posting "certain" results to the database... and they're passed into the main causal_grammar fn as fluent_on_probability and fluent_off_probability
kFluentThresholdOnEnergy = 0.36 # TODO: may want to tune: 0.36 = 0.7 probability
kFluentThresholdOffEnergy = 1.2 # TODO: may want to tune: 1.2 = 0.3 probability
kReportingThresholdEnergy = 0.5 # TODO: may want to tune
kDefaultEventTimeout = 10 # shouldn't need to tune because this should be tuned in grammar
kFilterNonEventTriggeredParseTimeouts = False # what the uber-long variable name implies
kDebugEnergies = False # if true, print out fluent current/prev and event energies when completing a parse tree

kFluentStatusUnknown = 1
kFluentStatusOn = 2
kFluentStatusOff = 3

def get_simplified_forest_for_example(forest, example):
	splits = example.split("_")
	fluents = splits[::2]
	if len(splits) % 2:
		fluents = fluents[:-1]
	#TODO: pulling in "fluent_extensions" is a hack needed for summerdata, we should figure out how to generalize or remove.... (water/waterstream root nodes specified at the "file name" level also want their "thirst_*" and "cup_*" fluents to be pulled in, don't oversimplify!)
	import summerdata
	more_fluents = []
	for fluent in fluents:
		if fluent in summerdata.fluent_extensions:
			more_fluents = more_fluents + summerdata.fluent_extensions[fluent]
	fluents = set(fluents + more_fluents) #set to make terms distinct just in case
	return get_simplified_forest_for_fluents(forest,fluents)

def get_simplified_forest_for_fluents(forest, fluents):
	#TODO: does not work with phone ~ PHONE_ACTIVE ... fluent = "PHONE_ACTIVE" ... need more universal munging or to make our data uniform throughout
	simplified_forest = []
	for root in forest:
		found = False
		for fluent in fluents:
			if root['symbol'].startswith(fluent + "_"):
				simplified_forest.append(root)
				break
	return simplified_forest

def sequence_generator():
	i = 0
	while 1:
		yield i
		i += 1

actionid_generator = sequence_generator()
fluentid_generator = sequence_generator()
branchid_generator = sequence_generator()

def generate_causal_forest_from_abbreviated_forest(abbreviated_forest):
	forest = []
	for child in abbreviated_forest:
		tree = {}
		if child[0]:
			tree['node_type'] = child[0]
		if child[1]:
			tree['symbol_type'] = child[1]
			if tree['symbol_type'] in ('jump','timer',):
				tree['alternate'] = child[6]
		if child[2]:
			tree['symbol'] = child[2]
		if child[3]:
			tree['probability'] = child[3]
		if child[4]:
			tree['timeout'] = child[4]
		if child[5]:
			tree['children'] = generate_causal_forest_from_abbreviated_forest(child[5])
			
		forest.append(tree)
	return forest

def import_summerdata(exampleName,actionDirectory):
	import parsingSummerActionAndFluentOutput
	fluent_parses = parsingSummerActionAndFluentOutput.readFluentResults(exampleName)
	action_parses = parsingSummerActionAndFluentOutput.readActionResults("{}.{}".format(actionDirectory,exampleName))
	#import pprint
	#pp = pprint.PrettyPrinter(depth=6)
	#pp.pprint(action_parses)
	#pp.pprint(fluent_parses)
	return [fluent_parses, action_parses]

def import_xml(filename):
	fluent_parses = {'initial':{}}
	action_parses = {}
	document = minidom.parse(filename)
	interpretation_chunk = document.getElementsByTagName('interpretation')[0]
	interpretation_probability = float(interpretation_chunk.attributes['probability'].nodeValue)
	interpretation_energy = probability_to_energy(interpretation_probability)
	action_chunk = document.getElementsByTagName('temporal')[0]
	initial_fluents = fluent_parses['initial'];
	for fluent_change in action_chunk.getElementsByTagName('fluent_change'):
		fluent_attributes = fluent_change.attributes;
		frame_number = int(fluent_attributes['frame'].nodeValue)
		fluent = fluent_attributes['fluent'].nodeValue
		if frame_number not in fluent_parses:
			fluent_parses[frame_number] = {}
		frame = fluent_parses[frame_number]
		new_value = fluent_attributes['new_value'].nodeValue
		if new_value == 1 or new_value == '1':
			new_value = interpretation_energy
		elif new_value == 0 or new_value == '0':
			new_value = kZeroProbabilityEnergy
		else:
			raise Exception("new value {} not 1 or 0 for frame {}: {}".format(fluent, frame_number, new_value))
		if fluent not in initial_fluents:
			old_value = fluent_attributes['old_value'].nodeValue
			if old_value == 1 or old_value == '1':
				old_value = interpretation_energy
			elif old_value == 0 or old_value == '0':
				old_value = kZeroProbabilityEnergy
			else:
				raise Exception("old value {} not 1 or 0 for frame {}: {}".format(fluent, frame_number, old_value))
			initial_fluents[fluent] = old_value
		frame[fluent] = new_value
	def add_event(events, agent, frame, name, energy):
		if frame not in events:
			events[frame] = {}
		frame = events[frame]
		frame[name] = {'energy': energy, 'agent': agent}
	for event in action_chunk.getElementsByTagName('event'):
		# all 'action' agents are pulled in as the event agents; actions have one and only one agent
		# events (and actions) are now split into _START and _END
		actions = event.getElementsByTagName('action')
		event_attributes = event.attributes;
		event_start_frame = int(event_attributes['begin_frame'].nodeValue)
		event_end_frame = int(event_attributes['end_frame'].nodeValue)
		event_name = event_attributes['name'].nodeValue
		event_agents = []
		for action in actions:
			action_attributes = action.attributes
			action_start_frame = int(action_attributes['begin_frame'].nodeValue)
			action_end_frame = int(action_attributes['end_frame'].nodeValue)
			action_name = action_attributes['name'].nodeValue
			action_agent = [action_attributes['agent'].nodeValue]
			event_agents.append(action_agent[0])
			add_event(action_parses,action_agent,action_start_frame,"{}_START".format(action_name),interpretation_energy)
			add_event(action_parses,action_agent,action_end_frame,"{}_END".format(action_name),interpretation_energy)
		add_event(action_parses,event_agents,event_start_frame,"{}_START".format(event_name),interpretation_energy)
		add_event(action_parses,event_agents,event_end_frame,"{}_END".format(event_name),interpretation_energy)
	return [fluent_parses,action_parses]

def import_csv(filename, fluents, events):
	raise Exception("THIS IS OUT OF DATE: IT HAS NOT BEEN UPDATED TO HAVE _START AND _END AT THE VERY LEAST")
	fluent_parses = {}
	action_parses = {}
	with open(filename,'r') as file:
		# read the first line as keys
		csv_keys = map(lambda k: k.strip(), file.readline().strip().split(","))
		for fluent in fluents:
			fluents[fluent] = { "to": fluents[fluent], "column": csv_keys.index(fluent) }
		for event in events:
			events[event] = { "to": events[event], "column": csv_keys.index(event) }
		agent = csv_keys.index("Agent")
		for line in file:
			csv_row = map(lambda k: k.strip(), line.strip().split(","))
			frame = int(csv_row[0])
			frame_agent = csv_row[agent]
			for fluent in fluents:
				on_value = float(csv_row[fluents[fluent]['column']])
				if "value" not in fluents[fluent] or fluents[fluent]["value"] != on_value:
					fluents[fluent]["value"] = on_value
					to = fluents[fluent]['to']
					if on_value == 1:
						on_value = 0.0
					elif on_value == 0:
						on_value = kZeroProbabilityEnergy
					else:
						raise Exception("{} not 1 or 0 for frame {}: {}".format(fluent, frame, on_value))
					if frame not in fluent_parses:
						fluent_parses[frame] = {}
					fluent_parses[frame][to] = on_value
			for event in events:
				trigger = float(csv_row[events[event]['column']])
				if trigger == 1:
					to = events[event]['to']
					if frame not in action_parses:
						action_parses[frame] = {}
					action_parses[frame][to] = {"energy": 0.0, "agent": frame_agent}
	return [fluent_parses,action_parses]

def hr():
	print("---------------------------------")

# TODO: a given event is assumed to have the same timeout everywhere in the grammar
def get_event_timeouts(forest):
	events = {}
	for tree in forest:
		if "children" in tree:
			child_timeouts = get_event_timeouts(tree["children"])
			for key in child_timeouts:
				events[key] = int(child_timeouts[key])
		if "symbol_type" in tree:
			if tree["symbol_type"] in ("event","nonevent",):
				if "timeout" in tree:
					events[tree["symbol"]] = int(tree["timeout"])
				else:
					events[tree["symbol"]] = int(kDefaultTimeout)
	return events

def get_fluent_and_event_keys_we_care_about(forest):
	fluents = set()
	events = set()
	for tree in forest:
		if "children" in tree:
			child_keys = get_fluent_and_event_keys_we_care_about(tree["children"])
			fluents.update(child_keys['fluents'])
			events.update(child_keys['events'])
		if "symbol_type" in tree:
			if tree["symbol_type"] in ("fluent","prev_fluent"):
				fluents.add(tree["symbol"])
			elif tree["symbol_type"] in ("event","nonevent"):
				events.add(tree["symbol"])
	return { "fluents": fluents, "events": events }

# filters "changes" for just the fluents and events we care about
# "changes" dict is changed by this function as python is always pass-by-reference
def filter_changes(changes, keys_in_grammar):
	keys_for_filtering = []
	for key in keys_in_grammar:
		# print("testing: {}".format(key))
		if "_" in key:
			prefix, postfix = key.rsplit("_",1)
			if postfix in ("on","off"):
				keys_for_filtering.append(prefix)
				continue
		keys_for_filtering.append(key)
	keys_for_filtering = set(keys_for_filtering)
	# print("KEYS FOR FILTERING: {}".format(keys_for_filtering))
	for x in [x for x in changes.keys() if x not in keys_for_filtering]:
		changes.pop(x)

# returns a forest where each option is a different parse. the parses have the same format as trees (but or-nodes now only have one option selected).
def generate_parses(causal_tree):
	node_type = causal_tree["node_type"]
	if "children" not in causal_tree:
		return (causal_tree,)
	partial_causal_parses = []
	# make a copy of the current node, minus the children (so we're keeping symbol_type, symbol, energy, node_type, etc)
	current_node = causal_tree.copy()
	current_node.pop("children")
	if node_type in ("or","root",):
		for child_node in causal_tree["children"]:
			for parse in generate_parses(child_node):
				current_node["children"] = (parse,)
				partial_causal_parses.append(current_node.copy())
	elif node_type in ("and",):
		# generate causal parses on each tree
		# build all cartesian products of those causal parses;
		# each cartesian product is a set of children for the and node, a separate partial parse graph to return
		child_parses = []
		for child_node in causal_tree["children"]:
			child_parses.append(generate_parses(child_node),)
		for product in itertools.product(*child_parses):
			current_node["children"] = product
			partial_causal_parses.append(current_node.copy())
	else:
		raise Exception("UNKNOWN NODE TYPE: {}".format(node_type))
	return partial_causal_parses

def energy_to_probability(energy):
	return math.exp(-energy)

def probability_to_energy(probability):
	if not type(probability) is int and not type(probability) is float:
		# TODO: what we've got here is a lambda, and if we're asking this, we're asking wrong
		return kZeroProbabilityEnergy
	if probability == 0:
		return kZeroProbabilityEnergy
	else:
		return -math.log(probability)

# changes '.*_on' to '.*_off' and vice versa
def invert_name(fluent):
	parts = fluent.split('_')
	if parts[-1] in ('on','off'):
		completion = {'on': 'off', 'off': 'on'}
	else:
		raise Exception("Unable to invert fluent '{}'".format(fluent))
	# which is more perverse? :)
	#return "{}_{}".format('_'.join(parts[:-1]),completion[parts[-1]])
	return '_'.join(parts[:-1] + [completion[parts[-1]],])

def calculate_energy(node, fluent_hash, event_hash):
	node_energy = 0.0
	if "probability" in node:
		# coming off a "root" or "or" node_type
		tmp_energy = probability_to_energy(node["probability"])
		if tmp_energy != kUnknownEnergy:
			node_energy += tmp_energy
	if "symbol_type" in node:
		if node["symbol_type"] in ("fluent",):
			tmp_energy = fluent_hash[node["symbol"]]["energy"]
			node_energy += tmp_energy
		elif node["symbol_type"] in ("prev_fluent",):
			tmp_energy = fluent_hash[node["symbol"]]["prev_energy"]
			node_energy += tmp_energy
		elif node["symbol_type"] in ("event",):
			tmp_energy = event_hash[node["symbol"]]["energy"]
			node_energy += tmp_energy
		elif node["symbol_type"] in ("nonevent",):
			tmp_energy = event_hash[node["symbol"]]["energy"]
			node_energy += probability_to_energy(1-energy_to_probability(tmp_energy)) + kNonActionPenaltyEnergy
		elif node["symbol_type"] in ("timer","jump",):
			# these are zero-probability events at this stage of evaluation
			#tmp_energy = event_hash[node["symbol"]]["energy"]
			#node_energy += probability_to_energy(1-energy_to_probability(tmp_energy))
			pass # TODO should this be dealt with in some other way?
		else:
			raise Exception("unhandled symbol_type '{}'".format(node['symbol_type']))
	if "children" in node:
		# "multiplies" child probabilities on all nodes (note to self: root nodes are always or nodes)
		# averaging on "and" nodes...need to work through that better
		# for now, it makes little difference as trees are neither deep nor wide
		average_ands = False
		if not average_ands or node["node_type"] in ("or","root",):
			# "multiplies" child probabilities on "or" nodes (root nodes are always or nodes)
			for child in node["children"]:
				child_energy = calculate_energy(child, fluent_hash, event_hash)
				node_energy += child_energy
		else:
			# "averages" over the "and" nodes
			child_energy = 0
			for child in node["children"]:
				child_energy += calculate_energy(child, fluent_hash, event_hash)
			node_energy += child_energy / len(node["children"])
	return node_energy

# TODO: this makes some very naiive assumptions about jumping--that the "paired" fluent(s) will all be met, and (others?)
def parse_can_jump_from(parse,prev_parse):
	# "timer" -> "jump"
	timer = get_symbol_matches_from_parse("timer",prev_parse)
	jump = get_symbol_matches_from_parse("jump",prev_parse)
	if timer and jump and timer["alternate"] == parse["symbol"] and timer["symbol"] == jump["symbol"]:
		return True
	return False

def get_symbol_matches_from_parse(symbol,parse):
	matches = []
	if "symbol_type" in parse:
		if parse["symbol_type"] == symbol:
			matches.append(parse)
	if "children" in parse:
		for child in parse["children"]:
			child_matches = get_symbol_matches_from_parse(symbol,child)
			matches += child_matches
	return matches

def parse_is_consistent_with_requirement(parse,requirement):
	if 'symbol_type' in parse:
		antithesis = invert_name(requirement)
		if parse['symbol_type'] in ('prev_fluent',) and parse['symbol'] == antithesis:
			return False
	if "children" in parse:
		for child in parse['children']:
			if not parse_is_consistent_with_requirement(child,requirement):
				return False
	return True

def make_tree_like_lisp(causal_tree):
	my_symbol = "?"
	if "symbol" in causal_tree:
		my_symbol = causal_tree["symbol"]
	if "children" not in causal_tree:
		if "symbol_type" in causal_tree and causal_tree["symbol_type"] in ("nonevent",):
			return "".join(("NOT ",my_symbol))
		else:
			return my_symbol
	simple_children = []
	for child in causal_tree["children"]:
		simple_children.append(make_tree_like_lisp(child))
	return (my_symbol, simple_children)

def print_current_energies(fluent_hash,event_hash):
	#fluent_energies = dict((k,k[v]) for k,v in fluent_hash.items() if v == "energy")
	fluent_energies = {}
	for fluent in fluent_hash:
		fluent_energies[fluent] = fluent_hash[fluent]["energy"]
	print("CURRENT FLUENT: {}".format(fluent_energies))
	event_energies = {}
	for event in event_hash:
		event_energies[event] = event_hash[event]["energy"]
	print("CURRENT EVENT: {}".format(event_energies))

def print_previous_energies(fluent_hash):
	fluent_energies = {}
	for fluent in fluent_hash:
		fluent_energies[fluent] = fluent_hash[fluent]["prev_energy"]
	print("PREV FLUENT: {}".format(fluent_energies))

# sets any events that haven't triggered within their timeout number of frames to kUnlikelyEnergy
# TODO: fix this to work on active_parses instead of event_hash
def clear_outdated_events(event_hash, event_timeouts, frame):
	for event in event_hash:
		if event_hash[event]["energy"] != kUnlikelyEnergy and frame - event_hash[event]["frame"] > event_timeouts[event]:
			# print("CLEARING EVENT {} @ {}".format(event,frame))
			event_hash[event]["frame"] = -1
			event_hash[event]["energy"] = kUnlikelyEnergy
			event_hash[event]["agent"] = False

# at all times there is a list of "currently active" parses, which includes a chain back to the beginning
# of events of the "best choice of transition" from each event (action, fluent, or timeout) to each previous
# COMPLETING a parse tree TODO wut? appends the frame
def complete_parse_tree(active_parse_tree, fluent_hash, event_hash, frame, completions, source):
	# we have a winner! let's show them what they've won, bob!
	energy = calculate_energy(active_parse_tree, fluent_hash, event_hash)
	fluent = active_parse_tree["symbol"]
	agents_responsible = []
	# if there are agents in the parse, print out who they were
	keys = get_fluent_and_event_keys_we_care_about((active_parse_tree,))
	for event in keys["events"]:
		agent = event_hash[event]["agent"]
		if agent:
			agents_responsible.append(agent,)
		if "_" in fluent:
			prefix, postfix = fluent.rsplit("_",1)
			if postfix in ("on","off",):
				fluent = prefix
		if fluent not in completions:
			completions[fluent] = {}
		completion = completions[fluent]
		if frame not in completion:
			completion[frame] = []
		completion_frame = completion[frame]
		completion_frame.append({"frame": frame, "fluent": fluent, "energy": energy, "parse": active_parse_tree, "agents": agents_responsible, "status": fluent_hash[active_parse_tree['symbol']]['energy'], 'source': source})
	#print("{}".format("\t".join([str(fluent),str(frame),"{:g}".format(energy),str(make_tree_like_lisp(active_parse_tree)),str(agents_responsible)])))
	#print("{} PARSE TREE {} COMPLETED at {}: energy({}) BY {}\n{}\n***{}***".format(fluent,active_parse_tree['id'],frame,energy,source,make_tree_like_lisp(active_parse_tree),active_parse_tree))
	#print("Agents responsible: {}".format(agents_responsible))
	if kDebugEnergies:
		print_current_energies(fluent_hash, event_hash)
		print_previous_energies(fluent_hash)
		hr()

def add_missing_parses(fluent, fluent_hash, event_hash, frame, completions):
	## here we're just getting the completions for one specific frame
	## we want to go through all the possible parses for that fluent
	## and make sure they're spoken for in completions
	#print "ADDING MISSING PARSES"
	for symbol in (completions[0]['parse']['symbol'],):
		parse_ids_completed = []
		for completion in completions:
			parse_ids_completed.append(completion['parse']['id'])
		#print("IDS: {}".format(parse_ids_completed))
		anti_symbol = invert_name(symbol)
		possible_trees = fluent_hash[symbol]['trees']
		unpossible_trees = fluent_hash[anti_symbol]['trees']
		for possible_tree in possible_trees + unpossible_trees:
			# if this tree is a "primary" for this symbol
			if possible_tree['symbol'] in (symbol,anti_symbol):
				other_parses = possible_tree['parses']
				for other_parse in other_parses:
					if other_parse['id'] not in parse_ids_completed:
						parse_ids_completed.append(other_parse['id'])
						#print("ADDING ID: {}".format(other_parse['id']))
						#complete_parse_tree(other_parse, fluent_hash, event_hash, effective_frames[symbol], completions, 'missing') ### what is this 'effective frames' thing?
						#complete_parse_tree(other_parse, fluent_hash, event_hash, frame, completions, 'missing')
						# we have a winner! let's show them what they've won, bob!
						energy = calculate_energy(other_parse, fluent_hash, event_hash)
						agents_responsible = []
						source = 'missing'
						completions.append({"frame": frame, "fluent": fluent, "energy": energy, "parse": other_parse, "agents": agents_responsible, "status": fluent_hash[other_parse['symbol']]['energy'], 'source': source})
						#print("{}".format("\t".join([str(fluent),str(frame),"{:g}".format(energy),str(make_tree_like_lisp(other_parse)),str(agents_responsible)])))
						#print("{} PARSE TREE {} COMPLETED at {}: energy({}) BY {}\n{}\n***{}***".format(fluent,other_parse['id'],frame,energy,source,make_tree_like_lisp(other_parse),other_parse))
						#print("Agents responsible: {}".format(agents_responsible))
						if kDebugEnergies:
							print_current_energies(fluent_hash, event_hash)
							print_previous_energies(fluent_hash)
							hr()
	#print "---"
	return completions

# clears out any parses that have not been touched within N frames, printing out any over reporting_threshold_energy
def complete_outdated_parses(active_parses, parse_array, fluent_hash, event_hash, event_timeouts, frame, reporting_threshold_energy, completions):
	# we're planning to remove things from active_parses while we loop through, so....
	active_parses_copy = active_parses.copy()
	parse_ids_completed = []
	parse_symbols_completed = []
	effective_frames = {}
	for parse_id in active_parses_copy:
		active_parse = parse_array[parse_id]
		symbol = active_parse['symbol']
		# get max event timeout relevant to given active_parse
		keys = get_fluent_and_event_keys_we_care_about((active_parse,))
		events = keys["events"]
		max_event_timeout = 0
		for event in events:
			event_timeout = event_timeouts[event]
			if event_timeout > max_event_timeout:
				max_event_timeout = event_timeout
		# if parse was last updated longer ago than max event timeout frames, cull
		if frame - active_parse['frame'] > max_event_timeout:
			# print("REMOVING {}".format(parse_id))
			active_parses.pop(parse_id)
			effective_frame = active_parse['frame'] # + max_event_timeout
			parse_ids_completed.append(parse_id,)
			parse_symbols_completed.append(symbol,)
			effective_frames[symbol] = effective_frame
			complete_parse_tree(active_parse, fluent_hash, event_hash, effective_frame, completions, 'timeout')
	for symbol in parse_symbols_completed:
		anti_symbol = invert_name(symbol)
		possible_trees = fluent_hash[symbol]['trees']
		unpossible_trees = fluent_hash[anti_symbol]['trees']
		for possible_tree in possible_trees: # + unpossible_trees:
			# if this tree is a "primary" for this symbol
			if possible_tree['symbol'] in (symbol,anti_symbol):
				other_parses = possible_tree['parses']
				for other_parse in other_parses:
					if other_parse['id'] not in parse_ids_completed:
						# TODO: dealing with a bug somewhere that's adding duplicate
						# copies of (some?) parses into fluent_hash[symbol][trees][parses]
						# maybe the trees themselves are referenced multiple times and so
						# added to? anyway, we can work around that by not doing the same
						# id multiple times here
						# raise Exception("TODO, EH??")
						parse_ids_completed.append(other_parse['id'])
						complete_parse_tree(other_parse, fluent_hash, event_hash, effective_frames[symbol], completions, 'timeout alt')
	clear_outdated_events(event_hash, event_timeouts, frame)

def process_events_and_fluents(causal_forest, fluent_parses, action_parses, fluent_threshold_on_energy, fluent_threshold_off_energy, reporting_threshold_energy, suppress_output = False):
	clever = True # clever (modified viterbi algorithm) or brute force (all possible parses)
	initial_conditions = False
	#TODO: initial condition stuff is suspect, investigate if/when these are in our source data. should probably never have assumed initial conditions and instead set everything to 50% likelihood
	if "initial" in fluent_parses:
		initial_conditions = fluent_parses["initial"]
		del fluent_parses["initial"]
	# do these for our local function, because we want these for figuring out which ones overlap
	fluent_parse_frames = sorted(fluent_parses, key=fluent_parses.get)
	fluent_parse_frames.sort()
	action_parse_frames = sorted(action_parses, key=action_parses.get)
	action_parse_frames.sort()
	fluent_and_event_keys_we_care_about = get_fluent_and_event_keys_we_care_about(causal_forest)
	# kind of a hack to attach fluent and event keys to each causal tree, lots of maps to make looking things up quick and easy
	event_hash = {}
	fluent_hash = {}
	event_timeouts = get_event_timeouts(causal_forest)
	# build out the list of all event types in our forest, setting their initial (frame -1) values
	# to kUnlikelyEnergy, and making a lookup to all relevant causal trees for those event types;
	# also build out the list of all fluent types in our forest, setting their initial
	# ('prev_energy' and 'energy') to either unknown or whatever our raw "initial" parses suggest
	for causal_tree in causal_forest:
		keys = get_fluent_and_event_keys_we_care_about([causal_tree])
		for key in keys['events']:
			if not key in event_hash:
				# initialize our event_hash for that key if we haven't seen it in another tree
				event_hash[key] = {"agent": False, "frame": -1, "energy": kUnlikelyEnergy, "trees": [causal_tree,]}
			else:
				event_hash[key]["trees"].append(causal_tree)
		for key in keys['fluents']:
			if key in fluent_hash:
				fluent_hash[key]["trees"].append(causal_tree)
			else:
				# new fluent goes into our hash, set it up with initial conditions if we have those
				initial_condition = kUnknownEnergy
				key_chop = key
				postfix = False
				if "_" in key:
					prefix, postfix = key.rsplit("_",1)
					if postfix in ("on","off",):
						key_chop = prefix
				if initial_conditions and key_chop in initial_conditions:
					if postfix == "on":
						initial_condition = initial_conditions[key_chop]
					else:
						initial_condition = initial_conditions[key_chop]
						if initial_condition == 0:
							initial_condition = kZeroProbabilityEnergy
						else:
							initial_condition = probability_to_energy(1-energy_to_probability(initial_condition))
				fluent_hash[key] = {"energy": initial_condition, "prev_energy": initial_condition, "trees": [causal_tree,]}
			#TODO: is this a bug? because we seem to think our status might be known in some cases above
			fluent_hash[key]["status"] = kFluentStatusUnknown

	# build lookups by fluent and event -- the parse_array will be all of the parses,
	# while the parse_id_hash* will list, for each fluent and event respectively, all of the
	# parses associated with it; these parses are flattened per generate_parses (they are implicitly
	# selected on OR nodes, so they depend only on one set of all things being true)
	parse_array = []
	parse_id_hash_by_fluent = {}
	parse_id_hash_by_event = {}
	parseid_generator = sequence_generator()
	for causal_tree in causal_forest:
		causal_tree["parses"] = generate_parses(causal_tree)
		for parse in causal_tree["parses"]:
			parse_id = parseid_generator.next()
			parse["id"] = parse_id
			parse_array.append(parse)
			keys = get_fluent_and_event_keys_we_care_about((parse,))
			for key in keys['events']:
				if key in parse_id_hash_by_event:
					parse_id_hash_by_event[key].append(parse_id)
				else:
					parse_id_hash_by_event[key] = [parse_id,]
			for key in keys['fluents']:
				if key in parse_id_hash_by_fluent:
					parse_id_hash_by_fluent[key].append(parse_id)
				else:
					parse_id_hash_by_fluent[key] = [parse_id,]
	completions = {}
	import pprint
	pp = pprint.PrettyPrinter(depth=6)
	# "complete" the initial parses, which is to say "make the energies for all of our initial state possibilities"
	for parse in parse_array:
		complete_parse_tree(parse, fluent_hash, event_hash, 0, completions, 'initial')
	if not suppress_output:
		print("PARSE_ARRAY")
		pp.pprint(parse_array)
		pp.pprint("----")
		print("COMPLETIONS AFTER INITIAL")
		pp.pprint(completions)
		pp.pprint("----")
		print("FLUENT_HASH")
		pp.pprint(fluent_hash)
		print("EVENT_HASH")
		pp.pprint(event_hash)
		pp.pprint("----")
	# loop through the parses, getting the "next frame a change happens in"; if a change happens
	# in both fluents and events at the same time, they will be handled sequentially,
	# the fluent first
	# TODO: create every combination that removes overlapping fluents and overlapping actions....

	#print "-=-=-=-=-=-=-= fluent parses -=-=-=-=-=-=-="
	#print fluent_parses
	# {8: {'light': 0.10536051565782628}, 6: {'light': 0.5108256237659907}}
	#print "-=-=-=-=-=-=-= event parses -=-=-=-=-=-=-="
	#print action_parses
	# {5: {'A1': {'energy': 0.10536051565782628, 'agent': 'uuid4'}}}
	#print "-=-=-=-=-=-=-= ...........  -=-=-=-=-=-=-="

	print "FLUENT AND EVENT KEYS WE CARE ABOUT: {}".format(fluent_and_event_keys_we_care_about)
	# ONLY MIXING UP FLUENT PARSES AS A STARTER. ACITON PARSES WOULD MEAN MORE INTERACTIONS, MORE COMPLEXITY
	# SEE inference-overlappingevents jupyter file to make sense of below
	fluents_to_recombine = defaultdict(set)
	for frame in fluent_parses:
		for fluent in fluent_parses[frame]:
			fluents_to_recombine[fluent].add(frame)
	powersets = dict()
	for fluent in fluents_to_recombine:
		frames_to_recombine = fluents_to_recombine[fluent]
		splits = split_fluents_into_windows(frames_to_recombine)
		if not suppress_output:
			print("GOT SPLITS {} for {}".format(splits, fluent))
		split_combinations = list()
		for item in splits:
			split_combinations.append(list(powerset(item))[1:])
		all_combos = split_combinations[0]
		for i in range(1,len(split_combinations)):
			all_combos = list(list(flatten(x)) for x in itertools.product(all_combos, split_combinations[i]))
		powersets[fluent] = all_combos
	powerset_counts = map(lambda x: (x,len(powersets[x]),),powersets.keys())
	if not suppress_output:
		print("powersets: {}".format(powersets))
		print("powerset counts: {}".format(powerset_counts))
	powerset_count_split_combinations = map(lambda x: range(0,x[1]),powerset_counts)
	if len(powerset_count_split_combinations) > 1:
		merge_combinations = list(itertools.product(powerset_count_split_combinations[0], powerset_count_split_combinations[1]))
		for item in powerset_count_split_combinations[2:]:
			merge_combinations = list(itertools.product(merge_combinations, item))
			merge_combinations = list(list(flatten(x)) for x in map(lambda x: (x[0],(x[1],)),merge_combinations))
	elif not powerset_count_split_combinations:
		merge_combinations = list()
	else:
		merge_combinations = powerset_count_split_combinations[0]
	if not suppress_output:
		print("MERGE_COMBINATIONS: {}".format(merge_combinations))
	results_for_xml_output = list()
	for combination in merge_combinations:
		if not suppress_output:
			print("RUNNING COMBINATION: {}".format(combination))
		if type(combination) == type(1):
			combination = (combination, )
		parses_to_recombine = dict(map(lambda x:(x[0][0],powersets[x[0][0]][x[1]]),zip(powerset_counts,combination)))
		recombined_parses = defaultdict(dict)
		#print parses_to_recombine ~ {'door': [175, 191, 272], 'light': (227,), 'screen': [147, 175]}
		if not suppress_output:
			print("parses to recombine: {}".format(parses_to_recombine))
		for fluent in parses_to_recombine:
			for frame in parses_to_recombine[fluent]:
				recombined_parses[frame][fluent] = fluent_parses[frame][fluent]
		result = _without_overlaps(recombined_parses, action_parses, parse_array, copy.deepcopy(event_hash), copy.deepcopy(fluent_hash), event_timeouts, reporting_threshold_energy, copy.deepcopy(completions), fluent_and_event_keys_we_care_about, parse_id_hash_by_fluent, parse_id_hash_by_event, fluent_threshold_on_energy, fluent_threshold_off_energy, suppress_output, clever)
		results_for_xml_output.append(copy.deepcopy(result))
	if not merge_combinations:
		result = _without_overlaps(merge_combinations, action_parses, parse_array, copy.deepcopy(event_hash), copy.deepcopy(fluent_hash), event_timeouts, reporting_threshold_energy, copy.deepcopy(completions), fluent_and_event_keys_we_care_about, parse_id_hash_by_fluent, parse_id_hash_by_event, fluent_threshold_on_energy, fluent_threshold_off_energy, suppress_output, clever)
		results_for_xml_output.append(copy.deepcopy(result))
	results_for_xml_output = sorted(results_for_xml_output, key = lambda(k): k[0][0][1])
	if not suppress_output:
		print("RESULTS_FOR_XML_OUTPUT (sorted):")
	doc = build_xml_output_for_chain(results_for_xml_output[0],parse_array,suppress_output) # for lowest energy chain
	if not suppress_output:
		for result in results_for_xml_output:
			print result
		print("BEST RESULT ::")
		print(results_for_xml_output[0])
		print("BEST RESULT as XML::")
		print("{}".format(minidom.parseString(ET.tostring(doc,method='xml',encoding='utf-8')).toprettyxml(encoding="utf-8",indent="\t")))
	print "----------------------------------------------------"
	return ET.tostring(doc,encoding="utf-8",method="xml")

#def _without_overlaps(causal_forest, fluent_parses, action_parses, fluent_threshold_on_energy, fluent_threshold_off_energy, reporting_threshold_energy, suppress_output = False):
def _without_overlaps(fluent_parses, action_parses, parse_array, event_hash, fluent_hash, event_timeouts, reporting_threshold_energy, completions, fluent_and_event_keys_we_care_about, parse_id_hash_by_fluent, parse_id_hash_by_event, fluent_threshold_on_energy, fluent_threshold_off_energy, suppress_output, clever):
	results_for_xml_output = []
	#fluent_parse_frames
	#action_parse_frames
	#fluent_and_event_keys_we_care_about
	#event_hash
	#fluent_hash
	#event_timeouts
	active_parse_trees = {}
	fluent_parse_frames = sorted(fluent_parses)
	action_parse_frames = sorted(action_parses)

	fluent_parse_index = 0
	action_parse_index = 0
	# TODO: since we complete 'actions' when we look at fluents, if they happen in the same frame
	# we should probably handling actions first
	while fluent_parse_index < len(fluent_parses) or action_parse_index < len(action_parses):
		fluents_complete = fluent_parse_index >= len(fluent_parses)
		action_complete = action_parse_index >= len(action_parses)
		# if we're not done with our fluents and either we're done with our actions OR next fluent frame is <= next action frame
		if not fluents_complete and (action_complete or fluent_parse_frames[fluent_parse_index] <= action_parse_frames[action_parse_index]):
			frame = fluent_parse_frames[fluent_parse_index]
			# print("CHECKING FLUENT FRAME: {}".format(frame))
			# before we do anything with our new fluent information, complete any actions-that-need-timing out!
			complete_outdated_parses(active_parse_trees, parse_array, fluent_hash, event_hash, event_timeouts, frame, reporting_threshold_energy, completions)
			changes = fluent_parses[frame]
			filter_changes(changes, fluent_and_event_keys_we_care_about['fluents'])
			fluent_parse_index += 1
			fluents_actually_changed = []
			for fluent in changes:
				fluent_changed = False
				fluent_on_energy = changes[fluent]
				fluent_on_probability = math.exp(-fluent_on_energy)
				fluent_off_probability = 1 - fluent_on_probability
				# print ("Fluent: {}; on probability: {}; off probability: {}".format(fluent,fluent_on_probability,fluent_off_probability))
				if 0 == fluent_off_probability:
					# TODO: might also need to catch this for fluent_on_probability 
					fluent_off_energy = kZeroProbabilityEnergy
				else:
					fluent_off_energy = -math.log(fluent_off_probability)
				fluent_on_string = "{}_on".format(fluent)
				fluent_off_string = "{}_off".format(fluent)
				fluent_on_status = fluent_hash[fluent_on_string]["status"]
				fluent_off_status = fluent_hash[fluent_off_string]["status"]
				#print ("Fluent: {}; on probability: {}; off probability: {}".format(fluent,fluent_on_probability,fluent_off_probability))
				#print ("on status: {}; off status: {}".format(fluent_on_status,fluent_off_status))
				#print ("on energy: {}; off energy: {}".format(fluent_on_energy,fluent_off_energy))
				#print ("thresh on energy: {}; thresh off energy: {}".format(fluent_threshold_on_energy,fluent_threshold_off_energy))
				# check to see if these fluents changed enough to consider starting a parse
				# note: we only care about fluents "going to true" (either "door_on" goes to true, or "door_off" does, for instance)
				if fluent_on_energy < fluent_threshold_on_energy:
					fluent_changed = fluent_on_string
					fluent_hash[fluent_on_string]["status"] = kFluentStatusOn
				if fluent_off_energy < fluent_threshold_off_energy:
					fluent_changed = fluent_off_string
					fluent_hash[fluent_off_string]["status"] = kFluentStatusOn
				# fluent_on and fluent_off _should_ never both change to on, so we consider this safe
				if fluent_changed:
					#print "fluent changed: {}".format(fluent_changed)
					fluent_hash[fluent_on_string]["prev_energy"] = fluent_off_energy
					fluent_hash[fluent_off_string]["prev_energy"] = fluent_on_energy
					fluent_hash[fluent_on_string]["energy"] = fluent_on_energy
					fluent_hash[fluent_off_string]["energy"] = fluent_off_energy
					# go through all parses that this fluent touches, or its inverse
					fluents_actually_changed.append(fluent_changed,)
					for parse_id in parse_id_hash_by_fluent[fluent_changed] + parse_id_hash_by_fluent[invert_name(fluent_changed)]:
						if parse_id not in active_parse_trees:
							# create this parse if it's not in our list of active parses
							active_parse_trees[parse_id] = parse_array[parse_id]
						active_parse_trees[parse_id]["frame"] = frame
			# complete any active parse trees that had their "primary" fluent change (or its inverse)
			for fluent in fluents_actually_changed:
				for key in active_parse_trees.keys():
					active_parse_tree = active_parse_trees[key]
					if active_parse_tree["symbol"] in (fluent, invert_name(fluent)):
						active_parse_trees.pop(key)
						complete_parse_tree(active_parse_tree, fluent_hash, event_hash, frame, completions, 'fluent_changed')
					elif kFilterNonEventTriggeredParseTimeouts:
						# TODO: this is a bug!  this will kill all but the first type of fluent
						# if we want to remove the case of parses timing out when they never
						# actually had an event create them
						raise Exception("@TODO: this is a bug! WUT!?")
						active_parse_trees.pop(key)
		else:
			frame = action_parse_frames[action_parse_index]
			complete_outdated_parses(active_parse_trees, parse_array, fluent_hash, event_hash, event_timeouts, frame, reporting_threshold_energy, completions)
			changes = action_parses[frame]
			filter_changes(changes, fluent_and_event_keys_we_care_about['events'])
			action_parse_index += 1
			for event in changes:
				# for more complex situations, we need to think this through further; for instance,
				# with the elevator: if agent 1 pushes the button; and then agent 2 pushes the button...
				# then are each of those separate parses, or are they a combined parse, or is one subsumed
				# by the other...? NOT worrying about this now.
				info = changes[event]
				# print("SETTING EVENT {} AT {} TO {}".format(event,frame,info['energy']))
				event_hash[event]['prev_energy'] = event_hash[event]['energy']
				event_hash[event]['energy'] = info['energy']
				event_hash[event]['agent'] = info['agent']
				event_hash[event]['frame'] = frame
				# print_current_energies(fluent_hash,event_hash)
				for parse_id in parse_id_hash_by_event[event]:
					if parse_id not in active_parse_trees:
						# create this parse if it's not in our list of active parses
						active_parse_trees[parse_id] = parse_array[parse_id]
					active_parse_trees[parse_id]["frame"] = frame
		"""
		if changes:
			print("{}: {}".format(frame,changes))
			for causal_tree in causal_forest:
				for parse in causal_tree["parses"]:
					print("*: {}".format(parse))
					parse_energy = calculate_energy(parse, fluent_hash, event_hash)
					print("E: {}".format(parse_energy))
			print_current_energies(fluent_hash,event_hash)
			# for any parse trees over reporting_threshold_energy, report?
			# close any completed parse trees? maintain list of completed parse trees (over reporting_threshold_energy)
			hr()
		"""
	# clean up
	complete_outdated_parses(active_parse_trees, parse_array, fluent_hash, event_hash, event_timeouts, frame+999999, reporting_threshold_energy, completions)
	if not suppress_output and False:
		import pprint
		pp = pprint.PrettyPrinter(depth=6)
		print "=-==-=-==-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--="
		pp.pprint(completions)
		print "=-==-=-==-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--="
	if clever:
		from itertools import izip
		for fluent in completions.keys():
			prev_chains = []
			prev_chain_energies = []
			if not suppress_output:
				print("{}".format(fluent))
				hr()
			for frame in sorted(completions[fluent].iterkeys()):
				if not suppress_output:
					print("\t***** frame {}".format(frame))
				completion_data = completions[fluent][frame]
				completion_data = add_missing_parses(fluent, fluent_hash, event_hash, frame, completion_data)
				completion_data_sorted = sorted(completion_data, key=lambda (k): k['energy'])
				
				next_chains = []
				next_chain_energies = []
				for node in completion_data_sorted:
					if not suppress_output:
						print("TESTING {}".format("\t".join(["{:12d}".format(frame), "{:>6.3f}".format(node['status']), "{:>6.3f}".format(node['energy']), node['source'], "{:d}".format(node['parse']['id']), str(make_tree_like_lisp(node['parse'])), str(node['agents'])])))
					# go through each chain and find the lowest energy + transition energy for this node
					best_energy = -1 # not a possible energy
					best_chain = None
					for prev_chain, prev_chain_energy in izip(prev_chains, prev_chain_energies):
						prev_node = prev_chain[-1]
						prev_symbol = prev_node['parse']['symbol'] # TRASH_MORE_on, for example
						# if this pairing is possible, see if it's the best pairing so far
						# TODO: this function will be changed to get an energy-of-transition
						# which will no longer be "binary"
						matches = False
						if parse_is_consistent_with_requirement(node['parse'],prev_symbol):
							matches = True
							if best_energy == -1 or best_energy > prev_chain_energy:
								best_energy = prev_chain_energy
								best_chain = prev_chain
								#print("PREV: {}".format(prev_node['parse']))
								#print("CONX: {}".format(node['parse']))
						elif parse_can_jump_from(prev_node['parse'],node['parse']):
							# look for timer-based jumps ... so if this node['parse'] has a possible timer jump, let's see it
							print("{}".format(prev_node['parse']))
							print("{}".format(node['parse']))
							raise("HELL...O")
						else:
							pass
							#print("{}".format("\t".join(["{:12d}".format(frame), "{:>6.3f}".format(node['status']), "{:>6.3f}".format(node['energy']), node['source'], "{:d}".format(node['parse']['id']), str(make_tree_like_lisp(node['parse'])), str(node['agents'])])))
					# now we take our best chain for this node, and dump it and its energy in our new list
						if not suppress_output:
							print("{}   {}".format("+match" if matches else "-wrong","\t".join(["{:>6.3f}".format(prev_chain_energy), "{:>6.3f}".format(prev_node['status']), "{:>6.3f}".format(prev_node['energy']), prev_node['source'], "{:d}".format(prev_node['parse']['id']), str(make_tree_like_lisp(prev_node['parse'])), str(prev_node['agents'])])))
					if best_chain:
						#chain = best_chain.copy()
						chain = best_chain[:]
						chain.append(node)
						next_chains.append(chain)
						next_chain_energies.append(best_energy + node['energy'])
						if not suppress_output:
							print(">best<   {}".format("\t".join(["{:>6.3f}".format(best_energy), "{:>6.3f}".format(best_chain[-1]['status']), "{:>6.3f}".format(best_chain[-1]['energy']), best_chain[-1]['source'], "{:d}".format(best_chain[-1]['parse']['id']), str(make_tree_like_lisp(best_chain[-1]['parse'])), str(best_chain[-1]['agents'])])))
					else:
						if prev_chains:
							import pprint
							pp = pprint.PrettyPrinter(depth=6)
							print "*** NOTHING FOUND DESPITE {} CHAIN(S) EXISTING".format(len(prev_chains))
							#for chain in prev_chains:
							#	print chain
							#print "*** WILL NOT LINK TO"
							#pp.pprint(node['parse'])
							#assert(0)
						else:
							# hopefully this is only happening at the very beginning
							next_chains.append([node,])
							next_chain_energies.append(node['energy'])
				prev_chains = next_chains
				prev_chain_energies = next_chain_energies
			# and now we just wrap up our results... and print them out
			# TODO: sort by energy... but first let's just see that we're completing ;)
			chain_results = []
			for chain, energy in izip(prev_chains, prev_chain_energies):
				items = []
				for item in chain:
					items.append((item['frame'],item['parse']['id']))
				#print([items,energy])
				chain_results.append([items,energy])
			# print('\n'.join(['\t'.join(l) for l in chain_results]))
			chain_results = sorted(chain_results,key=lambda(k): k[1])[:20]
			results_for_xml_output.append(chain_results[:1])
			if not suppress_output:
				print('\n'.join(map(str,chain_results)))
				hr()
				hr()
	else: # not clever i.e. brute force
		for fluent in completions.keys():
			prev_chains = []
			if not suppress_output:
				print fluent
				hr()
			for frame in sorted(completions[fluent].iterkeys()):
				#print("\t***** frame {}".format(frame))
				completion_data_sorted = sorted(completions[fluent][frame], key=lambda (k): k['energy'])
				if not prev_chains:
					for child in completion_data_sorted:
						prev_chains.append((child,))
				else:
					children = []	
					for prev_chain in prev_chains:
						last_parent_node = prev_chain[-1]
						last_parent_symbol = last_parent_node['parse']['symbol'] # TRASH_MORE_on, for example
						for child in completion_data_sorted:
							# if this pairing is possible, cross it on down
							# pairing is considered "possible" if the parent's primary fluent status agrees with all relevant child fluent pre-requisites
							if parse_is_consistent_with_requirement(child['parse'],last_parent_symbol):
								chain = list(prev_chain)
								chain.append(child)
								children.append(chain)
					prev_chains = children
				for completion_data in completion_data_sorted:
					if not suppress_output:
						print("{}".format("\t".join(["{:12d}".format(frame), "{:>6.3f}".format(completion_data['status']), "{:>6.3f}".format(completion_data['energy']), completion_data['source'], "{:d}".format(completion_data['parse']['id']), str(make_tree_like_lisp(completion_data['parse'])), str(completion_data['agents'])])))
			chain_results = []
			for chain in prev_chains:
				items = []
				energy = 0
				for item in chain:
					items.append((item['frame'],item['parse']['id']))
					energy += item['energy']
				#print([items,energy])
				chain_results.append([items,energy])
			# print('\n'.join(['\t'.join(l) for l in chain_results]))
			chain_results = sorted(chain_results,key=lambda(k): k[1])[:20]
			results_for_xml_output.append(chain_results[:1])
			if not suppress_output:
				print('\n'.join(map(str,chain_results)))
				hr()
				hr()
	return results_for_xml_output

def build_xml_output_for_chain(all_chains,parse_array,suppress_output=False):
	temporal = ET.Element('temporal')
	fluent_changes = ET.SubElement(temporal,'fluent_changes')
	actions_el = ET.SubElement(temporal,"actions")
	seen = [] # keeping track of whether we've seen a fluent and thus have included its initial state
	for chain in all_chains:
		energy = chain[0][1]
		chain = chain[0][0]
		for instance in chain:
			frame_number = instance[0]
			parse_id = instance[1]
			parse = parse_array[parse_id]
			# get fluents where there's a prev-fluent and fluent.  or just stick with top level?
			if not suppress_output:
				#print("{}".format(frame_number))
				#print("{}".format(parse['symbol']))
				print("{}".format(parse))
			fluent, fluent_value = parse['symbol'].rsplit("_",1)
			fluent_attributes = {
				"fluent": fluent,
				"new_value": fluent_value,
				"frame": str(frame_number),
				"energy": str(energy)
			};
			prev_value = get_prev_fluent_value_from_parse(parse,fluent)
			if len(prev_value) != 1:
				print("{}".format(len(prev_value)))
				print("Parse: {}".format(parse))
				raise Exception("The tree does not have a previous fluent")
			#print("{}".format(prev_value))
			if prev_value[0] != fluent_value:
				fluent_attributes['old_value'] = prev_value[0];
			elif fluent in seen:
				# if we've been seen and there's no change, don't include it
				# TODO: is this okay even though it skips us getting actions from the "non"-parse?
				continue
			if not fluent in seen:
				seen.append(fluent,)
			fluent_parse = ET.SubElement(fluent_changes, "fluent_change", fluent_attributes)
			#TODO: missing attributes id, object, time in fluent_change
			# now let's see if there's an action associated with this fluent change and pop that in our bag
			actions = get_actions_from_parse(parse)
			if actions:
				for action in actions:
					action_el = ET.SubElement(actions_el,"event", {
						"frame": str(frame_number),
						"energy": str(energy),
						"action": str(action),
					});
	return temporal

# TODO: this assumes we're only going to find one previous fluent value for the given fluent
def get_prev_fluent_value_from_parse(parse,fluent):
	prev_fluents = []
	# get prev fluent
	if "symbol_type" in parse:
		if parse["symbol_type"] == "prev_fluent":
			tmp_fluent, tmp_fluent_value = parse["symbol"].rsplit("_",1)
			#print("11111")
			if tmp_fluent == fluent:
				#print("2221222")
				prev_fluents.append(tmp_fluent_value)
				#print("{}".format(prev_fluents))
	if "children" in parse:
		for child in parse["children"]:
			child_prev_fluents = get_prev_fluent_value_from_parse(child,fluent)
			prev_fluents += child_prev_fluents
	return prev_fluents

def get_actions_from_parse(parse):
	actions = []
	if "symbol_type" in parse:
		if parse["symbol_type"] == "event":
			#tmp_event, tmp_event_value = parse["symbol"].rsplit("_",1)
			actions.append(parse["symbol"])
	if "children" in parse:
		for child in parse["children"]:
			child_actions = get_actions_from_parse(child)
			actions += child_actions
	return actions

if __name__ == '__main__':
	# WHOO!
	import demo
