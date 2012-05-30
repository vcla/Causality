"""
causal grammar parser and helper functions
"""
# TODO: filter out "competing" parse trees below thresh

import itertools
import math # for log, etc

kUnknownEnergy = 0.7 # TODO: may want to tune
kUnlikelyEnergy = 10.0 # TODO: may want to tune
kZeroProbabilityEnergy = 10.0 # TODO: may want to tune: 10.0 = very low
kFluentThresholdOnEnergy = 0.36 # TODO: may want to tune: 0.36 = 0.7 probability
kFluentThresholdOffEnergy = 1.2 # TODO: may want to tune: 1.2 = 0.3 probability
kReportingThresholdEnergy = 0.5 # TODO: may want to tune
kDefaultEventTimeout = 10 # shouldn't need to tune because this should be tuned in grammar
kFilterNonEventTriggeredParseTimeouts = False # what the uber-long variable name implies
kDebugEnergies = False # if true, print out fluent current/prev and event energies when completing a parse tree

kFluentStatusUnknown = 1
kFluentStatusOn = 2
kFluentStatusOff = 3

def generate_causal_forest_from_abbreviated_forest(abbreviated_forest):
	forest = []
	for child in abbreviated_forest:
		tree = {}
		if child[0]:
			tree["node_type"] = child[0]
		if child[1]:
			tree["symbol_type"] = child[1]
		if child[2]:
			tree["symbol"] = child[2]
		if child[3]:
			tree["probability"] = child[3]
		if child[4]:
			tree["timeout"] = child[4]
		if child[5]:
			tree["children"] = generate_causal_forest_from_abbreviated_forest(child[5])
		forest.append(tree)
	return forest

def import_xml(filename):
	fluent_parses = {"initial":{}}
	temporal_parses = {}
	from xml.dom.minidom import parse
	document = parse(filename)
	interpretation_chunk = document.getElementsByTagName('interpretation')[0]
	interpretation_probability = float(interpretation_chunk.attributes['probability'].nodeValue)
	interpretation_energy = probability_to_energy(interpretation_probability)
	temporal_chunk = document.getElementsByTagName('temporal')[0]
	initial_fluents = fluent_parses["initial"];
	for fluent_change in temporal_chunk.getElementsByTagName('fluent_change'):
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
	for event in temporal_chunk.getElementsByTagName('event'):
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
			add_event(temporal_parses,action_agent,action_start_frame,"{}_START".format(action_name),interpretation_energy)
			add_event(temporal_parses,action_agent,action_end_frame,"{}_END".format(action_name),interpretation_energy)
		add_event(temporal_parses,event_agents,event_start_frame,"{}_START".format(event_name),interpretation_energy)
		add_event(temporal_parses,event_agents,event_end_frame,"{}_END".format(event_name),interpretation_energy)
	return [fluent_parses,temporal_parses]

def import_csv(filename, fluents, events):
	raise Exception("THIS IS OUT OF DATE: IT HAS NOT BEEN UPDATED TO HAVE _START AND _END AT THE VERY LEAST")
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
					if frame not in temporal_parses:
						temporal_parses[frame] = {}
					temporal_parses[frame][to] = {"energy": 0.0, "agent": frame_agent}
	return [fluent_parses,temporal_parses]

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
			if "event" == tree["symbol_type"]:
				if "timeout" in tree:
					events[tree["symbol"]] = int(tree["timeout"])
				else:
					events[tree["symbol"]] = int(kDefaultTimeout)
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
			elif tree["symbol_type"] in ("event","nonevent"):
				events.append(tree["symbol"])
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
			node_energy += probability_to_energy(1-energy_to_probability(tmp_energy))
		else:
			raise Exception("unhandled symbol_type '{}'".format(node['symbol_type']))
	if "children" in node:
		for child in node["children"]:
			child_energy = calculate_energy(child, fluent_hash, event_hash)
			node_energy += child_energy
	return node_energy
		
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
def clear_outdated_events(event_hash, event_timeouts, frame):
	for event in event_hash:
		if event_hash[event]["energy"] != kUnlikelyEnergy and frame - event_hash[event]["frame"] > event_timeouts[event]:
			# print("CLEARING EVENT {} @ {}".format(event,frame))
			event_hash[event]["frame"] = -1
			event_hash[event]["energy"] = kUnlikelyEnergy
			event_hash[event]["agent"] = False

def complete_parse_tree(active_parse_tree, fluent_hash, event_hash, frame, completions):
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
		completion_frame.append({"energy": energy, "parse": active_parse_tree, "agents": agents_responsible})
	# print("{}".format("\t".join([str(fluent),str(frame),"{:g}".format(energy),str(make_tree_like_lisp(active_parse_tree)),str(agents_responsible)])))
	# print("{} PARSE TREE {} COMPLETED at {}: energy({})\n{}\n***{}***".format(fluent,active_parse_tree['id'],frame,energy,make_tree_like_lisp(active_parse_tree),active_parse_tree))
	# print("Agents responsible: {}".format(agents_responsible))
	if kDebugEnergies:
		print_current_energies(fluent_hash, event_hash)
		print_previous_energies(fluent_hash)
		hr()

# clears out any parses that have not been touched within N frames, printing out any over reporting_threshold_energy
def complete_outdated_parses(active_parses, parse_array, fluent_hash, event_hash, event_timeouts, frame, reporting_threshold_energy, completions):
	# we're planning to remove things from active_parses while we loop through, so....
	active_parses_copy = active_parses.copy()
	for parse_id in active_parses_copy:
		active_parse = parse_array[parse_id]
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
			effective_frame = active_parse['frame'] + max_event_timeout
			complete_parse_tree(active_parse, fluent_hash, event_hash, effective_frame, completions)
			possible_trees = fluent_hash[active_parse['symbol']]['trees']
			parses_completed = [parse_id,]
			for possible_tree in possible_trees:
				# if this tree is a "primary" for this symbol
				if possible_tree['symbol'] == active_parse['symbol']:
					other_parses = possible_tree['parses']
					for other_parse in other_parses:
						if other_parse['id'] not in parses_completed:
							# TODO: dealing with a bug somewhere that's adding duplicate
							# copies of (some?) parses into fluent_hash[symbol][trees][parses]
							# maybe the trees themselves are referenced multiple times and so
							# added to? anyway, we can work around that by not doing the same
							# id multiple times here
							# raise Exception("TODO, EH??")
							parses_completed.append(other_parse['id'])
							complete_parse_tree(other_parse, fluent_hash, event_hash, effective_frame, completions)

def process_events_and_fluents(causal_forest, fluent_parses, temporal_parses, fluent_threshold_on_energy, fluent_threshold_off_energy, reporting_threshold_energy):
	fluent_parse_index = 0
	temporal_parse_index = 0
	initial_conditions = False
	if "initial" in fluent_parses:
		initial_conditions = fluent_parses["initial"]
		del fluent_parses["initial"]
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
				event_hash[key] = {"agent": False, "frame": -1, "energy": kUnlikelyEnergy, "trees": [causal_tree,]}
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
			fluent_hash[key]["status"] = kFluentStatusUnknown
	#for key in fluent_hash.keys():
	#	print("{}: {}".format(key,fluent_hash[key]['energy']))
	#print(initial_conditions)
	# print_current_energies(fluent_hash, event_hash)
	parse_id = 0 # give each parse tree a unique id
	parse_array = []
	parse_id_hash_by_fluent = {}
	parse_id_hash_by_event = {}
	# build lookups by fluent and event
	for causal_tree in causal_forest:
		# print("PARSES FOR CAUSAL TREE {}:".format(causal_tree["symbol"]))
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
			#print("*: {}".format(parse))
			#parse_energy = calculate_energy(parse, fluent_hash, event_hash)
			#print("E: {}".format(parse_energy))
			parse_id += 1
	# loop through the parses, getting the "next frame a change happens in"; if a change happens
	# in both at the same time, they will be handled sequentially, the fluent first
	active_parse_trees = {}
	completions = {}
	while fluent_parse_index < len(fluent_parses) or temporal_parse_index < len(temporal_parses):
		fluents_complete = fluent_parse_index >= len(fluent_parses)
		temporal_complete = temporal_parse_index >= len(temporal_parses)
		if not fluents_complete and (temporal_complete or fluent_parse_frames[fluent_parse_index] <= temporal_parse_frames[temporal_parse_index]):
			frame = fluent_parse_frames[fluent_parse_index]
			complete_outdated_parses(active_parse_trees, parse_array, fluent_hash, event_hash, event_timeouts, frame, reporting_threshold_energy, completions)
			clear_outdated_events(event_hash, event_timeouts, frame)
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
					# TODO: might also need to catch this for fluent_on_probability 
					fluent_off_energy = kZeroProbabilityEnergy
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
						complete_parse_tree(active_parse_tree, fluent_hash, event_hash, frame, completions)
					elif kFilterNonEventTriggeredParseTimeouts:
						# TODO: this is a bug!  this will kill all but the first type of fluent
						# if we want to remove the case of parses timing out when they never
						# actually had an event create them
						raise Exception("@TODO: this is a bug! WUT!?")
						active_parse_trees.pop(key)
		else:
			frame = temporal_parse_frames[temporal_parse_index]
			complete_outdated_parses(active_parse_trees, parse_array, fluent_hash, event_hash, event_timeouts, frame, reporting_threshold_energy, completions)
			clear_outdated_events(event_hash, event_timeouts, frame)
			changes = temporal_parses[frame]
			filter_changes(changes, fluent_and_event_keys_we_care_about['events'])
			temporal_parse_index += 1
			for event in changes:
				# for more complex situations, we need to think this through further; for instane, 
				# with the elevator: if agent 1 pushes the button; and then agent 2 pushes the button...
				# then are each of those separate parses, or are they a combined parse, or is one subsumed
				# by the other...? NOT worrying about this now.
				info = changes[event]
				# print("SETTING EVENT {} AT {} TO {}".format(event,frame,info['energy']))
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
	clear_outdated_events(event_hash, event_timeouts, frame+999999)
	# hr()
	# report all ... stuff ... at ... end
	# print("DONE")
	for fluent in completions.keys():
		print fluent
		hr()
		for frame in sorted(completions[fluent].iterkeys()):
			for completion_data in sorted(completions[fluent][frame], key=lambda (k): k['energy']):
				print("{}".format("\t".join([str(fluent),str(frame),"{:g}".format(completion_data['energy']),str(make_tree_like_lisp(completion_data['parse'])),str(completion_data['agents'])])))
		hr()

if __name__ == '__main__':
	# WHOO!
	import demo
