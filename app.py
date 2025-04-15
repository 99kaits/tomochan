import math

from flask import Flask, render_template, send_file, redirect, url_for, send_from_directory, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Optional
from datetime import datetime, timezone, timedelta
from markupsafe import escape
import configparser
import sqlite3
import random
import string
import magic
import os

config = configparser.ConfigParser()
if not os.path.exists('tomochan.ini'):
    new_key = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=72))
    new_pass = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=32))
    print("new admin password is " + new_pass)
    boards = ["b", "tomo", "nottomo"]
    config['GLOBAL'] = {'secret_key' : new_key,
                        'upload_folder' : 'uploads',
                        'admin_pass' : new_pass,
                        'boards' : ' '.join(boards)}
    for board in boards:
        config[board] = {'name' : "Placeholder",
                        'subtitle' : "wow you should change me in the ini",
                        'bump_limit' : 50,
                        'size' : 50,
                        'hidden' : False,
                        'r9k' : False}
    with open('tomochan.ini', 'w') as configfile:
        config.write(configfile)
else:
    config.read('tomochan.ini')

app = Flask(__name__)
app.config['SECRET_KEY'] = config['GLOBAL']['secret_key']
app.config['UPLOAD_FOLDER'] = config['GLOBAL']['upload_folder']

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'avif', 'webp', 'heic', 'heif', 'jxl'}
boards = config['GLOBAL']['boards'].split(' ')
boardlist = []
for board in boards:
    if not config[board].getboolean('hidden'):
        boardlist.append(board)

sql = ("INSERT INTO posts(post_id, board_id, thread_id, op, last_bump, sticky, time, name, email, subject, content, filename, file_actual, password, spoiler, ip) "
       "values(:post_id, :board_id, :thread_id, :op, :last_bump, :sticky, :time, :name, :email, :subject, :content, :filename, :file_actual, :password, :spoiler, :ip)")

"""
import sqlite3
con = sqlite3.connect("tomochan.db")
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS posts("
                "post_id INTEGER PRIMARY KEY UNIQUE NOT NULL, "
                "board_id TEXT NOT NULL, "
                "thread_id INTEGER NOT NULL, "
                "op INTEGER NOT NULL, "
                "last_bump INTEGER, "
                "sticky INTEGER, "
                "time INTEGER NOT NULL, "
                "name TEXT NOT NULL, "
                "email TEXT, "
                "subject TEXT, "
                "content TEXT NOT NULL, "
                "filename TEXT, "
                "file_actual TEXT, "
                "spoiler INTEGER NOT NULL, "
                "ip TEXT NOT NULL)")

con.close()

"""

def allowed_mime_type(file):
    mime = magic.from_buffer(file.stream.read(2048), mime=True)
    file.stream.seek(0)  # Reset file pointer after reading
    return mime in ['image/png', 'image/jpeg', 'image/gif', 'image/avif', 'image/webp', 'image/heic', 'image/heif', 'image/jxl']

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def post(form, board, thread_id):
    con = sqlite3.connect("tomochan.db")
    cur = con.cursor()
    largest_post_id = cur.execute('SELECT max(post_id) from posts').fetchone()[0]

    if form.name.data:
        name = form.name.data
    else:
        name = "Anonymous"

    timestamp = datetime.now(timezone.utc).timestamp()

    if not largest_post_id:
        post_id = 1
    else:
        post_id = largest_post_id + 1

    if not thread_id:
        thread_id = post_id
        last_bump = timestamp
        op = 1
    else:
        last_bump = None
        op = 0
        
    if op == 0:
        if not form.email.data == 'sage' or form.email.data == 'nonokosage':
            cur.execute('UPDATE posts SET last_bump = ? WHERE post_id = ?', (timestamp, thread_id))

    if form.file.data and allowed_mime_type(form.file.data):
        filename = secure_filename(form.file.data.filename)
        file_actual = str(post_id) + '.' + filename.rsplit('.', 1)[1].lower()
        form.file.data.save(os.path.join(app.config['UPLOAD_FOLDER'], file_actual))
    else:
        filename = None
        file_actual = None

    if 'X-Forwarded-For' in request.headers:
        ip = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        ip = request.remote_addr

    content = escape(form.post.data)

    new_post = {'post_id' : post_id,
                'board_id' : board,
                'thread_id' : thread_id,
                'op' : op,
                'last_bump' : last_bump,
                'sticky' : 0,
                'time' : timestamp,
                'name' : name,
                'email' : form.email.data,
                'subject' : form.subject.data,
                'content' : content,
                'filename' : filename,
                'file_actual' : file_actual,
                'password' : form.password.data,
                'spoiler' : form.spoiler.data,
                'ip' : ip}
    cur.execute(sql, new_post)
    con.commit()
    con.close()
    return post_id

def get_banner(board):
    # TODO: board specific banners
    banner = random.choice(os.listdir("static/banners"))
    return "/static/banners/" + banner

def content_parser(content):
    # TODO: MAKE SURE THE TAGS CLOSE
    # TODO: replace \n with <br>
    # TODO: replace > with span with class quote
    if "&gt;" in content:
        pass

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


def get_threads(board):
    con = sqlite3.connect("tomochan.db")
    con.row_factory = dict_factory
    cur = con.cursor()

    oplist = []
    threadsquery = cur.execute("SELECT * FROM posts WHERE op = 1 AND board_id = ? ORDER BY sticky DESC, last_bump DESC", (board,))
    oplist = oplist + threadsquery.fetchall()

    threadlist = []
    for op in oplist:
        numberpostsquery = cur.execute("SELECT COUNT(*) FROM posts WHERE thread_id = ? AND op = 0", (op['post_id'],))
        numposts = numberpostsquery.fetchone()['COUNT(*)']
        last5 = cur.execute("SELECT * FROM posts WHERE thread_id = ? AND op = 0 ORDER BY post_id DESC LIMIT 5", (op['post_id'],))
        thread = list(reversed(last5.fetchall()))
        if numposts > 5:
            op['numposts'] = numposts - 5
        thread.insert(0, op)
        threadlist.append(thread)
    
    con.close()
    return threadlist

app.jinja_env.globals.update(get_swatch=get_swatch, get_strftime=get_strftime)

class PostForm(FlaskForm):
    name = StringField('Name', validators=[Optional()])
    email = StringField('Email', validators=[Optional()])
    subject = StringField('Subject', validators=[Optional()])
    post = TextAreaField('Content', validators=[DataRequired()])
    # TODO: FILE SIZE LIMIT, THE VALIDATOR DOESNT WORK FOR SOME REASON
    file = FileField('File', validators=[FileAllowed(ALLOWED_EXTENSIONS, "the fuck is this shit?")])
    spoiler = BooleanField('Spoiler?', validators=[Optional()])
    password = StringField('Password', validators=[Optional()])
    submit = SubmitField('Post')

@app.route("/<board>/", methods=['GET', 'POST'])
def board_page(board):
    if board in boards:
        
        threadlist = get_threads(board)
        banner = get_banner(board)
        boardname = config[board]['name']
        boardsubtitle = config[board]['subtitle']
        randompassword = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        form = PostForm()
        if form.validate_on_submit():
            print("submitted")
            if form.file.data and form.post.data:
                print("file and post checked out")
                thread_id = None
                new_post = post(form, board, thread_id)
                if form.email.data == "nonoko" or form.email.data == "nonokosage":
                    return redirect(url_for('board_page', board=board))
                else:
                    return redirect(url_for('thread_page', board=board, thread=new_post))
            else:
                # TODO: error code for trying to make a new thread without a picture
                return redirect('/static/posterror.html')
        return render_template('board.html', boardlist=boardlist, board=board, boardname=boardname, boardsubtitle=boardsubtitle, 
                                form=form, threads=threadlist, banner=banner, password=randompassword)
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
            boardname = config[board]['name']
            boardsubtitle = config[board]['subtitle']
            randompassword = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=12))

            form = PostForm()
            if form.validate_on_submit():
                new_post = post(form, board, thread)
                response = redirect(url_for('thread_page', board=board, thread=thread))
                if form.name.data:
                    response.set_cookie('Name', form.name.data)
                return response

            return render_template('thread.html', boardlist=boardlist, board=board, boardname=boardname, boardsubtitle=boardsubtitle, 
                                    form=form, posts=posts, banner=banner, password=randompassword)
    else:
        return send_file('static/404.html'), 404


@app.route("/uploads/<path:name>")
def show_upload(name):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        name,
        as_attachment=False
    )