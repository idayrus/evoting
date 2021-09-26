from flask import url_for, redirect, g, abort, request, flash
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from app import app
from app.helper.network import get_real_ip
from functools import wraps
from werkzeug.exceptions import HTTPException
from traceback import format_exc as get_traceback
from json import dumps as json_dumps
from click import echo as c_echo, style as c_style
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app import app
from base64 import b64decode
from PIL import Image
from io import BytesIO
from hashlib import sha512
from random import randrange


def save_base64_image(img_base64, file_path, width=500):
    try:
        # Split base64 margin and decode
        img_decoded = b64decode(img_base64.split(",")[1])

        # Open decoded data using pillow
        img = Image.open(BytesIO(img_decoded))

        # Resize image
        width_percent = (width / float(img.size[0]))
        height = int((float(img.size[1]) * float(width_percent)))
        img = img.resize((width, height), Image.ANTIALIAS)

        # Save
        img.save(file_path)

        # End
        return file_path

    except Exception as e:
        # Log
        app.logger.error(get_traceback())
        # End
        return False


def echo(text, color):
    c_echo(c_style(text, fg=color))


def sqlalchemy_info(response):
    if app.config.get("DEV_MODE"):
        color = "green"
        if response.mimetype in ["text/html", "application/json"]:
            query = get_debug_queries()
            echo(f" * Total query call: {str(len(query))} times", color)
            total = 0.0
            for q in query:
                total += q.duration
            echo(f" * Duration: {str(total)} seconds", color)


def accepted_role(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if role in current_user.Role:
                return f(*args, **kwargs)
            return abort(403)
        return decorated
    return decorator


def wrap_log(on_error=None, tag=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                return f(*args, **kwargs)

            except HTTPException:
                raise

            except Exception as e:
                # Error builder
                error_message = {
                    "ip_address":	get_real_ip(),
                    "traceback":	get_traceback(),
                    "url":			str(request.full_path),
                    "auth":			str(request.authorization),
                    "blueprint":	str(request.blueprint),
                    "method":		str(request.method),
                    "user_agent":	str(request.user_agent),
                }

                # On dev mode
                if app.config.get("DEV_MODE"):
                    echo(str(get_traceback()), "red")
                else:
                    # Insert to logger
                    app.logger.error(json_dumps(error_message))

                # Custom error
                if on_error:
                    if isinstance(on_error, int):
                        return abort(on_error)
                    else:
                        return on_error
                else:
                    return abort(500)

        return decorated
    return decorator


def filter_name(name, allowed=None, num=True):
    # Data
    output = ""
    value = name.strip()

    # Allowed chars
    if allowed is None:
        allowed = ["'", " "]

    # Loop chars
    for char in value:
        if char.isalnum() and num:
            output += char
        if char.isalpha() and not num:
            output += char
        elif char in allowed:
            output += char

    # Reformat space and return
    output = " ".join(output.split())
    return output


def objectid(value):
    try:
        return ObjectId(str(value))
    except (InvalidId, ValueError, TypeError):
        return None


def get_gerbang():
    return request.headers.get('X-Gerbang')


def msg_out(success, message="", tag="error", payload=None, flash=True):
    return MessageOutput(success, message=message, tag=tag, payload=payload, flash=flash)


def current_url():
    return request.url


def generate_token_secret():
    token = str(ObjectId())
    string = token + str(randrange(1000000, 9999999))
    secret = sha512(string.encode("utf-8")).hexdigest()
    return token, secret


# Register jinja
app.jinja_env.globals.update(current_url=current_url)


class DataModel():
    def __init__(self, data=None):
        # Dict data
        if isinstance(data, dict):
            # Update data
            self.__dict__.update(data)

    def __getattr__(self, name):
        return None

    def _payload(self):
        return dict(self.__dict__)

    @property
    def to_dict(self):
        return dict(self.__dict__)


class ClientInfo():
    def __init__(self):
        self.ip_address = get_real_ip()
        self.user_agent = str(request.user_agent)
        self.platform = request.user_agent.platform
        self.browser = request.user_agent.browser
        self.version = request.user_agent.version
        self.language = [x.replace('-', '_') for x in request.accept_languages.values()]

        # Check for lova client
        self._check_lova_client()

    def _check_lova_client(self):
        # Process
        if not self.browser:
            if "LovaClient" in self.user_agent:
                lova_client = self.user_agent.split(" ")[-1]
                if lova_client:
                    lova_client = lova_client.split("/")
                    if len(lova_client) == 2:
                        self.browser = lova_client[0]
                        self.version = lova_client[1]

    @property
    def to_dict(self):
        return dict(self.__dict__)


class MessageOutput():
    # Defined Variable
    success = None
    message = None
    tag = None
    payload = None
    flash = True

    def __init__(self, success, message=None, tag=None, payload=None, flash=True):
        # Setter
        self.success = success
        self.message = message
        self.tag = tag
        self.payload = payload
        self.flash = flash

    def get(self, key):
        # Emulate get function
        return self.__dict__.get(key)

    def do_flash(self):
        if self.flash and self.message:
            flash(self.message, self.tag)
