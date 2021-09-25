from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.widgets import TextArea
from wtforms.validators import Required, Email, Length


class ExampleForm(FlaskForm):
    pass
