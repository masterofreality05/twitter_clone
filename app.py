import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from forms import UserAddForm, LoginForm, MessageForm, UserEditForm
from models import db, connect_db, User, Message, Likes
import pdb

CURR_USER_KEY = "curr_user"
app = Flask(__name__)
# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///warbler'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)
app.app_context().push()
connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    # IMPLEMENT THIS
    if CURR_USER_KEY in session:
        do_logout()
        flash("Successfully logged out!", "success")
        return redirect("/")
    
    else:
        flash("not yet logged in")
        return redirect("/")

##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)
    print("-----------", user.likes)
   
    #----------- [<Message 650>, <Message 948>]
    liked_posts = user.likes

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    own_messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())
    
    print(own_messages)
    
    return render_template('users/show.html', user=user, messages=own_messages, likes=liked_posts)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""
    if g.user:
        user_id = session[CURR_USER_KEY]
        user = User.query.filter(User.id == user_id).first()
        form = UserEditForm(obj=user)


        if form.validate_on_submit():
            if user.authenticate(user.username, form.password.data):
                for k,v in form.data.items():
                   print("key is ", k, "value is ", v)
                   setattr(user, k, v)
                db.session.commit()    
                flash("User updated successfully","success")
                return redirect(f"/users/{user.id}")
            else:
                flash("password not entered correctly","danger")
             

            

        return render_template('users/edit.html', form=form)
    
    else:
        flash("You need to be logged in to edit your profile","danger")
        return redirect("/")

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")

##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/new.html', form=form)

@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["GET","POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get(message_id)
    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")

##############################################################################
# Homepage and error pages

@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """
    #The homepage for logged-in-users should show the last 100 warbles only
   #from the users that the logged-in user is following, and that user, 
    #rather than warbles from all users.
    if g.user:
        user = User.query.filter(User.id == g.user.id).first()
        user_likes = []
        user_messages = []
        for message in user.likes:
            user_likes.append(message.id)
            for message in user.messages:
                user_messages.append(message.id)
        messages = (Message
                    .query
                    .order_by(Message.timestamp.desc())
                    #.filter(or_(Message.user_id == user.id, Message.id in user.likes))
                    .limit(100)
                    .all())
        
        print("our likes list is", user_likes)

        return render_template('home.html', messages=messages, user=user, likes= user_likes, own_messages=user_messages)

    else:
        return render_template('home-anon.html')
    
@app.route("/users/add_like/<int:message_number>", methods=['GET','POST'])
def add_like(message_number):
    print(message_number, "3383388383")
    """get and post view to add message to user likes"""
    if g.user:
       user_id = g.user.id
       user = User.query.filter(User.id == user_id).first()
       message = Message.query.filter(Message.id == message_number).first()
       new_liked = Likes(user_id=user.id,message_id=message.id)
       db.session.add(new_liked)
       db.session.commit()
       flash("Sucessfully added to likes","success")
       return redirect("/")

@app.route("/users/remove_like/<int:message_number>", methods=['GET','POST'])
def remove_like(message_number):
    print(message_number, "3383388383")
    """get and post view to add message to user likes"""

    if g.user:
       user_id = g.user.id
       user = User.query.filter(User.id == user_id).first()
       message = Message.query.filter(Message.id == message_number).first()
       remove_like_relation = Likes.query.filter(Likes.message_id == message.id, Likes.user_id == user.id).first()
       print("removed like-------------", remove_like_relation.id)
       db.session.delete(remove_like_relation)
       db.session.commit()
       flash("Sucessfully removed from likes","danger")
       return redirect("/")





##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req

