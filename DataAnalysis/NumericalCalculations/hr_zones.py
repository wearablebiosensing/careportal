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
# Takes in a folder_path.
# Apllies the analysis pipeline for all the partients.
def hr_zone_detection(folder_path):
    for idx,file in enumerate(os.listdir(folder_path)):
        if file.startswith("PatientID_53"):
            for all_files in os.listdir(folder_path + file):
                # Read only HR files
                if all_files.startswith("Resample_40Hz") and all_files.endswith("Date_ID_HR.csv"):
                    start_time = time.time()
                    # print(",Reading File,")
                    print("File Read- ",file)
                    df = pd.read_csv(folder_path + file + "/" + all_files)
                    act_zone_lables = []
                    # print("Detecting HR Zones,")
                    # Iterate over each row of HR value to determine Activity Levels.
                    # Based on HR activity zone calcualtion above label the activities.
                    for idx, row in df.iterrows():
                        if row["Heart.Rate..BPM."] <= 102.5:
                            act_zone_lables.append(0)
                        #50%-70%
                        elif row["Heart.Rate..BPM."] > 102.5 and row["Heart.Rate..BPM."] <= 143.5:
                            act_zone_lables.append(1)
                        #70%-85%
                        elif row["Heart.Rate..BPM."] > 143.5 and row["Heart.Rate..BPM."] <= 174.25:
                            act_zone_lables.append(2)
                        else:
                            # No calssification.
                            act_zone_lables.append(-1)
                    df["HR_ACT_ZONE_MORE"] = act_zone_lables
                    end_time = time.time()
                    #df.to_csv(folder_path + file + "/HR_ACT_" + all_files)
                    print("PatientID,",df["Patient.ID"].unique()[0],",Date ID,",df["Date"].unique()[0],",Filename,",all_files,",Time(sec),",str(end_time-start_time))
if __name__ == "__main__":
    folder_path = "/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/WBL/My_Thesis/care-portal-thesis-sub/"
    hr_zone_detection(folder_path)
