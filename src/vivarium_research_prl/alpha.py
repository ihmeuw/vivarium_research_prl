"""Module with utility functions for alpha testing the Pseudopeople package.
"""
import numpy as np
from pseudopeople import get_config

def percent_missing(df):
    return 100 * df.isna().sum() / len(df)

def percent_different_in_columns(df1, df2):
    return 100 * (df1 != df2).sum() / len(df1)

def percent_of_rows_with_difference(df1, df2):
    return 100 * (df1 != df2).any(axis=1).sum() / len(df1)

def compare_columns(df1, df2, colname, notna=False):
    if notna:
        notna = df1[colname].notna() & df2[colname].notna()
        return df1[colname].loc[notna].compare(df2[colname].loc[notna])
    else:
        return df1[colname].compare(df2[colname])

def index_is_consecutive(df):
    index = df.index
    return (index == np.arange(len(index))).all()

def get_zero_noise_config(row_or_col='both'):
    if row_or_col not in ['row', 'column', 'both']:
        raise ValueError("row_or_col must be 'row', 'column', or 'both'")
    config = get_config()
    for dataset_config in config.values():
        if row_or_col in ['row', 'both']:
            for row_noise_config in dataset_config['row_noise'].values():
                row_noise_config['row_probability'] = 0
        if row_or_col in ['column', 'both']:
            for column_config in dataset_config['column_noise'].values():
                for noise_config in column_config.values():
                    if 'cell_probability' in noise_config:
                        noise_config['cell_probability'] = 0
    return config

def recursive_zero(d):
    """Recursively set all probabilities to 0 in a configuration dictionary.
    Modifies the dictionary in place. This is Abie's solution posted in
    Slack on April 21, 2023.
    """
    if not isinstance(d, dict):
        return

    for k in d.keys():
        if 'probability' in str(k):
            d[k] = 0.0
        else:
            recursive_zero(d[k])
