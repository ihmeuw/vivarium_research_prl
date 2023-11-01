from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, max as spark_max
import os

spark = (
    SparkSession.builder
        .master(os.getenv("DUMMY_STEP_SPARK_MASTER_URL", "local[2]"))
        .getOrCreate()
)

input_file_type = os.environ.get("DUMMY_STEP_INPUT_FILE_TYPE", "parquet")
input_file_path = os.environ["DUMMY_STEP_INPUT_PATH"]

if input_file_type == "parquet":
    df = spark.read.parquet(input_file_path)
elif input_file_type == "csv":
    df = spark.read.csv(input_file_path, header=True, inferSchema=True)
else:
    raise ValueError()

counter = int(df.agg(spark_max(col('counter'))).collect()[0][0]) + 1
df = df.withColumn('counter', lit(counter))

df = df.withColumn(f'added_column_{counter}', lit(counter))

columns_to_drop = [
    c for c in df.columns if 'added_column_' in c and int(c.split('_')[-1]) < counter - 4
]
df = df.drop(*columns_to_drop)

output_file_type = os.environ.get("DUMMY_STEP_OUTPUT_FILE_TYPE", "parquet")
output_file_path = os.environ["DUMMY_STEP_OUTPUT_PATH"]

# NOTE: Go back to pandas in order to save a single file
if output_file_type == "parquet":
    df.toPandas().to_parquet(output_file_path)
elif output_file_type == "csv":
    df.toPandas().to_csv(output_file_path, index=False)
else:
    raise ValueError()
