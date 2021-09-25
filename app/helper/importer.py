from app import app
from flask import request
from werkzeug import secure_filename
from os import path, remove as remove_file
from random import randrange
from time import time
from openpyxl import load_workbook


def allowed_ext(filename, allowed=[".xlsx"]):
    # Extension
    ext = path.splitext(filename)[1]
    # End
    return ext in allowed


def stringify(value):
    if value:
        return bytes(str(value), 'utf-8').decode('utf-8-sig').strip()
    else:
        return ""


def remove_temp(filepath):
    if path.isfile(filepath):
        remove_file(filepath)
    return True


def get_uploaded_import_wb_file():
    # Default output
    output = None

    # Form name
    form_name = "file_import"

    # On post
    if request.method == "POST":
        # Check form
        if form_name in request.files:
            # Get file
            file = request.files[form_name]
            filename = file.filename.strip()
            is_update = request.form.get("update") == "y"
            # Check filename
            if not filename == "":
                # Check extension
                if allowed_ext(filename):
                    # Path
                    filename_clean = secure_filename(f"import_{randrange(1000, 9999)}_{int(time())}.xlsx")
                    save_path = path.join(
                        app.config.get("PRIVATE_DIR"),
                        "temp",
                        filename_clean
                    )
                    # Save
                    file.save(save_path)
                    # Load file
                    try:
                        # Load workbook
                        wb = load_workbook(save_path)
                        # End
                        return (True, save_path, wb, is_update)
                    except Exception as e:
                        # Remove file
                        remove_file(save_path)
                        # End
                        return (False, "Terjadi kesalahan saat memuat file")
                else:
                    # End
                    return (False, "Ekstensi tidak diizinkan, silahkan upload file berekstensi *.xlsx")
            else:
                # End
                return (False, "Silahkan pilih file terlebih dahulu")
        else:
            # End
            return (False, "Gagal menemukan file pada permintaan form")

    # End
    return output
