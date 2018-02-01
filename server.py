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

    return render_template("user_list.html", users=users)


@app.route('/users/<user_id>')
def individual_user(user_id):

    user = User.query.filter_by(user_id=user_id).one()


    # Method-1
    # all_ratings_objects = Rating.query.filter_by(user_id=user_id).all()

    # movies_they_rated = []

    # for rating_obj in all_ratings_objects:
    #     movie_title = rating_obj.movie.title
    #     movie_score = rating_obj.score
    #     movies_they_rated.append((movie_title, movie_score))
    #

    #Method-2
    # all_ratings_objects = Rating.query.filter_by(user_id=user_id).all()
    # movies_they_rated = []

    # for rating_obj in all_ratings_objects:
    #     movie_title = db.session.query(Movie.title).filter_by(movie_id=rating_obj.movie_id).one()
    #     movie_score = rating_obj.score
    #     movies_they_rated.append((movie_title, movie_score))


    # Method-3
    # all_ratings_objects = db.session.query(Movie.title, Rating.score).join(Rating).filter(Rating.user_id==user_id).all()
    # movies_they_rated = all_ratings_objects

    # return render_template("user_details.html",age=user.age,zipcode=user.zipcode,movies_they_rated=movies_they_rated)

    return render_template("user_details.html", user=user)


@app.route('/movies')
def display_movies():
    """Displays list of movie titles"""

    # query
    movies = Movie.query.order_by('title').all()
    #movies = db.session.query
    return render_template("movie_list.html", movies=movies)


@app.route('/movies/<movie_id>')
def display_movie_detail(movie_id):
    """Display individual movie's details"""

    movie = Movie.query.filter_by(movie_id=movie_id).one()
    #ratings = Rating.query.filter_by(movie_id=movie_id).all()

    # return render_template("movie_details.html", movie=movie, ratings=ratings)
    # , ordered_movies=movie.ratings. # sort by ratings
    return render_template("movie_details.html", movie=movie)


@app.route('/rate_movie', methods=["POST"])
def rate_movie():
    """Lets logged in user rate/update rating for the movie"""

    user_id = session['user_id']
    movie_id = request.form.get('movie_id')

    user_rating = request.form.get("ratings")

    # check if user has rated that movie
    user_rated_movie = Rating.query.filter_by(movie_id=movie_id, user_id=user_id).first()

    if user_rated_movie:
        user_rated_movie.score = user_rating #Update
        flash("You have successfully updated your rating")
    else:
        new_entry = Rating(movie_id=movie_id, user_id=user_id, score=user_rating)
        db.session.add(new_entry)           # Add new entry
        flash("You have successfully added your rating")
    db.session.commit()

    return redirect("/movies/{}".format(movie_id))
    #return redirect("/movies/{movie_id}".format(movie_id=movie_id))


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
        flash('User already exists. Please register with another email address.')
        print "user already exists"

        return redirect('/register')

    else:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('User was successfully added to the database.')
        print "successfully added"

        return redirect('/')


@app.route('/login')
def show_login_form():
    """Show login form"""

    return render_template("login-form.html")


@app.route('/login', methods=['POST'])
def login_check():
    """Login check"""


    email = request.form.get('email')
    password = request.form.get('password')

    existing_user = User.query.filter_by(email=email).first()


    if not existing_user:
        flash('Please register first.')
        return redirect('/register')
    elif existing_user.email == email and existing_user.password != password:
        flash('The password is incorrect. Please check the spelling.')
        return redirect('/login')
    elif existing_user.email == email and existing_user.password == password:
        flash('You are logged in.')
        # probably bug here
        session['user_id'] = existing_user.user_id
        print session['user_id']
        return redirect("/")


@app.route('/logout')
def logout():
    """Logout User"""

    #del session['user_id']
    session.clear()
    flash("You were logged out.")

    return redirect("/")


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
