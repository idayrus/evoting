from app import db_main as db
from sqlalchemy.dialects.mysql import LONGTEXT
from app.helper.database import Database


class SettingModel(Database):
    identifier = db.Column(db.String(16), nullable=False)
    vote_start = db.Column(db.DateTime, nullable=True)
    vote_end = db.Column(db.DateTime, nullable=True)
    template = db.Column(LONGTEXT, nullable=True)
