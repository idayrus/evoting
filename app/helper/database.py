from app import db_main, app
from app.helper.sqlalchemy import ObjectIDField
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
from re import sub as re_sub
from bson.objectid import ObjectId
from bson.errors import InvalidId
from werkzeug.routing import BaseConverter, ValidationError
from functools import wraps


@app.after_request
def after_request(response):
    # Check status
    if not int(response._status_code or 0) == 500:
        db_main.session.commit()
    else:
        db_main.session.rollback()
    # Bypass response
    return response


def auto_commit():
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # Commit
                db_main.session.commit()
                return f(*args, **kwargs)
            except Exception as e:
                # Rollback transaction
                db_main.session.rollback()
                raise e
        return decorated
    return decorator


def objectid(value):
    try:
        return ObjectId(value)
    except (InvalidId, ValueError, TypeError):
        return None


def transform_table_name(text):
    s0 = text.replace("Model", "")
    s1 = re_sub('(.)([A-Z][a-z]+)', r'\1_\2', s0)
    s2 = re_sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return s2


class ObjectIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            return ObjectId(str(value))
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()

    def to_url(self, value):
        return str(value)


class CopiedData():
    def __init__(self, data, tablename):
        # Update data
        self.__dict__.update(data)
        self.__tablename__ = tablename

    def __getattr__(self, name):
        return None


class Database(db_main.Model):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return transform_table_name(cls.__name__)

    _utc_now = datetime.utcnow
    _object_id = ObjectId

    id_ = db_main.Column(ObjectIDField(32), default=_object_id, index=True, primary_key=True)
    created = db_main.Column(db_main.DateTime(), default=_utc_now)
    modified = db_main.Column(db_main.DateTime(), default=_utc_now, onupdate=_utc_now)
    deleted = db_main.Column(db_main.Integer, index=True, default=0)  # 1-Soft delete

    def add(self):
        # Add to transaction
        db_main.session.add(self)
        # End
        return self

    def save(self):
        # Add to transaction
        db_main.session.add(self)
        db_main.session.flush()
        # End
        return self

    def remove(self):
        # Remove record
        db_main.session.delete(self)
        db_main.session.flush()
        # End
        return True

    def delete(self):
        # Set delete parameter
        self.deleted = 1
        db_main.session.flush()
        # End
        return True

    def detach_copy(self):
        # Container
        data = {}
        # Get data
        for attr, val in self.__dict__.items():
            # Check
            if not attr.startswith("_"):
                data[attr] = val
        # End
        return CopiedData(data, self.__tablename__)