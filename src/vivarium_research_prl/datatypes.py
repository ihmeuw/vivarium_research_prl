"""
Module for specifying and converting datatypes when working with
the output of the Vivarium PRL simulation in pandas.
"""

import pandas as pd

ID_PAD_WIDTH = 9 # Width to which to pad the 2nd component of an id when converting to int
STR_ID_COLUMNS = (
    'simulant_id', 'household_id', 'guardian_1', 'guardian_2',
    # The rest of these should be gone from post-processed data in final version:
    'first_name_id', 'middle_name_id', 'last_name_id',
    'address_id', 'household_id', 'guardian_id',
)
SSN_COLUMNS = ('ssn', 'itin')

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

def ssn_to_int(ssn):
    """Convert a column of social security numbers from strings
    of the form 'abc-def-ghij' to 32-bit ints of the form abcdefghi.
    NaNs will be replaced by -1. The function also works on string
    SSNs in the format 'abcdefghi'.
    """
    ssn_int = (
        ssn.str.replace('-', '')
        .fillna(-1)
        .astype('int32')
    )
    return ssn_int

def get_columns_by_dtype(use_categorical='maximal'):
    """Returns a dictionary mapping dtypes to lists of columns in the
    pseudopeople data. The datatypes and lists of columns were
    hand-curated for working with intermediate versions of the datasets.
    This function and its main user load_csv_data have mostly become
    obsolete for the final version of the data
    produced for the CODS seminar on April 26, 2023.
    """
    categorical = [
        'relation_to_household_head', 'housing_type',
        'sex', 'race_ethnicity', 'middle_initial',
        'state', 'mailing_address_state', 'employer_state',
        'zipcode', 'mailing_address_zipcode', 'employer_zipcode',
        'year_of_birth', 'census_year', 'wic_year', 'tax_year',
        'event_type', 'tax_form',
    ]
    optional_categorical = [
        'first_name', 'last_name', 'date_of_birth', 'employer_name',
        'street_number', 'street_name', 'unit_number', 'city',
        'mailing_address_street_number', 'mailing_address_street_name',
        'mailing_address_unit_number', 'mailing_address_city',
        'employer_street_number', 'employer_street_name',
        'employer_unit_number', 'employer_city',
        'po_box', 'mailing_address_po_box',
        'event_date', 'survey_date',
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
            'address_id', 'household_id', 'guardian_id', 'ssn',
        ],
        'category': categorical_cols,
        'int8': ['random_seed', 'state_id'],
        'int16': ['puma'],
#         'int32': ['guardian_1', 'guardian_2'], # This broke with new data like '7359_-1' vs. '-1'
        'float32': [
            'age', 'income',
            'guardian_1_address_id', 'guardian_2_address_id'
        ],
#         'float16': ['age'],
    }
    return columns_by_dtype

def merge_series_categories(series, category_mapping):
    """Maps values of a Series to new values and converts the resulting
    Series to type 'category'. If `series` is already of type 'category'
    and has many fewer categories than its length, calling `merge_categories`
    on series.cat will produce the same result (if converted back to a Series)
    but may use less memory and may be faster.
    """
    # https://stackoverflow.com/questions/32262982/pandas-combining-multiple-categories-into-one
    return series.map(category_mapping).astype('category')

def merge_categories(categorical: pd.Categorical, old_cat_to_new_cat):
    """Merge the categories in a pandas Categorical according to the mapping
    old_cat_to_new_cat, which can be a function, dict, or Series, and is passed
    to categorical.categories.map. If the mapping is one-to-one, the categories
    will simply be renamed according to the mapping using categorical.rename_categories.
    Otherwise, categorical.categories is replaced with a new array containing
    the unique categories resulting from the mapping, and the old categories
    are mapped accordingly. If s is a Series of type 'category', calling this function
    on s.cat produces the same result as pandas.Categorical(s.map(old_cat_to_new_cat)),
    but it doesn't convert back to a non-categorical Series as an intermediate
    step, hence typically uses less memory and is faster when the number of categories
    is much smaller than the length of the Series.
    Returns a new Categorical with the merged categories.
    """
    new_cat_array = categorical.categories.map(old_cat_to_new_cat)
    new_cats = new_cat_array.unique()
    if len(new_cats) == len(new_cat_array):
        # one-to-one mapping -> no merging is necessary, just renaming of categories
        # Note: Index.unique() returns values in order of appearance, not sorted,
        # therefore new_cats is guaranteed to equal new_cat_array
        new_categorical = categorical.rename_categories(new_cats)
    else:
        # Map each new category to its index in the categories array, i.e., its code
        new_cat_to_new_code = dict(zip(new_cats, range(len(new_cats))))
        # This array replaces each old category with the index (code) of the new category
        new_code_array = new_cat_array.map(new_cat_to_new_code)
        # The index (code) of the old category is mapped to the index (code) of the new category
        old_code_to_new_code = dict(zip(range(len(new_code_array)), new_code_array))
        # -1 indicates NaN and needs to stay the same in the new codes
        old_code_to_new_code[-1] = -1
        new_codes = categorical.codes.map(old_code_to_new_code)
        new_categorical = pd.Categorical.from_codes(new_codes, new_cats)
    return new_categorical

def convert_category_dtype(df, dtype):
    """Converts the dtype of the categories in categorical columns of df.
    If dtype is a single dtype, the categories in all categorical columns
    in df will be converted to this dtype. Otherwise, dtype must be a dict
    mapping the names of categorical columns to the desired dtype for the
    categories. Note that every column name listed in dtype must be of type
    'category'; otherwise you will get an error.
    Modifies df in place.
    """
    if not isinstance(dtype, dict):
        # Assume a single dtype was passed -- apply it to all categorical columns
        category_cols = df.dtypes.loc[df.dtypes == 'category'].index
        dtype = {col: dtype for col in category_cols}
    for col, col_dtype in dtype.items():
        new_categories = df[col].cat.categories.astype(col_dtype)
        cat_map = dict(zip(df[col].cat.categories, new_categories))
        df[col] = merge_categories(df[col].cat, cat_map)

def convert_string_cats_to_ints(df):
    """Renames categories in select categorical columns to change string categories to ints.
    """
    int_categorical = ['year', 'year_of_birth', 'census_year', 'wic_year', 'tax_year']
#     int_categorical += ['po_box', 'mailing_address_po_box'] # Also these?
#     int_categorical += ['zipcode', 'mailing_address_zipcode'] # And these?
    dtype_dict = {col: int for col in int_categorical if col in df and df[col].dtype == 'category'}
    convert_category_dtype(df, dtype_dict)

def convert_string_ids_to_ints(df, string_id_cols=None, include_ssn=None):
    """Convert string id columns to ints. Convert all string ID columns
    if string_id_cols=None, or convert the explicit columns passed if
    string_id_cols is list-like. The 'ssn' and 'itin' columns are included by default
    when string_id_cols=None, but this can be overridden by passing
    include_ssn=False. If a list of columns is passed explicitly to
    string_id_cols, by default the 'ssn' and 'itin' columns will *not* be included
    unless the list includes 'ssn' or 'itin'. This can be overridden by passing
    include_ssn=True.
    Modifies df in place.
    """
    if string_id_cols is None:
        string_id_cols = STR_ID_COLUMNS
        if include_ssn is None:
            include_ssn = True # If no columns were passed, include SSN by default
    elif include_ssn is None:
        include_ssn = False # If columns were passed explicitly, don't include SSN by default

    # FIXME: I think this fails in the case that string_id_cols contains
    # 'ssn' and/or 'itin'. Regardless of the value of include_ssn, the
    # first for loop will incorrectly apply id_str_to_int to these
    # columns before the 2nd for loop tries to apply ssn_to_int.
    for col in string_id_cols:
        if col in df and df[col].dtype == 'object': # Could modify to check for type str instead
            df[col] = id_str_to_int(df[col])
    if include_ssn:
        for col in SSN_COLUMNS:
            if col in df and df[col].dtype == 'object':
                df[col] = ssn_to_int(df[col])

def string_ids_to_ints(df, string_id_cols=None, include_ssn=None, concat=True):
    """Convert string id columns to ints. Convert all string ID columns
    if cols_to_convert=None, or convert the explicit columns passed if
    cols_to_convert is list-like. The 'ssn' and 'itin' columns are included by default
    when cols_to_convert=None, but this can be overridden by passing
    include_ssn=False. If a list of columns is passed explicitly to
    cols_to_convert, by default the 'ssn' and 'itin' columns will *not* be included
    unless the list includes 'ssn' or 'itin'. This can be overridden by passing
    include_ssn=True (if string_id_cols contains these columns) or
    include_ssn=False (if string_id_cols does not contain these
    columns).
    Returns a new dataframe if `concat` is True, or a list of new
    columns if `concat` is False.
    """
    if string_id_cols is None:
        string_id_cols = STR_ID_COLUMNS
        if include_ssn is None:
            # If no columns were passed, include SSN by default
            include_ssn = True
    # elif include_ssn is None:
    #     # If columns were passed, don't include SSN by default
    #     include_ssn = False

    if include_ssn == True:
        # If necessary, add SSN columns to the list of cols to convert
        string_id_cols = set(string_id_cols).union(SSN_COLUMNS)
    elif include_ssn == False:
        # Remove SSN columns if they were passed but include_ssn was False
        string_id_cols = set(string_id_cols).difference(SSN_COLUMNS)
    elif include_ssn is not None:
        raise ValueError("include_ssn must be True, False, or None")
    # else:
    #     # include_ssn=None, and string_id_cols was passed,
    #     # so use whatever columns were passed
    #     pass

    def get_column(colname):
        if (colname in string_id_cols
                and pd.api.types.is_string_dtype(df[colname])):
            if colname in SSN_COLUMNS:
                return ssn_to_int(df[colname])
            else:
                return id_str_to_int(df[colname])
        else:
            return df[colname]

    columns = [get_column(colname) for colname in df.columns]
    result = pd.concat(columns, axis=1) if concat else columns
    return result

def load_csv_data(filepath, use_categorical='maximal', convert_str_ids=False, **kwargs):
    """Loads a csv with dtypes specified according to the dictionary returned by
    get_columns_by_dtype(use_categorical), and ensures that certain categorical
    columns contain integers for their categories. Optionally converts STR_ID_COLUMNS
    to integer IDs using convert_string_ids_to_ints. Allows passing keywords to
    pandas.read_csv. If 'dtype' is passed as a keyword, it will override the call to
    get_columns_by_dtype.
    """
    if 'dtype' not in kwargs:
        columns_by_dtype = get_columns_by_dtype(use_categorical)
        col_to_dtype = {col: dtype for dtype, columns in columns_by_dtype.items() for col in columns}
        kwargs['dtype'] = col_to_dtype
    df = pd.read_csv(filepath, **kwargs)
    # Convert appropriate categories (e.g., years) to integers,
    # since all categories are read in as strings:
    # https://stackoverflow.com/questions/64652975/pandas-read-csv-with-dtype-pd-categoricaldtype-creates-object-categories-ev
    convert_string_cats_to_ints(df)
    if convert_str_ids:
        convert_string_ids_to_ints(df)
    return df

def convert_dtypes(df, use_categorical='maximal'):
    """Converts dtypes of the columns in df according to the dtypes
    specified in get_columns_by_dtype(use_categorical).
    Modifies df in place.
    """
    columns_by_dtype = get_columns_by_dtype(use_categorical)
    for dtype, columns in columns_by_dtype.items():
        for col in columns:
            if col in df:
                df[col] = df[col].astype(dtype)

def convert_to_int_and_categorical(df):
    """Converts STR_ID_COLUMNS in df to ints using convert_string_ids_to_ints,
    and converts all other 'object' columns to type 'category'.
    Modifies df in place.
    """
    convert_string_ids_to_ints(df)
    for col, dtype in df.dtypes.items():
        if dtype == 'object':
            df[col] = df[col].astype('category')

def to_int_and_categorical(df, exclude=(), concat=True):
    """Converts STR_ID_COLUMNS in df to ints using convert_string_ids_to_ints,
    and converts all other 'object' columns to type 'category'.
    Returns a new dataframe if `concat` is True, or a list of new
    columns if `concat` is False.
    """
    if isinstance(exclude, str):
        exclude = (exclude,)

    # Convert all string id and ssn columns, unless they were excluded
    string_id_cols = (set(STR_ID_COLUMNS + SSN_COLUMNS)
                      .difference(exclude))
    columns = string_ids_to_ints(df, string_id_cols, concat=False)

    def convert_if_necessary(column):
        if (column.name not in exclude
                and pd.api.types.is_object_dtype(column)):
            return column.astype('category')
        else:
            return column

    columns = [convert_if_necessary(column) for column in columns]
    result = pd.concat(columns, axis=1) if concat else columns
    return result
