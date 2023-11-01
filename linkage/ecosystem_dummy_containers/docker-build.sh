#!/bin/bash

set -e

cd python_pandas
docker build -t linker:dummy_step_python_pandas .

cd ../python_pandas_broken
docker build -t linker:dummy_step_python_pandas_broken .

cd ../python_pyspark
docker build -t linker:dummy_step_python_pyspark .

cd ../r
docker build -t linker:dummy_step_r .