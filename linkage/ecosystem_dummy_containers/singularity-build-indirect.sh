#!/bin/bash

set -e

singularity build --force python_pandas/python-pandas-image.sif docker-archive://$(pwd)/python_pandas/python-pandas-image.tar.gz
singularity build --force python_pandas/python-pandas-broken-image.sif docker-archive://$(pwd)/python_pandas/python-pandas-broken-image.tar.gz
singularity build --force python_pyspark/python-pyspark-image.sif docker-archive://$(pwd)/python_pyspark/python-pyspark-image.tar.gz
singularity build --force r/r-image.sif docker-archive://$(pwd)/r/r-image.tar.gz
