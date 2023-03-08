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

def filter_bad_rows(state_table_df):
    alive =  (state_table_df['cause_of_death'] == 'not_dead')
    # Filter out nonstandard zipcode formats
    five_digit_zip = (state_table_df['zipcode'].str.len() == 5)
    included = alive & five_digit_zip
    return included

def select_random_wic_participants(state_table_df, random_state=None):
    wic_coverage_df = get_wic_coverage_df()
    # Make sure we only initialize with a seed once so that the same
    # seed doesn't get used in every iteration of the for loop
    rng = np.random.default_rng(random_state)
    included = filter_bad_rows(state_table_df)
    included &= state_table_df['age'] < 5 # Only include kids for now
    age_year = np.floor(state_table_df['age'])
    for age in range(5):
        wic_category = 'Infants' if age == 0 else f'{age}-year-old children'
        pop_group = included & (age_year == age)
        pop_size = pop_group.sum() # Number of True's
        included.loc[pop_group] &= (
            rng.random(pop_size) < wic_coverage_df.loc[wic_category, 'population_coverage']
        )
    return included

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
    overall_frac,
    kid_frac,
    random_state=None
):
    rng = np.random.default_rng(random_state) # Always use Generator instead of RandomState
    included = filter_bad_rows(state_table_df)
    num_included = included.sum()
#     unif_rvs = rng.random(len(state_table_df))
#     pd.Series(True, index=state_table_df.index, name='census_respondent')
    under5 = included & (state_table_df['age'] < 5)
    num_under5 = under5.sum() # Number of True's
    over5 = included & ~under5
    num_over5 = over5.sum() #num_included - num_under5 #len(state_table_df) - num_under5
    if num_over5 == 0:
        over5_frac = 0 # Value doesn't matter
    else:
        # Calculate probability of including over-5-year-olds to get correct overall fraction
        over5_frac = overall_frac + (num_under5 / num_over5) * (overall_frac - kid_frac)
    included.loc[under5] &= rng.random(num_under5) < kid_frac
    included.loc[over5] &= rng.random(num_over5) < over5_frac
    return included

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

def generate_census_data(
    state_table_df,
    overall_frac=0.95,
    kid_frac=0.90,
    random_state=None
):
    include_in_census = select_random_census_respondents(
        state_table_df, overall_frac, kid_frac, random_state
    )
    census_df = select_census_columns(state_table_df, include_in_census)
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

###### Things for new, larger, more complete data, starting 2023-03-05 #####

ID_PAD_WIDTH = 9 # Width to which to pad the 2nd component of an id when converting to int

def id_str_to_int(id_col_str):
    """Convert a column of string IDs to integer IDs"""
    id_pieces = id_col_str.str.split('_')
    seed_id, sim_id = id_pieces.str[0].astype(int), id_pieces.str[1].astype(int)
    id_col_int = seed_id * 10**ID_PAD_WIDTH + sim_id
    return id_col_int

def id_int_to_str(id_col_int):
    """Convert a column of integer IDs to string IDs"""
    seed_id, sim_id = id_col_int.divmod(10**ID_PAD_WIDTH)
    id_col_str = seed_id.astype(str) + '_' + sim_id.astype(str)
    return id_col_str

def get_columns_by_dtype(use_categorical='maximal'):
    categorical = [
            'sex', 'race_ethnicity', 'relation_to_household_head', 'housing_type', 'state',
            'middle_initial', 'year_of_birth', 'census_year', 'wic_year',
            'zipcode', 'mailing_address_zipcode',
        ]
    optional_categorical = [
            'date_of_birth', 'first_name',
            'last_name', 'street_number', 'street_name',
            'unit_number', 'city', 'mailing_address_street_number',
            'mailing_address_street_name', 'mailing_address_unit_number',
            'mailing_address_state', 'mailing_address_city',
            'po_box', 'mailing_address_po_box',
        ]

    if not use_categorical: # E.g., False or None
        categorical_cols = []
    if use_categorical == 'natural':
        categorical_cols = categorical
    elif use_categorical == 'maximal':
        categorical_cols = categorical + optional_categorical
    else:
        raise ValueError(f"Unknown categorical option: {use_categorical}")

    columns_by_dtype = {
        'str': [
            'simulant_id', 'first_name_id', 'middle_name_id', 'last_name_id', 'address_id'
        ],
        'category': categorical_cols,
        'int8': ['random_seed', 'state_id'],
        'int16': ['puma'],
        'int32': ['guardian_1', 'guardian_2'],
        'float32': ['age', 'guardian_1_address_id', 'guardian_2_address_id'],
#         'float16': ['age'],
    }
    return columns_by_dtype

def convert_string_id_cols(df):
    string_id_cols = [col for col in get_columns_by_dtype()['str'] if '_id' in col]
    for col in string_id_cols:
        if col in df:
            df[col] = id_str_to_int(df[col])

def load_data(filepath, use_categorical='maximal', convert_str_ids=False, **kwargs):
    columns_by_dtype = get_columns_by_dtype(use_categorical)
    col_to_dtype = {col: dtype for dtype, columns in columns_by_dtype.items() for col in columns}
    if 'dtype' not in kwargs:
        kwargs['dtype'] = col_to_dtype
    df = pd.read_csv(filepath, **kwargs)
    if convert_str_ids:
        convert_string_id_cols(df)
    return df
