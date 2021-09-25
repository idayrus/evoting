from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.widgets import TextArea
from wtforms.validators import Required, Email, Length


class CandidateForm(FlaskForm):
    number = StringField('No. Paslon', [Required(message='Nomor paslon tidak boleh kosong')])
    leader_name = StringField('Nama Calon Ketua', [Required(message='Nama Calon Ketua tidak boleh kosong')])
    deputy_name = StringField('Nama Calon Wakil Ketua')
    note = StringField('Catatan')
    campaign_video = StringField('URL Video Kampanye')
    campaign_info = StringField('Informasi Kampanye', widget=TextArea())
