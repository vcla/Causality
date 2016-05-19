import dealWithDBResults
import hitrate
import os
import gc
with open('results/actionDetectionFolders.txt','rb') as folders:
	connType = "sqlite"
	conn = dealWithDBResults.getDB(connType)
	dealWithDBResults.withoutoverlaps = True
	dealWithDBResults.suppress_output = True
	dealWithDBResults.debugQuery = False
	dealWithDBResults.connType = connType
	hitrate.args = lambda:None
	hitrate.args.__dict__.update({"normalizefirst": True, "debug":False, "scan":False, "summary":True, "smart":False, "latex":False, "examples_only":False, "failures":False})
	try:
		for folder in (x.rstrip() for x in folders if not x.startswith("#")):
			gc.collect()
			folderPath = os.path.join("results",folder)
			examples = dealWithDBResults.getExamples(folderPath,mode="list")
			os.system("python dealWithDBResults.py -a {} upanddown".format(folderPath))
			#dealWithDBResults.processAndUploadExamples(folderPath,examples,conn)
			#dealWithDBResults.downloadExamples(examples,connType,conn)
			hitrate.exceptions = list()
			summary = hitrate.doit()
			with open('results/{}.csv'.format(folder),'wb') as results:
				for key in summary.keys():
					results.write("{},{}\n".format(key,summary[key]))
				results.write("diff,{}\n".format(summary['causalgrammar']-summary['origdata']))
	finally:
		conn.close()
