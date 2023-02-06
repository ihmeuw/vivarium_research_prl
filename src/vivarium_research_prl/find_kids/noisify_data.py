"""
Module for adding noise to the decennial census and WIC data before linking.
"""
import numpy as np
from ..noise import noisify, corruption, fake_names

def add_noise_to_census(df_census, random_state=None):
    rng = np.random.default_rng(random_state)
    # Copy the dataframe since we're going to alter it
    df_census = df_census.copy()

    # First name
    noisify.apply_noise_function_to_column(
        df_census, 'first_name', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column( # Replace random 1% with random fake name
        df_census, 'first_name', 0.01, rng,
        corruption.random_choice, (fake_names.fake_first_names('title'),), inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'first_name', 0.01, rng,
        corruption.phonetic_corrupt, (1/6,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'first_name', 0.01, rng,
        corruption.ocr_corrupt, (1/6,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'first_name', 0.01, rng,
        corruption.keyboard_corrupt, (1/6, 1/10), vectorized=False, inplace=True)

    # Last name
    noisify.apply_noise_function_to_column(
        df_census, 'last_name', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column( # Replace random 1% with random fake name
        df_census, 'last_name', 0.01, rng,
        corruption.random_choice, (fake_names.fake_last_names('title'),), inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'last_name', 0.01, rng,
        corruption.phonetic_corrupt, (1/6.8,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'last_name', 0.01, rng,
        corruption.ocr_corrupt, (1/6.8,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'last_name', 0.01, rng,
        corruption.keyboard_corrupt, (1/6.8, 1/10), vectorized=False, inplace=True)

    # Date of birth
    noisify.apply_noise_function_to_column(
        df_census, 'date_of_birth', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'date_of_birth', 0.01, rng,
        corruption.swap_month_day, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'date_of_birth', 0.01, rng,
        corruption.keyboard_corrupt, (1/8, 0), vectorized=False, inplace=True)

    # Zipcode
    noisify.apply_noise_function_to_column(
        df_census, 'zipcode', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'zipcode', 0.01, rng,
        corruption.miswrite_zipcode, (0.04, 0.2, 0.36), inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'zipcode', 0.01, rng,
        corruption.ocr_corrupt, (1/5,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'zipcode', 0.01, rng,
        corruption.keyboard_corrupt, (1/5, 0), vectorized=False, inplace=True)

    # Address
    noisify.apply_noise_function_to_column(
        df_census, 'address', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'address', 0.01, rng,
        corruption.phonetic_corrupt, (1/33,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'address', 0.01, rng,
        corruption.ocr_corrupt, (1/33,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'address', 0.01, rng,
        corruption.keyboard_corrupt, (1/33, 1/10), vectorized=False, inplace=True)

    # Sex
    noisify.apply_noise_function_to_column(
        df_census, 'sex', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column( # Approximately 1%*(1/2)=0.5% will be different
        df_census, 'sex', 0.01, rng,
        corruption.random_choice, (['Male', 'Female'],), inplace=True,
    )

    # Age
    noisify.apply_noise_function_to_column(
        df_census, 'age', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'age', 0.01, rng,
        corruption.miswrite_age, ([-1, 1],), inplace=True,
    )

    # Race/Ethnicity
    noisify.apply_noise_function_to_column(
        df_census, 'race_ethnicity', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column( # Approximately 1%*(6/7) will be different
        df_census, 'race_ethnicity', 0.01, rng,
        corruption.random_choice,
        (['Black', 'White', 'Latino', 'Multiracial or Other', 'Asian','AIAN', 'NHOPI'],),
        inplace=True
    )

    # Middle initial
    noisify.apply_noise_function_to_column(
        df_census, 'middle_initial', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'middle_initial', 0.01, rng,
        corruption.phonetic_corrupt, (1,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'middle_initial', 0.01, rng,
        corruption.ocr_corrupt, (1,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'middle_initial', 0.01, rng,
        corruption.keyboard_corrupt, (1, 0), vectorized=False, inplace=True)

    return df_census

def add_noise_to_wic(df_wic, random_state=None):
    rng = np.random.default_rng(random_state)
    # Copy the dataframe since we're going to alter it
    df_wic = df_wic.copy()

    # First name
    noisify.apply_noise_function_to_column(
        df_wic, 'first_name', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'first_name', 0.01, rng,
        corruption.phonetic_corrupt, (1/6,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'first_name', 0.01, rng,
        corruption.ocr_corrupt, (1/6,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'first_name', 0.01, rng,
        corruption.keyboard_corrupt, (1/6, 1/10), vectorized=False, inplace=True)

    # Last name
    noisify.apply_noise_function_to_column(
        df_wic, 'last_name', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'last_name', 0.01, rng,
        corruption.phonetic_corrupt, (1/6.8,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'last_name', 0.01, rng,
        corruption.ocr_corrupt, (1/6.8,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'last_name', 0.01, rng,
        corruption.keyboard_corrupt, (1/6.8, 1/10), vectorized=False, inplace=True)

    # Date of birth
    noisify.apply_noise_function_to_column(
        df_wic, 'date_of_birth', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'date_of_birth', 0.01, rng,
        corruption.swap_month_day, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'date_of_birth', 0.01, rng,
        corruption.keyboard_corrupt, (1/8, 0), vectorized=False, inplace=True)

    # Zipcode
    noisify.apply_noise_function_to_column(
        df_wic, 'zipcode', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'zipcode', 0.01, rng,
        corruption.miswrite_zipcode, (0.04, 0.2, 0.36), inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'zipcode', 0.01, rng,
        corruption.ocr_corrupt, (1/5,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'zipcode', 0.01, rng,
        corruption.keyboard_corrupt, (1/5, 0), vectorized=False, inplace=True)

    # Address
    noisify.apply_noise_function_to_column(
        df_wic, 'address', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'address', 0.01, rng,
        corruption.phonetic_corrupt, (1/33,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'address', 0.01, rng,
        corruption.ocr_corrupt, (1/33,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'address', 0.01, rng,
        corruption.keyboard_corrupt, (1/33, 1/10), vectorized=False, inplace=True)

    # Sex
    noisify.apply_noise_function_to_column(
        df_wic, 'sex', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column( # Approximately 1%*(1/2)=0.5% will be different
        df_wic, 'sex', 0.01, rng,
        corruption.random_choice, (['Male', 'Female'],), inplace=True,
    )

    # Race/Ethnicity
    noisify.apply_noise_function_to_column(
        df_wic, 'race_ethnicity', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column( # Approximately 1%*(6/7) will be different
        df_wic, 'race_ethnicity', 0.01, rng,
        corruption.random_choice,
        (['Black', 'White', 'Latino', 'Multiracial or Other', 'Asian','AIAN', 'NHOPI'],),
        inplace=True
    )

    # Middle name
    noisify.apply_noise_function_to_column(
        df_wic, 'middle_name', 0.01, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'middle_name', 0.01, rng,
        corruption.phonetic_corrupt, (1/6,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'middle_name', 0.01, rng,
        corruption.ocr_corrupt, (1/6,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'middle_name', 0.01, rng,
        corruption.keyboard_corrupt, (1/6, 1/10), vectorized=False, inplace=True)

    return df_wic
