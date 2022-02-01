from twilio.rest import Client
import pandas as pd 
import numpy as np 
import plotly.express as px
import psutil # CPU info
import plotly.express as px
import multiprocessing as mp
import plotly.graph_objects as go
import time 
import glob
import shutil, os
import json
from re import search
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from twilio.rest import Client
from datetime import datetime
import sys
from distutils.dir_util import copy_tree


# # For automated Messaging init using twilio.
# account_sid = "ACa0e5b5d76caee673cd469d14df89bbb7"
# auth_token = '8f7e7b1899cc3adb72cb5553ba8bcabb'
# client = Client(account_sid, auth_token)

# Takes in a dataframe for one patient resamples to 8hz and retruns that df.
def resample_8_hz(hr,file,all_files):
    upsample_df_hr_list = []
    for idx, i in enumerate(hr["Date"].unique()):
        # Write each date file seperately.
        #hr[hr["Date"]==i].to_csv(folder_path + file + "/" + "PID_" + str(hr["Patient.ID"].unique()[0]) + "_" + "DateID_" + str(idx) + "_" + all_files,index=0)
        # 1. Remove any duplicate timestamps and keep only first occurence of the duplicate
        hr = hr.drop_duplicates(subset=["Time"],keep="first")
        snr_before_resample = (sum(hr[hr["Date"]==i]["X.Acceleration..m.s.s."])/len(hr[hr["Date"]==i]["X.Acceleration..m.s.s."]))**2/(hr[hr["Date"]==i]["X.Acceleration..m.s.s."].std())**2
        start_interp = time.time()
        # 2. Convert to DT format.
        dt_convert_hr = pd.to_datetime(hr.Time,format="%H:%M:%S.%f")
        # Set time as index.
        hr_dt_index = hr.set_index(dt_convert_hr)
        #print("Date Based Shape Before Resampling: ",hr_dt_index[hr_dt_index["Date"]==i].shape)
        # 3. Up sample date wise to 8 HZ -> 0.125 seconds to match acc data.
        hr_upsample = hr_dt_index[hr_dt_index["Date"]==i].resample("0.025S").mean()
        # 4. Interpolate using linear interpolation.
        interpolated = hr_upsample.interpolate(method='linear')
        end_interp = time.time()
        time_interp = end_interp - start_interp
        # Now calculate SNR Aftder Resampling.
        snr_after_resample = (sum(hr_upsample[hr_upsample["Date"]==i]["X.Acceleration..m.s.s."])/len(hr_upsample[hr_upsample["Date"]==i]["X.Acceleration..m.s.s."]))**2/(hr_upsample[hr_upsample["Date"]==i]["X.Acceleration..m.s.s."].std())**2
        # Print comma seperated lines every time to save as text file so it can be later read as csv files.
        print("Patient ID:,",hr["Patient.ID"].unique()[0], ",Date:," , i, ",Shape Before:,","Cols," , hr_dt_index[hr_dt_index["Date"]==i].shape[0], ",SNR Before sampling,",snr_before_resample,",Rows,",hr_dt_index[hr_dt_index["Date"]==i].shape[1],",Shape After:,","Cols,",hr_upsample.shape[0],",Rows,",hr_upsample.shape[1],",SNR After Resample,",snr_after_resample,",Time it Took in (Seconds),",str(time_interp))
        # Need to write Datewise.
        # interpolated.to_csv(folder_path + file + "/" + "Resample_40Hz_PID_" + str(hr["Patient.ID"].unique()[0]) + "_" + str(idx) + "_" + all_files)
        # message = client.messages .create(
        # body =  "Done Interpolating Data" + "For PID: " + str(hr_dt_index["Patient.ID"].unique()[0]) + "For Date: " + str(i), # Message you send
        # from_ = "+19852289336", # Provided phone number.
        # to =    "+17746412663") # Your phone number.
        upsample_df_hr_list.append(hr_upsample)
    df_upsample_hr = pd.concat(upsample_df_hr_list)
    return df_upsample_hr

# For each of the 13 patients calcualte the RMS per row & saves the file as csv.
# Takes in a folder_path.
# Apllies the analysis pipeline for all the partients.
def careportal_resampling_all(folder_path):
    for idx,file in enumerate(os.listdir(folder_path)):
        if file.startswith("RMSPatientID"):
            for all_files in os.listdir(folder_path + file):
                if all_files.startswith("Date_ID_Acc.csv"):
                    start = time.time()
                    start_time = time.time()
                    df = pd.read_csv(folder_path + file + "/" + all_files)
                    # ( 1) Resample data.
                    df_resample = resample_8_hz(df,file,all_files)
                    df_resample.to_csv(folder_path + file + "/" +"Resample_40Hz_" + all_files)
if __name__ == "__main__":
    folder_path = "/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/care-portal-thesis-sub/"
    careportal_resampling_all(folder_path)
