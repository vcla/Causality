'DATA
* CVPR2012_fluent_result (fluent source data by Bruce) 
* CVPR2012_* (action source data (.txt) by Ping, parsed results (.mat) by Mingtian, parsed results (.py) by ...?)
* cvpr_db_results.csv (humans, source data, causalgrammar all merged -- see below)

'WORKFLOW
* dealWithDBResults.py
** python dealWithDBResults.py (upload|download|upanddown)
*** upload: 
**** runs causal_grammar.import_summerdata -- importing from CVPR2012_reverse_slidinwindow_action_detection_logspace - python files)
**** munge_parses_to_xml(fluent_parses, temporal_parses) -> "orig_xml" results
**** causal_grammar.process_events_and_fluents --> "fluent_and_action_xml" results
**** "orig_xml" uploaded to db as 'origdata' and 'origsmrt'
**** "fluent_and_action_xml" uploaded to db as 'causalgrammar' and 'causalsmrt'
***** in uploadComputerResponseToDB, if source.endswith('smrt'), buildDictForFluentBetweenFramesIntoResults is called, which does some very basic fixing of local inconsistencies (versus buildDictForDumbFluentBetweenFramesIntoResults)
*** download:
**** creates unified results/dvpr_db_results/*.csv for each user (human or algorithm)
* analyze_results.R converts the cvpr_db_results/*.csv to a single cvpr_db_results.csv
** R --vanilla < analyze_results.R
* and then on to actual analysis....

'ANALYSIS
* analyze_results.go by Mingtian reads cvpr_db_results.csv; "analyzeData.py" refers to the results of the go code in "findDistanceGivenLineOfGoOutput", calling it obsolete.
* analyzeData.py -- runs on combined cvpr_db_results.csv; "PR DICT" for each action or fluent, not sure how to read it. (Jan 2 2014, from earlier than that, commit comment is "first pass at cleaning things up for handoff")
* analyzeData-besthuman.py -- best human is the human that was most agreed with by all the other humans (Nov 8 2014)
* analyzeData-nearesthuman.py -- nearest human is the one that was closest to a given computer algorithm (Nov 8 2014) ... this 
* analyzeData-nearesthuman-pr.py -- "first pass on trying to do precision and recall against db data" (Nov 14 2014)

evaluateCausalGrammer:
* getFluentChangesForFluent (operates on causal_grammar.process_events_and_fluents xml)
* getFluentChangesForFluentBetweenFrames (operates on causal_grammar.process_events_and_fluents xml)

* 108 videos -- cut up from "maybe 10" -- in SIX scenes (9406, 9404, 8145, lounge) -- 2 grammars (
* and what if we ran computer-solver together on whole chain?

GRAPH over time, bar chart,
human a
human b
computer x // base fluents
computer y // base k
computer z

DOOR, LIGHT, MONITOR, PHONE
