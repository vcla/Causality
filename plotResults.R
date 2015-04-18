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
kDrawFluentTrace <- TRUE
#kFluentLinesegmentColor <- rgb(.5,.7,1.)
kFluentLinesegmentShadowColor <- rgb(0,.4,0)
#kFluentLinesegmentColor <- rgb(1,1,1)
kFluentLinesegmentColor <- rgb(1,1,.7)

if (length(args) == 0) {
	kSourceCSV <- "/projects/inference-master/results/timelines/light/door_12_light_2_9406-light.csv"
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
kColors = colorRampPalette(c(
	'white', 
	rgb(104,175,237,maxColorValue=255), 
	rgb(44,127,184,maxColorValue=255)
))(255)

#yellow->green ramp from http://colorbrewer2.org/
kColors = colorRampPalette(c(
rgb(255,247,243,maxColorValue=255),rgb(253,224,221,maxColorValue=255),rgb(252,197,192,maxColorValue=255),rgb(250,159,181,maxColorValue=255),rgb(247,104,161,maxColorValue=255),rgb(221,52,151,maxColorValue=255),rgb(174,1,126,maxColorValue=255),rgb(122,1,119,maxColorValue=255),rgb(73,0,106,maxColorValue=255)
))(255)

# kColorsAlt = colorRampPalette(c('white','purple'))(255)
kColorsAlt = colorRampPalette( c(
	rgb(197,27,138,maxColorValue=255),
	rgb(250,159,181,maxColorValue=255), 
	'white'
))(255)

#purple->pink->red ramp
kColorsAlt = colorRampPalette(c(
rgb(247,252,240,maxColorValue=255),rgb(224,243,219,maxColorValue=255),rgb(204,235,197,maxColorValue=255),rgb(168,221,181,maxColorValue=255),rgb(123,204,196,maxColorValue=255),rgb(78,179,211,maxColorValue=255),rgb(43,140,190,maxColorValue=255),rgb(8,104,172,maxColorValue=255),rgb(8,64,129,maxColorValue=255)
))(255)

kAlternateColors <- TRUE

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
	timeline_matrix[rowsToColorDifferently,] <- timeline_matrix[rowsToColorDifferently,] * -1.
	minValue = abs(min(timeline_matrix, na.rm = TRUE)) # 0 <= minValue <= 1 -- this is our kColorsAlt bar
	maxValue = max(timeline_matrix, na.rm = TRUE)      # 0 <= maxValue <= 1 -- this is our kColors bar
	kColorsAlt <- rev(kColorsAlt[(length(kColorsAlt)*(1-minValue)):length(kColorsAlt)])
	kColors <- kColors[1:(length(kColors)*maxValue)]
	if (minValue == 0) {
		kColorsAlt = c()
	}
	if (maxValue == 0) {
		kColors = c()
	}
	colors <- append(kColorsAlt,kColors)
} else {
	#TODO: fix the scaling problem when we're not doing alternating colors. At this point, we need to look at both min and max...
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

fluentLineSegments <- function(matrix, draw=TRUE, lwd=2, col=2, lty=1) {
	if (!draw) {
		return (FALSE)
	}
	on  <- 1.5 - 2/30
	off <- 0.5 + 2/30
	rows <- dim(timeline_matrix)[1]
	cols <- dim(timeline_matrix)[2]
	thresh_matrix <- 0 + (abs(timeline_matrix[seq(1,rows,by=2),]) > 0.5)
	thresh_rows <- dim(thresh_matrix)[1]
	changepoints_to_set = c()
	changepoints_from_set = c()
	changevalues_to_set = c()
	changevalues_from_set = c()
	for (i in 0:thresh_rows) {
		diffs <- c(0,rle(c(0,diff(thresh_matrix[thresh_rows - i, ]))))
		changepoints_to = cumsum(diffs$lengths)
		changepoints_from <- append(0,head(changepoints_to,-1))
		initialvalue <- thresh_matrix[thresh_rows - i,][1] # 0: our first change will be 1; 1: our first change will be -1
		changevalues = (cumsum(diffs$values) + initialvalue) * (on-off) + off
		changepoints_from_set <- append(changepoints_from_set, changepoints_from)
		changepoints_to_set <- append(changepoints_to_set, changepoints_to)
		changevalues_from_set <- append(changevalues_from_set, changevalues + (i * 2) + 1)
		changevalues_to_set <- append(changevalues_to_set, changevalues + (i * 2) + 1)
		if (length(changepoints_to) > 1) {
			whichpoints <- which(diffs$values != 0)
			changepoints_to <- changepoints_from[whichpoints]
			changepoints_to_set <- append(changepoints_to_set, changepoints_to)
			changepoints_from_set <- append(changepoints_from_set, changepoints_to)
			offs <- rep(off  + (i * 2) + 1, length(changepoints_to))
			ons <- rep(on + (i * 2) + 1, length(changepoints_to))
			changevalues_from_set <- append(changevalues_from_set, offs)
			changevalues_to_set <- append(changevalues_to_set, ons)
		}
	}
	segments(changepoints_from_set, changevalues_from_set, changepoints_to_set, changevalues_to_set, lwd=lwd, col=col, lty=lty);
	return (TRUE)
}

timeline_heatmap <- myheatmap(
	timeline_matrix, 
	lmat = rbind(c(4,3),c(2,1)),
	lwid = lwid,
	lhei = lhei,
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
	na.color="red",
	cexRow=0.7, # make row text labels smaller
	#cexCol=1.2,
	xlab=filename,
	add.expr=eval( {
		fluentLineSegments(timeline_matrix,draw=kDrawFluentTrace,lwd=4,col=kFluentLinesegmentShadowColor);
fluentLineSegments(timeline_matrix,draw=kDrawFluentTrace,lwd=2,col=kFluentLinesegmentColor)
	}) 	
#	ylab="bar",
#	main="main",
)
#title(filename)
if (doOutputPNG) {
	par(op)
}
