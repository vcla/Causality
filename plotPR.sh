python analyzeData-nearesthuman-pr.py | sed '1,/\*\*\*\*\*\*\*/ d' > results/cvpr_db_results-pr.csv
Rscript --vanilla plotPR.R results/cvpr_db_results-pr.csv results/cvpr_db_results-pr.png
