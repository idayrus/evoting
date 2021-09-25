from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.widgets import TextArea
from wtforms.validators import Required, Email, Length
from app import app

# Data
password_min = 6
gender_option = [('1', 'Laki-laki'), ('0', 'Perempuan')]
tz_option = []
for i in app.config.get('ALLOWED_TIMEZONE'):
    tz_option.append((i[0], f"{i[1]}, {i[2]}"))


class FormEmail(FlaskForm):
    email = StringField('Email', [Required(message='Email tidak boleh kosong'), Email(message='Mohon masukan email yang valid')])


class FormLogin(FlaskForm):
    usermail = StringField('Username atau Email', [Required(message='Silahkan masukan username atau alamat email anda')])
    password = PasswordField('Password', [Required(message='Password tidak boleh kosong')])
    remember = BooleanField('Ingat saya')


class FormEditorBase(FlaskForm):
    name = StringField('Nama Lengkap', [Required(message='Silahkan masukan nama lengkap pengguna')])
    gender = SelectField('Jenis Kelamin', [Required(message='Jenis kelamin tidak boleh kosong')], choices=gender_option)  # 1-Male, 0-Female
    birthdate = StringField('Tanggal Lahir')
    contact = StringField('Kontak')
    address = StringField('Alamat Lengkap', widget=TextArea())


class FormEditorAdd(FormEditorBase):
    email = StringField('Email', [Required(message='Email tidak boleh kosong'), Email(message='Mohon masukan email yang valid')])
    password = PasswordField('Password', [Required(message='Password tidak boleh kosong')])


class FormEditorEdit(FormEditorBase):
    email = StringField('Email', [Required(message='Email tidak boleh kosong'), Email(message='Mohon masukan email yang valid')])
    password = PasswordField('Password')


class FormUpdateUser(FlaskForm):
    name = StringField('Nama Lengkap', [Required(message='Silahkan masukan nama lengkap anda')])
    gender = SelectField('Jenis Kelamin', [Required(message='Jenis kelamin tidak boleh kosong')], choices=gender_option)  # 1-Male, 0-Female
    birthdate = StringField('Tanggal Lahir')
    timezone = SelectField('Zona Waktu', [Required(message='Zona waktu tidak boleh kosong')], choices=tz_option)
    contact = StringField('Kontak')
    address = StringField('Alamat Lengkap', widget=TextArea())


class FormUpdatePassword(FlaskForm):
    password_old = PasswordField('Password Saat Ini', [Required(message='Password Saat Ini tidak boleh kosong')])
    password_new = PasswordField('Password Baru', [Required(message='Password Baru tidak boleh kosong'), Length(min=password_min, message=f'Password harus memiliki panjang minimal {password_min} karakter')])
