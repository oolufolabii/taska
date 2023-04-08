"""Module for flask forms"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email

STYLE = {'class': 'ourClasses',
         'style': 'margin: 1%; font-family: "DM Serif Display", serif; font-weight: 400;'}


class RegistrationForm(FlaskForm):
    """Class for to create the registration form"""
    username = StringField("Name", validators=[
                           DataRequired()], render_kw=STYLE)
    email = StringField(
        "E-Mail", validators=[DataRequired(), Email()], render_kw=STYLE)
    password = PasswordField("Password", validators=[
                             DataRequired()], render_kw=STYLE)
    submit = SubmitField("REGISTER", render_kw=STYLE)


class Login(FlaskForm):
    """Login info"""
    email = StringField("Email", validators=[
                        DataRequired(), Email()], render_kw=STYLE)
    password = PasswordField("Password", validators=[
                             DataRequired()], render_kw=STYLE)
    submit = SubmitField("LOG IN!", render_kw=STYLE)


class AddTag(FlaskForm):
    """Adding and creating new tags for tasks"""
    tag_name = StringField("Tag Name", validators=[
                           DataRequired()], render_kw=STYLE)
    submit = SubmitField("ADD TAG", render_kw=STYLE)
