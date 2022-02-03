
# CarePortal: A Clinician-Centered Digital Health Portal For Wearable Data Analytics. 

 CarePortal is a web based flask application designed to visualize of wearable sensor data collected via smartwatch (Microsofy Band). Project funded by NIH-R01 (ED-ear) grant. In fulfillment of MS-Electrical Engineering thesis by Shehjar Sadhu. CarePortal is an extension of the ED-Ear project that collected data from Microsoft Band.


![](/webapp/static/overview.png)

![](/webapp/static/systemarch.png)

![](/webapp/static/database_Arch.png)

For converting to JSON from HR data use convert_to_json.py file. 

## CarePortal Demo

![](/webapp/static/demo.gif)

## How to Run CarePortal flaskapp:
1. Create a virtual environment  
    * https://docs.python.org/3/library/venv.html
    * https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
2. In order to run flask app 
   * `$ cd webapp`
   * `$ export FLASK_APP=init`
   * `$ flask run`