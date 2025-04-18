import configparser
import os
import random
import string
from functools import lru_cache


@lru_cache(maxsize=1)
def create_config():
    config = configparser.ConfigParser()
    if os.path.exists("tomochan.ini"):
        return
    else:
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

        default_board = {
            "name": "Placeholder",
            "subtitle": "wow you should change me in the ini",
            "bump_limit": 300,
            "size": 150,
            "hidden": False,
            "r9k": False,
        }

        for board in boards:
            config[board] = default_board.copy()

        with open("tomochan.ini", "w") as configfile:
            config.write(configfile)
