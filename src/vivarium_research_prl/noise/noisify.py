"""
Module to apply noise to dataframe columns.
"""

def apply_noise_function_to_column(
    df, colname, row_prob, rng, noise_function, args=(), kwargs={},
    vectorized=True, share_random_state=True, inplace=False
):
    if not inplace:
        df = df.copy()
    """Apply a noise function that operates on scalars or on pandas Series
    to a fraction of rows in a single column of a dataframe.
    """
    corrupted = rng.random(len(df)) < row_prob
    if share_random_state:
        kwargs['random_state'] = rng
    if vectorized:
        df.loc[corrupted, colname] = noise_function(df.loc[corrupted, colname], *args, **kwargs)
    else:
        df.loc[corrupted, colname] = df.loc[corrupted, colname].map(
            lambda x: noise_function(x, *args, **kwargs))
    if not inplace:
        return df
