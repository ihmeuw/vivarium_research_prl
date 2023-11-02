#!/bin/bash

set -e

cd python_pandas
docker build -t linker:dummy_container_python_pandas .

cd ../python_pyspark
docker build -t linker:dummy_container_python_pyspark .

cd ../r
docker build -t linker:dummy_container_r .