import base64
import configparser
import magic
import math
import os
import random
import sqlite3
import string
import xml.etree.ElementTree as ET

from captcha.image import ImageCaptcha
from captcha.audio import AudioCaptcha
from datetime import datetime, timedelta, timezone
from io import BytesIO
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    url_for,
)
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from markupsafe import escape
from wand.image import Image
from werkzeug.utils import secure_filename
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional
from functools import lru_cache

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

app = Flask(__name__)
app.config["SECRET_KEY"] = config["GLOBAL"]["secret_key"]
app.config["UPLOAD_FOLDER"] = config["GLOBAL"]["upload_folder"]

if config['GLOBAL']['captcha'] == "simple":
    imagecaptcha = ImageCaptcha()
    audiocaptcha = AudioCaptcha()
else:
    imagecaptcha = None
    audiocaptcha = None

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "avif",
    "webp",
    "heic",
    "heif",
    "jxl",
}
boards = config["GLOBAL"]["boards"].split(" ")
boardlist = [board for board in boards if not config[board].getboolean("hidden")]

sql = (
    "INSERT INTO posts(post_id, board_id, thread_id, op, last_bump, "
    "reply_count, sticky, time, name, email, subject, content, filename, "
    "file_actual, file_thumbnail, filesize, file_width, file_height, password, spoiler, ip) "
    "values(:post_id, :board_id, :thread_id, :op, :last_bump, "
    ":reply_count, :sticky, :time, :name, :email, :subject, :content, "
    ":filename, :file_actual, :file_thumbnail, :filesize, :file_width, :file_height, :password, :spoiler, :ip)"
)


def allowed_mime_type(file):
    mime = magic.from_buffer(file.stream.read(2048), mime=True)
    file.stream.seek(0)  # Reset file pointer after reading
    return mime in [
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/avif",
        "image/webp",
        "image/heic",
        "image/heif",
        "image/jxl",
    ]

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def post(form, board, thread_id):
    con = sqlite3.connect("tomochan.db")
    cur = con.cursor()

    if board in boards:
        largest_post_id = cur.execute("SELECT max(post_id) from posts").fetchone()[0]

        if form.name.data:
            name = form.name.data
        else:
            name = "Anonymous"

        timestamp = datetime.now(timezone.utc).timestamp()

        if not largest_post_id:
            post_id = 1
        else:
            post_id = largest_post_id + 1

        # TODO: CHECK THREAD IDS IN THE POST CODE!!!!
        """
        if thread_id:
            threadquery = cur.execute('SELECT * FROM posts WHERE thread_id = ?', (thread_id,))
            if threadquery
        """

        if not thread_id:
            thread_id = post_id
            last_bump = timestamp
            op = 1
        else:
            last_bump = None
            op = 0

        if op == 0:
            if not form.email.data == "sage" or form.email.data == "nonokosage":
                cur.execute(
                    "UPDATE posts SET last_bump = ?, reply_count = reply_count + 1"
                    " WHERE post_id = ? AND op == 1",
                    (timestamp, thread_id),
                )

        if form.file.data and allowed_mime_type(form.file.data):
            filename = secure_filename(form.file.data.filename)
            with Image(file=form.file.data.stream, format=filename.rsplit(".", 1)[1].lower()) as original:
                file_width = original.width
                file_height = original.height
                with original.clone() as thumbnail:
                    thumbnail.transform(resize="250x250>")
                    file_thumbnail = str(post_id) + "_thumbnail.webp"
                    thumbnail.save(filename=os.path.join(app.config["UPLOAD_FOLDER"], file_thumbnail))

                file_actual = str(post_id) + "." + filename.rsplit(".", 1)[1].lower()
                original.save(filename=os.path.join(app.config["UPLOAD_FOLDER"], file_actual))
                filesize = os.stat(os.path.join(app.config["UPLOAD_FOLDER"], file_actual)).st_size

        else:
            filename = None
            file_actual = None
            file_thumbnail = None
            filesize = None
            file_width = None
            file_height = None

        if "X-Forwarded-For" in request.headers:
            ip = request.headers.getlist("X-Forwarded-For")[0].rpartition(" ")[-1]
        else:
            ip = request.remote_addr

        content = escape(form.post.data)

        new_post = {
            "post_id": post_id,
            "board_id": board,
            "thread_id": thread_id,
            "op": op,
            "last_bump": last_bump,
            "reply_count": 0,
            "sticky": 0,
            "time": timestamp,
            "name": name,
            "email": form.email.data,
            "subject": form.subject.data,
            "content": content,
            "filename": filename,
            "file_actual": file_actual,
            "file_thumbnail": file_thumbnail,
            "filesize": filesize,
            "file_width": file_width,
            "file_height": file_height,
            "password": form.password.data,
            "spoiler": form.spoiler.data,
            "ip": ip,
        }
        cur.execute(sql, new_post)
        con.commit()
        con.close()
        return post_id
    else:
        return 0


def get_password():
    return "".join(
        random.choices(string.ascii_letters + string.digits + string.punctuation, k=12)
    )

def get_banners_mtime():
    # Get the latest modification time of the banners folder
    return max(os.path.getmtime(os.path.join("static/banners", f)) for f in os.listdir("static/banners"))

@lru_cache(maxsize=1) # Cache banner list.
def get_banner_list():
    return os.listdir("static/banners")

def get_banner(board):
    # TODO: board specific banners
    current_mtime = get_banners_mtime()
    if get_banner_list.cache_info().hits > 0 and current_mtime != get_banner_list.cache_clear():
        get_banner_list.cache_clear()
    banner = random.choice(get_banner_list())
    return "/static/banners/" + banner


@lru_cache(maxsize=1) # Cache ad list. Should only refresh when the .xml file is updated.
def get_ads_list():
    adtree = ET.parse("static/ads/ads.xml")  # TODO: move to a better spot
    root = adtree.getroot()
    return [
        [x.find("image").text, x.find("text").text, x.find("url").text, x.find("size").text]
        for x in root.findall("ad")
    ]


def get_ad(size):
    current_mtime = os.path.getmtime("static/ads/ads.xml")
    if get_ads_list.cache_info().hits > 0 and current_mtime != get_ads_list.cache_clear():
        get_ads_list.cache_clear() # Invalidate cache if the file has been updated.
    ads = get_ads_list() # Get cached ads
    filtered_ads = [ad for ad in ads if ad[3] == size] if size in ["small", "big"] else []
    if not filtered_ads:
        return
    ad = random.choice(filtered_ads)
    return ("/static/ads/" + ad[0]), ad[1], ad[2]


def content_parser(content):
    # TODO: MAKE SURE THE TAGS CLOSE
    # TODO: replace \n with <br>
    # TODO: replace > with span with class quote
    if "&gt;" in content:  # > escaped
        pass


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


def get_threads(board):
    con = sqlite3.connect("tomochan.db")
    con.row_factory = dict_factory
    cur = con.cursor()

    oplist = cur.execute(
        "SELECT * FROM posts WHERE op = 1 AND board_id = ? ORDER BY sticky DESC, last_bump DESC",
        (board,)
    ).fetchall()

    thread_ids = [op["post_id"] for op in oplist]
    replies = cur.execute(
        "SELECT * FROM posts WHERE thread_id IN ({}) AND op = 0 ORDER BY post_id DESC".format(
            ",".join("?" for _ in thread_ids)
        ),
        thread_ids
    ).fetchall()

    # Group replies by thread_id
    replies_by_thread = {}
    for reply in replies:
        replies_by_thread.setdefault(reply["thread_id"], []).append(reply)

    threadlist = []
    for op in oplist:
        thread = [op] + list(reversed(replies_by_thread.get(op["post_id"], [])[:5]))
        threadlist.append(thread)

    con.close()
    return threadlist


app.jinja_env.globals.update(get_swatch=get_swatch, get_strftime=get_strftime)


class PostForm(FlaskForm):
    name = StringField("Name", validators=[Optional()])
    email = StringField("Email", validators=[Optional()])
    subject = StringField("Subject", validators=[Optional()])
    post = TextAreaField("Content", validators=[DataRequired()])
    if imagecaptcha:
        captcha = StringField("Verification", validators=[DataRequired()])
    # TODO: FILE SIZE LIMIT, THE VALIDATOR DOESNT WORK FOR SOME REASON
    file = FileField(
        "File", validators=[FileAllowed(ALLOWED_EXTENSIONS, "the fuck is this shit?")]
    )
    spoiler = BooleanField("Spoiler?", validators=[Optional()])
    password = StringField("Password", validators=[Optional()])
    submit = SubmitField("Post")


@app.route("/<board>/", methods=["GET", "POST"])
def board_page(board):
    if board in boards:

        threadlist = get_threads(board)
        banner = get_banner(board)
        boardname = config[board]["name"]
        boardsubtitle = config[board]["subtitle"]
        randompassword = get_password()
        if imagecaptcha:
            captcha_code = "JOE BIDEN"
            captcha_data = imagecaptcha.generate(captcha_code)
            captcha = base64.b64encode(captcha_data.read()).decode()
            audio_code = "42069"
            audio_data = audiocaptcha.generate(audio_code)
            audio = base64.b64encode(audio_data)
        else:
            captcha = None
            audio = None

        form = PostForm()
        if form.validate_on_submit():
            if captcha:
                if form.captcha.data != captcha_code or form.captcha.data != audio_code:
                    return redirect("/static/posterror.html")
            if form.file.data and form.post.data:
                thread_id = None
                new_post = post(form, board, thread_id)
                if new_post > 0:
                    if form.email.data == "nonoko" or form.email.data == "nonokosage":
                        return redirect(url_for("board_page", board=board))
                    else:
                        return redirect(
                            url_for("thread_page", board=board, thread=new_post)
                        )
                else:
                    return redirect("/static/posterror.html")
            else:
                # TODO: error code for trying to make a new thread without a picture
                return redirect("/static/posterror.html")

        footad = get_ad("big")
        headad = get_ad("big")
        formad = get_ad("small")

        return render_template(
            "board.html",
            boardlist=boardlist,
            board=board,
            boardname=boardname,
            boardsubtitle=boardsubtitle,
            form=form,
            captcha=captcha,
            audio=audio,
            threads=threadlist,
            banner=banner,
            password=randompassword,
            footad=footad[0],
            footadtext=footad[1],
            footadurl=footad[2],
            headad=headad[0],
            headadtext=headad[1],
            headadurl=headad[2],
            formad=formad[0],
            formadtext=formad[1],
            formadurl=formad[2]
        )
    else:
        return send_file("static/404.html"), 404


@app.route("/<board>/catalog", methods=["GET", "POST"])
def catalog_page(board):
    if board in boards:
        con = sqlite3.connect("tomochan.db")
        con.row_factory = dict_factory
        cur = con.cursor()
        select_threads = cur.execute(
            "SELECT * FROM posts WHERE op = 1 ORDER BY last_bump DESC"
        )
        threads = select_threads.fetchall()
        con.close()

        banner = get_banner(board)
        boardname = config[board]["name"]
        boardsubtitle = config[board]["subtitle"]
        randompassword = get_password()
        if imagecaptcha:
            captcha_code = "JOE BIDEN"
            captcha_data = imagecaptcha.generate(captcha_code)
            captcha = base64.b64encode(captcha_data.read()).decode()
            audio_code = "42069"
            audio_data = audiocaptcha.generate(audio_code)
            audio = base64.b64encode(BytesIO(audio_data).read())
        else:
            captcha = None
            audio = None

        form = PostForm()
        if form.validate_on_submit():
            if captcha and form.captcha.data != captcha_code:
                return redirect("/static/posterror.html")
            if form.file.data and form.post.data:
                thread_id = None
                new_post = post(form, board, thread_id)
                if new_post > 0:
                    if form.email.data == "nonoko" or form.email.data == "nonokosage":
                        return redirect(url_for("board_page", board=board))
                    else:
                        return redirect(
                            url_for("thread_page", board=board, thread=new_post)
                        )
                else:
                    return redirect("/static/posterror.html")
            else:
                # TODO: error code for trying to make a new thread without a picture
                return redirect("/static/posterror.html")

        footad = get_ad("big")
        headad = get_ad("big")
        formad = get_ad("small")

        return render_template(
            "catalog.html",
            boardlist=boardlist,
            board=board,
            boardname=boardname,
            boardsubtitle=boardsubtitle,
            form=form,
            captcha=captcha,
            audio=audio,
            threads=threads,
            banner=banner,
            password=randompassword,
            footad=footad[0],
            footadtext=footad[1],
            footadurl=footad[2],
            headad=headad[0],
            headadtext=headad[1],
            headadurl=headad[2],
            formad=formad[0],
            formadtext=formad[1],
            formadurl=formad[2]
        )


@app.route("/<board>/<thread>/", methods=["GET", "POST"])
def thread_page(board, thread):
    if board in boards:

        con = sqlite3.connect("tomochan.db")
        con.row_factory = dict_factory
        cur = con.cursor()
        select_posts = cur.execute("SELECT * FROM posts WHERE thread_id = ?", (thread,))
        posts = select_posts.fetchall()
        con.close()

        if not posts:
            return send_file("static/404.html"), 404
        else:
            banner = get_banner(board)
            boardname = config[board]["name"]
            boardsubtitle = config[board]["subtitle"]
            randompassword = get_password()
            if imagecaptcha:
                captcha_code = "JOE BIDEN"
                captcha_data = imagecaptcha.generate(captcha_code)
                captcha = base64.b64encode(captcha_data.read()).decode()
                audio_code = "42069"
                audio_data = audiocaptcha.generate(audio_code)
                audio = base64.b64encode(BytesIO(audio_data).read())
            else:
                captcha = None
                audio = None

            form = PostForm()
            if form.validate_on_submit():
                if captcha and form.captcha.data != captcha_code:
                    return redirect("/static/posterror.html")
                new_post = post(form, board, thread)
                if new_post > 0:
                    return redirect(url_for("thread_page", board=board, thread=thread))
                else:
                    return redirect("/static/posterror.html")

            footad = get_ad("big")
            headad = get_ad("big")
            formad = get_ad("small")

            return render_template(
                "thread.html",
                boardlist=boardlist,
                board=board,
                boardname=boardname,
                boardsubtitle=boardsubtitle,
                form=form,
                captcha=captcha,
                audio=audio,
                posts=posts,
                banner=banner,
                password=randompassword,
                footad=footad[0],
                footadtext=footad[1],
                footadurl=footad[2],
                headad=headad[0],
                headadtext=headad[1],
                headadurl=headad[2],
                formad=formad[0],
                formadtext=formad[1],
                formadurl=formad[2]
            )
    else:
        return send_file("static/404.html"), 404


@app.route("/uploads/<path:name>")
def show_upload(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name, as_attachment=False)


if __name__ == '__main__':
    app.run()
