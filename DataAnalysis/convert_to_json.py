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
##################################################################
def convert_to_json_activity_levels(patient_ids,ts_list):    
    for patient_id in patient_ids:
        json_list = []
        print("------------------ For Patient ID " + str(patient_id) + "------------------")
        # GET PATIENT ID RELATED DATES.
        date_id_list = get_dates(patient_id)
        # ITERATE OVER EACH DATE FILE.
        for i in date_id_list:   
            mean_hr_l = []
            max_hr_l = []
            min_hr_l = []
            std_hr_l = []
            hrv_l = []
            print("--------------------------- For Day: ---------------------------" ,i)
            path = "/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/care-portal-thesis-sub/PatientID_" +str(patient_id) + "/HR_ACT_Resample_40Hz_PID_" + str(patient_id) + "_" + str(i) + "_Date_ID_HR.csv"
            df_hr_zone = pd.read_csv(path)
            ts_unique = unique_time_stamps(df_hr_zone)
            print("Timestamps unique",ts_unique)
            new_ts = df_hr_zone["Time"].str.split(" ", n = 1, expand = True)
            for ts in ts_list:
                df = df_hr_zone[new_ts[1].str.startswith(ts)]
                #print("df time filtered: ",df)
                if df.shape[0] ==0:
                    mean_hr = 0 #round(df['Heart.Rate..BPM.'].mean(),2)
                    max_hr = 0#int(max(df['Heart.Rate..BPM.']))
                    min_hr =0 #int(min(df['Heart.Rate..BPM.']))
                    std_hr =0 #round(df['Heart.Rate..BPM.'].std(),2)
                    hrv = 0#np.sqrt((((60000/df['Heart.Rate..BPM.']).diff())**2).sum())
                else:
                    mean_hr = round(df['Heart.Rate..BPM.'].mean(),2)
                    max_hr = int(max(df['Heart.Rate..BPM.']))
                    min_hr = int(min(df['Heart.Rate..BPM.']))
                    std_hr = round(df['Heart.Rate..BPM.'].std(),2)
                    hrv = np.sqrt((((60000/df['Heart.Rate..BPM.']).diff())**2).sum())
                #print("Mean",mean_hr, "Maximum",max_hr,"Minimum",min_hr,"Std",std_hr,"HRV",hrv)
                mean_hr_l.append(mean_hr)
                max_hr_l.append(max_hr)
                min_hr_l.append(min_hr)
                std_hr_l.append(std_hr)
                hrv_l.append(hrv)
            #print("mean_hr_l =",mean_hr_l,"max_hr_l ",max_hr_l,"min_hr_l",min_hr_l,"std_hr_l",std_hr_l,"hrv_l",hrv_l)
            json_27_stats = {
                "pid": patient_id,
                "dateID": i,
                "TimebyHour": ts_list,
                "mean":mean_hr_l,
                "min": min_hr_l,
                "max": max_hr_l,
                "std": std_hr_l,
                "hrv":hrv_l,
            }
            json_list.append(json_27_stats)
            #print("json_27_stats : ",json_27_stats)
    #     print("HR STATS:- ",json_27_stats)
    #     print("Json List for all days : ",json_list)
        #FOR FILE WRITES IN JSON FORMAT.
    #     with open('/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/static/plotlycharts/PatientID_'+ str(patient_id) + '/hr_stats_hour_pid_'+ str(patient_id) +'.json', 'w') as f:
    #         json.dump(json_list, f)
    #     print("DONE FOR PATIENT ID ", patient_id)

    ##################################################################

##################################################################
# Calculates MAX, MIN, Average hr Statistics by Hour
##################################################################

def convert_to_json_hr_stats_hourly(patient_ids):
    #patient_id = 88
    patient_id_list = [27,34,52,53,75,80,88,90,106,118,129,131,584]
    for patient_id in patient_id_list:
        print("--------Patient ID -------- :", patient_id)
        start_time = time.time()
        date_id_list = get_dates(patient_id)
        #print("date_id_list = ", date_id_list)
        day_wise_mins = []
        day_wise_mins_annotation_fotmat = []
        bucket_info_day_list = []
        # For all Dates of a particlar Patient.
        for i in date_id_list:
            print("--------Date-------- :", i)
            path = "/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/care-portal-thesis-sub/PatientID_" +str(patient_id) + "/HR_ACT_Resample_40Hz_PID_" + str(patient_id) + "_" + str(i) + "_Date_ID_HR.csv"
            hr = pd.read_csv(path)
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
        r = "/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-webapp/static/plotlycharts/"
    #     with open(r+"PatientID_"+ str(patient_id)+"timming_"+str(patient_id)+"activity_levels.json", 'w') as outfile:
    #         json.dump(json_Act_levels, outfile)

def google_drive_file_read():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # client_secrets.json need to be in the same directory as the script
    drive = GoogleDrive(gauth)
    seperate_Data_folder_id = "1lkNmQHD4Qc-Rz1htsbED8TuPuT1U93Z0"
    query = seperate_Data_folder_id +"in parents and trashed=false"
    print("query = ",type(query))
    fileList = drive.ListFile({'q':query }).GetList()
    # ED EAR - HR Datafolder - List of all HR files using google drive folder.
    print(fileList)
    for patient_folder in fileList:
        # patient_folder['title'] => PatientID_130
        #print("file_title: ",patient_folder['title'],"\n file_id: ",patient_folder['id'],type(patient_folder['id']))
        if patient_folder['title'].startswith("Pat"):
            print("------------------------------IF CONDITION----------------------------------------")
            print("title: - ",patient_folder['title'],"id: - ",patient_folder['id']) 
            data_files = drive.ListFile({
                'q': "'{patient_folder['id']}' in parents and trashed=false"
                }).GetList()
            print("data_files: ", data_files["id"])
        # for i in data_files:
        #     print("data_file " , i)
if __name__ == "__main__":
    patient_ids = [27,34,52,53,75,80,88,80,90,106,118,129,131]
    ts_list = ['00' ,'01' ,'02' ,'03' ,'04' ,'05', '06' ,'07', '08' ,'09', '10' ,'11' ,'12' ,'13', '14', '15', '16' ,'17', '18' ,'19', '20', '21','22','23']
    google_drive_file_read()
    # convert_to_json_hr_stats(patient_ids)
    # convert_to_json_hr_stats_hourly(patient_ids)
    # convert_to_json_activity_levels(patient_ids,ts_list)
