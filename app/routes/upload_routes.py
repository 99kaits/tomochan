from flask import Blueprint, send_from_directory, current_app

upload_bp = Blueprint("uploads", __name__)


@upload_bp.route("/uploads/<path:name>")
def show_upload(name):
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"], name, as_attachment=False
    )
