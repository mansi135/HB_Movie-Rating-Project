"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie
# import model

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Gives a list of all users"""

   # users = db.session.query(User).all()
    users = User.query.all()
    return render_template("user_list.html",users=users)

# @app.route('/users/<user_id>')

@app.route('/register')
def display_registration_form():
    """Displays registration form"""

    return render_template("register_form.html")


@app.route('/register', methods=["POST"])
def handle_registration_form():
    """Registration form post handler"""

    email = request.form.get('email')
    password = request.form.get('password')

    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        # flash message
        print "user already exists"
    else:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        # flash message
        print "successfully added"

    return redirect('/')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
