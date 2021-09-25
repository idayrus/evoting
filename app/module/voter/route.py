from flask import Blueprint, request, abort, redirect, url_for, render_template
from flask_login import current_user, login_required
from flask_paginate import Pagination
from app import app
from app.module.voter import Voter
from app.helper.utils import wrap_log, DataModel

# Init object
voter = Voter()
voter_route = Blueprint('voter', __name__, url_prefix='/voter')

# Routes


@voter_route.route('/', methods=['GET', 'POST'])
@login_required
@wrap_log()
def index():
    # Page data
    page_data = DataModel()
    page_data.title = "Data Pemilih"
    page_data.menu = "voter"

    return render_template("voter/index.html", data=page_data)
