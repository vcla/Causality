kHumanAnnotationClippoints = "results/CVPR2012_humanTestAnnotation.txt"
cutpoints = dict()
import re
with open(kHumanAnnotationClippoints, 'ra') as file:
	clip_frames_regexp = re.compile(r"Frame: (\d+).*End: (\d+)")
	newlines = (line.rstrip() for line in file)
	nextexample = dict()
	example_key = False
	for line in newlines:
		if line.startswith("Testing Data Name:"):
			example_key = line[19:]
		elif line.startswith("Clip Start Frame:"):
			match = re.findall(clip_frames_regexp, line)[0]
			nextexample[match[0]] = match[1]
		elif line.startswith("****"):
			cutpoints[example_key] = nextexample
			nextexample = dict()
