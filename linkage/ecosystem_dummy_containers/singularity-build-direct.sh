#!/bin/bash

set -e

cd python_pandas
spython recipe Dockerfile Singularity
sudo singularity build --force python-pandas-image.sif Singularity

cd ../python_pandas_broken
spython recipe Dockerfile Singularity
sudo singularity build --force python-pandas-broken-image.sif Singularity

cd ../python_pyspark
# NOTE: singularity works differently with respect to users, so we remove this part
spython recipe Dockerfile | sed 's/su *- *185/# do nothing/' > Singularity
sudo singularity build --force python-pyspark-image.sif Singularity

cd ../r
spython recipe Dockerfile Singularity
sudo singularity build --force r-image.sif Singularity
