from flask import Blueprint, request, abort, redirect, url_for, render_template
from flask_login import current_user, login_required
from flask_paginate import Pagination
from app import app
from app.module.candidate import Candidate
from app.module.candidate.form import CandidateForm
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

    # Filter
    query_data = DataModel()
    query_data.search = request.args.get('q', type=str, default="")
    query_data.page = request.args.get('page', type=int, default=1)
    query_data.per_page = 25  # Default
    page_data.query = query_data

    # Data
    candidate_data = candidate.candidate_get_paginated(query_data, page=query_data.page, per_page=query_data.per_page)

    # Pagination
    pagination = Pagination(total=candidate_data.total, page=query_data.page, per_page=query_data.per_page, bs_version=4)

    # Set to page data
    page_data.candidate = candidate_data
    page_data.pagination = pagination

    return render_template("candidate/index.html", data=page_data)


@candidate_route.route('/editor', methods=['GET', 'POST'], defaults={'id_': None})
@candidate_route.route('/editor/', methods=['GET', 'POST'], defaults={'id_': None})
@candidate_route.route('/editor/<ObjectID:id_>', methods=['GET', 'POST'])
@candidate_route.route('/editor/<ObjectID:id_>/', methods=['GET', 'POST'])
@login_required
@wrap_log()
def editor(id_):
    # Page data
    page_data = DataModel()
    page_data.title = "Tambah Data Pemilih"
    page_data.menu = "candidate"
    page_data.back_url = url_for('candidate.index')
    page_data.candidate = candidate.get_candidate_by_id(id_)

    # Check
    if page_data.candidate:
        # Set title
        page_data.title = "Edit Data Pemilih"

        # Form edit
        form = CandidateForm(
            number=page_data.candidate.number,
            leader_name=page_data.candidate.leader_name,
            deputy_name=page_data.candidate.deputy_name,
            note=page_data.candidate.note,
            campaign_video=page_data.candidate.campaign_video,
            campaign_info=page_data.candidate.campaign_info
        )

    else:
        # Form new
        form = CandidateForm()

    # Save
    if form.validate_on_submit():
        save = candidate.candidate_save_form(form, page_data.candidate)
        if save.success:
            return redirect(url_for('candidate.detail', id_=save.payload.id_))
        else:
            save.do_flash()

    return render_template("candidate/editor.html", form=form, data=page_data)


@candidate_route.route('/detail/<ObjectID:id_>', methods=['GET', 'POST'])
@candidate_route.route('/detail/<ObjectID:id_>/', methods=['GET', 'POST'])
@login_required
@wrap_log()
def detail(id_):
    # Page data
    page_data = DataModel()
    page_data.title = "Data Pemilih"
    page_data.menu = "candidate"
    page_data.back_url = url_for('candidate.index')
    page_data.candidate = candidate.get_candidate_by_id(id_)
    page_data.action = request.args.get('action', type=str, default=None)

    # Check
    if not page_data.candidate:
        return abort(404)

    # Handle delete
    if page_data.action == 'delete':
        candidate.candidate_soft_delete(page_data.candidate)
        return redirect(url_for('candidate.index'))

    return render_template("candidate/detail.html", data=page_data)
