"""
Module for specifying and converting datatypes when working with
the output of the Vivarium PRL simulation in pandas.
"""

import pandas as pd

ID_PAD_WIDTH = 9 # Width to which to pad the 2nd component of an id when converting to int

def id_str_to_int(id_col_str):
    """Convert a column of string IDs to integer IDs"""
    id_pieces = id_col_str.str.split('_')
    seed_id, sim_id = id_pieces.str[0].astype(int), id_pieces.str[1].astype(int)
    seed_id.loc[sim_id == -1] = 0 # Use single sentinel -1 for all missing ids, regardless of seed
    id_col_int = seed_id * 10**ID_PAD_WIDTH + sim_id
    return id_col_int

def id_int_to_str(id_col_int):
    """Convert a column of integer IDs to string IDs"""
    seed_id, sim_id = id_col_int.divmod(10**ID_PAD_WIDTH)
    id_col_str = seed_id.astype(str) + '_' + sim_id.astype(str)
    return id_col_str

def get_columns_by_dtype(use_categorical='maximal'):
    categorical = [
        'sex', 'race_ethnicity', 'relation_to_household_head', 'housing_type',
        'middle_initial', 'state', 'mailing_address_state',
        'zipcode', 'mailing_address_zipcode',
        'year_of_birth', 'census_year', 'wic_year',
    ]
    optional_categorical = [
        'first_name', 'last_name', 'date_of_birth',
        'street_number', 'street_name', 'unit_number', 'city',
        'mailing_address_street_number', 'mailing_address_street_name',
        'mailing_address_unit_number', 'mailing_address_city',
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
            'simulant_id', 'first_name_id', 'middle_name_id', 'last_name_id',
            'address_id', 'household_id',
        ],
        'category': categorical_cols,
        'int8': ['random_seed', 'state_id'],
        'int16': ['puma'],
#         'int32': ['guardian_1', 'guardian_2'], # This broke with new data like '7359_-1' vs. '-1'
        'float32': ['age', 'guardian_1_address_id', 'guardian_2_address_id'],
#         'float16': ['age'],
    }
    return columns_by_dtype

def convert_string_cats_to_ints(df):
    """Renames categories in select columns to change string categories to ints.
    """
    int_categorical = ['year_of_birth', 'census_year', 'wic_year']
#     int_categorical += ['po_box', 'mailing_address_po_box'] # Also these?
#     int_categorical += ['zipcode', 'mailing_address_zipcode'] # And these?
    for col in int_categorical:
        if col in df and df[col].dtype == 'category':
            df[col] = df[col].cat.rename_categories(df[col].cat.categories.astype(int))

def convert_string_ids_to_ints(df):
    string_id_cols = [col for col in get_columns_by_dtype()['str'] if '_id' in col]
    string_id_cols += ['guardian_1', 'guardian_2'] # These got prepended with random seeds
    for col in string_id_cols:
        if col in df and df[col].dtype == 'object': # Could modify to check for type str instead
            df[col] = id_str_to_int(df[col])

def load_csv_data(filepath, use_categorical='maximal', convert_str_ids=False, **kwargs):
    columns_by_dtype = get_columns_by_dtype(use_categorical)
    col_to_dtype = {col: dtype for dtype, columns in columns_by_dtype.items() for col in columns}
    if 'dtype' not in kwargs:
        kwargs['dtype'] = col_to_dtype
    df = pd.read_csv(filepath, **kwargs)
    # Convert appropriate categories (e.g., years) to integers,
    # since all categories are read in as strings:
    # https://stackoverflow.com/questions/64652975/pandas-read-csv-with-dtype-pd-categoricaldtype-creates-object-categories-ev
    convert_string_cats_to_ints(df)
    if convert_str_ids:
        convert_string_ids_to_ints(df)
    return df
