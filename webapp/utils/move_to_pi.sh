#!/bin/bash
echo "Hello"
scp -r /Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/database pi@ss.pdaware.dev:/var/www/html/web
scp -r /Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/templates pi@ss.pdaware.dev:/var/www/html/web
scp -r /Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/static pi@ss.pdaware.dev:/var/www/html/web
scp -r /Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/utils pi@ss.pdaware.dev:/var/www/html/web
scp -r /Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/init.py pi@ss.pdaware.dev:/var/www/html/web
scp -r /Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-flaskapp/forms.py pi@ss.pdaware.dev:/var/www/html/web
