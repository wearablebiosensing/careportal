import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, ForeignKey

# Change file path based on computer.
engine = db.create_engine('sqlite:////Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/database/careportal-deploy-permission.db')
connection = engine.connect()
metadata = db.MetaData()
# user_patient_table = db.Table('user_patient', metadata, autoload=True, autoload_with=engine)
# Creating a DB:
user_patient = db.Table('user_patient', metadata,
               db.Column('ID', db.Integer(),primary_key=True),
               db.Column('doctor_id', db.String(10000), ForeignKey("user_doctor.ID")),
               db.Column('file_name_acc', db.String(10000)),
               db.Column('file_name_hr', db.String(10000))
)
user_doctor = db.Table('user_doctor', metadata,
               db.Column('ID', db.Integer(),primary_key=True),
               db.Column('email', db.String(10000)),
               db.Column('password', db.String(10000))
)
metadata.create_all(engine) #Creates the table