for j in "screen"
do
	for i in `python dealWithDBResults.py list | grep ${j}_ | cut -d '	' -f 1`
		do
		echo RUNNING $i
		python plotResults.py $i $j > results/timelines/$i-$j.csv
		Rscript --vanilla plotResults.R results/timelines/$i-$j.csv results/timelines/$i-$j.png
	done
done
