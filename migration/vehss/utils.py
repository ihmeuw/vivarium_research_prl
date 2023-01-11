import itertools
import numpy as np, pandas as pd
from collections import OrderedDict

def unique(the_list):
    """
    Uniqs a list without losing order.
    """
    return list(OrderedDict.fromkeys(the_list))

def all_combinations(values, min_size=1):
    """
    All unique combinations of the elements in a list.
    By default, does not include the empty list; this can be customized with the
    min_size parameter.
    """
    # Based on https://stackoverflow.com/a/5898031/5981641
    result = []
    for L in range(min_size, len(values) + 1):
        for subset in itertools.combinations(values, L):
            result.append(list(subset))
    return result

def index_from_product_of_index(index):
    return pd.MultiIndex.from_product(
        [index.get_level_values(c).unique() for c in index.names]
    )

def update_where(df, column, condition, new_value, only_updates_nans=False):
    """
    Updates a column in a dataframe according to a condition, while also printing
    how many values were changed. If only_updates_nans=True, will raise an AssertionError
    if any non-nan values try to be updated by this.
    """
    previous = df[column].copy()
    df[column] = np.where(condition, new_value, previous)
    changed = (previous != df[column]) & (~(previous.isnull() & df[column].isnull()))
    if only_updates_nans:
        # Did not conflict with any already existing info in that column
        assert previous[changed].isnull().all()
    print(f'Changed {changed.sum()} {"null " if only_updates_nans else ""}values of {column}')

def add_mean_ui(df, suffix=''):
    """
    Adds mean and UI (equal-tailed) to a dataframe containing draws.
    """
    draws = df.filter(like='draw_')
    if len(suffix) > 0:
        draws = draws.loc[:, draws.columns.str.endswith(suffix)]
    df['mean' + suffix] = draws.mean(axis=1)
    df['lb' + suffix] = np.percentile(draws, 2.5, axis=1)
    df['ub' + suffix] = np.percentile(draws, 97.5, axis=1)

    return df

def mean_ui(draws):
    return (draws.mean(), np.percentile(draws, 2.5), np.percentile(draws, 97.5))

def drop_draws(df):
    return df.loc[:, ~df.columns.str.startswith('draw_')]

# Pandas utils, mainly generalizing functions to the empty-set-of-columns case
# which has to be special-cased in the current Pandas API.
def groupby_column_list(df, column_list):
    """
    Like df.groupby(column_list), except:
    1. Returns an iterator, not a GroupBy object. Do not modify the groups in place!
    2. Handles an empty list of columns (single group with the entire data in it).
    3. Instead of yielding a tuple of column values, yields a dictionary with column names
    as the keys.
    """
    if len(column_list) == 0:
        return [({}, df)]
    else:
        return ((_column_values_dictionary(column_list, values), df_g) for values, df_g in df.groupby(column_list))

def groupby_apply_by_iteration(df, column_list, func, *args, **kwargs):
    """
    Like df.groupby(column_list).apply(func, *args, **kwargs), except:
    1. The function must have no side effects and return a DataFrame. The result will include
    only the columns in the returned dataframe plus those in column_list.
    2. Because of #1, it is much faster.
    3. The grouped columns do not become an index in the output.
    4. Column list may be empty, in which case a single row with index 0 contains the
    results of func called with the whole dataframe.
    """
    groups = groupby_column_list(df, column_list)

    result_list = []
    for column_values, group_rows in groups:
        group_result = func(group_rows, *args, **kwargs)

        if isinstance(group_result, pd.Series):
            group_result = pd.DataFrame(group_result).T

        for c, v in column_values.items():
            group_result[c] = v

        # Reorder: put the grouped columns first
        group_result = group_result[column_list + [c for c in group_result.columns if c not in column_list]]
        result_list.append(group_result)

    if len(result_list) == 0:
        return pd.DataFrame()
    return pd.concat(result_list, ignore_index=True)

def groupby_agg(df, column_list, *args, **kwargs):
    """
    Like df.groupby(column_list).agg(*args, **kwargs), except:
    1. The grouped columns do not become an index in the output.
    2. Column list may be empty, in which case a single row with index 0 contains the
    values for the whole dataframe.
    """
    if len(column_list) > 0:
        return df.groupby(column_list).agg(*args, **kwargs).reset_index()

    return df.groupby(lambda x: True).agg(*args, **kwargs).reset_index(drop=True)

def merge(df1, df2, on, *args, **kwargs):
    """
    Like df1.merge(df2, on=on, *args, **kwargs), except:
    1. If on is empty, all rows are considered to match (a Cartesian product).
    """
    if len(on) > 0:
        return df1.merge(df2, on=on, *args, **kwargs)

    # Apparently the best way to do this in Pandas
    # https://stackoverflow.com/a/46895905/
    df1 = df1.copy()
    df2 = df2.copy()
    df1['key'] = 0
    df2['key'] = 0
    return df1.merge(df2, on='key', *args, **kwargs).drop(columns=['key'])

def _column_values_dictionary(column_list, values):
    values = _ensure_tuple(values)
    assert len(column_list) == len(values)
    return dict(zip(column_list, values))

def _ensure_tuple(obj):
    if not isinstance(obj, tuple):
        return (obj,)
    return obj

# Gets values from a dataframe without caring about whether the name passed is a column
# or an index level.
def values_from_column_or_index(df, name):
    if name in df.index.names:
        return df.index.get_level_values(name)
    else:
        return df[name]

def diff_dfs(df1, df2):
    """
    Returns rows not in common between two DataFrames.
    """
    assert len(df1) == len(df1.drop_duplicates())
    assert len(df2) == len(df2.drop_duplicates())
    return pd.concat([df1, df2]).drop_duplicates(keep=False)

def expand_index_to(df, index, any_match=True, full_match=True):
    """
    Changes a df to have a specified index, assuming that the df's index already contains
    some of the index's levels, by duplicating the rows that match on the subset it already
    contains.

    If full_match is True, the desired index must include everything already in the index.
    """
    # First, do some checks
    # Current and desired index have at least one column in common
    common_columns = [c for c in df.index.names if c in index.names]
    if any_match:
        assert len(common_columns) > 0
    if full_match:
        assert len(common_columns) == len(df.index.names)
    # Current and desired index are both unique and have all the same
    # values in the overlapping columns
    assert np.all(~df.index.duplicated())
    assert np.all(~index.duplicated())
    index_as_df = index.to_frame(index=False)
    df_index_as_df = df.index.to_frame(index=False)
    if any_match:
        assert len(diff_dfs(index_as_df[common_columns].drop_duplicates(), df_index_as_df[common_columns].drop_duplicates())) == 0

    return merge(index_as_df, df.reset_index(), on=common_columns, validate='m:1' if full_match else 'm:m')\
        .set_index(index.names)

def all_combos_of_index(index):
    return pd.MultiIndex.from_product([index.get_level_values(c).unique() for c in index.names], names=index.names)

def contains_all_combos(index):
    return index.sort_values().equals(all_combos_of_index(index).sort_values())
