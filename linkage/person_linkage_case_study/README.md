# Person linkage case study

This directory contains a case study emulating Census Bureau person linkage methods,
primarily based on public descriptions of the Person Identification Validation System.
For more details, see the notebook files themselves.

To run this, the steps are:
1. Create the appropriate conda environment
2. Run the pipeline, with [Snakemake](https://snakemake.readthedocs.io/en/stable/) or manually

## Setup/install

To essentially exactly replicate the conda environment that was used when making
this case study, run

```
$ conda create --name person_linkage_case_study --file conda_environment_lock_conda.txt
$ conda activate person_linkage_case_study
$ pip install -r conda_environment_lock_pip.txt
# Before running this, make sure you don't have anything weird in your .libPaths(),
# e.g. due to a ~/.Rprofile file. The first thing in your libPaths should the R library of the
# conda environment.
$ Rscript -e "renv::restore(library=.libPaths(), lockfile='./conda_environment_lock_renv.json')"
```

in this directory.
In rare cases that may not work due to a yanked conda package version.

You can *approximately* recreate the environment (e.g. if you want to update
all dependencies) with:

```
$ conda env create -n person_linkage_case_study --file conda_environment.yaml
$ conda activate person_linkage_case_study
# Before running this, make sure you don't have anything weird in your .libPaths(),
# e.g. due to a ~/.Rprofile file. The first thing in your libPaths should the R library of the
# conda environment.
$ Rscript conda_environment_R.R
```

If you do this, you can re-generate the lock files like so:

```
$ conda activate person_linkage_case_study
$ conda list --explicit > conda_environment_lock_conda.txt
# Greps:
# - exclude python packages installed via conda, which are linked by file
# - exclude editable packages
$ pip freeze | grep -v 'file:///' | grep -v '\-e ' > conda_environment_lock_pip.txt
$ Rscript -e "renv::snapshot(type='all', lockfile='./conda_environment_lock_renv.json')"
```

### Spark version

Unfortunately, it isn't possible to install Spark with conda.
Instead, we use a Singularity image.

If you are running on Slurm, you will need to have a "slurm" user in the image,
and some additional libraries installed, which means the Docker Hub image for Spark
won't work for you. In this case, build the custom Singularity image in this directory:

```
$ singularity build --fakeroot spark.sif Singularity
```

If you don't need Slurm inside the image, you can simply do:

```
$ singularity pull --force spark.sif docker://apache/spark@sha256:a1dd2487a97fb5e35c5a5b409e830b501a92919029c62f9a559b13c4f5c50f63
```

If you'd like to update the Singularity image:

```
$ singularity pull --force spark.sif docker://apache/spark:latest
```

and update the SHA in the Singularity file.

The exact singularity pull assumes amd64 architecture.

### (Optional) Spark nodes

You can use the Spark case study environment both to run the script, and to run Spark itself on
the master/worker nodes.
However, for the nodes, all you _need_ is Python, with the same version as you have in your
Spark case study environment.
You can create a separate conda environment for this.

## Run the pipeline, with Snakemake

Now, in your conda environment, simply run:

```
$ snakemake
```

to execute the entire pipeline on the small sample data.
This should take only a few minutes.

You can configure the data size to run with like so:

```
$ snakemake --config data_to_use=ri ri_simulated_population=/path/to/unzipped/simulated/population
```

**However, the larger data sizes will automatically use distributed Dask and Spark,
which currently will only work on a Slurm cluster.**
This is also why conda and Singularity must be used.
You need to make sure that Slurm, conda, and a writable temporary directory are bound
into the Singularity container, with e.g. `--singularity-args "-B /tmp,/opt/slurm/bin"`.

You can also configure Snakemake by creating a `snakemake_config_overrides.yaml` in this directory.
See `snakemake_config_defaults.yaml` and the notebooks themselves for what can be customized.

## Run the pipeline, manually

First, you will need to generate the input files;
look at the `generate_simulated_data` subdirectory and follow the directions
in its README before continuing.

These instructions basically only work on the IHME cluster, because they assume that the
location of your conda, and the location where it creates new conda environments,
both are subdirectories of `/mnt`.

### Base version

Run the notebook `person_linkage_case_study.ipynb`
in the `person_linkage_case_study` environment created above.
Note that the outputs shouldn't be saved to that notebook file,
and you should probably run with Papermill.

Note that you can change both the Python "compute engine" (Pandas or Dask)
and the Splink engine (DuckDB, Spark local, Spark distributed over Slurm nodes).
This can be done by editing the notebook, or by running the notebook directly with Papermill like so:

```
$ papermill person_linkage_case_study.ipynb person_linkage_case_study_small_sample_pandas_duckdb.ipynb -k python3
$ papermill person_linkage_case_study.ipynb person_linkage_case_study_small_sample_dask_spark_distributed.ipynb -p compute_engine dask -p splink_engine spark -k python3
$ papermill person_linkage_case_study.ipynb person_linkage_case_study_ri_dask_spark_local.ipynb -p data_to_use ri -p compute_engine dask -p splink_engine spark -p spark_local True -k python3
```

**However** if you pass any options that require Spark, the notebook needs to be run inside both the conda environment and the Singularity container:

```
$ mkdir /tmp/person_linkage_case_study_spark_$USER
# We don't use "singularity shell" because that runs a non-login shell, so conda wouldn't be on the PATH
# TODO: Binding SSH in is probably not good!
$ singularity run -B /mnt:/mnt,/tmp/person_linkage_case_study_spark_$USER:/tmp,/usr/bin/ssh:/usr/bin/ssh spark.sif bash -l
Singularity> conda activate person_linkage_case_study
(person_linkage_case_study) Singularity> jupyter lab # to run interactively, or
(person_linkage_case_study) Singularity> papermill ... # to run with Papermill
```

### R version

Run the notebook `person_linkage_case_study_small_sample_r.ipynb`
in the `person_linkage_case_study` environment created above.

## Check ground-truth accuracy

The notebook `ground_truth_accuracy.ipynb` uses the ground truth information from pseudopeople
to inspect some metrics about how accurate the linkage was.
