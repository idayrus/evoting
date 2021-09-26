from flask import request
from flask_login import current_user
from sqlalchemy.sql.elements import outparam
from app import app
from app.module.voter.model import VoterModel, VoterBallotModel
from app.helper.utils import msg_out, DataModel
from sqlalchemy import or_, and_, not_
from datetime import datetime
from random import randrange


class Voter():
    def __init__(self):
        pass

    def get_voter_by_id(self, id_):
        return VoterModel.query.available().filter_by(id_=id_).first()

    #
    # Voter
    #

    def voter_get_paginated(self, query_data, page=1, per_page=20):
        # Base query
        voter_data = VoterModel.query.available()

        # Search
        if query_data.search:
            voter_data = voter_data.filter(or_(
                VoterModel.id_number.ilike("%"+query_data.search+"%"),
                VoterModel.name.ilike("%"+query_data.search+"%")
            ))

        # Sort
        voter_data = voter_data.order_by(VoterModel.id_number.asc())

        # Paginate
        voter_data = voter_data.paginate(page=page, per_page=per_page)

        # Output
        output = DataModel()
        output.total = voter_data.total
        output.items = []

        # Process
        for item in voter_data.items:
            item_data = DataModel(item.detach_copy().__dict__)
            item_data.ballot = self.voter_get_ballot(item)
            output.items.append(item_data)

        # End
        return output

    def voter_get_ballot(self, voter_data):
        return VoterBallotModel.query.filter_by(voter_id=voter_data.id_).first()

    def voter_save_form(self, form, voter_data):
        # Data
        data = DataModel()
        data.id_number = form.id_number.data
        data.name = form.name.data
        data.gender = form.gender.data
        data.birthdate = form.birthdate.data
        data.contact = form.contact.data
        data.address = form.address.data

        # End
        return self.voter_save(data, voter_data)

    def voter_save(self, data, voter_data):
        # Create new
        if not voter_data:
            voter_data = VoterModel()
            voter_data.pin = randrange(100000, 999999)

        # Save
        voter_data.id_number = data.id_number
        voter_data.name = data.name
        voter_data.gender = data.gender
        voter_data.birthdate = data.birthdate
        voter_data.contact = data.contact
        voter_data.address = data.address
        voter_data.save()

        # End
        return msg_out(True, payload=voter_data)

    def voter_soft_delete(self, voter_data):
        if voter_data:
            voter_data.delete()
        return True

    def voter_refresh_pin(self, voter_data):
        # Update
        voter_data.pin = randrange(100000, 999999)
        voter_data.save()
        return voter_data
