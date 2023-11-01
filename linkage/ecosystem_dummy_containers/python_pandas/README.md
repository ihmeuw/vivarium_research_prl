# Pandas container performing the dummy step

## Running with Docker

```
docker build -t linker:dummy_step_python_pandas .
mkdir -p /tmp/dummy_step_python_pandas_results/
docker run --mount type=bind,source=./../input_file_1.parquet,target=/input_data/input_file.parquet --mount type=bind,source=/tmp/dummy_step_python_pandas_results/,target=/results -e DUMMY_STEP_INPUT_PATH=/input_data/input_file.parquet -e DUMMY_STEP_OUTPUT_PATH=/results/result.parquet -i -t linker:dummy_step_python_pandas
```

Or, going to .tar.gz and back:

```
docker build -t linker:dummy_step_python_pandas .
docker save linker:dummy_step_python_pandas | gzip > python-pandas-image.tar.gz
docker load -i python-pandas-image.tar.gz # Could be on a different machine
docker run --mount type=bind,source=./../input_file_1.parquet,target=/input_data/input_file.parquet --mount type=bind,source=/tmp/dummy_step_python_pandas_results/,target=/results -e DUMMY_STEP_INPUT_PATH=/input_data/input_file.parquet -e DUMMY_STEP_OUTPUT_PATH=/results/result.parquet -i -t linker:dummy_step_python_pandas
```

## Running with Singularity

Install [`spython` from PyPI](https://github.com/singularityhub/singularity-cli). Then:

```
spython recipe Dockerfile Singularity
singularity build --force python-pandas-image.sif Singularity
mkdir -p /tmp/dummy_step_python_pandas_results/
SINGULARITYENV_DUMMY_STEP_INPUT_PATH=/input_data/input_file.parquet SINGULARITYENV_DUMMY_STEP_OUTPUT_PATH=/results/result.parquet singularity run --pwd / -B ../input_file_1.parquet:/input_data/input_file.parquet,/tmp/dummy_step_python_pandas_results/:/results ./python-pandas-image.sif
```

Or, using the Docker .tar.gz:

```
docker build -t linker:dummy_step_python_pandas .
docker save linker:dummy_step_python_pandas | gzip > python-pandas-image.tar.gz
singularity build --force python-pandas-image.sif docker-archive://$(pwd)/python-pandas-image.tar.gz
mkdir -p /tmp/dummy_step_python_pandas_results/
SINGULARITYENV_DUMMY_STEP_INPUT_PATH=/input_data/input_file.parquet SINGULARITYENV_DUMMY_STEP_OUTPUT_PATH=/results/result.parquet singularity run --pwd / -B ../input_file_1.parquet:/input_data/input_file.parquet,/tmp/dummy_step_python_pandas_results/:/results ./python-pandas-image.sif
```