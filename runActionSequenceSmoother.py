import parsingSummerActionAndFluentOutput 
import os

actionResults = "CVPR2012_computer_test_action_detection_monday/"
#actionResults = "CVPR2012_computer_test_action_detection/"
gamma = 1.0
#beamwidth = 100000
beamwidth = 1000
storingResultsFolder = "CVPR2012_smoothed_action_detections_monday_1000/"
#storingResultsFolder = "CVPR2012_smoothed_action_detections/"

# get example folder names
exampleNames =  parsingSummerActionAndFluentOutput.returnExampleNames()

emptyExamples = []

for singleExample in exampleNames:
	exampleFolderPath = actionResults + singleExample
	lowframe = 1000000000
	highframe = -1
	for filename in os.listdir(exampleFolderPath):
		[frame, other] = filename.split(".")
		if frame != "act_parse":
			# then have a number
			tmp = int(frame)
			if tmp > highframe:
				highframe = tmp
			if tmp < lowframe:
				lowframe = tmp
	if lowframe == 1000000000 or highframe == -1:
		# then there were no frames of this sort
		emptyExamples.append(singleExample)
	else:
		# run mingtian's code on the example
		shellCommand = "./ActionSequenceSmoother " + exampleFolderPath + " " + str(lowframe) + " " + str(highframe) + " " + str(beamwidth) + " " + str(gamma)
		shellCommand += " > " + storingResultsFolder + singleExample + ".txt"
		os.system(shellCommand)

# empty examples for FYI purposes
print emptyExamples
