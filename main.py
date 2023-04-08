from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from all_forms import RegistrationForm, Login, AddTag
from wtforms import StringField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_required, LoginManager, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from typing import Callable
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = 'any secret'

#Connecting to the DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Bootstrap(app)


class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    Integer: Callable
    String: Callable
    Boolean: Callable
    Date: Callable
    relationship: Callable
    ForeignKey: Callable
    Table: Callable
    backref: Callable

db = MySQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)



if __name__ == "__main__":
    app.run(debug=True)