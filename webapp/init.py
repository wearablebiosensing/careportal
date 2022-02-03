#####################################
# Author: Shehjar Sadhu.            
# Project: Care- l.            
# Date: Updated Sept1st 2021 from Pi   
#####################################
import os
import json
from typing import Dict
from flask import Flask, render_template, url_for, flash, redirect,session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
import plotly
from flask_login import UserMixin
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from utils.hr_features import *
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from googleapiclient.http import MediaFileUpload
import time
app = Flask(__name__)
app.config['SECRET_KEY'] ="Kaya"
# Set database instances
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database/careportal-dev-hr.db'
app.config['RECAPTCHA_USE_SSL']= False
# Site key: 6LcijG0cAAAAACKIXc3CVPuEfvl6pf2dFERY7gNU
# Seceret Key 6LcijG0cAAAAAG38qeW2Ay0Y4bOSBN8ZmvSigNLm

app.config['RECAPTCHA_PUBLIC_KEY']= '6LcijG0cAAAAACKIXc3CVPuEfvl6pf2dFERY7gNU'
app.config['RECAPTCHA_PRIVATE_KEY']='6LcijG0cAAAAAG38qeW2Ay0Y4bOSBN8ZmvSigNLm'
app.config['RECAPTCHA_OPTIONS'] = {'theme':'white'}
# Create a db instance.
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
# Init log in manager for flask app.
login_manager = LoginManager(app)
login_manager.login_view = 'login'
root_pi = "/var/www/html/web"

gauth = GoogleAuth()
gauth.LocalWebserverAuth() 
drive = GoogleDrive(gauth)

p_27 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
p_34 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
p_52 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
p_53 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
p_75 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
p_80 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
p_88 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
p_90 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
p_106 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
p_118 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
p_129 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
p_131 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
# Returns a list of Dates based on Date ID.
def get_dates(patient_id):
    date_id_list = []
    if patient_id == 27:
        date_id_list = p_27
    elif patient_id == 34:
        date_id_list = p_34
    elif patient_id == 52:
        date_id_list = p_52
    elif patient_id == 53:
        date_id_list = p_53
    elif patient_id == 75:
        date_id_list = p_75
    elif patient_id == 80:
        date_id_list = p_80
    elif patient_id == 88:
        date_id_list = p_88
    elif patient_id == 90:
        date_id_list = p_90
    elif patient_id == 106:
        date_id_list = p_106
    elif patient_id == 118:
        date_id_list = p_118
    elif patient_id == 129:
        date_id_list = p_129
    elif patient_id == 131:
        date_id_list = p_131
    return date_id_list

class user_doctor(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    email = db.Column(db.String(1000),nullable=False)
    password = db.Column(db.String(600),nullable=False)

class user_patient(db.Model):
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user_doctor.id'),nullable=False)
    acc_path = db.Column(db.String(10000),nullable=False)
    hr_path = db.Column(db.String(10000),nullable=False)

# This import is here because of variable defined above are needed in forms .py
from forms import RegisterFormDoctors, LogInFormDoctors,DateDropDown_form

# To filter by Hour and Date&Time. Give it a dataset for one day only apply that filter before feeding.
def unique_time_stamps(df):
    time_stamp_list = [] # get the unique time stamps int he paricular df.
    for idx,val in enumerate(df["Time"]):
        #print("TS: ",val,val[11:13])
        time_stamp_list.append(val[11:13])
    return np.unique(np.array(time_stamp_list))

@login_manager.user_loader
def load_user(user_id):
    return user_doctor.query.get(int(user_id))
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/about')
def about():
    return render_template('about.html')
    
# Registers the doctors and inserts their information in the database
@app.route('/registerdoctor',methods = ["GET", "POST"])
def register_doctors():
    form = RegisterFormDoctors()
    # If form is valid print a message and redirect the users to the log in page
    if form.validate_on_submit():
        # Generate the hased the password using bcrypt API .
        pass_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        # Create a new user instance.
        user = user_doctor(email=form.email.data, password=pass_hash)
        db.session.add(user)
        db.session.commit()
        flash(f"Account is created for {form.name.data}!","success")
        return redirect(url_for("login_doctors"))
    #Else redirect back to the register page.
    return render_template('register_doctors.html',form=form)

@app.route('/logindoctor',methods = ["POST", "GET"])
def login_doctors():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LogInFormDoctors()
    print("user_doctor :",user_doctor.query.all())
    user = user_doctor.query.filter_by(email=form.email.data).first()
    #user_p = user_doctor.query.filter_by(password=form.email.data).first()
    # print("USER: ",user.columns.keys())
    print("Form FIelds = ",form.validate_on_submit())
    # Check is the fields in the form are valid.
    if form.validate_on_submit():
        print("user = ",form.email.data)
        # print("PSS: ",user.password, form.password.data)
        # If they are valid then check if the user exists in the database and check if they entered the correct password.
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f"Logged in {form.email.data}","success")
            return redirect(url_for("home"))        
        #Else display error message.
        else:
            flash(f"Not logged in","danger")
    return render_template('login_doctors.html', title='login',form=form)

@app.route('/signout')
def signout():
    logout_user()
    return redirect(url_for("home"))

def get_num_patients(seperate_Data_folder_id):
    # gauth = GoogleAuth()
    # gauth.LocalWebserverAuth() 
    # drive = GoogleDrive(gauth)
    query = f"'{seperate_Data_folder_id}' in parents and trashed=false"
    print("query = ",type(query))
    fileList = drive.ListFile({'q':query }).GetList()
    count_patient = []
    print("NUMBER OF AVALIABLE PATIENTS ===",len(fileList))
    for i in fileList:
        if i['title'].startswith("Pat"):
            print("FILETITLE- ",int(i['title'].split("_")[1]))
            count_patient.append(int(i['title'].split("_")[1]))
    return count_patient
@app.route('/view_patients')
@login_required
def view_patients():
    patients = user_patient.query.order_by(user_patient.id.asc())
    seperate_Data_folder_id = '1lkNmQHD4Qc-Rz1htsbED8TuPuT1U93Z0'
    count_patient = get_num_patients(seperate_Data_folder_id)
    print("patients[:]",patients[:])
    print("count_patient",count_patient)
    return render_template('patients.html', patients = count_patient)
def google_drive_file_read(seperate_Data_folder_id,patientID):

    query = f"'{seperate_Data_folder_id}' in parents and trashed=false"
    print("query = ",type(query))
    fileList = drive.ListFile({'q':query }).GetList()
    # ED EAR - HR Datafolder - List of all HR files using google drive folder.
    print("NUMBER OF AVALIABLE PATIENTS ===",len(fileList))
    for patient_folder in fileList:
        # patient_folder['title'] => PatientID_130
        if patient_folder['title'].startswith("Pat"): # If it starts with Pat only.
            #print("------------------------------IF CONDITION----------------------------------------")
            #print("title: - ",patient_folder['title'],"id: - ",patient_folder['id']) 
            if patient_folder["title"].startswith("PatientID_" + patientID):
                print("patientID ======",patientID)
                data_files = drive.ListFile({
                    'q': f"'{patient_folder['id']}' in parents and trashed=false"
                    }).GetList()
                # Gets each file in the SeperateData/PatientID_130/ filder Eg:- HR_all.csv, HR_SDNN.csv etc..
                for sensor_file in data_files:
                    # sensor_file["title"] = PatientID_146_hr_stats_daily.json
                    if sensor_file["title"].endswith("daily.json"): 
                        URL = f"https://drive.google.com/file/d/{sensor_file['id']}/view?usp=sharing"
                        path = 'https://drive.google.com/uc?export=download&id='+URL.split('/')[-2]
                        df = pd.read_json(path)
                        return df


##########################################################################
# Parameters - patient ID.
# Displays MAX, MIN heart rate data on an hourly and daily basis.
##########################################################################
@app.route('/patient/<int:patient_id>/overall', methods=['GET', 'POST'])
@login_required
def heart_rate_route(patient_id,methods=['GET', 'POST']):
     start_time_plot = time.time()
     form = DateDropDown_form()
     seperate_Data_folder_id = '1lkNmQHD4Qc-Rz1htsbED8TuPuT1U93Z0'
     # COLUMNS = pid, dates, mean, min, max, std, hrv
     df = google_drive_file_read(seperate_Data_folder_id,str(patient_id))
     hr_stats_daily = {
         "pid": df["pid"][0],
         "min": df["min"].tolist(),
         "max": df["max"].tolist(),
         "std": df["std"].tolist(),
         "mean": df["mean"].tolist(),
         "hrv":df["hrv"].tolist(),
         "dates": df["dates"].tolist()
     }
     hourly_stats =  "./static/plotlycharts/PatientID_"+str(patient_id) + "/hr_stats_hour_pid_"+ str(patient_id) +".json" 
     with open(hourly_stats, "r") as json_file:
         hourly_stats = json.load(json_file)
     return render_template("heart_rate.html",patientId=patient_id,
                            form =form,date_id_list=df["dates"].tolist(),
                            hr_stats = hr_stats_daily,
                            hourly_stats = hourly_stats[0],
                            selected_date = str(form.date.data))

# Displays Activity Level Data for patient selected. Get the patient ID from route.
##########################################################################
# Parameters - patient ID.
# Displays Activity levels data based on HR levles.
##########################################################################
@app.route('/patient/<int:patient_id>/activity', methods=['GET', 'POST'])
@login_required
def activity_levels(patient_id,methods=['GET', 'POST']):
     patientId = user_patient.query.get(patient_id)
     print("activity_levels: ",patientId)
     path =  os.getcwd()  + patientId.acc_path
     date_id_list = get_dates(patient_id)
     # Unique dates from a particular patient.
     dates = date_id_list #df['Date'].unique()
     print("Acc Dates:",dates)
     # wtf forms displays the forms on the web page
     form = DateDropDown_form()
     # Gets the unique avaliable dates from a patient.
     form.date.choices = [(date) for date in dates]
     print("date list: ",dates)
     print("selected date:  ",form.date.data)

     activity_levels_timmings =  "./static/plotlycharts/PatientID_" + str(patient_id) +"/PatientID_" + str(patient_id)+  "timming_"+str(patient_id) + "activity_levels.json"
     with open(activity_levels_timmings, "r") as json_file:
         act_levels = json.load(json_file)
    #  hr_activity_d_list = hr_stats["HR_Activity"][int(form.date.data)]
     return render_template('activity_level.html',patientId=patient_id,form=form,dates=dates,selected_date=str(form.date.data),act_levels =act_levels)

# Calculates HR features for a particular patient, plots the HR feaure values like RR interval,SSDRR.
@app.route('/heart_rate_variability/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def heart_rate_variability_route(patient_id):
    graphs = []
    day = []
    print("patient(): patient_id",patient_id)
    patientId = user_patient.query.get(patient_id)
    #path =  os.getcwd()  + patientId.hr_path
    print("patient(): From DB Before Conversion",patientId.id)
    patientId = patientId.id
    if patientId == 1:
        patientId = 27
    elif patientId  == 2: 
        patientId = 34
    elif patientId  == 3:
        patientId = 52
    elif patientId  == 4:
        patientId = 53
    elif patientId  == 5:
        patientId = 75
    elif patientId  == 6:
        patientId = 80
    elif patientId  == 7:
        patientId = 88
    elif patientId  == 8:
        patientId = 90
    elif patientId  == 9:
        patientId = 106   
    elif patientId  == 10:
        patientId = 118    
    elif patientId  == 10:
        patientId = 129    
    elif patientId  == 11:
        patientId = 131  
    elif patientId  == 12:
        patientId = 584   
    print("patient(): After Conversion",patientId)
    date_id_list = get_dates(patientId)
    # Unique dates from a particular patient.
    dates = date_id_list
    # wtf forms displays the forms on the web page
    form = DateDropDown_form()
    # Gets the unique avaliable dates from a patient.
    form.date.choices = [(date) for date in dates]
    #print("date list: ",dates)
    #print("selected date:  ",form.date.data)
    # Read from plotly json file and put it in. 
    stats_hr_json_path ="./static/plotlycharts/PatientID_"+ str(patientId)+"/hr_stats_pid_" + str(patientId) +".json" #"./static/plotlycharts/PatientID_"+str(27) + "/hr_stats_pid_" + str(27) + ".json"                
    patient_resuorce =  "./static/hl7_FHIR/patient_resource.json"
    with open(stats_hr_json_path, "r") as json_file:
        hr_stats = json.load(json_file)
    with open(patient_resuorce, "r") as json_file:
        patient_resuorce_json = json.load(json_file)
    print("patient_resuorce_json: \n",patient_resuorce_json["name"])
    family_name = patient_resuorce_json["name"][0]["family"]
    given_name  = patient_resuorce_json["name"][0]["given"][0]
    gender = patient_resuorce_json["gender"]
    max_d = hr_stats["max"][int(form.date.data)]
    min_d = hr_stats["min"][int(form.date.data)]
    std_d = round(hr_stats["std"][int(form.date.data)],2)
    mean_d = round(hr_stats["mean"][int(form.date.data)],2)

    file_name_hr = "plotlycharts/pid_27_did_"+ str(form.date.data) +"raw_hr.png"
    print("file_name_hr: ",file_name_hr)
    stats_hr_json_path =  "./static/plotlycharts/PatientID_" + str(patientId)+"/hr_stats_pid_" + str(patientId) + ".json"                
    hourly_stats =   "./static/plotlycharts/PatientID_"+str(patientId) + "/hr_stats_hour_pid_"+ str(patientId) +".json" 
    with open(stats_hr_json_path, "r") as json_file:
        hr_stats = json.load(json_file) 
    with open(hourly_stats, "r") as json_file:
        hourly_stats = json.load(json_file)
    return render_template( 
        'heart_rate_variability.html', patientId=patientId , dates=dates , form = form , submitted_date=form.date.data,max_d=max_d,min_d=min_d,mean_d=mean_d,std_d=std_d,selected_date=str(form.date.data),file_name_hr=file_name_hr,family_name=family_name,given_name=given_name,gender=gender,hr_stats=hr_stats,hourly_stats=hourly_stats[0])





    
