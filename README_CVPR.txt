'DATA
* CVPR2012_fluent_result (fluent source data by Bruce) 
* CVPR2012_* (action source data (.txt) by Ping, parsed results (.mat) by Mingtian, parsed results (.py) by ...?)
* cvpr_db_results.csv (humans, source data, causalgrammar all merged -- see below)

'WORKFLOW
* dealWithDBResults.py <-- requires CVPR2012_humanTestAnnotation.txt and CVPR2012_reverse_slidingwindow_action_detection_logspace/*
** python dealWithDBResults.py (upload|download|upanddown)
*** upload: 
**** runs causal_grammar.import_summerdata -- importing from CVPR2012_reverse_slidingwindow_action_detection_logspace/* - (python files)
**** munge_parses_to_xml(fluent_parses, temporal_parses) -> "orig_xml" results
**** causal_grammar.process_events_and_fluents --> "fluent_and_action_xml" results
**** "orig_xml" uploaded to db as 'origdata' and 'origsmrt'
**** "fluent_and_action_xml" uploaded to db as 'causalgrammar' and 'causalsmrt'
***** in uploadComputerResponseToDB, if source.endswith('smrt'), buildDictForFluentBetweenFramesIntoResults is called, which does some very basic fixing of local inconsistencies (versus buildDictForDumbFluentBetweenFramesIntoResults)
*** download:
**** creates unified results/cvpr_db_results/*.csv for each user (human or algorithm)
* analyze_results.R converts the cvpr_db_results/*.csv to a single cvpr_db_results.csv
** R --vanilla < analyze_results.R
** plotAllResults.sh loops through each table/element in summerdata and generates timeline heatmaps for every agent (human, computer, source, ...)
* and then on to actual analysis....

'ANALYSIS
* analyze_results.go by Mingtian reads cvpr_db_results.csv; "analyzeData.py" refers to the results of the go code in "findDistanceGivenLineOfGoOutput", calling it obsolete. # analyzeData.py has been removed, last existed in git hash 3032f8
* hitrate.py, formerly analyzeData-nearesthuman-hitrate.py -- "hitrate for CVPR 2015 submission" (Nov 2015)
* plotPR.R generates a set of precision/recall graphs from the output of analyzeData-nearesthuman-pr.py # analyzeData-nearesthuman-pr.py has been removed, last existed in git hash 3032f8
* plotPR.sh calls analyzeData-nearesthuman-pr.py and then plotPR.R to generate a set of precision/recall graphs # analyzeData-nearesthuman-pr.py has been removed, last existed in git hash 3032f8

evaluateCausalGrammer:
* getFluentChangesForFluent (operates on causal_grammar.process_events_and_fluents xml)
* getFluentChangesForFluentBetweenFrames (operates on causal_grammar.process_events_and_fluents xml)

* 108 videos -- cut up from "maybe 10" -- in SIX scenes (9406, 9404, 8145, lounge) -- 2 grammars (
* and what if we ran computer-solver together on whole chain?

'TODO
	DOOR, LIGHT, MONITOR, PHONE
