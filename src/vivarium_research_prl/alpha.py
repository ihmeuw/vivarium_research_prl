"""Module with utility functions for alpha testing the Pseudopeople package.
"""

from pseudopeople.configuration import get_configuration

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

def get_zero_column_noise_config():
    config = get_configuration()
    for dataset_config in config.values():
        for column_config in dataset_config['column_noise'].values():
            for noise_config in column_config.values():
                noise_config['probability'] = 0
    return config
