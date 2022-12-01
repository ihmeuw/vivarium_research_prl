"""
# Reproduce data corruption like GeCO

Informed by reading https://dmm.anu.edu.au/geco/flex-data-gen-manual.pdf but not looking at the sourcecode, since it might be in conflict with the license we end up using for this sim.
"""

import numpy as np
import pandas as pd

df_ocr = pd.read_csv('ocr-variations-upper-lower.csv', skiprows=[0,1], header=None, names=['ocr_true', 'ocr_err'])

ocr_error_dict = {}
for k, df_k in df_ocr.groupby('ocr_true'):
    ocr_error_dict[k] = list(df_k.ocr_err)
    
def ocr_corrupt(truth, corrupted_pr):
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
