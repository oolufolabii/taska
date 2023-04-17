#!/usr/bin/env python3
"""A Flask web app for my task manager.
"""

from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from app_forms import RegistrationForm, Login, AddTag
from wtforms import StringField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_required, LoginManager, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from typing import Callable


app = Flask(__name__)

app.config["SECRET_KEY"] = 'any secret'

# Database connection
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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


association_table = db.Table('association',
                             db.Column('users_id', db.Integer,
                                       db.ForeignKey('users.id')),
                             db.Column('tags_id', db.Integer,
                                       db.ForeignKey('tags.id'))
                             )


class User(UserMixin, db.Model):
    """Class for database created to store and manage registered users"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False, unique=True)

    tasks = relationship("Task", cascade="all,delete",
                         backref="creator", lazy=True)

    subscriptions = db.relationship(
        "Tag", secondary="association", backref=db.backref("subscribers", lazy="dynamic"))


class Task(db.Model):
    """Class for database created to store and manage tasks"""
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    due_date = db.Column(db.Date)
    progress = db.Column(db.Boolean, nullable=False)
    date_created = db.Column(db.Date, nullable=False)

    # Child relationship with users table
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # Child relationship with the tags table
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"))


class Tag(db.Model):
    """Class for database created to store and manage task tags"""
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String, nullable=False, unique=True)

    # Parent relationship with task table, one to many
    tasks = relationship("Task", cascade="all,delete",
                         backref="task_tag", lazy=True)

    def __repr__(self):
        """Updating the string representation"""
        return f'{self.tag_name}'


# Creating DB
db.create_all()


class NewTaskCreator(FlaskForm):
    """Class for creating new tasks."""
    style = {'class': 'ourClasses',
             'style': 'margin: 1%; font-family: "DM Serif Display", serif; font-weight: 400;'}

    title = StringField("Task Name", validators=[
                        DataRequired()], render_kw=style)
    description = StringField("Description", render_kw=style)
    due_date = DateField("Date Due", format='%Y-%m-%d',
                         render_kw={'placeholder': '2023/01/01 for January 01, 2023'})
    tag = SelectField("Choose Tag", validators=[
                      DataRequired()], render_kw=style)

    submit = SubmitField("ADD", render_kw=style)


@app.route("/")
def home():
    # using print statement for log/tracking
    print(current_user)
    return render_template("index.html", current_user=current_user)


@app.route("/login", methods=["POST", "GET"])
def login():
    """Login Page"""
    form_page = Login()
    if form_page.validate_on_submit():
        logged_user = User.query.filter_by(email=form_page.email.data).first()
        if logged_user is None:
            flash("This email has not been registered yet, please register first.")
            return redirect(url_for("register"))
        else:
            if check_password_hash(logged_user.password, form_page.password.data):
                login_user(logged_user)
                # User logged in with success
            else:
                flash("Incorrect password. Try again.")
                return redirect(url_for("login"))
            return redirect(url_for("show_dashboard", username=current_user.username))
    return render_template("login.html", form=form_page, current_user=current_user)


@app.route("/register", methods=["POST", "GET"])
def register():
    form_page = RegistrationForm()
    if form_page.validate_on_submit():
        print(User.query.filter_by(email=form_page.email.data).first())
        # logging
        if User.query.filter_by(email=form_page.email.data).first() is None:
            hashed_password = generate_password_hash(
                form_page.password.data, "pbkdf2:sha256", 10)
            new_user = User(username=form_page.username.data,
                            email=form_page.email.data, password=hashed_password)

            # update db with new user
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            flash("Registered successfully!")
            return redirect(url_for("show_dashboard", username=current_user.username))
        flash("This email has already been registered. Please sign in.")
        return redirect(url_for("login"))
    return render_template("register.html", form=form_page, current_user=current_user)


# Functions to manage tasks
@app.route("/add-task", methods=["POST", "GET"])
@login_required
def adding_task():
    form_page = NewTaskCreator()
    form_page.tag.choices = [x for x in current_user.subscriptions]
    if form_page.validate_on_submit():
        tag = Tag.query.filter_by(tag_name=form_page.tag.data).first()
        new_task = Task(
            title=form_page.title.data,
            description=form_page.description.data,
            due_date=form_page.due_date.data,
            progress=False,
            date_created=datetime.date.today(),
            creator_id=current_user.id,
            tag_id=tag.id
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("show_dashboard", username=current_user.username))
    return render_template("add_task.html", form=form_page, current_user=current_user, is_edit=False)


@app.route("/delete-task/<int:task_id>")
@login_required
def delete_task(task_id):
    the_task = Task.query.get(task_id)
    db.session.delete(the_task)
    db.session.commit()
    return redirect(url_for("show_dashboard", username=current_user.username))


@app.route("/edit-task/<int:task_id>", methods=["POST", "GET"])
@login_required
def edit_task(task_id):
    the_task = Task.query.get(task_id)
    edit_form = NewTaskCreator(
        title=the_task.title,
        description=the_task.description,
        due_date=the_task.due_date,
        tag=Tag.query.filter_by(id=the_task.tag_id).first()
    )
    edit_form.tag.choices = [x for x in current_user.subscriptions]
    if edit_form.validate_on_submit():
        new_tag = Tag.query.filter_by(
            tag_name=edit_form.tag.data.title()).first()

        the_task.title = edit_form.title.data
        the_task.description = edit_form.description.data
        the_task.due_date = edit_form.due_date.data
        the_task.tag_id = new_tag.id

        db.session.commit()
        return redirect(url_for("show_dashboard", username=current_user.username))
    return render_template("add_task.html", form=edit_form, current_user=current_user, is_edit=True)


@app.route("/done/<int:task_id>")
@login_required
def done(task_id):
    the_task = Task.query.get(task_id)
    if the_task.progress == 0:
        the_task.progress = 1
    else:
        the_task.progress = 0
    db.session.commit()
    return redirect(url_for("show_dashboard", username=current_user.username))


# TAG RELATED FUNCTIONS
@app.route("/new-kboard", methods=["POST", "GET"])
@login_required
def add_new_tag():
    form_page = AddTag()
    if form_page.validate_on_submit():
        if Tag.query.filter_by(tag_name=form_page.tag_name.data.title()).first() is None:
            current_tag = Tag(tag_name=form_page.tag_name.data.title())

            current_tag.subscribers.append(current_user)
            db.session.add(current_tag)

        else:
            current_tag = Tag.query.filter_by(
                tag_name=form_page.tag_name.data.title()).first()
            current_tag.subscribers.append(current_user)

        db.session.commit()
        # A default task as a template
        default_task = Task(title="New Task",
                            description="Add a new task to your new board.",
                            date_created=datetime.date.today(),
                            progress=False,
                            creator_id=current_user.id,
                            tag_id=current_tag.id)
        db.session.add(default_task)
        db.session.commit()
        return redirect(url_for("show_dashboard", username=current_user.username))
    return render_template("new_tag.html", current_user=current_user, form=form_page)


@app.route("/delete-kboard-<int:tag_id>")
@login_required
def delete_tag(tag_id):
    current_tag = Tag.query.get(tag_id)
    user_task = Task.query.filter_by(creator_id=current_user.id).all()
    for task in user_task:
        if task.tag_id == current_tag.id:
            db.session.delete(task)
            db.session.commit()

    current_user.subscriptions.remove(current_tag)
    db.session.commit()
    return redirect(url_for("show_dashboard", username=current_user.username))


@app.route("/dashboard/<username>")
@login_required
def show_dashboard(username):
    user_task = Task.query.filter_by(creator_id=current_user.id).all()
    user_tags = []
    for tag in Tag.query.all():
        if current_user in tag.subscribers:
            user_tags.append(tag)

    return render_template("dashboard.html", current_user=current_user, user_tasks=user_task, tags=user_tags)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home", current_user=current_user))


if __name__ == "__main__":
    app.run(debug=True)
