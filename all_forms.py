"""Module for flask forms"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email


class RegistrationForm(FlaskForm):
    """Class for to create the registration form"""
    style = {'class': 'ourClasses', 'style': 'margin: 1%; font-family: "DM Serif Display", serif; font-weight: 400;'}

    username = StringField("Name", validators=[DataRequired()], render_kw=style)
    email = StringField("E-Mail", validators=[DataRequired(), Email()], render_kw=style)
    password = PasswordField("Password", validators=[DataRequired()], render_kw=style)
    submit = SubmitField("REGISTER", render_kw=style)
    

class Login(FlaskForm):
    """Login info"""
    style = {'class': 'ourClasses', 'style': 'margin: 1%; font-family: "DM Serif Display", serif; font-weight: 400;'}
    email = StringField("Email", validators=[DataRequired(), Email()], render_kw=style)
    password = PasswordField("Password", validators=[DataRequired()], render_kw=style)
    submit = SubmitField("LOG IN!", render_kw=style)


class AddTag(FlaskForm):
    """Adding and creating new tags for tasks"""
    style = {'class': 'ourClasses', 'style': 'margin: 1%; font-family: "DM Serif Display", serif; font-weight: 400;'}
    tag_name = StringField("Tag Name", validators=[DataRequired()], render_kw=style)
    submit = SubmitField("ADD TAG", render_kw=style)
