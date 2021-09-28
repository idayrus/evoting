from flask_login import current_user
from app import app
from app.module.voter.model import VoterModel, VoterBallotModel
from app.helper.utils import msg_out, DataModel
from app.helper.phone import filter_phone, is_valid_phone
from sqlalchemy import or_, and_, not_
from datetime import datetime
from random import randrange
from os import path
from time import time
from io import BytesIO
from PIL import Image
from base64 import b64decode


class Voter():
    def __init__(self):
        pass

    def get_voter_by_id(self, id_):
        return VoterModel.query.available().filter_by(id_=id_).first()

    def get_identifier_status(self, id_number, current_id=None):
        # Check identifier
        voter_data = VoterModel.query.available().filter_by(id_number=id_number).first()
        if voter_data:
            # Check data
            if not str(current_id) == str(voter_data.id_):
                # End
                return True
        # End
        return False

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

    def voter_register_form(self, form):
        # Data
        data = DataModel()
        data.id_number = form.id_number.data
        data.name = form.name.data
        data.gender = form.gender.data
        data.contact = form.contact.data
        data.signature = form.signature.data
        data.birthdate = None
        data.address = None

        # End
        return self.voter_save(data)

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

    def voter_save(self, data, voter_data=None):
        # Get current ID
        current_id = None
        if voter_data:
            current_id = voter_data.id_

        # Check ID number
        if self.get_identifier_status(data.id_number, current_id):
            return msg_out(False, message="NIM sudah digunakan. Jika anda merasa ini adalah kesalahan, silahkan hubungi admin.")

        # Check GSM phone
        if not is_valid_phone(data.contact):
            return msg_out(False, message="Nomor WhatsApp yang dimasukan tidak valid")

        # Process signature
        signature_filename = None
        if data.signature:
            width = 400
            img_base64 = data.signature
            filename = f"signature_{int(time())}_{randrange(1000, 9999)}.jpg"
            filepath = path.join(app.config.get("PUBLIC_DIR"), "upload", filename)
            signature_filename = filename

            try:
                # Check
                if not img_base64:
                    return msg_out(False, message="Belum menulis tanda tangan")

                # Check
                img_base64_split = img_base64.split(",")
                if not len(img_base64_split) > 1:
                    return msg_out(False, message="Terjadi kesalahan saat men-split data")

                # Split base64 margin and decode
                img_decoded = b64decode(img_base64_split[1])
                img = Image.open(BytesIO(img_decoded))

                # Resize image
                width_percent = (width / float(img.size[0]))
                height = int((float(img.size[1]) * float(width_percent)))
                img = img.resize((width, height), Image.ANTIALIAS)

                # Load image
                img_original = img.convert("RGBA")

                # Paste to white bg
                img_new = Image.new("RGB", img_original.size, "WHITE")
                img_new.paste(img_original, (0, 0), img_original)

                # Save
                img_new.save(filepath)

            except Exception as e:
                # End
                return msg_out(False, message="Terjadi kesalahan, %s" % (e))

        # Create new
        if not voter_data:
            voter_data = VoterModel()
            voter_data.pin = randrange(100000, 999999)
            voter_data.status = 'unconfirmed'

        # Save
        voter_data.id_number = data.id_number
        voter_data.name = data.name
        voter_data.gender = data.gender
        voter_data.birthdate = data.birthdate
        voter_data.contact = filter_phone(data.contact)
        voter_data.address = data.address
        voter_data.signature = signature_filename
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

    def voter_confirm(self, voter_data):
        # Update
        voter_data.status = 'confirmed'
        voter_data.confirm_at = datetime.utcnow()
        voter_data.confirm_by = current_user.user.id_
        voter_data.save()
        return voter_data
