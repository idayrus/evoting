from flask import request
from flask_login import current_user, login_user, logout_user, UserMixin
from app import app
from app.module.setting.model import SettingModel
from app.module.user.model import UserModel, UserTokenModel, UserPasswordModel
from app.helper.utils import msg_out, DataModel, ClientInfo, get_gerbang, generate_token_secret
from app.helper.preference import USER_ROLE
from werkzeug.security import check_password_hash, generate_password_hash
from uuid import uuid4
from sqlalchemy import or_, and_, not_
from datetime import datetime, timedelta
from os import path


class User():
    def __init__(self):
        pass

    #
    # Utils
    #

    def get_user_by_id(self, id_):
        return UserModel.query.filter_by(id_=id_).first()

    def get_user_by_email(self, email):
        return UserModel.query.filter_by(email=email).first()

    def get_user_by_username(self, username):
        return UserModel.query.filter_by(username=username).first()

    def get_user_by_username_or_email(self, usermail):
        return UserModel.query.filter(or_(UserModel.username == usermail, UserModel.email == usermail)).first()

    def get_email_status(self, email, current_id=None):
        # Check username and email
        user_data = self.get_user_by_email(email)
        if user_data:
            # Check status
            if user_data.deleted == 0:
                # Check user
                if not str(current_id) == str(user_data.id_):
                    # End
                    return True
        # End
        return False

    def get_user_count(self):
        return UserModel.query.filter().count()

    def get_user_paginated(self, query_data, page=1, per_page=20):
        # Base query
        user_data = UserModel.query.available().filter_by(status=1).filter(not_(UserModel.email == "-"))

        # Search
        if query_data.search:
            user_data = user_data.filter(or_(
                UserModel.email.ilike("%"+query_data.search+"%"),
                UserModel.name.ilike("%"+query_data.search+"%")
            ))

        # Sort
        user_data = user_data.order_by(UserModel.created.desc())

        # Paginate
        user_data = user_data.paginate(page=page, per_page=per_page)

        # End
        return user_data

    #
    # Register
    #

    def register_generate_secret(self):
        return str(uuid4())

    def register(self, data, set_active=False):
        # Check username and email
        if self.get_email_status(data.email):
            return msg_out(False, message="Email sudah digunakan oleh pengguna lain", tag="error")

        # Set
        user_data = UserModel()
        user_data.email = data.email
        user_data.password = generate_password_hash(data.password)  # Hash password
        user_data.name = data.name
        user_data.gender = data.gender
        user_data.birthdate = data.birthdate
        user_data.contact = data.contact
        user_data.address = data.address

        # Set active
        if set_active:
            user_data.status = 1

        # Role
        if data.role:
            user_data.role = data.role

        # Save
        user_data.save()

        # End
        return msg_out(True, payload=user_data)

    def register_save_form(self, form, user_data=None):
        # Data
        data = DataModel()
        data.name = form.name.data
        data.gender = form.gender.data
        data.birthdate = form.birthdate.data
        data.contact = form.contact.data
        data.address = form.address.data
        data.password = form.password.data
        data.email = form.email.data.lower()

        # Update data
        if user_data:
            # Save password
            if data.password:
                self.setting_password(user_data, data.password)

            # Set information & End
            return self.setting_information(user_data, data)

        else:
            # Check if email already registered
            user_data = self.get_user_by_email(data.email)

            # Check
            if user_data:
                # Save password
                if data.password:
                    self.setting_password(user_data, data.password)

                # Set information & End
                return self.setting_information(user_data, data)

            else:
                # Register & End
                return self.register(data, set_active=True)

    #
    # Login
    #

    def login_trusted(self, email):
        # Do login
        login = self.login(email, '', trusted=True)

        # Check login
        if login.success:
            # Create session
            session_data = UserSession(
                token=login.payload.token,
                user=login.payload.user
            )
            # Login
            login_user(session_data, remember=True)

        # End
        return login

    def login_form(self, form):
        # Data
        data = DataModel()
        data.usermail = form.usermail.data.lower()
        data.password = form.password.data
        data.remember = form.remember.data

        # Do login
        login = self.login(data.usermail, data.password)

        # Check login
        if login.success:
            # Create session
            session_data = UserSession(
                token=login.payload.token,
                user=login.payload.user
            )
            # Login
            login_user(session_data, remember=data.remember)

        # End
        return login

    def login_generate_token(self, user_data, duration):
        # Generate
        token, secret = generate_token_secret()

        # Save
        token_data = UserTokenModel()
        token_data.user_id = user_data.id_
        token_data.token = token
        token_data.secret = secret
        token_data.expires = datetime.utcnow() + duration
        token_data.client_info = ClientInfo().to_dict
        token_data.save()

        # End
        return token, secret

    def login_failed(self, user_id, password):
        # End
        return msg_out(True)

    def login_check_banned(self, user_data):
        # Data
        banned = user_data.banned_expire
        utc_now = datetime.utcnow()

        # Check
        if banned:
            if utc_now < banned:
                # End
                return msg_out(False, message='Demi keamanan akun anda dibekukan untuk sementara waktu, silahkan coba lagi nanti')

        # End
        return msg_out(True)

    def login_security_limit(self, user_data):
        # End
        return msg_out(True)

    def login_as_register_first_user(self, usermail, password):
        # Check status
        if app.config.get("DEV_MODE"):
            # Get total user
            if self.get_user_count() <= 0:
                # Register new user
                data = DataModel()
                data.email = usermail
                data.password = password
                data.name = "Administrator"
                data.gender = 1
                data.role = self.setting_role_get_all()

                # Register
                self.register(data, set_active=True)

                # Get template
                file = open(path.join(app.config.get("PRIVATE_DIR"), "landing", "base.html"), "r")
                template_html = file.read()
                file.close()

                # Create setting
                setting_data = SettingModel()
                setting_data.identifier = 'default'
                setting_data.vote_start = datetime.utcnow()
                setting_data.vote_end = datetime.utcnow()
                setting_data.template = template_html
                setting_data.save()

    def login(self, usermail, password, trusted=False):
        # Login as Register for first user
        self.login_as_register_first_user(usermail, password)

        # User data
        user_data = self.get_user_by_username_or_email(usermail)

        # Check
        if user_data:
            # Check banned status
            login_banned = self.login_check_banned(user_data)
            if not login_banned.success:
                # End
                return login_banned

            # Check login failed limit
            login_limit = self.login_security_limit(user_data)
            if not login_limit.success:
                # End
                return login_limit

            # Check password or trusted login
            if check_password_hash(user_data.password, password) or trusted:
                # If user active
                if not user_data.status == 1:
                    # End
                    return msg_out(False, message='Akun anda berstatus tidak aktif atau dibekukan')

                # Check X-Gerbang
                x_gerbang = get_gerbang()

                # Token Duration, Platform, & Device
                if x_gerbang == "androidClient":
                    duration = timedelta(days=90)  # days
                else:
                    duration = timedelta(days=30)  # days

                # Generate token
                token, secret = self.login_generate_token(user_data, duration)

                # Data
                data = DataModel()
                data.token = token
                data.secret = secret
                data.user = user_data

                # End
                return msg_out(True, payload=data)

            else:
                # Login failed log
                self.login_failed(user_data.id_, password)

                # End
                return msg_out(False, message='Email atau password yang anda masukan salah')
        else:
            # End
            return msg_out(False, message='Email yang anda masukan belum terdaftar')

    #
    # Logout
    #

    def logout_current_token(self):
        # Delete current token
        if current_user.is_authenticated:
            token_data = UserTokenModel.query.filter_by(token=current_user.token).first()
            if token_data:
                token_data.delete()
        # End
        return msg_out(True)

    def logout(self):
        # Delete current token
        self.logout_current_token()
        # Logout user
        logout_user()
        # End
        return msg_out(True)

    #
    # Setting
    #

    def setting_soft_delete(self, user_data):
        # Delete
        if user_data:
            if not str(user_data.id_) == str(current_user.user.id_):
                user_data.delete()
                # End
                return msg_out(True)
        # End
        return msg_out(False, message="Tidak bisa menghapus data anda sendiri...")

    def setting_role_get_available(self, user_data=None):
        # Container
        output = []
        output += USER_ROLE

        # End
        return output

    def setting_role_get_all(self):
        # Container
        output = []
        role_list = self.setting_role_get_available()

        # Loop data
        for role_a in role_list:
            value = role_a.get("value")
            for k, _, _ in value:
                output.append(k)

        # End
        return output

    def setting_role_process(self, role_form):
        # Container
        output = []
        role_list = self.setting_role_get_available()

        # Check if data exist
        if role_form:
            # Loop form data as Data
            for data in role_form:
                # Loop role data
                for role_a in role_list:
                    # Get value from group
                    value = role_a.get("value")
                    # Extract Key, Value, Depend and loop
                    for k, v, d in value:
                        # If data same as key
                        if data == k:
                            # Append
                            output.append(k)
                            # Loop depend
                            for depend in d:
                                # Check if depend not exist in output
                                if not depend in output:
                                    # Append
                                    output.append(depend)
        # End
        return output

    def setting_role_update(self, user_data, role_form):
        # Prcoess role
        role_data = self.setting_role_process(role_form)

        # Save
        user_data.role = role_data
        user_data.save()

        # End
        return msg_out(True, message="Izin akses pengguna berhasil disimpan", tag="success")

    def setting_password_form(self, user_data, form):
        # Data
        password_old = form.password_old.data
        password_new = form.password_new.data

        # Validate old password
        if not check_password_hash(user_data.password, password_old):
            # End
            return msg_out(False, message="Password saat ini yang anda masukan salah")

        # End
        return self.setting_password(user_data, password_new)

    def setting_password(self, user_data, password):
        # Data
        old_password = user_data.password
        new_password = generate_password_hash(password)

        # Save
        user_data.password = new_password
        user_data.save()

        # Create password change log
        password_data = UserPasswordModel()
        password_data.user_id = user_data.id_
        password_data.password_prev = old_password
        password_data.password_new = new_password
        password_data.client_info = ClientInfo().to_dict
        password_data.save()

        # End
        return msg_out(True, message="Password berhasil disimpan", tag="success")

    def setting_information_form(self, user_data, form):
        # Data
        data = DataModel()
        data.name = form.name.data
        data.gender = form.gender.data
        data.birthdate = form.birthdate.data
        data.contact = form.contact.data
        data.address = form.address.data

        # Config
        config = DataModel(data=user_data.config)
        config.language = "id"
        config.timezone = form.timezone.data
        data.config = config.to_dict

        # End
        return self.setting_information(user_data, data)

    def setting_information(self, user_data, data):
        # Save
        user_data.deleted = 0
        user_data.name = data.name
        user_data.gender = data.gender
        user_data.birthdate = data.birthdate
        user_data.contact = data.contact
        user_data.address = data.address

        # Set
        extra_info = DataModel(user_data.extra_info or {})
        extra_info.name = data.name
        extra_info.gender = data.gender
        extra_info.birthdate = data.birthdate
        extra_info.contact = data.contact
        extra_info.address = data.address
        # Set
        user_data.extra_info = extra_info.to_dict

        # Set email
        if data.email:
            # Set
            user_data.status = 1
            user_data.email = data.email
            # Check username and email
            if self.get_email_status(data.email, user_data.id_):
                return msg_out(False, message="Email sudah digunakan oleh pengguna lain", tag="error")

        # Set config
        if data.config:
            user_data.config = data.config

        # Save
        user_data.save()

        # End
        return msg_out(True, payload=user_data, message="Data pengguna berhasil disimpan", tag="success")


class UserSession(UserMixin):
    def __init__(self, token, user):
        self.id = token
        self.token = token
        self.user = user
