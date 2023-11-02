library(tidyverse)
library(lubridate)

# Configuring the logger
logging_dir <- Sys.getenv("DUMMY_CONTAINER_LOGGING_DIRECTORY", "/extra_implementation_specific_results/")
log_file_path <- file.path(logging_dir, 'out.log')

# Check if logging directory is writable
if (dir.exists(logging_dir) && file.access(logging_dir, mode = 2) == 0) {
    log_file <- file(log_file_path, open = "wt")
    sink(log_file, type = "output")
    sink(log_file, type = "message")
} else {
    message("Logging directory is not writable.")
}

# Function to load file
load_file <- function(file_path, file_format = NULL) {
    if (is.null(file_format)) {
        file_format <- tools::file_ext(file_path)
    }
    if (file_format == "parquet") {
        return(arrow::read_parquet(file_path))
    } else if (file_format == "csv") {
        return(read_csv(file_path))
    } else {
        stop("Unsupported file format")
    }
}

# Check if "DUMMY_CONTAINER_MAIN_INPUT_FILE_PATHS" is in the environment
if ("DUMMY_CONTAINER_MAIN_INPUT_FILE_PATHS" %in% names(Sys.getenv())) {
    main_input_file_paths <- strsplit(Sys.getenv("DUMMY_CONTAINER_MAIN_INPUT_FILE_PATHS"), ",")[[1]]
} else {
    main_input_file_paths <- list.files(path = "/input_data", pattern = "main_input*", full.names = TRUE)
}

message('Loading main input')
df <- load_file(main_input_file_paths[1])

for (path in main_input_file_paths[-1]) {
    message('Loading additional primary input')
    df <- bind_rows(df, load_file(path)) %>%
        mutate(
            across(everything(), ~replace_na(.x, 0))
        )
}

# Check if "DUMMY_CONTAINER_SECONDARY_INPUT_FILE_PATHS" is in the environment
if ("DUMMY_CONTAINER_SECONDARY_INPUT_FILE_PATHS" %in% names(Sys.getenv())) {
    secondary_input_file_paths <- strsplit(Sys.getenv("DUMMY_CONTAINER_SECONDARY_INPUT_FILE_PATHS"), ",")[[1]]
} else {
    secondary_input_file_paths <- list.files(path = "/input_data", pattern = "secondary_input*", full.names = TRUE)
}

for (path in secondary_input_file_paths) {
    message('Loading secondary input')
    df <- bind_rows(df, load_file(path)) %>%
        mutate(
            across(everything(), ~replace_na(.x, 0))
        )
}

extra_implementation_specific_input_glob <- list.files(path = "/extra_implementation_specific_input_data", pattern = "input*", full.names = TRUE)
extra_implementation_specific_input_file_path <- Sys.getenv(
    "DUMMY_CONTAINER_EXTRA_IMPLEMENTATION_SPECIFIC_INPUT_FILE_PATH",
    if (length(extra_implementation_specific_input_glob) > 0) extra_implementation_specific_input_glob[1] else ""
)
if (extra_implementation_specific_input_file_path != "") {
    message('Loading extra, implementation-specific input')
    df <- bind_rows(df, load_file(extra_implementation_specific_input_file_path)) %>%
        mutate(
            across(everything(), ~replace_na(.x, 0))
        )
}

message(paste('Total input length is', nrow(df)))

broken <- tolower(Sys.getenv("DUMMY_CONTAINER_BROKEN", "false")) %in% c('true', 'yes', '1')
if (broken) {
    df <- rename(df, wrong = foo, column = bar, names = counter)
} else {
    increment <- as.integer(Sys.getenv("DUMMY_CONTAINER_INCREMENT", "1"))
    message(paste('Increment is', increment))

    df$counter <- as.integer(df$counter + increment)

    # Extract the maximum added column number from column names starting with "added_column_"
    added_column_numbers <- str_subset(names(df), "^added_column_") %>%
      str_extract("\\d+$") %>%
      as.integer()

    if (length(added_column_numbers) > 0) {
      max_added_column <- max(added_column_numbers, na.rm = TRUE) + increment
    } else {
      max_added_column <- increment
    }

    min_added_column <- max(max_added_column - 4, 0)

    # Generate the names of the desired added columns
    added_columns_desired_names <- paste0('added_column_', min_added_column:max_added_column)

    # Create new columns if they do not exist
    for (column_name in added_columns_desired_names) {
        if (!(column_name %in% names(df))) {
            column_value <- as.integer(str_extract(column_name, "\\d+$"))
            df <- df %>%
                mutate(!!column_name := column_value)
        }
    }

    # Drop the columns that are not desired
    columns_to_drop <- grep("added_column_", names(df), value = TRUE)
    columns_to_drop <- columns_to_drop[!(columns_to_drop %in% added_columns_desired_names)]
    df <- df %>% select(-all_of(columns_to_drop))
}

output_file_format <- Sys.getenv("DUMMY_CONTAINER_OUTPUT_FILE_FORMAT", "parquet")
output_file_paths <- strsplit(Sys.getenv("DUMMY_CONTAINER_OUTPUT_PATHS", paste0("/results/result.", output_file_format)), ",")[[1]]

for (output_file_path in output_file_paths) {
    message(paste('Writing output to', output_file_path, 'in', output_file_format, 'format'))

    if (output_file_format == "parquet") {
        arrow::write_parquet(df, output_file_path)
    } else if (output_file_format == "csv") {
        write_csv(df, output_file_path)
    } else {
        stop("Unsupported file format")
    }
}