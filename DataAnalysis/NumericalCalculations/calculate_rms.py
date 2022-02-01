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


# Calculates RMS value of 3 float values.
def calculate_rms(x,y,z):
    return np.sqrt(x**2 + y**2+z**2)

def rms_by_row(df_upsample_acc):
    # Calculate RMS for each Row.
    rms_list = []
    for idx, row in df_upsample_acc.iterrows():
        rms  = calculate_rms(row["X.Acceleration..m.s.s."],row["Y.Acceleration..m.s.s."],row["Z.Acceleration..m.s.s."])
        rms_list.append(rms)
    # Add RMS colto the DF.
    df_upsample_acc["RMS(ax,ay,az)"] =  rms_list
    return df_upsample_acc

# For each of the 13 patients calcualte the RMS per row & saves the file as csv.
# Takes in a folder_path.
# Apllies the analysis pipeline for all the partients.
def rms_calculation_all(folder_path):
    for idx,file in enumerate(os.listdir(folder_path)):
        if file.startswith("RMSPat"):
            for all_files in os.listdir(folder_path + file):
                if all_files.startswith("Resample_40Hz") and all_files.endswith("Date_ID_Acc.csv"):
                    start_time = time.time()
                    print(",Reading File,")
                    df = pd.read_csv(folder_path + file + "/" + all_files)
                    end_time_file_read = time.time()
                    print("File Read Time(Sec),",str(end_time_file_read-start_time),",")
                    print(",Calculating RMS,")
                    start_time_rms = time.time()
                    # Adds RMS To the particular DF.
                    df_rms = rms_by_row(df)
                    end_time_rms = time.time()
                    print("PatientID,",df["Patient.ID"].unique()[0],",Date ID,",df["Date"].unique()[0],",Filename,",all_files,",After RMS: ,",df_rms.columns,",Time(sec),",str(end_time_rms-start_time_rms))
                    df_rms.to_csv(folder_path + file + "/" +"RMS_" + all_files)

if __name__ == "__main__":
    folder_path = "/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/care-portal-thesis-sub/"
    rms_calculation_all(folder_path)
