from flask import Blueprint, render_template

home_bp = Blueprint("home", __name__, template_folder="../../templates")


@home_bp.route("/")
def home_page():
    # TODO: FIGURE OUT WHAT TO DO ABOUT THE CREATE_CONFIG() THING
    # also todo add recent threads and stuff idk
    boardlist = {"b": "Random/tomo", "tomo": "tomo/tomo", "nottomo": "not tomo/not tomo"}
    return render_template("homepage.html", boardlist=boardlist)
