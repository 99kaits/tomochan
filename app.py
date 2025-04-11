import math

from flask import Flask, render_template, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, FileField
from wtforms.validators import DataRequired, Optional
from datetime import datetime, timezone, timedelta
import sqlite3
import random
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '7f4bc5403ecbc99f2b10dc1c582be3f9632369dea8d6e45d'

boards = ['b', 'tomo', 'nottomo']
sql = "INSERT INTO posts(post_id, board_id, thread_id, op, last_bump, time, name, email, subject, content, filename, spoiler) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

"""
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
                "spoiler INTEGER NOT NULL)")
                

insert into posts (post_id, board_id, thread_id, op, last_bump, time, name, email, subject, content, filename, spoiler) values(1, 'b', 1, 1, 1744376519, 1744374813, 'Anonymous', NULL, 'wow', 'i am inserting this with sqlite cmd', NULL, 0);
insert into posts (post_id, board_id, thread_id, op, last_bump, time, name, email, subject, content, filename, spoiler) values(2, 'b', 2, 1, 1744375966, 1744375966, 'Anonymous', NULL, 'wow again', 'second test post', NULL, 0);
insert into posts (post_id, board_id, thread_id, op, last_bump, time, name, email, subject, content, filename, spoiler) values(3, 'b', 1, 0, NULL, 1744376519, 'tomo', NULL, NULL, 'i too am in this thread', NULL, 0);

"""

def post(new_post):
    con = sqlite3.connect("tomochan.db")
    cur = con.cursor()
    largest_post_id = cur.execute('SELECT max(post_id) from posts').fetchone()[0]
    if not largest_post_id:
        post_id = 1
    else:
        post_id = largest_post_id + 1
    if new_post['thread_id'] == 'new':
        largest_thread_id = cur.execute('SELECT max(thread_id) from posts').fetchone()[0]
        if not largest_thread_id:
            thread_id = 1
        else:
            thread_id = largest_thread_id + 1
    else:
        thread_id = new_post['thread_id']
    if new_post['email'] == 'sage':
        cur.execute(sql,
                    (post_id,
                     new_post['board_id'],
                     thread_id,
                     new_post['op'],
                     None,
                     new_post['time'],
                     new_post['name'],
                     new_post['email'],
                     new_post['subject'],
                     new_post['content'],
                     new_post['filename'],
                     new_post['spoiler']))
    else:
        cur.execute(sql,
                    (post_id,
                     new_post['board_id'],
                     thread_id,
                     new_post['op'],
                     new_post['last_bump'],
                     new_post['time'],
                     new_post['name'],
                     new_post['email'],
                     new_post['subject'],
                     new_post['content'],
                     new_post['filename'],
                     new_post['spoiler']))
    con.commit()

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
        cur = con.cursor()
        threads = cur.execute("SELECT * FROM posts WHERE op = 1 AND board_id = '" + board + "' ORDER BY last_bump DESC")
        threadlist = threads.fetchmany(size=15)
        print(threadlist)

        banner = get_banner(board)

        form = PostForm()
        if form.validate_on_submit():
            if form.name.data:
                name = form.name.data
            else:
                name = "Anonymous"
            email = form.email.data
            subject = form.subject.data
            spoiler = form.spoiler.data
            timestamp = last_bump = datetime.now(timezone.utc).timestamp()
            new_post = {'thread_id' : 'new',
                        'board_id' : board,
                        'op' : 1,
                        'last_bump' : last_bump,
                        'name' : name,
                        'email' : email,
                        'subject' : subject,
                        'content' : form.post.data,
                        'spoiler' : spoiler,
                        'time' : timestamp,
                        'filename' : None}
            post(new_post)
        return render_template('board.html', board=board, form=form, threads=threadlist, banner=banner)
    else:
        return send_file('static/404.html'), 404

"""
@app.route("/<board>/<thread>/", methods=['GET', 'POST'])
def thread_page(board, thread):
    if board in boards:
        thread = load_thread(board, thread)
        if thread in
"""