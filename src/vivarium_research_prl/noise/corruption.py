"""
# Reproduce data corruption like GeCO

Informed by reading https://dmm.anu.edu.au/geco/flex-data-gen-manual.pdf but not looking at the sourcecode, since it might be in conflict with the license we end up using for this sim.

NOTE: Noise functions that take strings as inputs can be vectorized by using pd.Series.str
See the swap_month_day and miswrite_zipcode functions for examples.
"""

import numpy as np
import pandas as pd
import os

# Store directory of this file to use relative filepaths for .csv's
# I'm using this as a solution to a FileNotFoundError on module import
# based on the answer to this StackOverflow question:
# https://stackoverflow.com/questions/61289041/python-import-module-from-directory-error-reading-file
_this_dir = os.path.dirname(__file__)

# Read in corruption data files as publicly available DataFrames

df_ocr = pd.read_csv(
    os.path.join(_this_dir, 'ocr-variations-upper-lower.csv'),
    skiprows=[0,1], header=None, names=['ocr_true', 'ocr_err']
)
df_phonetic = pd.read_csv(
    os.path.join(_this_dir, 'phonetic-variations.csv'),
    skiprows=[0,1], header=None,
    names=['where', 'orig', 'new', 'pre', 'post', 'pattern', 'start']
)
df_qwerty = pd.read_csv(
    os.path.join(_this_dir, 'qwerty-keyboard.csv'),
    skiprows=[0,1], header=None
)

# OCR corruption

def generate_ocr_error_dict(df_ocr=df_ocr):
    ocr_error_dict = {}
    for k, df_k in df_ocr.groupby('ocr_true'):
        ocr_error_dict[k] = list(df_k.ocr_err)
    return ocr_error_dict

ocr_error_dict = generate_ocr_error_dict()
    
def ocr_corrupt(truth, corrupted_pr, random_state=None):
    """
    # Algorithm sketch

    For each token decide if it is OCRed correctly, and if it is not, decide how it goes wrong.

    Since there are tokens of length 1, 2, and 3, how to handle?
    I guess I can start with threes, then twos, then ones, for each location in a string.
    """
    rng = np.random.default_rng(random_state)
    err = ''
    i = 0
    while i < len(truth):
        error_introduced = False
        for token_length in [3,2,1]:
            token = truth[i:(i+token_length)]
            if token in ocr_error_dict and not error_introduced:
                if rng.uniform() < corrupted_pr:
                    err += rng.choice(ocr_error_dict[token])
                    i += token_length
                    error_introduced = True
        if not error_introduced:
            err += truth[i:(i+1)]
            i += 1
    return err

# Hardest one: phonetic corruption
#
# This includes an undocumented microlanguage, with commands like `n;-1;t`
# to mean no using this rule if the character before it is a t.

def generate_phonetic_error_dict(df_phonetic=df_phonetic):
    phonetic_error_dict = {}
    for k, df_k in df_phonetic.groupby('orig'):
        phonetic_error_dict[k] = list(df_k.new.str.replace('@', ''))
    return phonetic_error_dict

phonetic_error_dict = generate_phonetic_error_dict()

def phonetic_corrupt(truth, corrupted_pr, random_state=None):
    rng = np.random.default_rng(random_state)
    err = ''
    i = 0
    while i < len(truth):
        error_introduced = False
        for token_length in [7,6,5,4,3,2,1]:
            token = truth[i:(i+token_length)]
            if token in phonetic_error_dict and not error_introduced:
                if rng.uniform() < corrupted_pr:
                    err += rng.choice(phonetic_error_dict[token]) # TODO: only consider possibilities allowed by where, pre, post, pattern, and start values
                    i += token_length
                    error_introduced = True
        if not error_introduced:
            err += truth[i:(i+1)]
            i += 1
    return err

# Keyboard corruption

def generate_qwerty_error_dict(df_qwerty=df_qwerty):
    qwerty_error_dict = {}
    for i in df_qwerty.index:
        for j in df_qwerty.columns:
            val = df_qwerty.loc[i,j]
            if str(val) != 'nan' and val != '#':
                nbrs = []
                for di in [-1,0,1]:
                    for dj in [-1,0,1]:
                        if di != 0 or dj != 0: # only actual nbrs, not val itself
                            if i+di in df_qwerty.index and j+dj in df_qwerty.columns:
                                nbr_val = df_qwerty.loc[i+di, j+dj]
                                if str(nbr_val) != 'nan' and nbr_val != '#':
                                    nbrs.append(nbr_val)
                qwerty_error_dict[val] = nbrs
    return qwerty_error_dict

qwerty_error_dict = generate_qwerty_error_dict()

def keyboard_corrupt(truth, corrupted_pr, addl_pr, random_state=None):
    rng = np.random.default_rng(random_state)
    err = ''
    i = 0
    while i < len(truth):
        error_introduced = False
        for token_length in [1]:
            token = truth[i:(i+token_length)]
            if token in qwerty_error_dict and not error_introduced:
                if rng.uniform() < corrupted_pr:
                    err += rng.choice(qwerty_error_dict[token])
                    if rng.uniform() < addl_pr:
                        err += token
                    i += token_length
                    error_introduced = True
        if not error_introduced:
            err += truth[i:(i+1)]
            i += 1
    return err

def swap_month_day(date, date_format="yyyy-mm-dd"):
    """Swaps month and day in a date or pandas Series of dates.
    The dates must be stored as strings (either a single str or Series of str objects).
    The format of the date(s) must be specified; default is "yyyy-mm-dd",
    and currently no other formats are supported except replacing '-' with
    a different separator like '/'.
    """
    if isinstance(date, pd.Series):
        date = date.str
    date_format = date_format.lower()
    y_idx = date_format.find("yyyy")
    m_idx = date_format.find("mm")
    d_idx = date_format.find("dd")
    if y_idx == -1:
         # in case year format is yy not yyyy
         # NOTE: yy format is not yet implemented below and will raise a ValueError
        y_idx = date_format.find("yy")
        year = date[y_idx:y_idx+2]
    else:
        year = date[y_idx:y_idx+4]
    month = date[m_idx:m_idx+2]
    day = date[d_idx:d_idx+2]
    if y_idx==0 and m_idx==5 and d_idx==8: # e.g. "yyyy-mm-dd" or "yyyy/mm/dd"
        # Use same separators as in original date
        swapped_date = year + date[4] + day + date[7] + month
    else:
        raise ValueError(f"unsupported date format: {date_format}")
    return swapped_date

def miswrite_zipcode(
    zipcode,
    first2_prob,
    middle_prob,
    last2_prob,
    random_state=None
):
    """Randomly change digits in a 5-digit zipcode or pandas Series of 5-digit zipcodes.
    Zipcodes must be stored as strings.
    The probabilities of changing the first 2 digits, middle digit, and last 2 digits
    are separately specified.
    """
    rng = np.random.default_rng(random_state)
    is_series = isinstance(zipcode, pd.Series)
    if is_series:
        zipcode_series = zipcode
        zipcode = zipcode.str
        shape = (len(zipcode_series),5)
    else: # type should be str
        shape = (1,5)
    threshold = np.array([2*[first2_prob] + [middle_prob] + 2*[last2_prob]])
    replace = rng.random(shape) < threshold
    random_digits = rng.choice(list('0123456789'), shape)
    digits = []
    for i in range(5):
        digit = np.where(replace[:,i], random_digits[:,i], zipcode[i])
        if is_series:
            digit = pd.Series(digit, index=zipcode_series.index, name=zipcode_series.name)
        else:
            digit = digit[0]
        digits.append(digit)
    new_zipcode = digits[0] + digits[1] + digits[2] + digits[3] + digits[4]
    return new_zipcode

def random_choice(current_choice, choices=None, replace=True, p=None, shuffle=True, random_state=None):
    # TODO: Add an option to exclude current_choice
    # from the list of choices (easy when current_choice is a scalar,
    # a bit trickier when it's a Series)
    rng = np.random.default_rng(random_state)
    is_series = isinstance(current_choice, pd.Series)
    if is_series:
        shape = len(current_choice)
        if choices is None:
            choices = current_choice.unique()
            choices.sort() # Sort so that p vector can be specified if desired
    elif choices is not None:
        shape = None # if shape = 1, then rng.choice returns returns an array, not a scalar
    else:
        raise ValueError("Must specify choices when current_choice is a scalar")
    new_choice = rng.choice(choices, shape, replace, p, shuffle=shuffle)
    if is_series:
        new_choice = pd.Series(new_choice, index=current_choice.index, name=current_choice.name)
    return new_choice

def add_random_increment(current_value, increment_choices, replace=True, p=None, shuffle=True, random_state=None):
    increment = random_choice(current_value, increment_choices, replace, p, shuffle, random_state)
    new_value = current_value+increment
    return new_value

def miswrite_age(age, increment_choices, p=None, random_state=None):
    """Add a random increment to each age."""
    # TODO: It might be better to do something different when age=0 than when age>0.
    # For ages>0, it's probably more likely to write age-1, but for age=0,
    # it's probably more likely to write age+1. Currently any ages that end up < 0
    # are simply clipped to 0 -- it might be better to make these 1 instead, but
    # this intuition is based on the assumption that increment_choices=[-1,1] and p=None.
    new_age = add_random_increment(age, increment_choices, p=p, random_state=random_state)
    new_age = np.maximum(new_age, 0) # Make sure all ages are non-negative
    return new_age

def replace_with_missing(value, missing_value=np.nan):
    if isinstance(value, pd.Series):
        missing = pd.Series(missing_value, index=value.index, name=value.name)
    else:
        missing = missing_value
    return missing
