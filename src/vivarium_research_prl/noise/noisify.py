"""
Module to apply noise to dataframe columns.
"""
from . import corruption, fake_names

def apply_noise_function_to_column(
    df, colname, row_prob, rng, noise_function, args=None, kwargs=None,
    vectorized=True, share_random_state=True, inplace=False
):
    """Apply a noise function that operates on scalars or on pandas Series
    to a fraction of rows in a single column of a dataframe.
    """
    if not inplace:
        df = df.copy()
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
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

def apply_noise_to_column(df, colname, rng, function_args_dict, inplace=False):
    """Apply multiple noise functions to a column, using parameters specified in a dictionary."""
    if not inplace:
        df = df.copy()
    for funckey, params in function_args_dict.items():
        module_name, funcname = funckey.split('.')
        noise_func = getattr(globals()[module_name], funcname)
        apply_noise_function_to_column(
            df, colname, params['row_prob'], rng, noise_func,
            params.get('args'), prams.get('kwargs'),
            params.get('vectorized', True), params.get('share_random_state', True),
            inplace=True
        )
    if not inplace:
        return df

def _locals_globals_test():
    a,b,c=1,2,3 # This is all that's in locals
    return locals(), globals()
