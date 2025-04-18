import configparser
import math
from datetime import timezone, timedelta, datetime

from flask import Flask

from app.routes import blueprints

config = configparser.ConfigParser()
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
    [app.register_blueprint(blueprint) for blueprint in blueprints]

    return app
