from app import db_main as db
from app.helper.sqlalchemy import DictField, ObjectIDField, MutableDict, MutableList
from app.helper.database import Database


class UserModel(Database):
    status = db.Column(db.Integer, default=0)  # 0-Inactive, 1-Active
    email = db.Column(db.String(512), index=True, nullable=False)
    username = db.Column(db.String(512), nullable=True)
    password = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    gender = db.Column(db.Integer, default=0, nullable=False)  # 1-Male, 0-Female
    birthdate = db.Column(db.String(64), nullable=True)
    contact = db.Column(db.Text, nullable=True)
    address = db.Column(db.Text, nullable=True)
    # More...
    extra_info = db.Column(MutableDict.as_mutable(DictField), nullable=True, default={})
    role = db.Column(MutableList.as_mutable(DictField), nullable=True, default=[])
    config = db.Column(MutableDict.as_mutable(DictField), nullable=True, default={})
    security_question = db.Column(MutableDict.as_mutable(DictField), nullable=True, default={})
    banned_expire = db.Column(db.DateTime(), nullable=True)


class UserTokenModel(Database):
    user_id = db.Column(ObjectIDField(32), db.ForeignKey('user.id_', ondelete="CASCADE"), nullable=False)
    user = db.relationship('UserModel', backref='user_token', lazy=True)
    token = db.Column(db.String(512), index=True, nullable=True)
    secret = db.Column(db.String(512), nullable=True)
    expires = db.Column(db.DateTime, nullable=True)
    client_info = db.Column(MutableDict.as_mutable(DictField), nullable=True, default={})


class UserPasswordModel(Database):
    user_id = db.Column(ObjectIDField(32), db.ForeignKey('user.id_', ondelete="CASCADE"), nullable=False)
    user = db.relationship('UserModel', backref='user_password', lazy=True)
    password_prev = db.Column(db.String(512), nullable=False)
    password_new = db.Column(db.String(512), nullable=False)
    client_info = db.Column(MutableDict.as_mutable(DictField), nullable=True, default={})
