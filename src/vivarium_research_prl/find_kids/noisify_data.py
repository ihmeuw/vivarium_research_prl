"""
Module for adding noise to the decennial census and WIC data before linking.
"""
from ..noise import noisify, corruption, fake_names

def add_noise_to_wic(df_wic, random_state):
    rng = np.random.default_rng(random_state)
    # Copy the dataframe since we're going to alter it
    df_wic = df_wic.copy()
    
    # First name
    noisify.apply_noise_function_to_column(
        df_wic, 'first_name', 0.01, rng,
        corruption.keyboard_corrupt, (1/6, 1/10), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'first_name', 0.01, rng,
        corruption.phonetic_corrupt, (1/6,), vectorized=False, inplace=True)
    
    # Last name
    noisify.apply_noise_function_to_column(
        df_wic, 'last_name', 0.01, rng,
        corruption.keyboard_corrupt, (1/6.8, 1/10), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'last_name', 0.01, rng,
        corruption.phonetic_corrupt, (1/6.8,), vectorized=False, inplace=True)
    
    # Date of birth
    noisify.apply_noise_function_to_column(
        df_wic, 'date_of_birth', 0.01, rng,
        corruption.swap_month_day, share_random_state=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'date_of_birth', 0.01, rng,
        corruption.keyboard_corrupt, (1/8, 0.02), vectorized=False, inplace=True)
    
    # Zipcode
    noisify.apply_noise_function_to_column(
        df_wic, 'zipcode', 0.01, rng,
        corruption.miswrite_zipcode, (0.04, 0.2, 0.36), inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'zipcode', 0.01, rng,
        corruption.keyboard_corrupt, (0.05, 0.02), vectorized=False, inplace=True)
    
    # Address
    noisify.apply_noise_function_to_column(
        df_wic, 'address', 0.01, rng,
        corruption.keyboard_corrupt, (1/33, 1/10), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'address', 0.01, rng,
        corruption.phonetic_corrupt, (1/33,), vectorized=False, inplace=True)
    
    # Sex
    noisify.apply_noise_function_to_column(
        df_wic, 'sex', 0.01, rng,
        corruption.incorrect_select, (['M', 'F'],), inplace=True,
    )
    
    # Race/Ethnicity
    noisify.apply_noise_function_to_column(
        df_wic, 'race_ethnicity', 0.01, rng,
        corruption.incorrect_select,
        (['Black', 'White', 'Latino', 'Multiracial or Other', 'Asian','AIAN', 'NHOPI'],),
        inplace=True
    )
    
    # Middle name
    noisify.apply_noise_function_to_column(
        df_wic, 'middle_name', 0.01, rng,
        corruption.keyboard_corrupt, (1/6, 1/10), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'middle_name', 0.01, rng,
        corruption.phonetic_corrupt, (1/6,), vectorized=False, inplace=True)
    noisify.apply_noise_function_to_column(
        df_wic, 'middle_name', 0.60, rng,
        corruption.replace_with_missing, share_random_state=False, inplace=True
    )
    
    return df_wic