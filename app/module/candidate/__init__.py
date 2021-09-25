from flask import request
from flask_login import current_user
from app import app
from app.helper.utils import msg_out, DataModel
from sqlalchemy import or_, and_, not_
from datetime import datetime


class Candidate():
    def __init__(self):
        pass
