# for easier writing of the causal grammar
def write_causal_forest_for_python():
	pass

# xml formatted causal grammar
def write_xml_for_forest(causal_forest):
	print '<causal>'
	for tree in causal_forest:
		write_xml_for_tree(tree)
	print '</causal>'

def write_xml_for_tree(tree):
	#print "***{}".format(tree)
	if tree["node_type"] in ("root", "or"):
		for child in tree["children"]:
			print '\t<production_rule id=\"\" fluent=\"{}\" probability=\"{}\">'.format(tree["symbol"], 0)#tree["probability"])
			write_xml_for_tree(child)
			print '\t</production_rule>'
	elif tree["node_type"] == "and":
		for child in tree["children"]:
			#print "*** CHILD: {}".format(child)
			write_xml_for_tree(child)
	elif tree["node_type"] == "leaf":
		if tree["symbol_type"] == "prev_fluent":
			print '\t\t\t<fluent symbol=\"{}\" />'.format(tree["symbol"])
		elif tree["symbol_type"] == "event":
			print '\t\t\t<action symbol=\"{}\" />'.format(tree["symbol"])
		else:
			raise Exception("unknown symbol type: {}".format(tree["symbol_type"]))
	elif tree["node_type"] == "or":
		print "OR"


	
	#    <causal>
	#        <production_rule id="5e73a424-7ab9-4451-949e-998b2293d9ac" fluent_change="DOOR,DOOR_STATUS,OPEN,CLOSED">
	#            <actions>
	#                <action symbol="TOUCH_DOOR" />
	#            </actions>
	#        </production_rule>
	#        <production_rule id="19aa751e-adfe-4292-aaab-edb3d0156585" fluent_change="ROOM,LIGHT_STATUS,ON,OFF">
	#            <actions>
	#                <action symbol="TOUCH_LIGHT_SWITCH" />
	#            </actions>
	#        </production_rule>
	#        <production_rule id="10c26e5d-d6e0-4aec-a070-46a3d88d54c0" fluent_change="ROOM,LIGHT_STATUS,OFF,ON">
	#            <actions>
	#                <action symbol="TOUCH_LIGHT_SWITCH" />
	#            </actions>
	#        </production_rule>
	#    </causal>



def write_xml_for_parse_tree(completed_parse_tree):
	#xml_string = '<relation id=\"' + ***ID 
	#        <causal>
	#            <relation id="f775d305-8abb-4744-9986-eee9588e1f04" production_rule="5e73a424-7ab9-4451-949e-998b2293d9ac">
	#                <instance fluent_change="9236e488-e050-4362-8c29-c0f78a3fd911">
	#                    <action id="637b9b66-ac48-4071-98b8-406c55ba47af" />
	#                </instance>
	#            </relation>
	#            <relation id="fa517b00-30b0-4615-bc56-e73a47afd500" production_rule="19aa751e-adfe-4292-aaab-edb3d0156585">
	#                <instance fluent_change="72e4c44d-9b90-4aaf-ac65-82c41fdac99f">
	#                    <action id="f50742cf-cc9d-4610-83bb-d34b43e9c599" />
	#                </instance>
	#            </relation>
	#        </causal>
	#    </interpretation>
	pass
