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
# To filter by Hour and Date&Time. Give it a dataset for one day only apply that filter before feeding.
def unique_time_stamps(df):
    time_stamp_list = [] # get the unique time stamps int he paricular df.
    for idx,val in enumerate(df["Time"]):
        #print("TS: ",val,val[11:13])
        time_stamp_list.append(val[11:13])
    return np.unique(np.array(time_stamp_list))

# Calculates RMS value of 3 float values.
def calculate_rms(x,y,z):
    return np.sqrt(x**2 + y**2+z**2)
# Calculates the lower quantile 0.25% tail of the given accelerometer rms values calcualted based on the calculate_rms(x,y,z) which takes in the x,y,z values of the accelerometer.
# Takes in accelerometer_df for which to calcualte the lower quartile.
# Returns: 0.25,0.5,0.75 quantiles Given the RMS array of Acc x,y,z.
def rms_lower_quantaile_thresh(accelerometer_df):
    rms_list = []
    # For Each accelerometer value in that hour calculate rms append to rms_list. 
    for index, row in accelerometer_df.iterrows():
        # row["X.Acceleration..m.s.s."],row["Y.Acceleration..m.s.s."],row["Z.Acceleration..m.s.s."]
        #print(type(row["Y.Acceleration..m.s.s."]))
        rms = calculate_rms(row["X.Acceleration..m.s.s."],row["Y.Acceleration..m.s.s."],row["Z.Acceleration..m.s.s."])
        rms_list.append(rms)
    # Calculate the quartiles.
    df_rms = pd.DataFrame(rms_list)
    quantiles = df_rms.quantile([0.05,0.5,0.75])
    #print("quantiles: - ",quantiles)
    return quantiles.iloc[0, 0] ,quantiles.iloc[1, 0],quantiles.iloc[2, 0] # Get the 0.05 quantile.


# Takes in acc df and caluclates the Lower quartile of that window of 1Hour Uses rms_lower_quantaile_thresh() to do so.
# Returns 1. thresh_df (Hourly Threshold for the acc df ), 2. df_acc_date_time, 3. df_act_det: With Act detected labels.
def calculate_thresh_window(df_acc):
    # Get list of unique timestamps of each day daubset.
    acc_unique_ts = unique_time_stamps(df_acc)
    df_all_hours_list = []
    for ts in acc_unique_ts: # Time Filter.
        #print("df time",df_acc["Time"])
        new_ts = df_acc["Time"].str.split(" ", n = 1, expand = True)
        df_acc_date_time = df_acc[new_ts[1].str.startswith(ts)]
#         print("Filtered by date: ",i,"time: ",ts, df_acc_date_time.shape, "\n")
        # Calculate threshold in each hour.
        lq_rms,midq_rms,uq_rms = rms_lower_quantaile_thresh(df_acc_date_time)
        #print("Lower Quatile threshold: ",lq_rms)
        act_Det_list =[] # List of 0s and 1s for activity beign detected or not.
        # For each row in the df.
        for idx,row in df_acc_date_time.iterrows():
            #print("row RMS = ",row["RMS(ax,ay,az)"])
            if row["RMS(ax,ay,az)"]>=lq_rms:
                act_Det_list.append(1)  
            else:
                act_Det_list.append(0)
            # DF for that one hour only
        df_acc_date_time["ActDet"] = act_Det_list
#         print("Date and time ",df_acc_date_time["Time"].unique(),df_acc_date_time["Date"].unique())
        df_all_hours_list.append(df_acc_date_time)
#         print("New Df columns : = ",df_acc_date_time.columns)
#         print("After act detection df= ",df_acc_date_time)
    df_act_det = pd.concat(df_all_hours_list)
    #print(df_act_det.head())
    return df_acc_date_time,df_act_det 

if __name__ == "__main__":
    patient_id = 27
    thresh_list = []
    dates = [ 0 , 1  ,2 , 3,  4  ,5  ,6,  7,  8,  9, 10, 11, 12, 13, 14, 15]
    for i in dates:
        # Read each file date wise.
        root_path = "/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/care-portal-thesis-sub/"
        path = root_path + "PatientID_" +str(patient_id) + "/RMS_Resample_40Hz_PID_" + str(patient_id) + "_" + str(i) + "_Date_ID_Acc.csv"
        #print(path)
        df_rms_acc_zone = pd.read_csv(path)
        thresholds_write_path = "/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/care-portal-thesis-sub/DataAnalysis/RMS_Thresholds"
        start_time = time.time()
        df_acc_date_time,df_act_det = calculate_thresh_window(df_rms_acc_zone)
        end_time = time.time()
        df_act_det.to_csv(root_path +"PatientID_" +str(patient_id) + "/RMS_Resample_Act_Det_40Hz_PID_" + str(patient_id) + "_" + str(i) + "_Date_ID_Acc.csv",index=0)
        #thresh_list.append(thresh_df)
        #thresh_df.to_csv(thresholds_write_path + "/" + str(patient_id) +"_date_ID_" + str(i) + "_thresholds_rms.csv" ,index=0)
        print("PatientID," + str(df_rms_acc_zone["Patient.ID"].unique()[0]) + ",DateID," + str(i) + ",Time,"+ str(end_time-start_time)+",Seconds")

    #df_thresh = pd.concat(thresh_list)
