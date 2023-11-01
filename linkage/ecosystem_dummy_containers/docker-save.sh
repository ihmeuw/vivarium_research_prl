#!/bin/bash

set -e

docker save linker:dummy_step_python_pandas | gzip > python_pandas/python-pandas-image.tar.gz
docker save linker:dummy_step_python_pandas_broken | gzip > python_pandas/python-pandas-broken-image.tar.gz
docker save linker:dummy_step_python_pyspark | gzip > python_pyspark/python-pyspark-image.tar.gz
docker save linker:dummy_step_r | gzip > r/r-image.tar.gz