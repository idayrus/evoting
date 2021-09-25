from flask_sqlalchemy import BaseQuery
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, VARCHAR, Text as Type_TEXT
from sqlalchemy.dialects.mysql import LONGTEXT
from json import dumps as json_dumps, loads as json_loads
from bson.objectid import ObjectId
from bson.errors import InvalidId


class ObjectIDField(TypeDecorator):
    # Type
    impl = VARCHAR
    cache_ok = True

    def _validate_objectid(self, value):
        try:
            value = ObjectId(value)
        except (InvalidId, ValueError, TypeError):
            raise InvalidId
        return value

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = self._validate_objectid(value)
            value = str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = self._validate_objectid(value)
        return value


class PriceField(TypeDecorator):
    # Type
    impl = Type_TEXT

    def process_bind_param(self, value, dialect):
        if type(value) is str:
            value = value
        return value

    def process_result_value(self, value, dialect):
        if type(value) is str:
            value = float(value)
        return value


class DictField(TypeDecorator):
    # Type
    impl = LONGTEXT

    def process_bind_param(self, value, dialect):
        if isinstance(value, dict) or isinstance(value, list):
            value = json_dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None and isinstance(value, str):
            value = json_loads(value)
        return value


class MutableDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.changed()


class MutableList(Mutable, list):
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        list.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        list.__delitem__(self, key)
        self.changed()


class MyQuery(BaseQuery):
    def available(self):
        # Filter undeleted record
        return self.filter_by(deleted=0)