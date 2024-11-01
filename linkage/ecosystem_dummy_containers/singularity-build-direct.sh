#!/bin/bash

set -e

cd python_pandas
spython recipe Dockerfile Singularity
sudo singularity build --force python-pandas-image.sif Singularity

cd ../python_pyspark
spython recipe Dockerfile Singularity
sudo singularity build --force python-pyspark-image.sif Singularity

cd ../r
spython recipe Dockerfile Singularity
sudo singularity build --force r-image.sif Singularity
