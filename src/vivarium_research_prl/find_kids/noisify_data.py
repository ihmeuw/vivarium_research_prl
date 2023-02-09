"""
Module for adding noise to the decennial census and WIC data before linking.
"""
import numpy as np
from ..noise import noisify, corruption, fake_names

def add_noise_to_census(
    df_census,
    row_eligibility_rate = 0.01,
    token_rate_multiplier = 1,
    orig_token_prob = 1/5,
    random_state=None,
):
    rng = np.random.default_rng(random_state)
    # Copy the dataframe since we're going to alter it
    df_census = df_census.copy()

    # First name
    print('first name')
    fname_mean_length = df_census['first_name'].str.len().mean()
    fname_token_rate = token_rate_multiplier / fname_mean_length
    noisify.apply_noise_function_to_column(
        df_census, 'first_name', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column( # Replace random 1% with random fake name
        df_census, 'first_name', row_eligibility_rate, rng,
        corruption.random_choice, (fake_names.fake_first_names('title'),), inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'first_name', row_eligibility_rate, rng,
        corruption.phonetic_corrupt, (fname_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'first_name', row_eligibility_rate, rng,
        corruption.ocr_corrupt, (fname_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'first_name', row_eligibility_rate, rng,
        corruption.keyboard_corrupt, (fname_token_rate, orig_token_prob),
        vectorized=False, inplace=True)

    # Last name
    print('last name')
    lname_mean_length = df_census['last_name'].str.len().mean()
    lname_token_rate = token_rate_multiplier / lname_mean_length
    noisify.apply_noise_function_to_column(
        df_census, 'last_name', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column( # Replace random 1% with random fake name
        df_census, 'last_name', row_eligibility_rate, rng,
        corruption.random_choice, (fake_names.fake_last_names('title'),), inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'last_name', row_eligibility_rate, rng,
        corruption.phonetic_corrupt, (lname_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'last_name', row_eligibility_rate, rng,
        corruption.ocr_corrupt, (lname_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'last_name', row_eligibility_rate, rng,
        corruption.keyboard_corrupt, (lname_token_rate, orig_token_prob),
        vectorized=False, inplace=True)

    # Date of birth
    print('DOB')
    dob_token_rate = token_rate_multiplier / len('yyyymmdd')
    noisify.apply_noise_function_to_column(
        df_census, 'date_of_birth', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'date_of_birth', row_eligibility_rate, rng,
        corruption.swap_month_day, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'date_of_birth', row_eligibility_rate, rng,
        corruption.keyboard_corrupt, (dob_token_rate, 0), # Don't add additional characters to DOB
        vectorized=False, inplace=True)

    # Zipcode
    print('zip')
    zipcode_len = 5
    zipcode_token_rate = token_rate_multiplier / zipcode_len
    # Define relative error rates between first 2 digits, middle digit, last 2 digits
    zipcode_token_weights = np.array([1,4,10])
    zipcode_token_probs = zipcode_token_rate * zipcode_token_weights / zipcode_token_weights.mean()
    noisify.apply_noise_function_to_column(
        df_census, 'zipcode', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'zipcode', row_eligibility_rate, rng,
        corruption.miswrite_zipcode, zipcode_token_probs, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'zipcode', row_eligibility_rate, rng,
        corruption.ocr_corrupt, (zipcode_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'zipcode', row_eligibility_rate, rng,
        corruption.keyboard_corrupt, (zipcode_token_rate, 0), # Don't add extra characters to zip
        vectorized=False, inplace=True)

    # Address
    print('address')
    address_mean_length = df_census['address'].str.len().mean()
    address_token_rate = token_rate_multiplier / address_mean_length
    noisify.apply_noise_function_to_column(
        df_census, 'address', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'address', row_eligibility_rate, rng,
        corruption.phonetic_corrupt, (address_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'address', row_eligibility_rate, rng,
        corruption.ocr_corrupt, (address_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'address', row_eligibility_rate, rng,
        corruption.keyboard_corrupt, (address_token_rate, orig_token_prob),
        vectorized=False, inplace=True)

    # Sex
    print('sex')
    noisify.apply_noise_function_to_column(
        df_census, 'sex', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column( # Approximately 1%*(1/2)=0.5% will be different
        df_census, 'sex', row_eligibility_rate, rng,
        corruption.random_choice, (['Male', 'Female'],), inplace=True,
    )

    # Age
    print('age')
    noisify.apply_noise_function_to_column(
        df_census, 'age', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'age', row_eligibility_rate, rng,
        corruption.miswrite_age, ([-2, -1, 1, 2],), inplace=True,
    )

    # Race/Ethnicity
    print('race/ethnicity')
    noisify.apply_noise_function_to_column(
        df_census, 'race_ethnicity', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column( # Approximately 1%*(6/7) will be different
        df_census, 'race_ethnicity', row_eligibility_rate, rng,
        corruption.random_choice,
        (['Black', 'White', 'Latino', 'Multiracial or Other', 'Asian','AIAN', 'NHOPI'],),
        inplace=True
    )

    # Middle initial
    print('middle initial')
    middle_initial_length = 1
    mi_token_rate = token_rate_multiplier / middle_initial_length
    noisify.apply_noise_function_to_column(
        df_census, 'middle_initial', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'middle_initial', row_eligibility_rate, rng,
        corruption.phonetic_corrupt, (mi_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'middle_initial', row_eligibility_rate, rng,
        corruption.ocr_corrupt, (mi_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_census, 'middle_initial', row_eligibility_rate, rng,
        corruption.keyboard_corrupt, (mi_token_rate, 0), # Don't add extra characters to middle initial
        vectorized=False, inplace=True)

    return df_census

def add_noise_to_wic(
    df_wic,
    row_eligibility_rate = 0.01,
    token_rate_multiplier = 1,
    orig_token_prob = 1/5,
    random_state=None,
):
    rng = np.random.default_rng(random_state)
    # Copy the dataframe since we're going to alter it
    df_wic = df_wic.copy()

    # First name
    print('first name')
    fname_mean_length = df_wic['first_name'].str.len().mean()
    fname_token_rate = token_rate_multiplier / fname_mean_length
    noisify.apply_noise_function_to_column(
        df_wic, 'first_name', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'first_name', row_eligibility_rate, rng,
        corruption.phonetic_corrupt, (fname_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'first_name', row_eligibility_rate, rng,
        corruption.ocr_corrupt, (fname_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'first_name', row_eligibility_rate, rng,
        corruption.keyboard_corrupt, (fname_token_rate, orig_token_prob),
        vectorized=False, inplace=True)

    # Last name
    print('last name')
    lname_mean_length = df_wic['last_name'].str.len().mean()
    lname_token_rate = token_rate_multiplier / lname_mean_length
    noisify.apply_noise_function_to_column(
        df_wic, 'last_name', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'last_name', row_eligibility_rate, rng,
        corruption.phonetic_corrupt, (lname_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'last_name', row_eligibility_rate, rng,
        corruption.ocr_corrupt, (lname_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'last_name', row_eligibility_rate, rng,
        corruption.keyboard_corrupt, (lname_token_rate, orig_token_prob),
        vectorized=False, inplace=True)

    # Date of birth
    print('DOB')
    dob_token_rate = token_rate_multiplier / len('yyyymmdd')
    noisify.apply_noise_function_to_column(
        df_wic, 'date_of_birth', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'date_of_birth', row_eligibility_rate, rng,
        corruption.swap_month_day, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'date_of_birth', row_eligibility_rate, rng,
        corruption.keyboard_corrupt, (dob_token_rate, 0), # Don't add additional characters to DOB
        vectorized=False, inplace=True)

    # Zipcode
    print('zip')
    zipcode_len = 5
    zipcode_token_rate = token_rate_multiplier / zipcode_len
    # Define relative error rates between first 2 digits, middle digit, last 2 digits
    zipcode_token_weights = np.array([1,4,10])
    zipcode_token_probs = zipcode_token_rate * zipcode_token_weights / zipcode_token_weights.mean()
    noisify.apply_noise_function_to_column(
        df_wic, 'zipcode', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'zipcode', row_eligibility_rate, rng,
        corruption.miswrite_zipcode, zipcode_token_probs, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'zipcode', row_eligibility_rate, rng,
        corruption.ocr_corrupt, (zipcode_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'zipcode', row_eligibility_rate, rng,
        corruption.keyboard_corrupt, (zipcode_token_rate, 0), # Don't add extra characters to zip
        vectorized=False, inplace=True)

    # Address
    print('address')
    address_mean_length = df_wic['address'].str.len().mean()
    address_token_rate = token_rate_multiplier / address_mean_length
    noisify.apply_noise_function_to_column(
        df_wic, 'address', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'address', row_eligibility_rate, rng,
        corruption.phonetic_corrupt, (address_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'address', row_eligibility_rate, rng,
        corruption.ocr_corrupt, (address_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'address', row_eligibility_rate, rng,
        corruption.keyboard_corrupt, (address_token_rate, orig_token_prob),
        vectorized=False, inplace=True)

    # Sex
    print('sex')
    noisify.apply_noise_function_to_column(
        df_wic, 'sex', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column( # Approximately 1%*(1/2)=0.5% will be different
        df_wic, 'sex', row_eligibility_rate, rng,
        corruption.random_choice, (['Male', 'Female'],), inplace=True,
    )

    # Race/Ethnicity
    print('race/ethnicity')
    noisify.apply_noise_function_to_column(
        df_wic, 'race_ethnicity', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column( # Approximately 1%*(6/7) will be different
        df_wic, 'race_ethnicity', row_eligibility_rate, rng,
        corruption.random_choice,
        (['Black', 'White', 'Latino', 'Multiracial or Other', 'Asian','AIAN', 'NHOPI'],),
        inplace=True
    )

    # Middle name
    print('middle name')
    mname_mean_length = df_wic['middle_name'].str.len().mean()
    mname_token_rate = token_rate_multiplier / mname_mean_length
    noisify.apply_noise_function_to_column(
        df_wic, 'middle_name', row_eligibility_rate, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'middle_name', row_eligibility_rate, rng,
        corruption.phonetic_corrupt, (mname_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'middle_name', row_eligibility_rate, rng,
        corruption.ocr_corrupt, (mname_token_rate,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'middle_name', row_eligibility_rate, rng,
        corruption.keyboard_corrupt, (mname_token_rate, orig_token_prob),
        vectorized=False, inplace=True)

    return df_wic
