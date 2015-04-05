for i in `python dealWithDBResults.py list | grep screen_ | cut -d '	' -f 1`
	do
	echo RUNNING $i
	python plotResults.py $i screen > results/timelines/$i.csv
	Rscript --vanilla plotResults.R results/timelines/$i.csv results/timelines/$i.png
done
