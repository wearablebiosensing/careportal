import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, ForeignKey
import pandas as pd

engine = db.create_engine('sqlite:////Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/database/careportal-deploy-permission.db')
connection = engine.connect()
metadata = db.MetaData()
df = pd.read_csv("/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/database/CSV_DB_FILES/pi_deploy_USB.csv")

df.to_sql('user_patient', con=engine,if_exists='replace')
