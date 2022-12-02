"""
# Reproduce data corruption like GeCO

Informed by reading https://dmm.anu.edu.au/geco/flex-data-gen-manual.pdf but not looking at the sourcecode, since it might be in conflict with the license we end up using for this sim.
"""

import numpy as np
import pandas as pd

# OCR corruption

df_ocr = pd.read_csv('ocr-variations-upper-lower.csv', skiprows=[0,1], header=None, names=['ocr_true', 'ocr_err'])

ocr_error_dict = {}
for k, df_k in df_ocr.groupby('ocr_true'):
    ocr_error_dict[k] = list(df_k.ocr_err)
    
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

df_phonetic = pd.read_csv('phonetic-variations.csv', skiprows=[0,1], header=None,
                          names=['where', 'orig', 'new', 'pre', 'post', 'pattern', 'start'])

phonetic_error_dict = {}
for k, df_k in df_phonetic.groupby('orig'):
    phonetic_error_dict[k] = list(df_k.new.str.replace('@', ''))

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

df_qwerty = pd.read_csv('qwerty-keyboard.csv', skiprows=[0,1], header=None)

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
