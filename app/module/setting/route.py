from flask import Blueprint, request, abort, redirect, url_for, render_template
from flask_login import current_user, login_required
from flask_paginate import Pagination
from app import app
from app.module.setting import Setting
from app.module.setting.form import TemplateForm, SettingForm
from app.helper.utils import wrap_log, DataModel

# Init object
setting = Setting()
setting_route = Blueprint('setting', __name__, url_prefix='/setting')

# Routes


@app.route('/', methods=['GET', 'POST'])
@wrap_log()
def landing():
   return "OK"


@setting_route.route('/', methods=['GET', 'POST'])
@login_required
@wrap_log()
def index():
    # Page data
    page_data = DataModel()
    page_data.title = "Template"
    page_data.menu = "setting"
    page_data.tab = request.args.get('tab', type=str, default='setting')

    # Override tab
    if not page_data.tab in ['setting', 'template']:
        page_data.tab = 'setting'

    # Check
    if page_data.tab == 'setting':
        # Form
        form = SettingForm()

        # Save
        if form.validate_on_submit():
            pass

    elif page_data.tab == 'template':
        # Form
        form = TemplateForm()

        # Save
        if form.validate_on_submit():
            pass

    return render_template("setting/index.html", form=form, data=page_data)
