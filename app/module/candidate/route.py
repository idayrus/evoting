from flask import Blueprint, request, abort, redirect, url_for, render_template
from flask_login import current_user, login_required
from flask_paginate import Pagination
from app import app
from app.module.candidate import Candidate
from app.helper.utils import wrap_log, DataModel

# Init object
candidate = Candidate()
candidate_route = Blueprint('candidate', __name__, url_prefix='/candidate')

# Routes


@candidate_route.route('/', methods=['GET', 'POST'])
@login_required
@wrap_log()
def index():
    # Page data
    page_data = DataModel()
    page_data.title = "Data Calon"
    page_data.menu = "candidate"

    return render_template("candidate/index.html", data=page_data)
