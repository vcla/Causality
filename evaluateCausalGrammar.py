def getFluentChangesForFluent(xml, fluent):
	return xml.findall("./fluent_changes/fluent_change[@fluent='{}'][@old_value]".format(fluent))

def getFluentChangesForFluentBetweenFrames(xml, fluent, frame1, frame2):
	assert(frame1 <= frame2)
	changes = getFluentChangesForFluent(xml, fluent)
	retval = []
	for change in changes:
		if int(change.attrib['frame']) >= frame1 and int(change.attrib['frame']) <= frame2:
			retval.append(change)
	return retval
