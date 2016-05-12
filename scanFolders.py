import dealWithDBResults
import hitrate
import os
with open('results/actionDetectionFolders.txt','rb') as folders:
	connType = "sqlite"
	conn = dealWithDBResults.getDB(connType)
	try:
		for folder in (x.rstrip() for x in folders):
			examples = dealWithDBResults.getExamples(os.path.join("results",folder),mode="list")
			dealWithDBResults.processAndUploadExamples(examples,conn)
			dealWithDBResults.downloadExamples(examples,connType,conn)
			hitrate.args = lambda:None
			hitrate.args.__dict__.update({"normalizefirst": True, "debug":False, "scan":False, "summary":True, "smart":False, "latex":False, "examples_only":False, "failures":False})
			hitrate.exceptions = list()
			summary = hitrate.doit()
			with open('results/{}.csv'.format(folder),'wb') as results:
				for key in summary.keys():
					results.write("{},{}\n".format(key,summary[key]))
				results.write("diff,{}\n".format(summary['causalgrammar']-summary['origdata']))
	finally:
		conn.close()
