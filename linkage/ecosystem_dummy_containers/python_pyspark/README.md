# PySpark container performing the dummy step

Similar to Pandas, except it requires a writeable working directory, which means the Singularity instructions are a bit different.

This container has an additional configurable environment variable, `DUMMY_STEP_SPARK_MASTER_URL`, which is the URL of the Spark
master; this defaults to `local[2]` which runs Spark within the container with 2 threads.

## Running with Docker

```
docker build -t linker:dummy_step_python_pyspark .
mkdir -p /tmp/dummy_step_python_pyspark_results/
docker run --mount type=bind,source=./../input_file_1.parquet,target=/input_data/main_input_file.parquet --mount type=bind,source=/tmp/dummy_step_python_pyspark_results/,target=/results -i -t linker:dummy_step_python_pyspark
```

Or, going to .tar.gz and back:

```
docker build -t linker:dummy_step_python_pyspark .
docker save linker:dummy_step_python_pyspark | gzip > python-pyspark-image.tar.gz
docker load -i python-pyspark-image.tar.gz # Could be on a different machine
docker run --mount type=bind,source=./../input_file_1.parquet,target=/input_data/main_input_file.parquet --mount type=bind,source=/tmp/dummy_step_python_pyspark_results/,target=/results -i -t linker:dummy_step_python_pyspark
```

## Running with Singularity

Install [`spython` from PyPI](https://github.com/singularityhub/singularity-cli). Then:

```
spython recipe Dockerfile Singularity
singularity build --force python-pyspark-image.sif Singularity
mkdir -p /tmp/dummy_step_python_pyspark_results/
mkdir -p /tmp/dummy_step_python_pyspark_workdir/
singularity run --pwd /workdir -B ../input_file_1.parquet:/input_data/main_input_file.parquet,/tmp/dummy_step_python_pyspark_results/:/results,/tmp/dummy_step_python_pyspark_workdir/:/workdir ./python-pyspark-image.sif
```

Or, using the Docker .tar.gz:

```
docker build -t linker:dummy_step_python_pyspark .
docker save linker:dummy_step_python_pyspark | gzip > python-pyspark-image.tar.gz
singularity build --force python-pyspark-image.sif docker-archive://$(pwd)/python-pyspark-image.tar.gz
mkdir -p /tmp/dummy_step_python_pyspark_results/
mkdir -p /tmp/dummy_step_python_pyspark_workdir/
singularity run --pwd /workdir -B ../input_file_1.parquet:/input_data/main_input_file.parquet,/tmp/dummy_step_python_pyspark_results/:/results,/tmp/dummy_step_python_pyspark_workdir/:/workdir ./python-pyspark-image.sif
```