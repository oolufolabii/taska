from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email


class RequiredLogin:
    pass


class ForgotPassword:
    pass


class UpdateTasks:
    pass