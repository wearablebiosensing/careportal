
#####################################
# Author: Shehjar Sadhu.            #
# Project: Kaya web scoring portal. #
# Date: December 2019.              #
# Updated by: La Raw Nov 2020.      #
#####################################
from flask_wtf import FlaskForm
from wtforms import  StringField, DecimalField, TextAreaField, SelectField, PasswordField, validators,SubmitField  #for form validation.
from wtforms.validators import DataRequired, Length, EqualTo, Email,ValidationError, NumberRange
from flask_wtf.file import FileField
from init import user_doctor, user_patient
# Register Form class specifies all the fields for the wtf forms.
class RegisterFormDoctors(FlaskForm):
    name = StringField('Name' ,validators=[]) #'''Length(min = 1, max = 100)'''
    email = StringField('Email', validators=[Email()])#''',Length(min = 1, max = 1000)'''
    password = PasswordField('Password',
                 validators=[ DataRequired(), ])
    comfirm = PasswordField('Confirm Password',
                validators=[DataRequired(),
                    EqualTo('password', 
                    message = "Passwords do not match")])
    submit = SubmitField("Sign up")
    
    #This validates against any names or emails that are already taken.
    def validate_username(self, name):
        user = user_doctor.query.filter_by(name=name.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = user_doctor.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LogInFormDoctors(FlaskForm):

    email = StringField('Email', 
                         validators=[Email(), 
                         Length(min = 1, max = 1000)])
    password = PasswordField('Password',
                 validators=[ DataRequired(), 
                  ])
    submit = SubmitField("Log in")
class DateDropDown_form(FlaskForm):
    date = SelectField('date', choices=[],default=0)
