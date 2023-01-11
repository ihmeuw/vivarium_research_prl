# NOTE: Not all of this file was copied from the VEHSS repository.
# This was to avoid unnecessary dependencies (DisMod) and behaviors (setting the randomness seed).

import numpy as np, matplotlib.pyplot as plt, pandas as pd
import os, sys
import scipy.stats
from . import utils

def drawwise_weighted_proportion(
    df,
    weights='weight',
    draw_cols=[f'draw_{n:03}' for n in range(1000)],
    zero_weight_equal=False
):
    if isinstance(weights, str):
        weights = df[weights]
    if isinstance(weights, pd.DataFrame) and len(weights.columns) == 1:
        weights = weights[weights.columns[0]]

    if isinstance(weights, pd.Series):
        assert len(weights) == len(df)
        if weights.sum() == 0 and zero_weight_equal:
            weights = np.ones(len(df))
        draws = np.dot(weights, df[draw_cols]) / weights.sum()
        return pd.DataFrame(data=np.asarray([draws]), columns=draw_cols, dtype=float)
    else:
        assert weights.index.sort_values().equals(df.index.sort_values())
        weights = weights[draw_cols].copy()
        if zero_weight_equal:
            weights.loc[:, weights.sum(axis=0) == 0] = 1
        draws = (df[draw_cols] * weights).sum(axis=0) / weights.sum(axis=0)
        return pd.DataFrame(draws).T

def distribute_values(low_granularity_values, proportional_values, aggregation_type, high_granularity_weights=None, any_match=True, full_match=True, zero_weight_equal=True):
    """
    Distribute values at a lower level of granularity to a higher level of granularity, using the value
    *proportions* from the proportional_values argument.
    In other words, generate the unique set of higher-granularity values that satisfy these two constraints:
    - For each lower granularity row, the aggregation of that value in the corresponding higher-granularity
      rows equals the original lower-granularity value.
    - Within each group at the lower granularity, the values in the component higher-granularity strata
      are proportional to the proportion values given (the ratios match). Note that this does not guarantee
      that e.g. prevalences are <= 1.
    Aggregation can be either summation '+' (e.g. for populations) or weighted average '*' (e.g. for prevalences).
    For now, weights for a weighted average aggregation must be specified at high granularity. In the weighted
    average case, correlation with the weight can cause normalization to be required; the normalization factor
    for each group as a DataFrame is the second element of the tuple returned.
    If aggregation is summation '+', there may be arbitrary columns in the low_granularity_values and proportional_values;
    the operation will be done on each column.
    If aggregation is weighted average '*', low_granularity_values must have columns draw_001, draw_002, etc. The operation
    will be done on each one of these draws. In the future this could be extended to arbitrary columns, right now it is
    due to the upstream limitation of drawwise_weighted_proportion.
    Proportional values may be missing one or more of the low granularity columns; in that case, they will be applied
    within each set of values of those columns. In the extreme case of this where proportional values do not share
    any columns with the low granularity values, they are applied equally in each low granularity group.
    """
    low_granularity_columns = low_granularity_values.index.names
    assert utils.contains_all_combos(low_granularity_values.index)
    print(f'Starting from values at the {"/".join(low_granularity_columns)} level')
    print(f'Applying proportions at the {"/".join(proportional_values.index.names)} level')
    high_granularity_columns = utils.unique(low_granularity_columns + proportional_values.index.names)
    print(f'Generating values at the {"/".join(high_granularity_columns)} level')
    shared_columns = [c for c in low_granularity_columns if c in proportional_values.index.names]
    if len(shared_columns) > 0:
        print(f'Linking on {"/".join(shared_columns)}')
    else:
        print('Applying proportions within each low-granularity group')

    # Expand proportional_values if it doesn't include (all) the low_granularity_columns
    if not proportional_values.index.names == high_granularity_columns:
        if full_match:
            raise ValueError('Match was not full')
        # Not lower-granularity-group specific
        proportional_values = utils.expand_index_to(proportional_values, low_granularity_values.index, any_match=any_match, full_match=False)\
            .reset_index().set_index(high_granularity_columns)

    df = utils.expand_index_to(low_granularity_values, proportional_values.index)
    assert len(df) == len(proportional_values)

    # Transform proportional_values from their raw values to within-group proportions
    # This is not mathematically necessary, but it means that the normalization factor
    # below is meaningful.
    # In a sum aggregation, after doing this we are guaranteed to have no normalization
    # necessary.
    if aggregation_type == '*':
        proportional_values_group_totals = utils.expand_index_to(
            proportional_values.groupby(low_granularity_columns).mean(), proportional_values.index
        )
    elif aggregation_type == '+':
        proportional_values_group_totals = utils.expand_index_to(
            proportional_values.groupby(low_granularity_columns).sum(), proportional_values.index
        )
    else:
        raise ValueError('Unknown aggregation_type')
    # It's not obvious what to do when there is a non-zero low granularity value but all the
    # proportions that would be used to distribute it are zero. This should really never or
    # almost never happen with prevalences/multiplicative aggregation, but it will be quite
    # common in small groups with sum aggregation.
    # If we are making an assumption that zero weight means equal, we split the lower granularity
    # value evenly.
    if zero_weight_equal:
        proportions_default = 1 / utils.expand_index_to(
            proportional_values.groupby(low_granularity_columns).count(), proportional_values.index
        )
        if aggregation_type == '+':
            # Note: this is not an interesting stat for multiplicative aggregation, because the zero-weight
            # assumption is only used when the weight is zero and therefore doesn't contribute to the prevalence
            # count at all.
            zero_weighted = (df[proportional_values_group_totals == 0].fillna(0).sum() / df.sum()).mean()
            print(f'% of low-granularity total distributed by zero-weight assumption: {zero_weighted:.2%}')
    else:
        # If this default were ever to be used, the assert below about matching the original values would
        # fail anyway.
        assert np.all(proportional_values_group_totals > 0)
        proportions_default = 0

    assert np.all(proportional_values.notnull())
    assert np.all(proportional_values_group_totals.notnull())
    proportions = (
        proportional_values /
            proportional_values_group_totals
    ).fillna(proportions_default)

    df = df * proportions
    if aggregation_type == '*':
        assert high_granularity_weights is not None
        assert set(high_granularity_weights.index.names) == set(high_granularity_columns)
        assert utils.contains_all_combos(high_granularity_weights.index)
        high_granularity_weights = high_granularity_weights.reorder_levels(df.index.names)
        assert high_granularity_weights.index.sort_values().equals(df.index.sort_values())
        aggregation_function = (
            lambda df: drawwise_weighted_proportion(df, weights=high_granularity_weights.loc[df.index], zero_weight_equal=zero_weight_equal)
        )
    elif aggregation_type == '+':
        assert high_granularity_weights is None, "No weights allowed for a sum aggregation"
        aggregation_function = lambda df: df.sum()
    else:
        raise ValueError('Unknown aggregation_type')

    aggregated_values = utils.groupby_apply_by_iteration(df, low_granularity_columns, aggregation_function)\
        .set_index(low_granularity_columns)
    normalization_factor = (aggregated_values / low_granularity_values).fillna(1)
    if aggregation_type == '+':
        assert np.allclose(normalization_factor.values, 1)
    else:
        expanded_normalization_factor = utils.expand_index_to(normalization_factor, df.index)
        df = df / expanded_normalization_factor

        # Check that our normalization has resulted in the same low-granularity values
        reaggregated_values = utils.groupby_apply_by_iteration(df, low_granularity_columns, aggregation_function)\
            .set_index(low_granularity_columns)
        assert reaggregated_values.index.sort_values().equals(low_granularity_values.index.sort_values())
        assert np.allclose(reaggregated_values.values, low_granularity_values.loc[reaggregated_values.index].values)

    return df, normalization_factor