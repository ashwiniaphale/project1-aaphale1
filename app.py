# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=trailing-whitespace
# pylint: disable=trailing-newlines
# pylint: disable=missing-module-docstring
# pylint: disable=global-variable-undefined
import os
import random
import flask
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from api import get_title, get_tagline, get_genre, get_image, get_wiki_page

app = flask.Flask(__name__) 
app.config["SECRET_KEY"] = os.getenv("app.secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "default"

class UserTable(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(120), nullable=False)
    
    def __repr__(self):
        return f"<User {self.title}"
    
    def get_username(self):
        return self.username
    
    
class CommentsTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviews=db.Column(db.String(300))
    rating=db.Column(db.String(5))
    movie_id=db.Column(db.Integer)
    current_username=db.Column(db.String(120), nullable=False)
    
    def __repr__(self):
        return f"<Comments {self.title}"
    
db.create_all()   

@login_manager.user_loader
def load_user(user_id):
    return UserTable.query.get(int(user_id))

@app.route("/", methods=["GET"])  
def default():
    return flask.redirect(flask.url_for("login"))

#start with default on login page
@app.route("/register", methods=["GET", "POST"])  
def register():
    if flask.request.method == "POST":
        user_form_data = flask.request.form.get("user_form")
        if(db.session.query(UserTable.id).filter_by(username=user_form_data).first() is not None): #if returns a user, then the username is already taken
            flask.flash("That username is already taken. Please try another one.")
        else:
            db.session.add(UserTable(username=user_form_data))
            db.session.commit()
            return flask.redirect(flask.url_for("get_movie"))
        
    return flask.render_template("register.html")

@app.route("/login", methods=["GET", "POST"])  
def login():
    if flask.request.method == "POST":
        user_form_data = flask.request.form.get("user_form")
        if(UserTable.query.filter_by(username=user_form_data).first() is not None): #if the username is in the DB
            login_user(UserTable.query.filter_by(username=user_form_data).first())
            return flask.redirect(flask.url_for("get_movie")) # go to movie page
        else:
            return flask.redirect(flask.url_for("register")) #otherwise go to register
    else:
        return flask.render_template("login.html")
    
        

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return flask.redirect("/login")

@app.route("/index", methods=["GET"])
@login_required
def get_movie():
    '''calls functions from api and renders the output to flask'''
    favorite_movies = [313369, 122906, 27205, 673, 38757, 2062] #lalaland, about time, inception, HP, tangled, ratatouille
    random_movie_id = random.choice(favorite_movies) #chooses random movie_id from the list
    all_comments=CommentsTable.query.filter_by(movie_id=random_movie_id).all()
    num_comments = len(all_comments)
    return flask.render_template(
        "index.html", 
        movie_title=get_title(random_movie_id),
        movie_tagline=get_tagline(random_movie_id),
        movie_genre=get_genre(random_movie_id),
        movie_image=get_image(random_movie_id),
        movie_wiki=get_wiki_page(random_movie_id), 
        all_comments=all_comments,
        num_comments=num_comments, 
        random_movie_id=random_movie_id
    )
@app.route("/review", methods=["GET", "POST"])
def comments():
    if flask.request.method == "POST":
        movie_reviews = flask.request.form.get("review") #column name = data[form name]
        movie_ratings = flask.request.form.get("rating")
        movie_id = flask.request.form.get("movieID")
        now_user = current_user.username
        db.session.add(CommentsTable(reviews=movie_reviews, rating=movie_ratings, movie_id=movie_id, current_username=now_user))
        db.session.commit()
    return flask.redirect(flask.url_for("get_movie"))
       
app.run(
    debug=True
)
