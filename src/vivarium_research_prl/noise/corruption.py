"""
# Reproduce data corruption like GeCO

Informed by reading https://dmm.anu.edu.au/geco/flex-data-gen-manual.pdf but not looking at the sourcecode, since it might be in conflict with the license we end up using for this sim.
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
    
def ocr_corrupt(truth, corrupted_pr):
    """
    # Algorithm sketch

    For each token decide if it is OCRed correctly, and if it is not, decide how it goes wrong.

    Since there are tokens of length 1, 2, and 3, how to handle?
    I guess I can start with threes, then twos, then ones, for each location in a string.
    """
    err = ''
    i = 0
    while i < len(truth):
        error_introduced = False
        for token_length in [3,2,1]:
            token = truth[i:(i+token_length)]
            if token in ocr_error_dict and not error_introduced:
                if np.random.uniform() < corrupted_pr:
                    err += np.random.choice(ocr_error_dict[token])
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

def phonetic_corrupt(truth, corrupted_pr):
    err = ''
    i = 0
    while i < len(truth):
        error_introduced = False
        for token_length in [7,6,5,4,3,2,1]:
            token = truth[i:(i+token_length)]
            if token in phonetic_error_dict and not error_introduced:
                if np.random.uniform() < corrupted_pr:
                    err += np.random.choice(phonetic_error_dict[token]) # TODO: only consider possibilities allowed by where, pre, post, pattern, and start values
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

def keyboard_corrupt(truth, corrupted_pr, addl_pr):
    err = ''
    i = 0
    while i < len(truth):
        error_introduced = False
        for token_length in [1]:
            token = truth[i:(i+token_length)]
            if token in phonetic_error_dict and not error_introduced:
                if np.random.uniform() < corrupted_pr:
                    err += np.random.choice(qwerty_error_dict[token])
                    if np.random.uniform() < addl_pr:
                        err += token
                    i += token_length
                    error_introduced = True
        if not error_introduced:
            err += truth[i:(i+1)]
            i += 1
    return err
