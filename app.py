import math

from flask import Flask, render_template, send_file, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, FileField
from wtforms.validators import DataRequired, Optional
from datetime import datetime, timezone, timedelta
import sqlite3
import random
import magic
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '7f4bc5403ecbc99f2b10dc1c582be3f9632369dea8d6e45d'
app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'avif', 'webp', 'heic', 'heif' 'jxl'}
boards = ['b', 'tomo', 'nottomo']
sql = ("INSERT INTO posts(post_id, board_id, thread_id, op, last_bump, time, name, email, subject, content, filename, file_actual, spoiler) "
       "values(:post_id, :board_id, :thread_id, :op, :last_bump, :time, :name, :email, :subject, :content, :filename, :file_actual, :spoiler)")


con = sqlite3.connect("tomochan.db")
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS posts("
                "post_id INTEGER PRIMARY KEY UNIQUE NOT NULL, "
                "board_id TEXT NOT NULL, "
                "thread_id INTEGER NOT NULL, "
                "op INTEGER NOT NULL, "
                "last_bump INTEGER, "
                "time INTEGER NOT NULL, "
                "name TEXT NOT NULL, "
                "email TEXT, "
                "subject TEXT, "
                "content TEXT NOT NULL, "
                "filename TEXT, "
                "file_actual TEXT, "
                "spoiler INTEGER NOT NULL)")

con.close()

"""
insert into posts (post_id, board_id, thread_id, op, last_bump, time, name, email, subject, content, filename, spoiler) values(1, 'b', 1, 1, 1744376519, 1744374813, 'Anonymous', NULL, 'wow', 'i am inserting this with sqlite cmd', NULL, 0);
insert into posts (post_id, board_id, thread_id, op, last_bump, time, name, email, subject, content, filename, spoiler) values(2, 'b', 2, 1, 1744375966, 1744375966, 'Anonymous', NULL, 'wow again', 'second test post', NULL, 0);
insert into posts (post_id, board_id, thread_id, op, last_bump, time, name, email, subject, content, filename, spoiler) values(3, 'b', 1, 0, NULL, 1744376519, 'tomo', NULL, NULL, 'i too am in this thread', NULL, 0);

"""

def allowed_mime_type(file):
    mime = magic.from_buffer(file.stream.read(2048), mime=True)
    file.stream.seek(0)  # Reset file pointer after reading
    return mime in ['image/png', 'image/jpeg', 'application/pdf']

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def post(new_post):
    # TODO: ACTUAL FILE CODE
    new_post['file_actual'] = None
    con = sqlite3.connect("tomochan.db")
    cur = con.cursor()
    largest_post_id = cur.execute('SELECT max(post_id) from posts').fetchone()[0]
    if not largest_post_id:
        new_post['post_id'] = 1
    else:
        new_post['post_id'] = largest_post_id + 1
    if new_post['thread_id'] == 'new':
        new_post['thread_id'] = new_post['post_id']
    if (new_post['email'] == 'sage' or new_post['email'] == 'nonokosage') and new_post['op'] == 0:
        new_post['last_bump'] = None
        cur.execute(sql, new_post)
    else:
        cur.execute(sql, new_post)
    con.commit()
    con.close()
    return new_post

def get_banner(board):
    banner = random.choice(os.listdir("static/banners"))
    return "/static/banners/" + banner

def get_swatch(timestamp):
    time = datetime.fromtimestamp(timestamp)
    bmt = time + timedelta(hours=1)
    beat = math.floor(
        bmt.hour * 41.666 +
        bmt.minute * 0.6944 +
        bmt.second * 0.011574
    ) % 1000
    return beat

def get_strftime(timestamp):
    time = datetime.fromtimestamp(timestamp)
    return time.strftime("%Y-%m-%d(%a) %H:%M:%S")


app.jinja_env.globals.update(get_swatch=get_swatch, get_strftime=get_strftime)

class PostForm(FlaskForm):
    name = StringField('Name', validators=[Optional()])
    email = StringField('Email', validators=[Optional()])
    subject = StringField('Subject', validators=[Optional()])
    post = TextAreaField('Content', validators=[DataRequired()])
    file = FileField('File', validators=[Optional()])
    spoiler = BooleanField('Spoiler?', validators=[Optional()])
    submit = SubmitField('Post')

@app.route("/<board>/", methods=['GET', 'POST'])
def board_page(board):
    if board in boards:
        con = sqlite3.connect("tomochan.db")
        con.row_factory = dict_factory
        cur = con.cursor()
        threads = cur.execute("SELECT * FROM posts WHERE op = 1 AND board_id = ? ORDER BY last_bump DESC", (board,))
        threadlist = threads.fetchall()
        con.close()
        print(threadlist)

        banner = get_banner(board)

        form = PostForm()
        if form.validate_on_submit():
            if form.name.data:
                name = form.name.data
            else:
                name = "Anonymous"
            timestamp = last_bump = datetime.now(timezone.utc).timestamp()
            new_post = {'thread_id' : 'new',
                        'board_id' : board,
                        'op' : 1,
                        'last_bump' : last_bump,
                        'name' : name,
                        'email' : form.email.data,
                        'subject' : form.subject.data,
                        'content' : form.post.data,
                        'spoiler' : form.spoiler.data,
                        'time' : timestamp,
                        'filename' : None}
            posted = post(new_post)
            if form.email.data == "nonoko" or form.email.data == "nonokosage":
                return redirect(url_for('board_page', board=board))
            else:
                return redirect(url_for('thread_page', board=posted['board_id'], thread=posted['thread_id']))
        return render_template('board.html', board=board, form=form, threads=threadlist, banner=banner)
    else:
        return send_file('static/404.html'), 404


@app.route("/<board>/<thread>/", methods=['GET', 'POST'])
def thread_page(board, thread):
    if board in boards:
        con = sqlite3.connect("tomochan.db")
        con.row_factory = dict_factory
        cur = con.cursor()
        select_posts = cur.execute("SELECT * FROM posts WHERE thread_id = ?", (thread,))
        posts = select_posts.fetchall()
        con.close()
        if not posts:
            return send_file('static/404.html'), 404
        else:
            banner = get_banner(board)

            form = PostForm()
            if form.validate_on_submit():
                if form.name.data:
                    name = form.name.data
                else:
                    name = "Anonymous"
                timestamp = datetime.now(timezone.utc).timestamp()
                new_post = {'thread_id': thread,
                            'board_id': board,
                            'op': 0,
                            'last_bump': None,
                            'name': name,
                            'email': form.email.data,
                            'subject': form.subject.data,
                            'content': form.post.data,
                            'spoiler': form.spoiler.data,
                            'time': timestamp,
                            'filename': None}
                posted = post(new_post)
                return redirect(url_for('thread_page', board=board, thread=thread))

            return render_template('thread.html', board=board, form=form, posts=posts, banner=banner)
    else:
        return send_file('static/404.html'), 404
