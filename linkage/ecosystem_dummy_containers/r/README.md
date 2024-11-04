# R container performing the dummy step

Similar to Pandas, except it requires a writeable /tmp directory, which means the Singularity instructions are a bit different.

## Running with Docker

```
docker build -t linker:dummy_step_r .
mkdir -p /tmp/dummy_step_r_results/
docker run --mount type=bind,source=./../input_file_1.parquet,target=/input_data/main_input_file.parquet --mount type=bind,source=/tmp/dummy_step_r_results/,target=/results -i -t linker:dummy_step_r
```

Or, going to .tar.gz and back:

```
docker build -t linker:dummy_step_r .
docker save linker:dummy_step_r | gzip > r-image.tar.gz
docker load -i r-image.tar.gz # Could be on a different machine
docker run --mount type=bind,source=./../input_file_1.parquet,target=/input_data/main_input_file.parquet --mount type=bind,source=/tmp/dummy_step_r_results/,target=/results -i -t linker:dummy_step_r
```

## Running with Singularity

Install [`spython` from PyPI](https://github.com/singularityhub/singularity-cli). Then:

```
spython recipe Dockerfile Singularity
singularity build --force r-image.sif Singularity
mkdir -p /tmp/dummy_step_r_results/
mkdir -p /tmp/dummy_step_r_tmp/
singularity run --pwd / -B ../input_file_1.parquet:/input_data/main_input_file.parquet,/tmp/dummy_step_r_results/:/results,/tmp/dummy_step_r_tmp/:/tmp ./r-image.sif
```

Or, using the Docker .tar.gz:

```
docker build -t linker:dummy_step_r .
docker save linker:dummy_step_r | gzip > r-image.tar.gz
singularity build --force r-image.sif docker-archive://$(pwd)/r-image.tar.gz
mkdir -p /tmp/dummy_step_r_results/
mkdir -p /tmp/dummy_step_r_tmp/
singularity run --pwd / -B ../input_file_1.parquet:/input_data/main_input_file.parquet,/tmp/dummy_step_r_results/:/results,/tmp/dummy_step_r_tmp/:/tmp ./r-image.sif
```