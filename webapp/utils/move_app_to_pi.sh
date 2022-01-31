#!/bin/bash
echo "Hello"
scp -r /Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/ccareportal-webapp/database pi@ss.pdaware.dev:/var/www/html/web
scp -r /Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-webapp/templates pi@ss.pdaware.dev:/var/www/html/web
scp -r /Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-webapp/static pi@ss.pdaware.dev:/var/www/html/web
scp -r /Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-webapp/utils pi@ss.pdaware.dev:/var/www/html/web
scp -r /Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-webapp/init.py pi@ss.pdaware.dev:/var/www/html/web
scp -r /Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/ResearchWBL/My_Thesis/careportal-webapp/forms.py pi@ss.pdaware.dev:/var/www/html/web