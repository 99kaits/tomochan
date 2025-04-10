from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional
from time import strftime
import pickle

app = Flask(__name__)
app.config['SECRET_KEY'] = '7f4bc5403ecbc99f2b10dc1c582be3f9632369dea8d6e45d'

def load_posts():
    try:
        postfile = open('posts', 'rb')
        posts = pickle.load(postfile)
    except:
        posts = []
    return posts

def post(posts, new_post):
    posts.append(new_post)
    postfile = open('posts', 'wb')
    pickle.dump(posts, postfile)


class PostForm(FlaskForm):
    name = StringField('name', validators=[Optional()])
    subject = StringField('subject', validators=[Optional()])
    post = TextAreaField('post', validators=[DataRequired()])
    submit = SubmitField('post')

@app.route("/<board>/", methods=['GET', 'POST'])
def board_page(board):
    posts = load_posts()
    form = PostForm()
    if form.name.data:
        name = form.name.data
    else:
        name = "tomo"
    if form.validate_on_submit():
        postcontent = form.post.data.split('\n')
        #postcontent = form.post.data.replace('\n', '<br>')
        new_post = { 'name' : name, 'subject' : form.subject.data, 'content' : postcontent, 'timestamp' : strftime("%Y-%m-%d %H:%M:%S")}
        post(posts, new_post)

    return render_template('board.html', board=board, form=form, posts=posts)