from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_heroku import Heroku
import cloudinary as Cloud
import os

app = Flask(__name__)
heroku = Heroku(app)
CORS(app)

Cloud.config.update = ({
    'cloud_name':os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'api_key': os.environ.get('CLOUDINARY_API_KEY'),
    'api_secret': os.environ.get('CLOUDINARY_API_SECRET')
})

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL')

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    public_id = db.Column(db.String(200), nullable=False)

    def __init__(self, title, genre, image_url, public_id):
        self.title = title
        self.genre = genre
        self.image_url = image_url
        self.public_id = public_id

class MovieSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "genre", "image_url", "public_id")

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

# POST
@app.route("/api/v1/movie", methods=["POST"])
def add_movie():
    title = request.json["title"]
    genre = request.json["genre"]
    image_url = request.json["image_url"]
    public_id = request.json["public_id"]

    new_movie = Movie(title, genre, image_url, public_id)

    db.session.add(new_movie)
    db.session.commit()

    movie = Movie.query.get(new_movie.id)
    return movie_schema.jsonify(movie)


# GET
@app.route("/api/v1/movies", methods=["GET"])
def get_movies():
    all_movies = Movie.query.all()
    result = movies_schema.dump(all_movies)

    return jsonify(result)


# GET
@app.route("/api/v1/movie/<id>", methods=["GET"])
def get_one_movie(id):
    movie = Movie.query.get(id)
    return movie_schema.jsonify(movie)


# PUT/PATCH by ID
@app.route("/api/v1/movie/<id>", methods=["PATCH"])
def update_movie(id):
    movie = Movie.query.get(id)

    new_title = request.json["title"]
    new_genre = request.json["genre"]
    new_image_url = request.json["image_url"]

    movie.title = new_title
    movie.genre = new_genre
    movie.image_url = new_image_url

    db.session.commit()
    return movie_schema.jsonify(movie)

# DELETE
@app.route("/api/v1/movie/<id>", methods=["DELETE"])
def delete_movie(id):
    movie = Movie.query.get(id)
    db.session.delete(movie)
    db.session.commit()
    Cloud.api.delete_resources([movie.public_id])

    return jsonify("Movie GONE!")


if __name__ == "__main__":
    app.debug = True
    app.run()