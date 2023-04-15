import pandas as pd
import os
from tqdm import tqdm

def convert_csvs_to_hdf(output_dir, save_dir):
    """Loads all shards stored as .csv.bz2 files in all subdirectories of
    output_directory, converts datatypes to numerics and categoricals,
    concatenates all shards, and saves the concatenated DataFrames to .hdf
    files in save_dir.
    """
    observer_names = []
    nrows = None
    ext = '.csv.bz2'
    seed_length=4
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
