import numpy as np
import pandas as pd

def get_wic_coverage_df():
    wic_coverage_df = pd.DataFrame(
        {
            'eligibility': [43.3, 43.9, 45.6, 45.0, 47.7, 38.2, 29.8],
            'coverage': [98.4, 64.9, 48.5, 43.7, 24.5, 52.3, 84.7],
        },
        index=[
            'Infants',
            '1-year-old children',
            '2-year-old children',
            '3-year-old children',
            '4-year-old children',
            'Pregnant women',
            'Postpartum women',
        ]
    ) / 100
    
    wic_coverage_df.rename_axis('category', inplace=True)
    wic_coverage_df['population_coverage'] = (
        wic_coverage_df['eligibility'] * wic_coverage_df['coverage']
    )
    return wic_coverage_df

def select_random_wic_participants(state_table_df, random_state=None):
    wic_coverage_df = get_wic_coverage_df()
    # Make sure we only initialize with a seed once so that the same
    # seed doesn't get used in every iteration of the for loop
    rng = np.random.default_rng(random_state)
    include_in_wic = pd.Series(False, index=state_table_df.index, name='wic_participant')
    age_year = np.floor(state_table_df['age'])
    for age in range(5):
        wic_category = 'Infants' if age == 0 else f'{age}-year-old children'
        pop_group = (age_year == age) & (state_table_df['cause_of_death'] == 'not_dead')
        pop_size = pop_group.sum() # Number of True's
        include_in_wic.loc[pop_group] = (
            rng.random(pop_size) < wic_coverage_df.loc[wic_category, 'population_coverage']
        )
    return include_in_wic

def select_wic_columns(state_table_df, rows_to_include=None):
    if rows_to_include is None:
        rows_to_include = state_table_df.index
    columns_for_wic = (
        ['first_name', 'middle_name', 'last_name', 'date_of_birth']
        + ['sex', 'race_ethnicity']
        + ['address', 'zipcode', 'household_id']
    )
    wic_df = state_table_df.loc[rows_to_include, columns_for_wic]
    wic_df['date_of_birth'] = wic_df['date_of_birth'].dt.strftime('%Y-%m-%d')
    wic_df['wic_id'] = range(1, 1+len(wic_df))
    return wic_df

def generate_wic_data(state_table_df, random_state=None):
    include_in_wic = select_random_wic_participants(state_table_df, random_state)
    wic_df = select_wic_columns(state_table_df, include_in_wic)
    return wic_df

def select_random_census_respondents(
    state_table_df,
    overall_frac=0.95,
    kid_frac=0.90,
    random_state=None
):
    rng = np.random.default_rng(random_state) # Always use Generator instead of RandomState
    include_in_census =  (state_table_df['cause_of_death'] == 'not_dead')
#     unif_rvs = rng.random(len(state_table_df))
#     pd.Series(True, index=state_table_df.index, name='census_respondent')
    under5 = include_in_census & (state_table_df['age'] < 5)
    num_under5 = under5.sum() # Number of True's
    num_over5 = len(state_table_df) - num_under5
    if num_over5 == 0:
        over5_frac = 0 # Value doesn't matter
    else:
        # Calculate probability of including over-5-year-olds to get correct overall fraction
        over5_frac = overall_frac + (num_under5 / num_over5) * (overall_frac - kid-frac)
    include_in_census.loc[under5] &= rng.random(num_under5) < kid_frac
    include_in_census.loc[~under5] &= rng.random(num_over5) < over5_frac
    return include_in_census

def select_census_columns(state_table_df, rows_to_include=None):
    if rows_to_include is None:
        rows_to_include = state_table_df.index
    columns_for_census = (
        ['first_name', 'middle_name', 'last_name', 'date_of_birth']
        + ['age', 'sex', 'race_ethnicity']
        + ['relation_to_household_head', 'address', 'zipcode']
    )
    census_df = state_table_df.loc[rows_to_include, columns_for_census]
    census_df['middle_name'] = census_df['middle_name'].str[0]
    census_df.rename(columns={'middle_name': 'middle_initial'}, inplace=True)
    census_df['age'] = np.floor(census_df['age'])
    census_df['date_of_birth'] = census_df['date_of_birth'].dt.strftime('%Y-%m-%d')
#     census_df = (
#         state_table_df.loc[rows_to_include, columns_for_census]
#         .assign(
#             middle_name=lambda df: df['middle_name'].str[0],
#             age=lambda df: np.floor(df['age']),
#             date_of_birth=lambda df: df['date_of_birth'].dt.strftime('%Y-%m-%d')
#         )
#         .rename(columns={'middle_name': 'middle_initial'})
#     )
    return census_df

def omit_kids_from_census(census_df, frac=0.05, random_state=None):
    """Generate decennial census data to link by dropping additional kids.
    
    Note:
    `frac` is the fraction of *additional* kids to drop, beyond kids that
    have already been omitted from census_df (e.g., kids that were already
    omitted within the simulation if `census_df` is the file output by the
    decennial census observer.)
    
    For example, in the file output on 10/14/22, there were
    already about 4.7% of kids missing, so the default `frac` of .02
    will drop an additional 2% of the remaining kids, for a total of
    1-(1-.047)*(1-0.02) = 6.6% of kids omitted.
    """
    rng = np.random.default_rng(random_state) # Always use Generator instead of RandomState
    under_five_df = census_df.loc[census_df['age'] < 5]
    rows_to_drop = under_five_df.sample(frac=frac, random_state=rng)
    altered_census_df = census_df.drop(rows_to_drop.index)
    return altered_census_df

def get_census_data_with_missing_kids(state_table_df, frac=0.05, random_state=None):
    census_df = omit_kids_from_census(state_table_df, frac, random_state)
    census_df['age'] = np.floor(census_df['age'])
    return census_df
