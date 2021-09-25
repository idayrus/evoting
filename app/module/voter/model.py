from app import db_main as db
from app.helper.sqlalchemy import DictField, ObjectIDField, MutableDict, MutableList
from app.helper.database import Database


class VoterModel(Database):
    id_number = db.Column(db.String(128), nullable=False) # Identifier Number
    pin = db.Column(db.Integer, default=0)
    name = db.Column(db.Text, nullable=False)
    gender = db.Column(db.Integer, default=0)  # 1-Male, 0-Female
    birthdate = db.Column(db.String(64), nullable=True)
    contact = db.Column(db.Text, nullable=True)
    address = db.Column(db.Text, nullable=True)
    extra_info = db.Column(MutableDict.as_mutable(DictField), nullable=True, default={})

class VoterBallotModel(Database):
    candidate_id = db.Column(ObjectIDField(32), db.ForeignKey('candidate.id_', ondelete="CASCADE"), nullable=False)
    candidate = db.relationship('CandidateModel', backref='voter_ballot', lazy=True)
    voter_id = db.Column(ObjectIDField(32), db.ForeignKey('voter.id_', ondelete="CASCADE"), nullable=False)
    voter = db.relationship('VoterModel', backref='voter_ballot', lazy=True)
