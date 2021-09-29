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
   return setting.template_render()


@setting_route.route('/', methods=['GET', 'POST'])
@login_required
@wrap_log()
def index():
    # Page data
    page_data = DataModel()
    page_data.title = "Template"
    page_data.menu = "setting"
    page_data.tab = request.args.get('tab', type=str, default='setting')
    page_data.action = request.args.get('action', type=str, default=None)
    page_data.setting = setting.get_setting()

    # Override tab
    if not page_data.tab in ['setting', 'template']:
        page_data.tab = 'setting'

    # Check
    if page_data.tab == 'setting':
        # Date
        setting_date = setting.setting_date(page_data.setting)

        # Form
        form = SettingForm(
            start_date = setting_date.start_date,
            start_time = setting_date.start_time,
            end_date = setting_date.end_date,
            end_time = setting_date.end_time,
        )
        if form.validate_on_submit():
            save = setting.setting_save_form(page_data.setting, form)
            save.do_flash()
            return redirect(url_for('setting.index', tab=page_data.tab))

    elif page_data.tab == 'template':
        # Handle reset
        if page_data.action == 'reset':
            setting.template_reset(page_data.setting)
            return redirect(url_for('setting.index', tab=page_data.tab))

        # Form
        form = TemplateForm(content=page_data.setting.template)
        if form.validate_on_submit():
            save = setting.template_save_form(page_data.setting, form)
            save.do_flash()
            return redirect(url_for('setting.index', tab=page_data.tab))

    return render_template("setting/index.html", form=form, data=page_data)
