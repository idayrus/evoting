from flask import Blueprint, request, abort, redirect, url_for, render_template
from flask_login import current_user, login_required
from flask_paginate import Pagination
from app import app
from app.module.user.form import *
from app.module.user import User
from app.helper.utils import wrap_log, DataModel, objectid

# Init object
user = User()
user_route = Blueprint('user', __name__, url_prefix='/user')

# Routes


@user_route.route('/', methods=['GET', 'POST'])
@login_required
@wrap_log()
def index():
    # Permission
    if not "user_read" in current_user.user.role:
        return abort(403)

    # Query
    search = request.args.get('q', type=str, default="")
    page = request.args.get('page', type=int, default=1)
    per_page = 25  # Default

    # Page data
    page_data = DataModel()
    page_data.title = "Pengguna"
    page_data.menu = "user"
    page_data.search = search
    page_data.tab = "user"

    # Filter
    query_data = DataModel()
    query_data.search = search

    # Data
    user_data = user.get_user_paginated(query_data, page=page, per_page=per_page)

    # Pagination
    pagination = Pagination(total=user_data.total, page=page, per_page=per_page, bs_version=4)

    # Set to page data
    page_data.user = user_data
    page_data.pagination = pagination

    return render_template("user/index.html", data=page_data)


@user_route.route('/editor', methods=['GET', 'POST'], defaults={'id_': None})
@user_route.route('/editor/', methods=['GET', 'POST'], defaults={'id_': None})
@user_route.route('/editor/<ObjectID:id_>/', methods=['GET', 'POST'])
@user_route.route('/editor/<ObjectID:id_>/', methods=['GET', 'POST'])
@login_required
@wrap_log()
def editor(id_):
    # Page data
    page_data = DataModel()
    page_data.title = "Tambah Pengguna"
    page_data.menu = "user"
    page_data.back_url = url_for('user.index')
    page_data.tab = request.args.get('tab', type=str, default=None)
    page_data.action = request.args.get('action', type=str, default=None)

    # Get user data
    user_data = user.get_user_by_id(id_)
    page_data.user = user_data

    # Permission
    if user_data:
        if not "user_update" in current_user.user.role:
            return abort(403)
    else:
        if not "user_create" in current_user.user.role:
            return abort(403)

    # Action delete
    if user_data:
        if page_data.action == "delete":
            # Permission
            if not "user_delete" in current_user.user.role:
                return abort(403)

            # Do delete
            user.setting_soft_delete(user_data)
            return redirect(url_for('user.index'))

    # Default
    form = None

    # Check tab
    if not page_data.tab in ["information", "role"] or not user_data:
        page_data.tab = "information"

    # Tab
    if page_data.tab == "information":
        # Check
        if user_data:
            # Set title
            page_data.title = "Edit Pengguna"

            # Form edit
            form = FormEditorEdit(
                email=user_data.email or "",
                name=user_data.name,
                gender=user_data.gender,
                birthdate=user_data.birthdate,
                contact=user_data.contact,
                address=user_data.address
            )

        else:
            # Form new
            form = FormEditorAdd()

        # Save form
        if form.validate_on_submit():
            # Do register
            register = user.register_save_form(form, user_data)
            if register.success:
                if user_data:
                    register.do_flash()
                    return redirect(url_for('user.editor', id_=register.payload.id_))
                else:
                    return redirect(url_for('user.editor', id_=register.payload.id_, tab='role'))
            else:
                register.do_flash()

        print(form.errors)

    elif page_data.tab == "role":
        # Check
        if not user_data:
            return abort(404)

        # Set title
        page_data.title = "Edit Pengguna"

        # Role list
        page_data.role_list = user.setting_role_get_available(user_data)

        # Save
        if request.method == 'POST':
            # Do save
            role = user.setting_role_update(user_data, request.form.getlist('role'))
            role.do_flash()
            return redirect(url_for('user.editor', id_=user_data.id_, tab='role'))

    else:
        return abort(404)

    return render_template("user/editor.html", form=form, data=page_data)


@user_route.route('/login', methods=['GET', 'POST'])
@user_route.route('/login/', methods=['GET', 'POST'])
@wrap_log()
def login():
    # If user already logged in
    if current_user.is_authenticated:
        return redirect('/')

    # Query
    email = request.args.get('email', type=str, default=None)
    next_page = request.args.get('next', type=str, default=None)

    # Page Data
    page_data = DataModel()
    page_data.email = email
    page_data.next_page = next_page
    page_data.wallpaper = None

    # Form
    form = FormLogin(usermail=email)
    if form.validate_on_submit():
        # Do login
        login = user.login_form(form)
        if login.success:
            return redirect('/')
        else:
            login.do_flash()

    return render_template("user/login.html", form=form, data=page_data)


@user_route.route('/logout', methods=['GET', 'POST'])
@user_route.route('/logout/', methods=['GET', 'POST'])
@login_required
@wrap_log()
def logout():
    # Do logout
    user.logout()
    return redirect(url_for('user.login'))


@user_route.route('/settings', methods=['GET', 'POST'], defaults={'tab': None})
@user_route.route('/settings/', methods=['GET', 'POST'], defaults={'tab': None})
@user_route.route('/settings/<tab>', methods=['GET', 'POST'])
@user_route.route('/settings/<tab>/', methods=['GET', 'POST'])
@login_required
@wrap_log()
def setting(tab):
    # Override
    if not tab in ["information", "password"]:
        tab = "information"

    # Page data
    page_data = DataModel()
    page_data.title = "Pengaturan Pengguna"
    page_data.menu = "user"
    page_data.tab = tab
    page_data.history = DataModel()
    page_data.user = current_user.user

    # Default
    form = None

    # Get data user
    user_data = page_data.user

    # Mode
    if tab == 'information':
        # Form
        form = FormUpdateUser(
            name=user_data.name,
            gender=user_data.gender,
            birthdate=user_data.birthdate,
            contact=user_data.contact,
            language=user_data.config.get("language"),
            timezone=user_data.config.get("timezone"),
        )
        if form.validate_on_submit():
            information = user.setting_information_form(user_data, form)
            information.do_flash()
            return redirect(url_for('user.setting', tab='information'))

    elif tab == 'password':
        # Form
        form = FormUpdatePassword()
        if form.validate_on_submit():
            password = user.setting_password_form(user_data, form)
            password.do_flash()
            return redirect(url_for('user.setting', tab='password'))

    else:
        return abort(404)

    return render_template("user/setting.html", data=page_data, form=form)
