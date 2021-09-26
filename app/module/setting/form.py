from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, HiddenField
from wtforms.widgets import TextArea
from wtforms.validators import Required, Email, Length


class TemplateForm(FlaskForm):
    content = HiddenField('Content')

class SettingForm(FlaskForm):
    start_date = StringField('Tanggal Mulai', [Required(message='Tanggal mulai tidak boleh kosong')])
    start_time = StringField('Jam Mulai', [Required(message='Jam mulai tidak boleh kosong')])
    end_date = StringField('Tanggal Selesai', [Required(message='Tanggal selesai tidak boleh kosong')])
    end_time = StringField('Waktu Selesai', [Required(message='Waktu selesai tidak boleh kosong')])
