from app import db_main as db
from app.helper.sqlalchemy import DictField, ObjectIDField, MutableDict, MutableList
from app.helper.database import Database


class CandidateModel(Database):
    number = db.Column(db.String(128), nullable=False)
    leader_name = db.Column(db.Text, nullable=False)
    deputy_name = db.Column(db.Text, nullable=True)
    photo = db.Column(db.Text, nullable=True)
    note = db.Column(db.Text, nullable=True)
    campaign_video = db.Column(db.Text, nullable=True)
    campaign_info = db.Column(db.Text, nullable=True)
    extra_info = db.Column(MutableDict.as_mutable(DictField), nullable=True, default={})
