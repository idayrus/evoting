from flask import request, url_for
from flask_login import current_user
from app import app
from app.helper.utils import msg_out, DataModel, save_base64_image
from app.module.candidate.model import CandidateModel
from sqlalchemy import or_, and_, not_
from datetime import datetime
from os import path, remove as remove_file
from time import time
from random import randrange


class Candidate():
    def __init__(self):
        app.jinja_env.globals.update(get_candidate_photo=self.get_candidate_photo)

    def get_candidate_by_id(self, id_):
        return CandidateModel.query.available().filter_by(id_=id_).first()

    def get_candidate_photo(self, candidate_data):
        if candidate_data.photo:
            photo_file = path.join(app.config.get('PUBLIC_DIR'), 'img', 'candidate', candidate_data.photo)
            if path.isfile(photo_file):
                return url_for('static', filename=f"img/candidate/{candidate_data.photo}")
        return url_for('static', filename="img/candidate-default.jpg")

    #
    # Candidate
    #

    def candidate_get_paginated(self, query_data, page=1, per_page=20):
        # Base query
        candidate_data = CandidateModel.query.available()

        # Search
        if query_data.search:
            candidate_data = candidate_data.filter(or_(
                CandidateModel.leader_name.ilike("%"+query_data.search+"%"),
                CandidateModel.deputy_name.ilike("%"+query_data.search+"%")
            ))

        # Sort
        candidate_data = candidate_data.order_by(CandidateModel.number.asc())

        # Paginate
        candidate_data = candidate_data.paginate(page=page, per_page=per_page)

        # End
        return candidate_data

    def candidate_save_form(self, form, candidate_data):
        # Data
        data = DataModel()
        data.number = form.number.data
        data.leader_name = form.leader_name.data
        data.deputy_name = form.deputy_name.data
        data.note = form.note.data
        data.campaign_video = form.campaign_video.data
        data.campaign_info = form.campaign_info.data

        # End
        return self.candidate_save(data, candidate_data)

    def candidate_save(self, data, candidate_data):
        # Create new
        if not candidate_data:
            candidate_data = CandidateModel()

        # Save
        candidate_data.number = data.number
        candidate_data.leader_name = data.leader_name
        candidate_data.deputy_name = data.deputy_name
        candidate_data.note = data.note
        candidate_data.campaign_video = data.campaign_video
        candidate_data.campaign_info = data.campaign_info
        candidate_data.save()

        # End
        return msg_out(True, payload=candidate_data)

    def candidate_soft_delete(self, candidate_data):
        if candidate_data:
            candidate_data.delete()
        return True

    def candidate_upload_photo(self, candidate_data):
        # Get data
        cover_base64 = request.form.get('cover')

        # Check
        if cover_base64.strip():
            # Delete old file
            if candidate_data.photo:
                old_file = path.join(app.config.get('PUBLIC_DIR'), 'img', 'candidate', candidate_data.photo)
                if path.isfile(old_file):
                    remove_file(old_file)

            # Process
            filename = f"{int(time())}_{randrange(100000, 999999)}.jpg"
            file_path = path.join(app.config.get('PUBLIC_DIR'), 'img', 'candidate', filename)
            save_base64_image(cover_base64, file_path, width=512)

            # Save
            candidate_data.photo = filename
            candidate_data.save()

        # End
        return True
