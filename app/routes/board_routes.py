import configparser
import os
import magic
import sqlite3
import string
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from functools import lru_cache
from collections import defaultdict
import random

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
    current_app,
)
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from markupsafe import escape
from wand.image import Image
from werkzeug.utils import secure_filename
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FieldList
from wtforms.validators import Optional, DataRequired
from app.config import create_config

board_bp = Blueprint("board", __name__)


@lru_cache(maxsize=1)
def get_config():
    create_config()
    config = configparser.ConfigParser()
    config.read("tomochan.ini")
    return config


boards = get_config()["GLOBAL"]["boards"].split(" ")
boardlist = [board for board in boards if not get_config()[board].getboolean("hidden")]

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

sql = (
    "INSERT INTO posts(post_id, board_id, thread_id, op, last_bump, "
    "reply_count, sticky, time, name, email, subject, content, filename, "
    "file_actual, file_thumbnail, filesize, file_width, file_height, password, spoiler, ip) "
    "values(:post_id, :board_id, :thread_id, :op, :last_bump, "
    ":reply_count, :sticky, :time, :name, :email, :subject, :content, "
    ":filename, :file_actual, :file_thumbnail, :filesize, :file_width, :file_height, :password, :spoiler, :ip)"
)


def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


@lru_cache(maxsize=1)
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
            with Image(
                file=form.file.data.stream, format=filename.rsplit(".", 1)[1].lower()
            ) as original:
                file_width = original.width
                file_height = original.height
                with original.clone() as thumbnail:
                    thumbnail.transform(resize="250x250>")
                    file_thumbnail = str(post_id) + "_thumbnail.webp"
                    thumbnail.save(
                        filename=os.path.join(
                            "app/"+current_app.config["UPLOAD_FOLDER"], file_thumbnail
                        )
                    )

                file_actual = str(post_id) + "." + filename.rsplit(".", 1)[1].lower()
                original.save(
                    filename=os.path.join(
                        "app/"+current_app.config["UPLOAD_FOLDER"], file_actual
                    )
                )
                filesize = os.stat(
                    os.path.join("app/"+current_app.config["UPLOAD_FOLDER"], file_actual)
                ).st_size

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


@lru_cache(maxsize=1)  # Cache banner list.
def get_banner_list():
    bantree = ET.parse("app/static/banners/banners.xml")
    root = bantree.getroot()
    return [
        [x.find("image").text, x.find("board").text] for x in root.findall("banner")
    ]


def get_banner(board):
    current_mtime = os.path.getmtime("app/static/banners/banners.xml")
    if (
        not hasattr(get_banner, "_last_mtime")
        or get_banner._last_mtime != current_mtime
    ):
        get_banner_list.cache_clear()
        get_banner._last_mtime = current_mtime
    banners = get_banner_list()
    filtered_banners = [
        banner for banner in banners if ((banner[1] == board) or (banner[1] == "all"))
    ]
    if not filtered_banners:
        return
    banner = random.choice(filtered_banners)
    return "/static/banners/" + banner[0]


@lru_cache(
    maxsize=1
)  # Cache ad list. Should only refresh when the .xml file is updated.
def get_ads_list():
    adtree = ET.parse("app/static/ads/ads.xml")  # TODO: move to a better spot
    root = adtree.getroot()
    return [
        [
            x.find("image").text,
            x.find("text").text,
            x.find("url").text,
            x.find("size").text,
        ]
        for x in root.findall("ad")
    ]


def get_ad(size):
    current_mtime = os.path.getmtime("app/static/ads/ads.xml")
    if not hasattr(get_ad, "_last_mtime") or get_ad._last_mtime != current_mtime:
        get_ads_list.cache_clear()  # Invalidate cache if the file has been updated.
        get_ad._last_mtime = current_mtime  # Update mtime
    ads = get_ads_list()  # Get cached ads
    filtered_ads = (
        [ad for ad in ads if ad[3] == size] if size in ["small", "big"] else []
    )
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


def get_threads(board):
    con = sqlite3.connect("tomochan.db")
    con.row_factory = dict_factory
    cur = con.cursor()

    query = """
        SELECT
            op.*,
            replies.post_id AS replies_post_id,
            replies.content AS replies_content,
            replies.time AS replies_time,
            replies.filename AS replies_file,
            replies.file_actual AS replies_actual,
            replies.file_thumbnail AS replies_thumbnail,
            replies.filesize AS replies_filesize,
            replies.file_width AS replies_filewidth,
            replies.file_height AS replies_fileheight,
            replies.name AS replies_name,
            replies.subject AS replies_subject,
            replies.email AS replies_email,
            replies.spoiler AS replies_spoiler,
            replies.sticky AS replies_sticky,
            replies.reply_count AS replies_count
        FROM
            posts AS op
        LEFT JOIN (
            SELECT * FROM posts
            WHERE op = 0
            ORDER BY post_id DESC
        ) AS replies
        ON op.post_id = replies.thread_id
        WHERE op.op = 1 AND op.board_id = ?
        ORDER BY op.sticky DESC, op.last_bump DESC
    """
    results = cur.execute(query, (board,)).fetchall()

    # Group replies by thread ID and limit to the latest 5 replies
    thread_map = defaultdict(lambda: {"thread": None, "replies": []})

    for row in results:
        thread_id = row["post_id"]
        if thread_map[thread_id]["thread"] is None:
            thread_map[thread_id]["thread"] = {j: k for j, k in row.items() if "replies_" not in j }
        if row["replies_post_id"]:
            thread_map[thread_id]["replies"].append({
                "post_id": row["replies_post_id"],
                "content": row["replies_content"],
                "time": row["replies_time"],
                "reply_count": 0,
                "filename": row["replies_file"],
                "file_actual": row["replies_actual"],
                "file_thumbnail": row["replies_thumbnail"],
                "filesize": row["replies_filesize"],
                "file_width": row["replies_filewidth"],
                "file_height": row["replies_fileheight"],
                "name": row["replies_name"],
                "subject": row["replies_subject"],
                "email": row["replies_email"],
                "spoiler": row["replies_spoiler"],
                "sticky": row["replies_sticky"],
                "reply_count": row["replies_count"],

            })

    threadlist = [
        [data["thread"]] + data["replies"][-5:] for data in thread_map.values()
    ]

    con.close()
    return threadlist


class PostForm(FlaskForm):
    name = StringField("Name", validators=[Optional()])
    email = StringField("Email", validators=[Optional()])
    subject = StringField("Subject", validators=[Optional()])
    post = TextAreaField("Content", validators=[DataRequired()])
    # TODO: FILE SIZE LIMIT, THE VALIDATOR DOESNT WORK FOR SOME REASON
    file = FileField(
        "File", validators=[FileAllowed(ALLOWED_EXTENSIONS, "the fuck is this shit?")]
    )
    spoiler = BooleanField("Spoiler?", validators=[Optional()])
    password = StringField("Password", validators=[Optional()])
    submit = SubmitField("Post")


# doesnt work because wtforms apparently doesnt support booleans in fieldlists lol
# gonna need to figure out a different way to get checkboxes on each post
"""
class DeleteForm(FlaskForm):
    checkboxes = FieldList(BooleanField("Delete", validators=[DataRequired()]), min_entries=0)
    fileonly = BooleanField("File Only", validators=[DataRequired()])
    password = StringField("Password", validators=[Optional()])
    delete = SubmitField("Delete")
    report = SubmitField("Report")
"""


@board_bp.route("/<board>/", methods=["GET", "POST"])
def board_page(board):
    if board in boards:

        threadlist = get_threads(board)

        banner = get_banner(board)
        boardname = get_config()[board]["name"]
        boardsubtitle = get_config()[board]["subtitle"]
        randompassword = get_password()

        # TODO FIGURE OUT HOW TO MAKE THIS SHIT ACTUALLY WORK
        # the issue rn is that i cant have the indexes line up with the post ids
        """
        postlist = []
        for thread in threadlist:
            for post in thread:
                postlist.append(post)
        deleteform = DeleteForm(checkboxes=postlist)
        if deleteform.validate_on_submit():
            pass
        """
        form = PostForm()
        if form.validate_on_submit():
            if form.file.data and form.post.data:
                thread_id = None
                new_post = post(form, board, thread_id)
                if new_post > 0:
                    if form.email.data == "nonoko" or form.email.data == "nonokosage":
                        return redirect(url_for("board.board_page", board=board))
                    else:
                        return redirect(
                            url_for("board.thread_page", board=board, thread=new_post)
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
            # deleteform=deleteform,
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
            formadurl=formad[2],
        )
    else:
        return send_file("static/404.html"), 404


@board_bp.route("/<board>/catalog", methods=["GET", "POST"])
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
        boardname = get_config()[board]["name"]
        boardsubtitle = get_config()[board]["subtitle"]
        randompassword = get_password()

        form = PostForm()
        if form.validate_on_submit():
            if form.file.data and form.post.data:
                thread_id = None
                new_post = post(form, board, thread_id)
                if new_post > 0:
                    if form.email.data == "nonoko" or form.email.data == "nonokosage":
                        return redirect(url_for("board.board_page", board=board))
                    else:
                        return redirect(
                            url_for("board.thread_page", board=board, thread=new_post)
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
            formadurl=formad[2],
        )


@board_bp.route("/<board>/<thread>/", methods=["GET", "POST"])
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
            boardname = get_config()[board]["name"]
            boardsubtitle = get_config()[board]["subtitle"]
            randompassword = get_password()

            form = PostForm()
            if form.validate_on_submit():
                new_post = post(form, board, thread)
                if new_post > 0:
                    return redirect(
                        url_for("board.thread_page", board=board, thread=thread)
                    )
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
                formadurl=formad[2],
            )
    else:
        return send_file("static/404.html"), 404
