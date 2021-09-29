from flask import request, jsonify
from flask_login import current_user
from app import app
from app.module.candidate.model import CandidateModel
from app.module.voter.model import VoterModel, VoterBallotModel
from app.helper.utils import msg_out, DataModel
from sqlalchemy import or_, and_, not_
from datetime import datetime
from json import dumps as json_dumps


class Report():
    def __init__(self):
        pass

    def get_candidate_all(self):
        return CandidateModel.query.available().order_by(CandidateModel.number.asc()).all()

    def get_overview(self):
        # Container
        data = DataModel()
        data.candidate_total = CandidateModel.query.available().count()
        data.voter_total = VoterModel.query.available().count()
        data.ballot_total = VoterBallotModel.query.available().count()

        # End
        return data

    def get_vote_count(self, candidate_id):
        return VoterBallotModel.query.filter_by(candidate_id=candidate_id).count() or 0

    def get_chart(self):
        # Colors
        colors = [
            'rgba(54, 162, 235, 0.75)',
            'rgba(255, 99, 132, 0.75)',
            'rgba(255, 206, 86, 0.75)',
            'rgba(75, 192, 192, 0.75)',
            'rgba(153, 102, 255, 0.75)',
            'rgba(255, 159, 64, 0.75)'
        ]

        # Container
        data = DataModel()
        data.total = []
        data.color = []
        data.name = []

        # Process
        for i, candidate in enumerate(self.get_candidate_all()):
            try:
                color = colors[i]
            except Exception as e:
                color = "29b6f6"
            data.name.append(candidate.leader_name)
            data.color.append(color)
            data.total.append(self.get_vote_count(candidate.id_))

        # Convert to JSON
        data.total_json = json_dumps(data.total)
        data.color_json = json_dumps(data.color)
        data.name_json = json_dumps(data.name)

        # End
        return data
