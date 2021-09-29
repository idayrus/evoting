from flask import render_template_string, request
from flask_login import current_user
from app import app
from app.module.setting.model import SettingModel
from app.module.candidate.model import CandidateModel
from app.helper.utils import msg_out, DataModel
from app.helper.datetime import DateTime
from sqlalchemy import or_, and_, not_
from datetime import datetime
from os import path


class Setting():
    def __init__(self):
        pass

    def get_setting(self):
        return SettingModel.query.filter_by(identifier='default').first()

    #
    # Setting
    #

    def setting_save_form(self, setting_data, form):
        try:
            # Parse
            date_format = "%d-%m-%Y %H:%M"
            start_text = f"{form.start_date.data} {form.start_time.data}"
            end_txt = f"{form.end_date.data} {form.end_time.data}"
            start = DateTime().from_local(start_text, date_format).to_utc().as_datetime()
            end = DateTime().from_local(end_txt, date_format).to_utc().as_datetime()

            # Validate
            if not start > end:
                # Container
                data = DataModel()
                data.vote_start = start
                data.vote_end = end
                # End
                return self.setting_save(setting_data, data)
            else:
                # End
                return msg_out(False, message='Waktu mulai tidak boleh lebih lama dari waktu selesai')

        except Exception as e:
            # End
            return msg_out(False, message=f'Terjadi kesalahan: {e}')

    def setting_save(self, setting_data, data):
        # Save
        setting_data.vote_start = data.vote_start
        setting_data.vote_end = data.vote_end
        setting_data.save()

        # End
        return msg_out(True)

    def setting_date(self, setting_data):
        # Container
        data = DataModel()
        data.start_date = ""
        data.start_time = ""
        data.end_date = ""
        data.end_time = ""

        # Parse
        if setting_data.vote_start:
            start_date = DateTime().from_utc(setting_data.vote_start).to_local().as_datetime()
            data.start_date = start_date.strftime("%d-%m-%Y")
            data.start_time = start_date.strftime("%H:%M")

        if setting_data.vote_end:
            end_date = DateTime().from_utc(setting_data.vote_end).to_local().as_datetime()
            data.end_date = end_date.strftime("%d-%m-%Y")
            data.end_time = end_date.strftime("%H:%M")

        # End
        return data

    #
    # Template
    #

    def template_render(self, is_direct=False):
        # Data
        page_data = DataModel()
        page_data.candidate = CandidateModel.query.available().order_by(CandidateModel.number.asc()).all()
        page_data.setting = self.get_setting()

        # Check status
        page_data.current = datetime.utcnow()
        page_data.is_start = page_data.setting.vote_start <= page_data.current
        page_data.is_end = page_data.setting.vote_end <= page_data.current

        # Get HTML
        if request.args.get('__read_direct', type=str, default=None) == "true" or is_direct:
            # From File
            template_html = self.template_file()
        else:
            # From Database
            setting_data = self.get_setting()
            template_html = setting_data.template or ""

        # End
        return render_template_string(template_html, data=page_data)

    def template_save_form(self, setting_data, form):
        # Get HTML
        template_html = form.content.data

        # End
        return self.template_save(setting_data, template_html)

    def template_save(self, setting_data, template_html):
        # Save
        setting_data.template = template_html
        setting_data.save()

        # End
        return msg_out(True)

    def template_file(self):
        template_file = path.join(app.config.get("PRIVATE_DIR"), "landing", "base.html")
        file = open(template_file, "r")
        template_html = file.read()
        file.close()
        return template_html

    def template_reset(self, setting_data):
        # Save
        setting_data.template = self.template_file()
        setting_data.save()

        # End
        return msg_out(True)