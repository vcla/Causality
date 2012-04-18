"""
causal grammar parser and helper functions
"""
# TODO: events have to turn off after a while, which probably means they need to be handled differently in our parses so the parse energies don't depend on the event happening "now"
# TODO: filter out "competing" parse trees below thresh
# TODO: complete parse trees after some "frame" threshold if key fluent not detected

import itertools
import math # for log, etc

kUnknownEnergy = 10.0 # TODO: may want to tune
kFluentThresholdOnEnergy = 0.36 # TODO: may want to tune: 0.36 = 0.7 probability
kFluentThresholdOffEnergy = 1.2 # TODO: may want to tune: 1.2 = 0.3 probability
kReportingThresholdEnergy = 0.5 # TODO: may want to tune
kDefaultEventTimeout = 10 # shouldn't need to tune because this should be tuned in grammar

kFluentStatusUnknown = 1
kFluentStatusOn = 2
kFluentStatusOff = 3

def import_csv(filename, fluents, events):
	fluent_parses = {}
	temporal_parses = {}
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
						on_value = kUnknownEnergy
					else:
						raise Exception("{} not 1 or 0 for frame {}: {}".format(fluent, frame, on_value))
					if frame not in fluent_parses:
						fluent_parses[frame] = {}
					fluent_parses[frame][to] = on_value
			for event in events:
				trigger = float(csv_row[events[event]['column']])
				if trigger == 1:
					to = events[event]['to']
					if frame not in temporal_parses:
						temporal_parses[frame] = {}
					temporal_parses[frame][to] = {"energy": 0.0, "agent": frame_agent}
	return [fluent_parses,temporal_parses]

def hr():
	print "---------------------------------"

# TODO: a given event is assumed to have the same timeout everywhere in the grammar
def get_event_timeouts(forest):
	global kDefaultTimeout
	events = {}
	for tree in forest:
		if "children" in tree:
			child_timeouts = get_event_timeouts(tree["children"])
			for key in child_timeouts:
				events[key] = child_timeouts[key]
		if "symbol_type" in tree:
			if "event" == tree["symbol_type"]:
				if "timeout" in tree:
					events[tree["symbol"]] = tree["timeout"]
				else:
					events[tree["symbol"]] = kDefaultTimeout
	return events

def get_fluent_and_event_keys_we_care_about(forest):
	fluents = []
	events = []
	for tree in forest:
		if "children" in tree:
			child_keys = get_fluent_and_event_keys_we_care_about(tree["children"])
			fluents += child_keys['fluents']
			events += child_keys['events']
		if "symbol_type" in tree:
			if tree["symbol_type"] in ("fluent","prev_fluent"):
				fluents.append(tree["symbol"])
			elif "event" == tree["symbol_type"]:
				events.append(tree["symbol"])
	return { "fluents": fluents, "events": events }

# filters "changes" for just the fluents and events we care about
# "changes" dict is changed by this function as python is always pass-by-reference
def filter_changes(changes, keys_in_grammar):
	keys_for_filtering = []
	for key in keys_in_grammar:
		if "_" in key:
			prefix, postfix = key.split("_",1)
			if postfix == "on":
				keys_for_filtering.append(prefix)
				continue
			elif postfix == "off":
				keys_for_filtering.append(prefix)
				continue
		keys_for_filtering.append(key)
	for x in [x for x in changes.keys() if x not in keys_for_filtering]:
		changes.pop(x)

def generate_parses(causal_tree):
	node_type = causal_tree["node_type"]
	if "children" not in causal_tree:
		return (causal_tree,);
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

def calculate_energy(node, fluent_hash, event_hash):
	node_energy = 0.0
	node_count = 0
	if "probability" in node:
		# coming off a "root" or "or" node_type
		tmp_energy = -math.log(node["probability"])
		if tmp_energy != kUnknownEnergy:
			node_count += 1
			node_energy += tmp_energy
	elif "symbol_type" in node:
		if node["symbol_type"] in ("fluent",):
			tmp_energy = fluent_hash[node["symbol"]]["energy"]
			if tmp_energy != kUnknownEnergy:
				node_count += 1
				node_energy += tmp_energy
		elif node["symbol_type"] in ("prev_fluent",):
			tmp_energy = fluent_hash[node["symbol"]]["prev_energy"]
			if tmp_energy != kUnknownEnergy:
				node_count += 1
				node_energy += tmp_energy
		elif node["symbol_type"] in ("event",):
			tmp_energy = event_hash[node["symbol"]]["energy"]
			if tmp_energy != kUnknownEnergy:
				node_count += 1
				node_energy += tmp_energy
	if "children" in node:
		for child in node["children"]:
			(child_energy,child_count) = calculate_energy(child, fluent_hash, event_hash)
			node_energy += child_energy
			node_count += child_count
	return (node_energy,node_count)
		
def make_tree_like_lisp(causal_tree):
	my_symbol = "?"
	if "symbol" in causal_tree:
		my_symbol = causal_tree["symbol"]
	if "children" not in causal_tree:
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
	print fluent_energies
	event_energies = {}
	for event in event_hash:
		event_energies[event] = event_hash[event]["energy"]
	print event_energies

# sets any events that haven't triggered within their timeout number of frames to kUnknownEnergy
def clear_outdated_events(event_hash, event_timeouts, frame):
	global kUnknownEnergy
	for event in event_hash:
		if event_hash[event]["energy"] != kUnknownEnergy and frame - event_hash[event]["frame"] > event_timeouts[event]:
			event_hash[event]["frame"] = -1
			event_hash[event]["energy"] = kUnknownEnergy
			event_hash[event]["agent"] = False

# clears out any parses that have not been touched within N frames, printing out any over reporting_threshold_energy
def complete_outdated_parses(active_parses, frame, reporting_threshold_energy):
	# TODO
	pass

def process_events_and_fluents(causal_forest, fluent_parses, temporal_parses, fluent_threshold_on_energy, fluent_threshold_off_energy, reporting_threshold_energy):
	global kUnknownEnergy
	fluent_parse_index = 0
	temporal_parse_index = 0
	fluent_parse_frames = sorted(fluent_parses, key=fluent_parses.get)
	fluent_parse_frames.sort()
	temporal_parse_frames = sorted(temporal_parses, key=temporal_parses.get)
	temporal_parse_frames.sort()
	fluent_and_event_keys_we_care_about = get_fluent_and_event_keys_we_care_about(causal_forest)
	# kind of a hack to attach fluent and event keys to each causal tree, lots of maps to make looking things up quick and easy
	event_hash = {}
	fluent_hash = {}
	event_timeouts = get_event_timeouts(causal_forest)
	for causal_tree in causal_forest:
		keys = get_fluent_and_event_keys_we_care_about([causal_tree])
		for key in keys['events']:
			if key in event_hash:
				event_hash[key]["trees"].append(causal_tree)
			else:
				event_hash[key] = {"frame": -1, "energy": kUnknownEnergy, "trees": [causal_tree,]}
		for key in keys['fluents']:
			if key in fluent_hash:
				fluent_hash[key]["trees"].append(causal_tree)
			else:
				fluent_hash[key] = {"energy": kUnknownEnergy, "prev_energy": kUnknownEnergy, "trees": [causal_tree,]}
			fluent_hash[key]["status"] = kFluentStatusUnknown
	# print "INITIAL CONDITIONS"
	# print_current_energies(fluent_hash, event_hash)
	parse_id = 0 # give each parse tree a unique id
	parse_array = []
	parse_id_hash_by_fluent = {}
	parse_id_hash_by_event = {}
	for causal_tree in causal_forest:
		# print "PARSES FOR CAUSAL TREE {}:".format(causal_tree["symbol"])
		causal_tree["parses"] = generate_parses(causal_tree)
		for parse in causal_tree["parses"]:
			parse["id"] = parse_id
			parse_array.append(parse)
			keys = get_fluent_and_event_keys_we_care_about((parse,)) # get_fluent_yadda expects a forest
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
			#print "*: {}".format(parse)
			#(parse_energy, parse_count) = calculate_energy(parse, fluent_hash, event_hash)
			#print "E: {}/{} ~ {}".format(parse_energy,parse_count,parse_energy/parse_count)
			parse_id += 1
		#hr()
	#print parse_array
	# loop through the parses, getting the "next frame a change happens in"; if a change happens
	# in both at the same time, they will be handled sequentially, the fluent first
	active_parse_trees = {}
	while fluent_parse_index < len(fluent_parses) or temporal_parse_index < len(temporal_parses):
		fluents_complete = fluent_parse_index >= len(fluent_parses)
		temporal_complete = temporal_parse_index >= len(temporal_parses)
		if not fluents_complete and (temporal_complete or fluent_parse_frames[fluent_parse_index] <= temporal_parse_frames[temporal_parse_index]):
			frame = fluent_parse_frames[fluent_parse_index]
			clear_outdated_events(event_hash, event_timeouts, frame)
			complete_outdated_parses(active_parse_trees, frame, reporting_threshold_energy)
			changes = fluent_parses[frame]
			filter_changes(changes, fluent_and_event_keys_we_care_about['fluents'])
			fluent_parse_index += 1
			fluents_actually_changed = []
			for fluent in changes:
				fluent_changed = False
				fluent_on_energy = changes[fluent]
				fluent_on_probability = math.exp(-fluent_on_energy)
				fluent_off_probability = 1 - fluent_on_probability
				if 0 == fluent_off_probability:
					fluent_off_energy = kUnknownEnergy
				else:
					fluent_off_energy = -math.log(fluent_off_probability)
				fluent_on_string = "{}_on".format(fluent)
				fluent_off_string = "{}_off".format(fluent)
				fluent_on_status = fluent_hash[fluent_on_string]["status"]
				fluent_off_status = fluent_hash[fluent_off_string]["status"]
				# check to see if these fluents changed enough to consider starting a parse
				# note: we only care about fluents "going to true"
				if fluent_on_status in (kFluentStatusUnknown, kFluentStatusOff):
					if fluent_on_energy < fluent_threshold_on_energy:
						fluent_changed = fluent_on_string
						fluent_hash[fluent_on_string]["status"] = kFluentStatusOn
				elif fluent_on_energy > fluent_threshold_off_energy:
					fluent_hash[fluent_on_string]["status"] = kFluentStatusOff
				if fluent_off_status in (kFluentStatusUnknown, kFluentStatusOff):
					if fluent_off_energy < fluent_threshold_on_energy:
						fluent_changed = fluent_off_string
						fluent_hash[fluent_off_string]["status"] = kFluentStatusOn
				elif fluent_off_energy > fluent_threshold_off_energy:
					fluent_hash[fluent_off_string]["status"] = kFluentStatusOff
				fluent_hash[fluent_on_string]["prev_energy"] = fluent_hash[fluent_on_string]["energy"]
				fluent_hash[fluent_off_string]["prev_energy"] = fluent_hash[fluent_off_string]["energy"]
				fluent_hash[fluent_on_string]["energy"] = fluent_on_energy
				fluent_hash[fluent_off_string]["energy"] = fluent_off_energy
				# fluent_on and fluent_off _should_ never both change to on, so we consider this safe
				if fluent_changed:
					fluents_actually_changed.append(fluent_changed,)
					for parse_id in parse_id_hash_by_fluent[fluent_changed]:
						if parse_id not in active_parse_trees:
							# create this parse if it's not in our list of active parses
							active_parse_trees[parse_id] = parse_array[parse_id]
						active_parse_trees[parse_id]["frame"] = frame
			# complete any active parse trees that had their "primary" fluent change
			for fluent in fluents_actually_changed:
				for key in active_parse_trees.keys():
					active_parse_tree = active_parse_trees[key]
					if active_parse_tree["symbol"] == fluent:
						active_parse_trees.pop(key)
						# we have a winner! let's show them what they've won, bob!
						energy = calculate_energy(active_parse_tree, fluent_hash, event_hash)
						energy = energy[0] / energy[1]
						print "{} PARSE TREE COMPLETED at {}: energy({})\n***{}***".format(fluent,frame,energy,active_parse_tree)
						print_current_energies(fluent_hash, event_hash)
						# TODO: if there are agents in the parse, print out who they were
		else:
			frame = temporal_parse_frames[temporal_parse_index]
			clear_outdated_events(event_hash, event_timeouts, frame)
			complete_outdated_parses(active_parse_trees, frame, reporting_threshold_energy)
			changes = temporal_parses[frame]
			filter_changes(changes, fluent_and_event_keys_we_care_about['events'])
			temporal_parse_index += 1
			for event in changes:
				# for more complex situations, we need to think this through further; for instane, 
				# with the elevator: if agent 1 pushes the button; and then agent 2 pushes the button...
				# then are each of those separate parses, or are they a combined parse, or is one subsumed
				# by the other...? NOT worrying about this now.
				info = changes[event]
				event_hash[event]['energy'] = info['energy']
				event_hash[event]['agent'] = info['agent']
				event_hash[event]['frame'] = frame
				for parse_id in parse_id_hash_by_event[event]:
					if parse_id not in active_parse_trees:
						# create this parse if it's not in our list of active parses
						active_parse_trees[parse_id] = parse_array[parse_id]
					active_parse_trees[parse_id]["frame"] = frame
		"""
		if changes:
			print "{}: {}".format(frame,changes)
			for causal_tree in causal_forest:
				for parse in causal_tree["parses"]:
					print "*: {}".format(parse)
					(parse_energy, parse_count) = calculate_energy(parse, fluent_hash, event_hash)
					print "E: {}/{} ~ {}".format(parse_energy,parse_count,parse_energy/parse_count)
			print_current_energies(fluent_hash,event_hash)
			# for any parse trees over reporting_threshold_energy, report?
			# close any completed parse trees? maintain list of completed parse trees (over reporting_threshold_energy)
			hr()
		"""
	hr()
	# report all ... stuff ... at ... end
	print "DONE"

if __name__ == 'main':
	# our causal forest:
	causal_forest = [ {
		"node_type": "root",
		"symbol_type": "fluent",
		"symbol": "light_on",
		"children": [
			{ "node_type": "leaf", "probability": .3, "symbol": "light_on", "symbol_type": "prev_fluent" },
			{ "node_type": "and", "probability": .7, "children": [
					{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_off" },
					{ "node_type": "leaf", "symbol_type": "event", "symbol": "E1", "timeout": 10 },
				]
			},
		],
	}, {
		"node_type": "root",
		"symbol_type": "fluent",
		"symbol": "light_off",
		"children": [
			{ "node_type": "leaf", "probability": .3, "symbol_type":"prev_fluent", "symbol": "light_off" },
			{ "node_type": "and", "probability": .7, "children": [
					{ "node_type": "leaf", "symbol_type": "prev_fluent", "symbol": "light_on" },
					{ "node_type": "leaf", "symbol_type": "event", "symbol": "E1", "timeout": 10 },
				]
			},
		],
	},
	]
	process_events_and_fluents(causal_forest, fluent_parses, temporal_parses, kFluentThresholdOnEnergy, kFluentThresholdOffEnergy, kReportingThresholdEnergy)
