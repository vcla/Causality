# options(echo=TRUE) # if you want see commands in output file
args <- commandArgs(trailingOnly = TRUE)
doOutputPNG = FALSE

if (length(args) == 0) {
	kSourceCSV <- "/projects/inference-master/results/cvpr_db_results-pr.csv"
} else {
	kSourceCSV <- args[1]
	doOutputPNG <- TRUE
	outputPNG <- args[2]
}

pr <- read.csv(kSourceCSV, sep=",")
row.names(pr) <- pr$TYPE
pr <- pr[-1]

kColors = c(
	rgb(104,175,237,maxColorValue=255), 
	rgb(255,255,138,maxColorValue=255),
	rgb(180,127,184,maxColorValue=255),
	rgb(159,250,181,maxColorValue=255)
	)

#colors: we want to duplicate the colors for fluent/action
ylim=c(0,1)

op <- par()
if (doOutputPNG) {
	png(outputPNG, width=10, height=11, units="in", res=300, pointsize=20)
	#pdf(outputPNG, width=10, height=11, pointsize=20)
	par(cex.axis = 0.7, cex.lab = 22)
	legendoffset = -25
} else {
	graphics.off() # because we're breaking the plot/graphics object with margins or something
	par(cex.axis = 0.7)
	legendoffset = -18
}
#layout(matrix(c(1,2,3,4))) # two figures in row 1, two figures in row two
graphs = dim(pr)[1] / 4
rows = ceiling(graphs / 2)
par(mfrow=c(rows,2))	
par(xpd=NA)

main="Causal Grammar P/R"
for (i in 1:graphs) {
	foo = row.names(pr)[i*4]
	foo = strsplit(foo,'_')[[1]][2]
	if (foo == "all") {
		foo <- "SUMMARY"
	}
	pr_item = pr[((i-1)*4+1):((i-1)*4+4),]
	barplot(as.matrix(pr_item), main=foo, beside=TRUE, col=kColors, ylim=ylim)
	#barplot(as.matrix(pr_all), add=TRUE, beside=TRUE, col=as.vector(rbind(kColors,kColors)), angle=90,density=density,ylim=ylim)
	if (i == graphs) {
		#legend("topleft", c("fluent precision","fluent recall","action precision", "action recall"), 	cex=0.8, bty="n", fill=kColors)
		legend(legendoffset,-0.35, ncol=4, c("fluent precision","fluent recall","action precision", "action recall"), bty="n", fill=kColors, cex = 1.0)
		
	}
}
par(xpd=FALSE)

if (doOutputPNG) {
	par(op)
}
