from flask import Blueprint, request, abort, redirect, url_for, render_template
from flask_login import current_user, login_required
from flask_paginate import Pagination
from app import app
from app.module.voter import Voter
from app.module.voter.form import VoterForm, VoterRegisterForm, VoterLoginForm
from app.helper.utils import wrap_log, DataModel

# Init object
voter = Voter()
voter_route = Blueprint('voter', __name__, url_prefix='/voter')


@voter_route.route('/', methods=['GET', 'POST'])
@login_required
@wrap_log()
def index():
    # Permission
    if not "voter_read" in current_user.user.role:
        return abort(403)

    # Page data
    page_data = DataModel()
    page_data.title = "Data Pemilih"
    page_data.menu = "voter"

    # Filter
    query_data = DataModel()
    query_data.search = request.args.get('q', type=str, default="")
    query_data.page = request.args.get('page', type=int, default=1)
    query_data.per_page = 100  # Default
    page_data.query = query_data

    # Data
    voter_data = voter.voter_get_paginated(query_data, page=query_data.page, per_page=query_data.per_page)

    # Pagination
    pagination = Pagination(total=voter_data.total, page=query_data.page, per_page=query_data.per_page, bs_version=4)

    # Set to page data
    page_data.voter = voter_data
    page_data.pagination = pagination

    return render_template("voter/index.html", data=page_data)


@voter_route.route('/register', methods=['GET', 'POST'])
@voter_route.route('/register/', methods=['GET', 'POST'])
@wrap_log()
def register():
    # Page Data
    page_data = DataModel()
    page_data.title = "Daftar"
    page_data.view = request.args.get('view', type=str, default=None)
    page_data.contact = request.args.get('contact', type=str, default=None)

    # Form new
    form = VoterRegisterForm()

    # Save
    if form.validate_on_submit():
        save = voter.voter_register_form(form)
        if save.success:
            return redirect(url_for('voter.register', view='success', contact=save.payload.contact))
        else:
            save.do_flash()

    return render_template("voter/register.html", form=form, data=page_data)


@voter_route.route('/vote', methods=['GET', 'POST'])
@voter_route.route('/vote/', methods=['GET', 'POST'])
@wrap_log()
def vote():
    # Page Data
    page_data = DataModel()
    page_data.title = "Berikan Suara"
    page_data.voter = voter.vote_get_voter()
    page_data.vote = request.args.get('vote', type=str, default=None)
    page_data.view = request.args.get('view', type=str, default=None)

    # Check vote
    if not voter.get_voting_status():
        return redirect('/')

    # Login
    if page_data.voter:
        # Get data
        page_data.candidate = voter.vote_get_candidate()
        page_data.ballot = voter.voter_get_ballot(page_data.voter)

        # Ballot used
        if page_data.ballot:
            voter.vote_logout()
            return redirect(url_for('voter.vote', view='success'))

        # Handle vote
        if page_data.vote:
            vote = voter.vote_set(page_data.voter, page_data.vote)
            vote.do_flash()
            return redirect(url_for('voter.vote', view='success'))

    else:
        # Not login
        page_data.form = VoterLoginForm()
        if page_data.form.validate_on_submit():
            login = voter.vote_login(page_data.form)
            if login.success:
                return redirect(url_for('voter.vote'))
            else:
                login.do_flash()

    return render_template("voter/vote.html", data=page_data)


@voter_route.route('/editor', methods=['GET', 'POST'], defaults={'id_': None})
@voter_route.route('/editor/', methods=['GET', 'POST'], defaults={'id_': None})
@voter_route.route('/editor/<ObjectID:id_>', methods=['GET', 'POST'])
@voter_route.route('/editor/<ObjectID:id_>/', methods=['GET', 'POST'])
@login_required
@wrap_log()
def editor(id_):
    # Page data
    page_data = DataModel()
    page_data.title = "Tambah Data Pemilih"
    page_data.menu = "voter"
    page_data.back_url = url_for('voter.index')
    page_data.voter = voter.get_voter_by_id(id_)

    # Check
    if page_data.voter:
        # Permission
        if not "voter_update" in current_user.user.role:
            return abort(403)

        # Set title
        page_data.title = "Edit Data Pemilih"

        # Form edit
        form = VoterForm(
            id_number=page_data.voter.id_number,
            name=page_data.voter.name,
            gender=page_data.voter.gender,
            birthdate=page_data.voter.birthdate,
            contact=page_data.voter.contact,
            address=page_data.voter.address
        )

    else:
        # Permission
        if not "voter_create" in current_user.user.role:
            return abort(403)

        # Form new
        form = VoterForm()

    # Save
    if form.validate_on_submit():
        save = voter.voter_save_form(form, page_data.voter)
        if save.success:
            return redirect(url_for('voter.detail', id_=save.payload.id_))
        else:
            save.do_flash()

    return render_template("voter/editor.html", form=form, data=page_data)


@voter_route.route('/detail/<ObjectID:id_>', methods=['GET', 'POST'])
@voter_route.route('/detail/<ObjectID:id_>/', methods=['GET', 'POST'])
@login_required
@wrap_log()
def detail(id_):
    # Permission
    if not "voter_read" in current_user.user.role:
        return abort(403)

    # Page data
    page_data = DataModel()
    page_data.title = "Data Pemilih"
    page_data.menu = "voter"
    page_data.back_url = url_for('voter.index')
    page_data.voter = voter.get_voter_by_id(id_)
    page_data.action = request.args.get('action', type=str, default=None)

    # Check
    if not page_data.voter:
        return abort(404)

    # Get ballot status
    page_data.ballot = voter.voter_get_ballot(page_data.voter)

    # Handle delete
    if page_data.action == 'delete' and "voter_delete" in current_user.user.role:
        voter.voter_soft_delete(page_data.voter)
        return redirect(url_for('voter.index'))

    # Handle update pin
    if page_data.action == 'refresh-pin' and "voter_refresh" in current_user.user.role:
        voter.voter_refresh_pin(page_data.voter)
        return redirect(url_for('voter.detail', id_=id_))

    # Handle confirm
    if page_data.action == 'confirm' and "voter_confirm" in current_user.user.role:
        voter.voter_confirm(page_data.voter)
        return redirect(url_for('voter.detail', id_=id_))

    return render_template("voter/detail.html", data=page_data)
