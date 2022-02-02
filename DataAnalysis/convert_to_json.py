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
import plotly
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pandas as pd
from googleapiclient.http import MediaFileUpload


# Add a column to df seperating date and time 1900-01-01 TimeStamp = 11:39:09.625
def split_date_time(hr):
    ts_only = []
    for i in hr["Time"]:
        ts_only.append(i[11:])
    hr["TimeStamp"] = ts_only
    
# Add a column to the dataframe containing 12 hour timestamp.
def convert_ts_human(hr):
    # Convert all timetamps to 12 hour format
    conveted_human_list = []
    for i in hr["Time"]:
        d = datetime.strptime(i.split(" ")[1], "%H:%M:%S.%f")
        conveted_human_list.append(d.strftime("%I:%M:%S %p")) #12 HR FORMAT.
# To filter by Hour and Date&Time. Give it a dataset for one day only apply that filter before feeding.

def unique_time_stamps(df):
    time_stamp_list = [] # get the unique time stamps int he paricular df.
    for idx,val in enumerate(df["Time"]):
        #print("TS: ",val,val[11:13])
        time_stamp_list.append(val[11:13])
    return np.unique(np.array(time_stamp_list))
# Returns a list of time in secods per activity bucket.
def calculate_time_seconds_each_act(hr):
    total_time_each_bucket_seconds = []
    unique_ts_each_bucket = []
    print("Number of buckets ",hr["HR_ACT_ZONE_MORE"].unique())
    bucket_info_list = hr["HR_ACT_ZONE_MORE"].unique()
    for bucket in [0,1,2,-1]:
        print("For BUCKET",bucket)
        # Both should have same number of elements.
        start_ts_hr_list = []
        end_ts_hr_list = []
        time_seconds_list = []
        #print("Bucket",bucket,"Data shape", hr[hr["HR_ACT_ZONE_MORE"]==bucket].shape[0])
        #print("Data = ", hr[hr["HR_ACT_ZONE_MORE"]==bucket])
        unique_ts_beyond_act = unique_time_stamps(hr[hr["HR_ACT_ZONE_MORE"]==bucket])
        unique_ts_each_bucket.append(unique_ts_beyond_act)
        print("UNIQUE TS LIST  = ",len(unique_ts_beyond_act))
        for ts_hour in unique_ts_beyond_act:
            # In order to calculate time we bucket the timestamp by hour and then for each hour find start and end times and take the diff between those and them sum everything.
            val_bool = []
            val = []
            for i in hr[hr["HR_ACT_ZONE_MORE"]==bucket]["TimeStamp"]:
                # Bool Ture if condition is met.
                val_bool.append(i.startswith(ts_hour))
                val.append(i) # Also create a list of actual values.
            # Convert to pandas aeries in order to use where.
            val_series = pd.Series(val_bool)
            start_index = val_series.where(val_series==True).first_valid_index()
            end_index = val_series.where(val_series==True).last_valid_index()
            start_ts = datetime.strptime(val[start_index], "%H:%M:%S.%f") 
            end_ts = datetime.strptime(val[end_index], "%H:%M:%S.%f")
            time_seconds = (end_ts - start_ts).total_seconds()
            start_ts_hr_list.append(start_ts)
            end_ts_hr_list.append(end_ts)
            #print("Each time in seconds",time_seconds)
            time_seconds_list.append(time_seconds/60) # Length of this list will vary based on ts hour info avaliable.
        print("time_seconds_list Time in SECONDS list = ",time_seconds_list,"Length: ",len(time_seconds_list))
        #time_seconds_list
        total_time = sum(time_seconds_list)
        print("Total Time = ",total_time)
        total_time_each_bucket_seconds.append(total_time)
    # Converted text for plot annotations.
    str_text_time_mins = []
    for i in total_time_each_bucket_seconds:
        str_text_time_mins.append(str(int(i)) + " Minutes")
    return total_time_each_bucket_seconds,str_text_time_mins,bucket_info_list

##################################################################
# Calculates MAX, MIN, Average hr Statistics by Day
# Takes in the 
##################################################################
def convert_to_json_hr_stats(patient_ids):
    
    for patient_id in patient_ids:
        print("------------------ For Patient ID " + str(patient_id) + "------------------")
        # GET PATIENT ID RELATED DATES.
        date_id_list = get_dates(patient_id)
        mean_hr_l = []
        max_hr_l = []
        min_hr_l = []
        std_hr_l = []
        hrv_l = []
        # ITERATE OVER EACH DATE FILE.
        for i in date_id_list:
            path = "/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/care-portal-thesis-sub/PatientID_" +str(patient_id) + "/HR_ACT_Resample_40Hz_PID_" + str(patient_id) + "_" + str(i) + "_Date_ID_HR.csv"
            df_hr_zone = pd.read_csv(path)
            # calculate max, min, std,avg, hrv and create json datastructure for it.
            mean_hr = round(df_hr_zone['Heart.Rate..BPM.'].mean(),2)
            max_hr = int(max(df_hr_zone['Heart.Rate..BPM.']))
            min_hr = int(min(df_hr_zone['Heart.Rate..BPM.']))
            std_hr = round(df_hr_zone['Heart.Rate..BPM.'].std(),2)
            hrv = np.sqrt((((60000/df_hr_zone['Heart.Rate..BPM.']).diff())**2).sum())
            mean_hr_l.append(mean_hr)
            max_hr_l.append(max_hr)
            min_hr_l.append(min_hr)
            std_hr_l.append(std_hr)
            hrv_l.append(hrv)

        json_27_stats = {
            "pid": patient_id,
            "dates": date_id_list,
            "mean":mean_hr_l,
            "min": min_hr_l,
            "max": max_hr_l,
            "std": std_hr_l,
            "hrv":hrv_l,
        }
        print("HR STATS:- ",json_27_stats)
    ############################################# FOR FILE WRITES IN JSON FORMAT.############################################
    #     with open('/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/static/plotlycharts/PatientID_'+ str(patient_id) + '/hr_stats_pid_'+ str(patient_id) +'.json', 'w') as f:
    #         json.dump(json_27_stats, f)

##################################################################
# Calculates hourly Activity levels.
# Takes in HR df split by date.
# **** FOR THIS TO WORK WE WOULD NEED "HR_ACT_ZONE_MORE" COLUMN
##################################################################
def calculate_hr_based_activity_levels(hr):
    split_date_time(hr)
    total_time_each_bucket_mins,str_text_time_mins,bucket_info_list = calculate_time_seconds_each_act(hr)
    day_wise_mins.append(total_time_each_bucket_mins)
    day_wise_mins_annotation_fotmat.append(str_text_time_mins)
    bucket_info_day_list.append(bucket_info_list)
    stop_time = time.time()
    day_pandas = pd.DataFrame(day_wise_mins,columns=["LessIntense","ModerateIntensity","HighIntensity","BeyondActivity"])
    day_pandas["Dates"] = date_id_list
    annotation_df = pd.DataFrame(day_wise_mins_annotation_fotmat,columns=["LessIntense","ModerateIntensity","HighIntensity","BeyondActivity"])
    json_Act_levels = {}
    for i in day_pandas["Dates"]:
        json_Act_levels[i] = day_pandas.iloc[i].to_list()
    return json_Act_levels
def daily_hr_stats(df):
    #print("Unique Date IDs ----- " ,df["Date"].unique())
    # date_id_list = get_dates(patient_id)
    mean_hr_l = []
    max_hr_l = []
    min_hr_l = []
    std_hr_l = []
    hrv_l = []
    for date in df["Date"].unique(): # Iterate over each date.
        # filter df by date
        print("DF BY DATE \n", df[df["Date"]==date])
        date_filtered_df = df[df["Date"]==date]
        # calculate max, min, std,avg, hrv and create json data structure for it.
        mean_hr = round(date_filtered_df['Heart.Rate..BPM.'].mean(),2)
        max_hr = int(max(date_filtered_df['Heart.Rate..BPM.']))
        min_hr = int(min(date_filtered_df['Heart.Rate..BPM.']))
        std_hr = round(date_filtered_df['Heart.Rate..BPM.'].std(),2)
        hrv = np.sqrt((((60000/date_filtered_df['Heart.Rate..BPM.']).diff())**2).sum())
        mean_hr_l.append(mean_hr)
        max_hr_l.append(max_hr)
        min_hr_l.append(min_hr)
        std_hr_l.append(std_hr)
        hrv_l.append(hrv)
    json_27_stats = {
        "pid": patient_folder['title'],
        "dates": df["Date"].unique().tolist(),
        "mean":mean_hr_l,
        "min": min_hr_l,
        "max": max_hr_l,
        "std": std_hr_l,
        "hrv":hrv_l,
        }
    return json_27_stats
    
##################################################################
# Calculates MAX, MIN, Average hr Statistics by Hour
##################################################################

#######################################################################################
# Writes a json file to local computer and then uploads the file to google drive.
#######################################################################################
def upload_file_google_drive(json_27_stats,patient_folder,json_filename):
    # 1. Write file to local folder.
    with open("/Users/shehjarsadhu/Desktop/SeperateDataJSON/" + patient_folder['title'] + json_filename, 'w') as outfile:
        json.dump(json_27_stats, outfile)
    # 2. Upload JSON file to google drive.
    gfile = drive.CreateFile({'title':  patient_folder['title'] + json_filename,'parents': [{'id':patient_folder['id']}]})
    # 3. Read file and set it as the content of this instance.
    gfile.SetContentFile("/Users/shehjarsadhu/Desktop/SeperateDataJSON/" +patient_folder['title'] + '_hr_stats_daily.json')
    gfile.Upload() # Upload the file.

def google_drive_file_read(seperate_Data_folder_id):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() 
    drive = GoogleDrive(gauth)
    
    query = f"'{seperate_Data_folder_id}' in parents and trashed=false"
    print("query = ",type(query))
    fileList = drive.ListFile({'q':query }).GetList()
    # ED EAR - HR Datafolder - List of all HR files using google drive folder.
    print(fileList)
    for patient_folder in fileList:
        # patient_folder['title'] => PatientID_130
        if patient_folder['title'].startswith("Pat"): # If it starts with Pat only.
            print("------------------------------IF CONDITION----------------------------------------")
            print("title: - ",patient_folder['title'],"id: - ",patient_folder['id']) 
            data_files = drive.ListFile({
                'q': f"'{patient_folder['id']}' in parents and trashed=false"
                }).GetList()
            # Gets each file in the PatientID_130/ filder Eg:- HR_all.csv, HR_SDNN.csv etc..
            for sensor_file in data_files:
                if sensor_file["title"].startswith("HR.csv"): 
                    print("sensor_file: ", sensor_file["title"],sensor_file["id"])
                    URL = f"https://drive.google.com/file/d/{sensor_file['id']}/view?usp=sharing"
                    path = 'https://drive.google.com/uc?export=download&id='+URL.split('/')[-2]
                    print("URL = \n",URL)
                    print("PATH = \n",path)
                    df = pd.read_csv(path)
                    #json_27_stats = daily_hr_stats(df)
                    #upload_file_google_drive(json_Act_levels,patient_folder,"_hr_stats_daily.json")
                    json_Act_levels = calculate_hr_based_activity_levels(df)
                    print(json_Act_levels)
                    #upload_file_google_drive(json_Act_levels,patient_folder,"activity_levels.json")


if __name__ == "__main__":
    patient_ids = [27,34,52,53,75,80,88,80,90,106,118,129,131]
    ts_list = ['00' ,'01' ,'02' ,'03' ,'04' ,'05', '06' ,'07', '08' ,'09', '10' ,'11' ,'12' ,'13', '14', '15', '16' ,'17', '18' ,'19', '20', '21','22','23']
    seperate_Data_folder_id = '1lkNmQHD4Qc-Rz1htsbED8TuPuT1U93Z0'
    google_drive_file_read(seperate_Data_folder_id)