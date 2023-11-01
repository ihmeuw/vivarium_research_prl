# Broken Pandas container performing the dummy step

## Running with Docker

```
docker build -t linker:dummy_step_python_pandas_broken .
mkdir -p /tmp/dummy_step_python_pandas_broken_results/
docker run --mount type=bind,source=./../input_file_1.parquet,target=/input_data/input_file.parquet --mount type=bind,source=/tmp/dummy_step_python_pandas_broken_results/,target=/results -e DUMMY_STEP_INPUT_PATH=/input_data/input_file.parquet -e DUMMY_STEP_OUTPUT_PATH=/results/result.parquet -i -t linker:dummy_step_python_pandas_broken
```

Or, going to .tar.gz and back:

```
docker build -t linker:dummy_step_python_pandas_broken .
docker save linker:dummy_step_python_pandas_broken | gzip > python-pandas-broken-image.tar.gz
docker load -i python-pandas-broken-image.tar.gz # Could be on a different machine
docker run --mount type=bind,source=./../input_file_1.parquet,target=/input_data/input_file.parquet --mount type=bind,source=/tmp/dummy_step_python_pandas_broken_results/,target=/results -e DUMMY_STEP_INPUT_PATH=/input_data/input_file.parquet -e DUMMY_STEP_OUTPUT_PATH=/results/result.parquet -i -t linker:dummy_step_python_pandas_broken
```

## Running with Singularity

Install [`spython` from PyPI](https://github.com/singularityhub/singularity-cli). Then:

```
spython recipe Dockerfile Singularity
singularity build --force python-pandas-broken-image.sif Singularity
mkdir -p /tmp/dummy_step_python_pandas_broken_results/
SINGULARITYENV_DUMMY_STEP_INPUT_PATH=/input_data/input_file.parquet SINGULARITYENV_DUMMY_STEP_OUTPUT_PATH=/results/result.parquet singularity run --pwd / -B ../input_file_1.parquet:/input_data/input_file.parquet,/tmp/dummy_step_python_pandas_broken_results/:/results ./python-pandas-broken-image.sif
```

Or, using the Docker .tar.gz:

```
docker build -t linker:dummy_step_python_pandas_broken .
docker save linker:dummy_step_python_pandas_broken | gzip > python-pandas-broken-image.tar.gz
singularity build --force python-pandas-broken-image.sif docker-archive://$(pwd)/python-pandas-broken-image.tar.gz
mkdir -p /tmp/dummy_step_python_pandas_broken_results/
SINGULARITYENV_DUMMY_STEP_INPUT_PATH=/input_data/input_file.parquet SINGULARITYENV_DUMMY_STEP_OUTPUT_PATH=/results/result.parquet singularity run --pwd / -B ../input_file_1.parquet:/input_data/input_file.parquet,/tmp/dummy_step_python_pandas_broken_results/:/results ./python-pandas-broken-image.sif
```