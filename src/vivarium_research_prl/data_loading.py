import pandas as pd
import os
import re
from tqdm import tqdm

def convert_csvs_to_hdf(output_dir, save_dir, nrows=None):
    """Loads all shards stored as .csv.bz2 files in all subdirectories of
    output_directory, converts datatypes to numerics and categoricals,
    concatenates all shards, and saves the concatenated DataFrames to .hdf
    files in save_dir.

    Copied from the notebook 2023_04_04a_large_data_tests_2023_03_16_17_21_09.ipynb
    """
    observer_names = []
    ext = '.csv.bz2'
    seed_length=4 # TODO: Fix this to account for seeds of length 2 or 3 as well
    for dirpath, dirnames, filenames in os.walk(output_dir):
        observer_name = dirpath[dirpath.rindex('/')+1:]
        if observer_name == 'logs':
            continue
        print("="*50)
        print("Loading data from", observer_name, "\n")
        shards = []
        for filename in filenames:
            if filename.endswith(ext):
                filename_root = filename[:-len(ext)]
    #             seed = filename_root[:-seed_length]
                filepath = os.path.join(dirpath, filename)
                shards.append(datatypes.load_csv_data(filepath, convert_str_ids=True, nrows=nrows))
        if shards:
            # Before concatenating the dataframes, we need to make sure they have the same categories
            # in each categorical column, so take the union of categories across shards
            print("\nSetting categories for", observer_name)
            categorical_cols = [col for col in shards[0] if shards[0][col].dtype == 'category']
            for col in categorical_cols:
                categories = shards[0][col].cat.categories
                for shard in shards[1:]:
                    categories = categories.union(shard[col].cat.categories)
                for shard in shards:
                    shard[col] = shard[col].cat.set_categories(categories)
            print("Concatenating data for", observer_name)
            df = pd.concat(shards, ignore_index=True)
            print("Calculating memory usage")
            print(sizemb(df), "MB")
            observer_names.append(observer_name)
            print("Saving data for", observer_name)
            df.to_hdf( \
                f'{save_dir}/{observer_name}.hdf', key=observer_name, \
                format='table', complib='bzip2', complevel=9, \
            )
            # Not sure if I need this, but we can delete dataframes to save memory
            del df
            del shards
    print('\nObservers:', observer_names, '\n')
    return 

def conform_categories(shards): # Operates in place...
    """Take an iterable of dataframes (shards) with identical columns,
    find the union of each of their categorical columns,
    and re-set the categories in each column to the union across shards.
    After this has been done, the dataframes can be concatenated while
    retaining the categorical dtypes, avoiding a memory blow-up from
    conversion to string dtypes.
    """
    # Code copied from:
    # 2023_08_04_check_address_ids_2023_07_28_08_33_09.ipynb
    # TODO: try this instead:
    # https://pandas.pydata.org/docs/reference/api/pandas.api.types.union_categoricals.html
    # Hmm, it looks like that doesn't do what I want -- it concatenates one categorical
    # column at a time, but I don't think I can use it to take the union of categories
    # before concatenating a list of dataframes.
    # So my solution below is probably still the best option for now.
    shards = list(shards)
    categorical_cols = [col for col in shards[0] if shards[0][col].dtype == 'category']
    for col in categorical_cols:
        categories = shards[0][col].cat.categories
        for shard in shards[1:]:
            categories = categories.union(shard[col].cat.categories)
        for shard in shards:
            shard[col] = shard[col].cat.set_categories(categories)
    return shards

def load_shards_and_concatenate(
    observer_dir,
    ext,
    seeds='all',
    filter_query=None,
    transform=None,
    ignore_index=True,
    **pd_read_kwargs
):
    """Loads shards from a directory with the output from a single observer
    and concatenates them. Optionally filters and transforms the data after
    loading and before concatenating. Can load a subset of all shards by
    passing a list of ints to `seeds` to specify which random seeds should
    be loaded. Supports various filetypes for shards (.parquet, .hdf,
    .csv.bz2, .csv), and allows passing keyword arguments
    to the corresponding pandas function that reads the data. For example,
    to save memory and/or time when loading, keyword arguments can be used
    to filter the data before loading a .parquet or .hdf, and for .csv's,
    the number of rows can be limited and/or datatypes can be converted.
    If you want to filter data after loading but before concatenating the shards,
    you can pass a string to `filter_query`, which will then be passed to
    DataFfame.query(). An example use of the `transform` parameter
    would be to pass a function that conforms the categories in a categorical
    column of the shards so that they can be concatenated as dtype 'category'
    instead of getting converted to dtype 'object' because of mismatched
    categories between shards.
    """
    pandas_read = {
        '.parquet': pd.read_parquet,
        '.hdf': pd.read_hdf,
        '.csv.bz2': pd.read_csv,
        '.csv': pd.read_csv,
    }
    shards = {}
    with os.scandir(observer_dir) as scanner:
        for entry in scanner:
            if entry.name.endswith(ext) and entry.is_file():
                # Use regex to identify seed as a string of digits before the extension, e.g.,
                # '9871' in 'social_security_observer_9871.hdf'
                seed = int(re.match(fr'^.+_(\d+){ext}$', entry.name).group(1))
                if seeds != 'all' and seed not in seeds:
                    continue
                shard = pandas_read[ext](entry, **pd_read_kwargs)
                if filter_query:
                    shard = shard.query(filter_query)
                if transform:
                    shard = transform(shard)
                shards[seed] = shard
    df = pd.concat(shards, ignore_index=ignore_index)
    return df
