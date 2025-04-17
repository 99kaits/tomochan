import configparser
import math
import os
import random
import string
from datetime import timezone, timedelta, datetime

from flask import Flask
from routes import blueprints

config = configparser.ConfigParser()
if not os.path.exists("tomochan.ini"):
    new_key = "".join(random.choices(string.ascii_letters + string.digits, k=72))
    new_pass = "".join(random.choices(string.ascii_letters + string.digits, k=32))
    print("admin password is " + new_pass + " probably change it idk")
    boards = ["b", "tomo", "nottomo"]
    config["GLOBAL"] = {
        "secret_key": new_key,
        "upload_folder": "uploads",
        "admin_pass": new_pass,
        "boards": " ".join(boards),
        "captcha": "off"
    }
    for board in boards:
        config[board] = {
            "name": "Placeholder",
            "subtitle": "wow you should change me in the ini",
            "bump_limit": 300,
            "size": 150,
            "hidden": False,
            "r9k": False,
        }
    with open("tomochan.ini", "w") as configfile:
        config.write(configfile)
else:
    config.read("tomochan.ini")

def get_swatch(timestamp):
    time = datetime.fromtimestamp(timestamp, timezone.utc)
    bmt = time + timedelta(hours=1)
    beat = (
            math.floor(bmt.hour * 41.666 + bmt.minute * 0.6944 + bmt.second * 0.011574)
            % 1000
    )
    return beat

def get_strftime(timestamp):
    time = datetime.fromtimestamp(timestamp, timezone.utc)
    return time.strftime("%Y-%m-%d(%a) %H:%M:%S")

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config["GLOBAL"]["secret_key"]
    app.config["UPLOAD_FOLDER"] = config["GLOBAL"]["upload_folder"]

    app.jinja_env.globals.update(get_swatch=get_swatch, get_strftime=get_strftime)

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app