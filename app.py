import base64
import os
from io import BytesIO

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, make_response, jsonify
from PIL import Image

import settings

app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"] = "fgggg5hyh56t5t54t43t34t"

db = SQLAlchemy(app)


class Place(db.Model):

    __tablename__ = "place"

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    creator_name = db.Column(db.String(256))
    place_name = db.Column(db.String(256))
    country = db.Column(db.String(256))
    province = db.Column(db.String(256))
    description = db.Column(db.String(512))
    type = db.Column(db.String(256))
    likes_count = db.Column(db.Integer())


class Favorites(db.Model):

    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.ForeignKey(Place.id))
    user_id = db.Column(db.Integer())


class Photo(db.Model):

    __tablename__ = "photo"

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.ForeignKey(Place.id))
    photo_url = db.Column(db.String(256))


class Comment(db.Model):

    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.ForeignKey(Place.id))
    user_id = db.Column(db.Integer())
    text = db.Column(db.String(1024))


SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username=settings.username,
    password=settings.password,
    hostname=settings.hostname,
    databasename=settings.databasename
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/api/places/create", methods=["GET", "POST"])
def create_places():
    req = request.json

    place_row = Place(
        latitude=req["latitude"],
        longitude=req["longitude"],
        place_name=req["place_name"],
        creator_name=req["creator_name"],
        province=req["province"],
        type=req["type"],
        description=req["description"],
        likes_count=0
                      )

    db.session.add(place_row)
    db.session.commit()
    place_id = Place.query.filter_by(place_name=req["place_name"]).first().id
    print(place_id)
    for i in req["photos"]:
        photo_row = Photo(
            place_id=place_id,
        )
        db.session.add(photo_row)
        db.session.flush()
        db.session.refresh(photo_row)
        photo_row.photo_url = "photos/{}.png".format(photo_row.id)
        db.session.commit()
        im = Image.open(BytesIO(base64.b64decode(i)))
        im.save(photo_row.photo_url, 'PNG')

    db.session.commit()
    return jsonify(req)


@app.route("/api/places/delete", methods=["GET", "POST"])
def delete_place():
    req = request.json

    place = Place.query.filter_by(place_name=req["place_name"]).first()
    photos_to_delete = Photo.query.filter_by(place_id = place.id)

    for photo in photos_to_delete:
        print(photo.photo_url)
        try:
            os.remove(photo.photo_url)
        except:
            pass
        db.session.delete(photo)

    db.session.commit()
    db.session.delete(place)
    db.session.commit()
    return jsonify(req)


@app.route("/", methods=["GET", "POST"])
def index():
    return "hello"


if __name__ == "__main__":
    app.run("localhost", port=8080)
