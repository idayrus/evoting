from flask import Blueprint, request, abort, redirect, url_for, render_template
from flask_login import current_user, login_required
from flask_paginate import Pagination
from app import app
from app.module.report import Report
from app.helper.utils import wrap_log, DataModel

# Init object
report = Report()
report_route = Blueprint('report', __name__, url_prefix='/report')

# Routes


@report_route.route('/', methods=['GET', 'POST'])
@login_required
@wrap_log()
def index():
    # Page data
    page_data = DataModel()
    page_data.title = "Laporan"
    page_data.menu = "report"

    return render_template("report/index.html", data=page_data)
