from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, NumberRange
import requests
from flask_sqlalchemy import SQLAlchemy

API_KEY = "25a661dad53fcca6dc07eb9b2238c42d"
API_URL = "https://api.themoviedb.org/3/search/movie"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
# #CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Movies-list.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# #CREATE TABLE


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500))
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(500), nullable=True)
    img_url = db.Column(db.String(500), nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Movie {self.title}>'


db.create_all()


class RatingForm(FlaskForm):
    rating = IntegerField('Your Rating out of 10', validators=[NumberRange(min=0, max=10)])
    review = StringField(label='Your Review', validators=[DataRequired()])
    submit = SubmitField(label="Done")


class AddMovie(FlaskForm):
    movie_name = StringField(label='Add a new Movie', validators=[DataRequired()])
    add = SubmitField(label="Add")


# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()

@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
        db.session.commit()
    return render_template("index.html",  movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    ratingform = RatingForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if request.method == "POST":
        # update Db

        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = request.form["rating"]
        movie_to_update.review = request.form["review"]
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=ratingform, movie=movie)


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    new_movie_add = AddMovie()
    if request.method == "POST":
        movie_search_title = request.form["movie_name"]
        print(movie_search_title)
        response = requests.get(url=API_URL, params={"api_key": API_KEY, "query": movie_search_title})
        movie_list = response.json()["results"]  # list of movies with that titles
        return render_template('select.html', list=movie_list)

        # render select page regarding search
        # choice from select page
        # call the api get data
        # update the data base
        # render the new page
    return render_template("add.html", form=new_movie_add)


@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/find")
def get_details():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"https://api.themoviedb.org/3/movie/{movie_api_id}"
        response = requests.get(movie_api_url, params={"api_key": API_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["original_title"],
            year=data["release_date"].split("-")[0],
            img_url=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}",
            description=data["overview"]
        )

        db.session.add(new_movie)
        db.session.commit()
        movie_id = request.args.get("id")
        movie_to_update = Movie.query.get(movie_id)
        return redirect(url_for("edit", id=new_movie.id))


if __name__ == "__main__":
    app.run(debug=True)