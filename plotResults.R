#TODO: maybe group screens together and actions together
#TODO: maybe color actions differently ~ every other row, add 1; have two different color ramps...

#NOTES
# https://stat.ethz.ch/R-manual/R-devel/library/stats/html/heatmap.html <- heatmap
# http://www.inside-r.org/packages/cran/gplots/docs/heatmap.2 <- heatmap.2
# http://cran.r-project.org/web/packages/RColorBrewer/index.html
# http://flowingdata.com/2010/01/21/how-to-make-a-heatmap-a-quick-and-easy-solution/
# http://sebastianraschka.com/Articles/heatmaps_in_r.html <- mentions how to do color breaks!
# http://colorbrewer2.org/ <- pretty color selection!
# http://stackoverflow.com/questions/17820143/how-to-change-heatmap-2-color-range-in-r <- also breaks
# http://stackoverflow.com/questions/16279492/r-heatmap-2-colsep-as-vector <- colsep weirdness
# http://mannheimiagoesprogramming.blogspot.com/2012/06/drawing-heatmaps-in-r-with-heatmap2.html 
# http://research.stowers-institute.org/mcm/efg/R/Graphics/Basics/mar-oma/index.htm <- on plot areas

# options(echo=TRUE) # if you want see commands in output file
args <- commandArgs(trailingOnly = TRUE)
doOutputPNG = FALSE
kIncludeLegendHistogram <- "none"
kShowLegend <- FALSE
kAlternateColors <- TRUE

if (length(args) == 0) {
	kSourceCSV <- "/projects/inference-master/results/timelines/screen_1_lounge-screen.csv"
} else {
	kSourceCSV <- args[1]
	doOutputPNG <- TRUE
	outputPNG <- args[2]
}
# filename <- tail(strsplit(kSourceCSV,"/")[[1]],1)
filename <- basename(kSourceCSV)
filename <- sub("\\.[[:alnum:]]+$", "", filename)
filename <- strsplit(filename,"-")
filename <- paste(filename[[1]][1]," (",filename[[1]][2], ")" )

# doOutputPNG <- TRUE
# outputPNG="/projects/inference-master/output.png"

# kColors = colorRampPalette(c('white','lightgreen','darkgreen'))(255)
kColors = colorRampPalette(c('white', rgb(127,205,187,maxColorValue=255), rgb(44,127,184,maxColorValue=255)))(255)
# kColorsAlt = colorRampPalette(c('white','purple'))(255)
kColorsAlt = colorRampPalette(c('white', rgb(250,159,181,maxColorValue=255), rgb(197,27,138,maxColorValue=255)))(255)

doInstall <- TRUE  # Change to FALSE if you don't want packages installed.

pkgTest <- function(x) {
	has <- suppressMessages(require(x, character.only = TRUE))
	if (!has) {
		devnull = install.packages(x, repos = "http://cran.us.r-project.org", dep=TRUE)
		has <- suppressMessages(require(x, character.only=TRUE))
		if (!has) stop("Package not found: "+x)
	}
}

toInstall <- c("gplots") # , "ggplot2") # , "reshape2", "RColorBrewer")
if (doInstall) pkgTest(toInstall)
devnull <- suppressPackageStartupMessages(lapply(toInstall, library, character.only = TRUE))

timeline <- read.csv(kSourceCSV, sep=",")
row.names(timeline) <- timeline$NAME
timeline <- timeline[,-1] # chop off the left column
timeline_matrix <- data.matrix(timeline)
firstframe = strtoi(substring(colnames(timeline)[1],2))

if (kAlternateColors) {
	rowsToColorDifferently = seq(0,dim(timeline)[1],2)
	timeline_matrix <- timeline_matrix / 2.01
	timeline_matrix[rowsToColorDifferently,] <- timeline_matrix[rowsToColorDifferently,] + 0.50005
	colors <- append(kColors,kColorsAlt)
} else {
	colors <- kColors
}
columnsN = dim(timeline_matrix)[2]
rowsN = dim(timeline_matrix)[1]

# fix the column labels since we only want a nice axis and these are ordered ints...
columnLabels = rep('',columnsN+1)
columnsToLabel = seq(0,columnsN,100)
columnsToLabel <- append(columnsToLabel,columnsN-1)
columnLabels[columnsToLabel + 1] = columnsToLabel + firstframe
columnsToLabel[length(columnsToLabel)] <- columnsToLabel[length(columnsToLabel)] + 1


#myheatmap = heatmap
myheatmap = heatmap.2

if (kShowLegend) {
	lwid = c(0.3,1)
	lhei = c(0.3,1)
} else {
	lwid = c(0.1,1)
	lhei = c(0.1,1)
}

op <- par()
if (doOutputPNG) {
	png(outputPNG, width=12, height=8, units="in", res=72, pointsize=20)
	par(cex.axis = 20, cex.lab = 22)
} else {
	graphics.off() # because we're breaking the plot/graphics object with margins or something
}

timeline_heatmap <- myheatmap(
	lmat = rbind(c(4,3),c(2,1)),
	lwid = lwid,
	lhei = lhei,
	timeline_matrix, 
	key=kShowLegend,
	dendrogram="none",
	scale="none",
	Rowv=NA,
	Colv=NA, 
	col = colors,
	margins=c(4,11),
	sepcolor=1,
	colsep=columnsToLabel,
	rowsep=seq(0,rowsN,2),
	sepwidth=c(0.01,0.01),
	trace="none", # otherwise there's a vertical line drawn for each timestamp, very slowly
	labCol=columnLabels,
	density.info=kIncludeLegendHistogram,
	notecol="red",
	cexRow=0.7, # make row text labels smaller
	#cexCol=1.2,
	xlab=filename,
#	ylab="bar",
#	main="main",
	)
title(filename)
if (length(outputPNG) == 0) {
	par(op)
}
