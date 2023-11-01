library(tidyverse)
library(arrow)
library(glue)

input_file_type <- Sys.getenv("DUMMY_STEP_INPUT_FILE_TYPE", "parquet")
input_file_path <- Sys.getenv("DUMMY_STEP_INPUT_PATH")

if (input_file_type == "parquet"){
    df <- arrow::read_parquet(input_file_path)
} else if (input_file_type == "csv"){
    df <- read_csv(input_file_path)
} else {
    stop("Unsupported input file type")
}

counter <- as.integer(max(df$counter, na.rm = TRUE)) + 1
df <- df %>%
    mutate(counter = !!counter) %>%
    mutate(!!glue('added_column_{counter}') := !!counter)

for (column in colnames(df)){
    if (startsWith(column, 'added_column_')){
        if (as.integer(str_extract(column, "\\d+$")) < counter - 4) {
            df <- df %>% select(-all_of(column))
        }
    }
}

output_file_type <- Sys.getenv("DUMMY_STEP_OUTPUT_FILE_TYPE", "parquet")
output_file_path <- Sys.getenv("DUMMY_STEP_OUTPUT_PATH")

if (output_file_type == "parquet"){
    arrow::write_parquet(df, output_file_path)
} else if (output_file_type == "csv"){
    write_csv(df, output_file_path)
} else {
    stop("Unsupported output file type")
}