import pandas as pd, numpy as np
import os

input_file_type = os.environ.get("DUMMY_STEP_INPUT_FILE_TYPE", "parquet")
input_file_path = os.environ["DUMMY_STEP_INPUT_PATH"]

if input_file_type == "parquet":
    df = pd.read_parquet(input_file_path)
elif input_file_type == "csv":
    df = pd.read_csv(input_file_path)
else:
    raise ValueError()

counter = df.counter.astype(int).max() + 1
df['counter'] = counter

df[f'added_column_{counter}'] = counter

columns_to_drop = [
    c for c in df.columns if 'added_column_' in c and int(c.split('_')[-1]) < counter - 4
]
df.drop(columns=columns_to_drop, inplace=True)

output_file_type = os.environ.get("DUMMY_STEP_OUTPUT_FILE_TYPE", "parquet")
output_file_path = os.environ["DUMMY_STEP_OUTPUT_PATH"]

if output_file_type == "parquet":
    df.to_parquet(output_file_path)
elif output_file_type == "csv":
    df.to_csv(output_file_path, index=False)
else:
    raise ValueError()
