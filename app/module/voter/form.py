from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, HiddenField
from wtforms.widgets import TextArea
from wtforms.validators import Required, Email, Length


class VoterForm(FlaskForm):
    id_number = StringField('No. Induk', [Required(message='Nomor induk tidak boleh kosong')])
    name = StringField('Nama Lengkap', [Required(message='Nama lengkap tidak boleh kosong')])
    gender = SelectField('Jenis Kelamin', [Required(message='Jenis kelamin tidak boleh kosong')], choices=[('1', 'Laki-laki'), ('0', 'Perempuan')])  # 1-Male, 0-Female
    birthdate = StringField('Tanggal Lahir')
    contact = StringField('Kontak')
    address = StringField('Alamat Lengkap', widget=TextArea())

class VoterRegisterForm(FlaskForm):
    id_number = StringField('NIM', [Required(message='Nomor induk tidak boleh kosong')])
    name = StringField('Nama Lengkap', [Required(message='Nama lengkap tidak boleh kosong')])
    gender = SelectField('Jenis Kelamin', [Required(message='Jenis kelamin tidak boleh kosong')], choices=[('1', 'Laki-laki'), ('0', 'Perempuan')])  # 1-Male, 0-Female
    contact = StringField('No. WhatsApp', [Required(message='Nomor WhatsApp tidak boleh kosong')])
    signature = HiddenField('Signature')
