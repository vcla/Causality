input_dir <- "cvpr_db_results"
output_csv <- "cvpr_db_results.csv"
setwd('results')

csv_files <- dir(input_dir, pattern=".csv", full.names=TRUE)
records <- matrix(c("entity", "instance", "subject", "option", "score"), nrow=1, ncol=5)
for (csv_file in csv_files) {
  data <- read.csv(csv_file)
  num_rows <- dim(data)[1]
  num_cols <- dim(data)[2]
  if (num_rows != 0 && num_cols != 0) {
    for (row in 1:dim(data)[1]) {
      for (col in 2:(dim(data)[2]-2)) {
        entity <- gsub("[0-9_]+_[a-z_]+", "", colnames(data)[col])
        instance <- paste(gsub("/[a-zA-z/]+/|.csv|_", "", csv_file), gsub("[a-z_]+", "", colnames(data)[col]), sep="@")
        subject <- as.character(data[row,1])
        option <- gsub("[a-z_]+_[0-9_]+", "", colnames(data)[col])
        score <- data[row,col]
        record <- cbind(entity, instance, subject, option, score)
        records <- rbind(records, record)
      }
    }
  }
}
write.table(records[order(records[,1]),], file=output_csv, quote=FALSE, sep=",", row.names=FALSE, col.names=FALSE)
