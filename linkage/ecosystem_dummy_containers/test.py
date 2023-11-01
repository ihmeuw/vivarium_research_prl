import subprocess
import os
import shutil

# https://stackoverflow.com/a/185941/
def rm_in_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

user = os.environ["USER"]
singularity_tmp = f"/tmp/singularity_{user}/tmp"
singularity_workdir = f"/tmp/singularity_{user}/workdir"
results_dir = f"/tmp/singularity_{user}/results"
subprocess.run(["mkdir", "-p", singularity_tmp])
subprocess.run(["mkdir", "-p", singularity_workdir])
subprocess.run(["mkdir", "-p", results_dir])
rm_in_directory(singularity_tmp)
rm_in_directory(singularity_workdir)
rm_in_directory(results_dir)

input_file = os.getenv("DUMMY_STEP_TEST_INPUT_FILE", './input_file_2.csv')
input_file_type = input_file.split('.')[-1]

container_engine = os.getenv("DUMMY_STEP_TEST_CONTAINER_ENGINE", 'singularity')

num_steps = 30

import random
random.seed(1234)

implementations = ['python_pandas', 'r' ,'python_pyspark']
if os.getenv("DUMMY_STEP_TEST_INCLUDE_BROKEN", 'false').lower() in ('true', '1', 't'):
    implementations += ['python_pandas_broken']

steps = [
    {
        'implementation': random.choice(implementations),
        'output_file_type': random.choice(['csv', 'parquet'])
    } for _ in range(num_steps)
]

from_tar = os.getenv("DUMMY_STEP_TEST_FROM_TAR", "false").lower() in ('true', '1', 't')
if from_tar:
    for implementation in implementations:
        command = ["docker", "load", "-i", f'./{implementation}/{implementation.replace("_", "-")}-image.tar.gz']
        print(" ".join(command))
        subprocess.check_output(command)

for i, step in enumerate(steps):
    print(step)

    implementation = step['implementation']
    output_file_type = step['output_file_type']
    output_file = f'{results_dir}/result_{i}.{output_file_type}'

    input_path_inside_container = f'/input_data/input_file.{input_file_type}'
    env_var_args = {
        'INPUT_PATH': input_path_inside_container,
        'INPUT_FILE_TYPE': input_file_type,
        'OUTPUT_PATH': output_file.replace(results_dir, '/results'),
        'OUTPUT_FILE_TYPE': output_file_type,
    }
    env_var_args = {
        f'DUMMY_STEP_{k}': v for k, v in env_var_args.items()
    }

    bindings = {
        input_file: input_path_inside_container,
        results_dir: '/results',
        singularity_tmp: '/tmp',
    }

    if implementation == 'python_pyspark':
        bindings[singularity_workdir] = '/workdir'
        workdir = '/workdir'
    else:
        workdir = '/'

    env = {**os.environ}

    if container_engine == "singularity":
        image = f'./{implementation}/{implementation.replace("_", "-")}-image.sif'
        command = [
            "singularity",
            "run",
            "--pwd", workdir,
            "-B", ",".join([f'{k}:{v}' for k, v in bindings.items()]),
            image,
        ]
        env = {**env, **{f'SINGULARITYENV_{k}': v for k, v in env_var_args.items()}}
    elif container_engine == "docker":
        image = f'linker:dummy_step_{implementation}'
        command = [
            "docker",
            "run",
        ]
        for k, v in bindings.items():
            command += ["--mount", f'type=bind,source={k},target={v}']

        for k, v in env_var_args.items():
            command += ["-e", f"{k}={v}"]

        command += ["-i", "-t", image]
    else:
        raise ValueError()

    print(" ".join(command))
    print(env_var_args)
    subprocess.check_output(command, env=env)

    input_file = output_file
    input_file_type = output_file_type

    # Just to ensure that steps aren't communicating in a way they shouldn't
    rm_in_directory(singularity_tmp)
    rm_in_directory(singularity_workdir)
