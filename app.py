import math

from flask import Flask, render_template, flash
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

"""
con = sqlite3.connect("tomochan.db")
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS posts("
                "post_id INTEGER PRIMARY KEY UNIQUE NOT NULL, "
                "board_id INTEGER NOT NULL, "
                "thread_id INTEGER NOT NULL, "
                "time INTEGER NOT NULL, "
                "name TEXT NOT NULL, "
                "email TEXT, "
                "subject TEXT, "
                "content TEXT NOT NULL, "
                "filename TEXT, "
                "spoiler INTEGER NOT NULL)")
"""

def post(new_post):
    con = sqlite3.connect("tomochan.db")
    cur = con.cursor()
    largest_post_id = cur.execute("SELECT max(post_id)")
    if not largest_post_id:
        post_id = 1
    else:
        post_id = largest_post_id.fetchone()[0]

    
    cur.execute("INSERT INTO post ")

def get_banner(board):
    banner = random.choice(os.listdir("static/banners"))
    return "/static/banners/" + banner

def get_swatch(time):
    bst = time + timedelta(hours=1)
    beat = math.floor(
        bst.hour * 41.666 +
        bst.minute * 0.6944 +
        bst.second * 0.011574
    ) % 1000
    return beat


class PostForm(FlaskForm):
    name = StringField('Name', validators=[Optional()])
    email = StringField('Email', validators=[Optional()])
    subject = StringField('Subject', validators=[Optional()])
    post = TextAreaField('Content', validators=[DataRequired()])
    file = FileField('File', validators=[Optional()])
    spoiler = BooleanField('Spoiler?', validators=[Optional()])
    submit = SubmitField('post')

@app.route("/<board>/", methods=['GET', 'POST'])
def board_page(board):
    if board in boards:
        con = sqlite3.connect("tomochan.db")
        cur = con.cursor()
        threads = cur.execute("SELECT thread_id, min(post_id) FROM posts")
        threadlist = threads.fetchmany(size=15)

        banner = get_banner(board)

        form = PostForm()

        """
        if form.validate_on_submit():
            postcontent = form.post.data.split('\n')
            #postcontent = form.post.data.replace('\n', '<br>')
            post_time = datetime.now(timezone.utc)
            timestamp = post_time.strftime("%Y-%m-%d %H:%M:%S")
            swatch = get_swatch(post_time)
            id = len(posts) + 1
            new_post = { 'name' : name, 'subject' : form.subject.data, 'content' : postcontent, 'time' : post_time, 'timestamp' : timestamp, 'swatch' : swatch, 'id' : id }
            post(board, posts, new_post)
        """
        if form.validate_on_submit():
            if form.name.data:
                name = form.name.data
            else:
                name = "Anonymous"
            email = form.email.data
            subject = form.subject.data
            content = form.post.data.split('\n')
            spoiler = form.spoiler.data
            timestamp = datetime.now(timezone.utc).timestamp()
            new_post = {'name' : name, 'email' : email, 'subject' : subject, 'content' : content, 'spoiler' : spoiler, 'timestamp' : timestamp}
            post(board, new_post)
        return render_template('board.html', board=board, form=form, threads=threadlist, banner=banner)
    else:
        return "not a real board lol", 404

"""
@app.route("/<board>/<thread>/", methods=['GET', 'POST'])
def thread_page(board, thread):
    if board in boards:
        thread = load_thread(board, thread)
        if thread in
"""