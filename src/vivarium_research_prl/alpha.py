"""Module with utility functions for alpha testing the Pseudopeople package.
"""
import numpy as np
import pseudopeople as psp
import logging
from linetimer import CodeTimer
from .utils import MappingViaAttributes
from pseudopeople.exceptions import ConfigurationError, DataSourceError

# Create a logger for this module, set by default to propagate to higher-level loggers
logger = logging.getLogger(__name__)

# # Define a console handler with a specified format
# console_handler = logging.StreamHandler()
# console_format = logging.Formatter('{asctime} - {name} - {levelname} - {message}', style='{')
# console_handler.setFormatter(console_format)

# # Add handlers to the logger
# logger.addHandler(console_handler)

def generate_datasets(*args, **kwargs) -> MappingViaAttributes:
    """Generate all pseudopeople datasets and return them in a MappingViaAttributes
    mapping, which is a light wrapper for a dictionary enabling easy tab completion
    of dict keys. The keys will be the strings that appear after 'generate_' in the
    function names, and the values will be the datasets. `args` and `kwargs` are
    passed to each of the dataset generation functions.
    """
    code_timer_silent = kwargs.pop('code_timer_silent', False)
    code_timer_unit = kwargs.pop('code_timer_unit', 'm')
    code_timer_logger_func = kwargs.pop('code_timer_logger_func', logger.info)

    def value_or_error(f):
        with CodeTimer(
            f.__name__,
            silent=code_timer_silent,
            unit=code_timer_unit,
            logger_func=code_timer_logger_func
        ):
            try:
                return f(*args, **kwargs)
            except (ConfigurationError, DataSourceError, Exception) as e:
                logger.exception('Exception occurred')
                return e

    generation_fns = (getattr(psp, name) for name in dir(psp) if 'generate' in name)
    data = {f.__name__.replace('generate_', ''): value_or_error(f) for f in generation_fns}
    return MappingViaAttributes(data)

def percent_missing(df):
    return 100 * df.isna().sum() / len(df)

def percent_different_in_columns(df1, df2):
    return 100 * ((df1 != df2)^(df1.isna() & df2.isna())).sum() / len(df1)

def percent_of_rows_with_difference(df1, df2):
    return 100 * ((df1 != df2)^(df1.isna() & df2.isna())).any(axis=1).sum() / len(df1)

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
    config = psp.get_config()
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

def flatten(d: dict)->dict:
    """Recursively flattens a nested dictionary d into a single dictionary
    with tuples for keys. The tuple components of each key are the nested
    keys from the original dict.
    """
    new_dict = {}
    current_tuple = [] # Stack to record nested keys in a tuple
    # Inner function for recursion
    def _flatten(dict_or_val):
        # Base case
        if not isinstance(dict_or_val, dict):
            new_dict[tuple(current_tuple)] = dict_or_val
            return

        # Do a depth-first traversal of the nested dict, tracking the
        # nested keys in the stack
        for key, val in dict_or_val.items():
            current_tuple.append(key)
            _flatten(val)
            current_tuple.pop()

    _flatten(d)
    return new_dict

def pad_flattened_dict(d: dict, pad_val=np.nan)->dict:
    """Pad tuples in a flattened dict d with pad_val at the end, so that
    all tuples in the resulting dict have the same length.
    """
    max_len = max(map(len, d.keys()))
    def pad_tuple(t):
        return (*t, *((max_len - len(t)) * [pad_val]))
    new_dict = {pad_tuple(key): val for key, val in d.items()}
    return new_dict
