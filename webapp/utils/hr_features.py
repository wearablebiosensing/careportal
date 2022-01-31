

import pandas as pd
import numpy as np

# Takes in a string file path recieved from database query and returns average heart rate for entire file.
def df_describe(file_path):
    df = pd.read_csv(file_path)
    return df.describe()
# Takes in df by day and calculates HRV.
def calculate_hrv(df):
    hrv = np.sqrt((df['(SSDRR)^2']).sum()/len(df))
    return hrv
    
# Takes in df by day and calculates HR.
def calculate_mean_hr(df):
    return df['Heart.Rate..BPM.'].mean()
