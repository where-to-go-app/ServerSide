
import os
import uuid
import json
from PIL import Image
from flask import Flask, request, jsonify
import settings
from models import *


app = Flask(__name__)
app.debug = True

DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username=settings.database_username,
    password=settings.database_password,
    hostname=settings.database_hostname,
    databasename=settings.database_name
)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    db.create_all()

# коды, возращаемые сервером
RESPONSE_OK = 0
CODE_USER_NOT_FOUND = 1
CODE_AUTH_ERROR = 2
CODE_NO_PERMISSION = 3
CODE_ENTITY_NOT_FOUND = 4

ALLOWED_EXTENSIONS = {"png"}


# Users
@app.route("/api/users/auth", methods=["POST"])
def auth_user():
    # получаем вк client_id, проверяем есть ли пользователь в бд
    # если пользователя нет, создаем пользователя, генерируем новый user_token с помощью uuid, и возвращаем его
    # если пользователь есть, отдаем уже когда-то созданный user_token
    secret_string = request.form.get("auth_secret_string")
    print(secret_string)
    if secret_string is None or secret_string != settings.auth_secret_string:
        return ErrorResponse(code=CODE_AUTH_ERROR, message="wrong secret key").to_json()

    client_id = request.form.get("client_id")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")

    users = User.query.get(client_id)
    if users is None:
        user_token = uuid.uuid4()

        new_user = User(
            client_id=client_id,
            user_token=str(user_token),
            first_name=first_name,
            last_name=last_name)

        db.session.add(new_user)
        db.session.commit()
    else:
        user_token = users.user_token

    return jsonify({"code": RESPONSE_OK,
                    "message": str(user_token)})


# Places
@app.route("/api/places/create", methods=["POST"])
def create_place():
    # получаем параметры из запроса
    place_name = request.form.get('place_name')
    place_desc = request.form.get('place_desc')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    user_token = request.form.get('user_token')
    country = request.form.get('country')
    address = request.form.get('address')
    photos = request.files
    print(user_token)
    # найти пользователя по токену
    creator = User.query.filter_by(user_token=user_token).first()
    if creator is None:
        return ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found").to_json()

    # сохранить место
    place = Place(
        latitude=latitude,
        longitude=longitude,
        creator_id=creator.client_id,
        place_name=place_name,
        place_desc=place_desc,
        country=country,
        address=address
    )
    db.session.add(place)
    db.session.commit()

    is_main = True
    # сохранить фотки
    for p in photos:
        if allowed_file(p):
            continue
        ph = photos[p]
        name = "{}.png".format(uuid.uuid4())
        url = "https://{}/{}/{}".format(settings.site_hostname, settings.images_dir, name)
        if is_main:
            avatar_photo = Image.open(ph)
            avatar_photo = avatar_photo.resize((100, 100))
            name_avatar = "{}.png".format(uuid.uuid4())
            url_avatar = "https://{}/{}/{}".format(settings.site_hostname, settings.images_dir, name_avatar)
            photo = Photo(
                place_id=place.id,
                photo_url=url_avatar,
                photo_name=name_avatar,
                is_main=True
            )
            is_main = False

            db.session.add(photo)
            avatar_photo.save(os.path.abspath(os.path.join(settings.images_dir, name_avatar)))


        photo = Photo(
            place_id=place.id,
            photo_url=url,
            photo_name=name,
            is_main=False
        )

        db.session.add(photo)
        db.session.commit()


    return jsonify({"code": RESPONSE_OK})


@app.route("/api/places/update", methods=["POST"])
def update_place():
    # получаем параметры из запроса
    place_id = request.args.get('place_id')
    place_name = request.args.get('place_name')
    place_desc = request.args.get('place_desc')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    country = request.args.get('country')
    address = request.args.get('address')
    user_token = request.args.get('user_token')

    # Найти пользователя по токену
    creator = User.query.filter_by(user_token=user_token).first()
    if creator is None:
        return ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found").to_json()

    # если пользователь - не автор места, тогда вернуть ошибку
    place = Place.query.get(place_id)
    if place is None:
        return ErrorResponse(code=CODE_ENTITY_NOT_FOUND, message="place was not found").to_json()
    if place.creator_id != creator.client_id:
        return ErrorResponse(code=CODE_NO_PERMISSION, message="user has not permission to edit this place").to_json()

    place.place_name = place_name
    place.place_desc = place_desc
    place.latitude = latitude
    place.longitude = longitude
    place.country = country
    place.address = address
    db.session.commit()

    return jsonify({"code": RESPONSE_OK})


@app.route("/api/places/delete", methods=["POST"])
def delete_place():
    # получаем параметры из запроса
    place_id = request.args.get('place_id')
    user_token = request.args.get('user_token')

    # Найти пользователя по токену
    creator = User.query.filter_by(user_token=user_token).first()
    if creator is None:
        return ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found").to_json()
    # если пользователь - не автор места, тогда вернуть ошибку
    place = Place.query.get(place_id)
    if place is None:
        return ErrorResponse(code=CODE_ENTITY_NOT_FOUND, message="place was not found").to_json()

    if place.creator_id != creator.client_id:
        return ErrorResponse(code=CODE_NO_PERMISSION, message="user has not permission to edit this place").to_json()

    # Удалить файлы
    photos = Photo.query.filter_by(place_id=place_id)
    for p in photos:
        db.session.delete(p)
        os.remove(os.path.join(settings.images_dir, p.photo_name))

    # Удалить запись из бд

    db.session.delete(place)
    db.session.commit()

    return jsonify({"code": RESPONSE_OK})


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Likes
@app.route("/api/likes/add_like", methods=["POST"])
def add_like():
    place_id = request.args.get('place_id')
    user_token = request.args.get('user_token')

    # найти пользователя по токену
    user = User.query.filter_by(user_token=user_token).first()
    if user is None:
        return ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found").to_json()

    place = Place.query.filter_by(id=place_id).first()
    if place is None:
        return ErrorResponse(code=CODE_ENTITY_NOT_FOUND, message="place was not found").to_json()

    like = Like.query.filter_by(user_id=user.client_id).first()
    if like is not None:
        return ErrorResponse(code=CODE_NO_PERMISSION, message="user has no permission to set a like twice").to_json()
    new_like = Like(
        place_id=place_id,
        user_id=user.client_id
    )
    db.session.add(new_like)
    db.session.commit()
    return jsonify({"code": RESPONSE_OK})


@app.route("/api/likes/delete_like", methods=["POST"])
def delete_like():
    like_id = request.args.get('like_id')
    user_token = request.args.get('user_token')

    # найти пользователя по токену
    user = User.query.filter_by(user_token=user_token).first()
    if user is None:
        return ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found").to_json()

    like = Like.query.filter_by(id=like_id).first()
    if like is None:
        return ErrorResponse(code=CODE_ENTITY_NOT_FOUND, message="like with such id was not found").to_json()
    # может ли пользователь удалить лайк
    if like.user_id != user.client_id:
        return ErrorResponse(code=CODE_NO_PERMISSION, message="user has not permission to delete this like").to_json()

    db.session.delete(like)
    db.session.commit()
    return jsonify({"code": RESPONSE_OK})


# Comments
@app.route("/api/comments/create", methods=["POST"])
def create_comment():
    place_id = request.args.get('place_id')
    user_token = request.args.get('user_token')
    comment_text = request.args.get('comment_text')

    # найти пользователя по токену
    user = User.query.filter_by(user_token=user_token).first()
    if user is None:
        return ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found").to_json()

    place = Place.query.filter_by(id=place_id).first()
    if place is None:
        return ErrorResponse(code=CODE_ENTITY_NOT_FOUND, message="place was not found").to_json()

    comment = Comment(
        place_id=place_id,
        text=comment_text,
        user_id=user.client_id
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({"code": RESPONSE_OK})


@app.route("/api/comments/update", methods=["POST"])
def update_comment():
    comment_id = request.args.get('comment_id')
    user_token = request.args.get('user_token')
    new_comment_text = request.args.get('comment_text')

    # найти пользователя по токену
    user = User.query.filter_by(user_token=user_token).first()
    if user is None:
        return ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found").to_json()

    # проверка, существует ли комментарий с таким id
    comment = Comment.query.filter_by(id=comment_id).first()
    if comment is None:
        return ErrorResponse(code=CODE_ENTITY_NOT_FOUND, message="comment was not found").to_json()
    # проверка, может ли пользователь изменять данный комментарий
    if comment.user_id != user.client_id:
        return ErrorResponse(code=CODE_NO_PERMISSION,
                             message="user has no permission to update this comment").to_json()

    comment.text = new_comment_text
    db.session.commit()
    return jsonify({"code": RESPONSE_OK})


@app.route("/api/comments/delete", methods=["POST"])
def delete_comment():
    comment_id = request.args.get('comment_id')
    user_token = request.args.get('user_token')

    # найти пользователя по токену
    user = User.query.filter_by(user_token=user_token).first()
    if user is None:
        return ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found").to_json()

    # проверка, существует ли комментарий с таким id
    comment = Comment.query.filter_by(id=comment_id).first()
    if comment is None:
        return ErrorResponse(code=CODE_ENTITY_NOT_FOUND, message="comment was not found").to_json()
    # проверка, может ли пользователь изменять данный комментарий
    if comment.user_id != user.client_id:
        return ErrorResponse(code=CODE_NO_PERMISSION,
                             message="user has no permission to delete this comment").to_json()

    db.session.delete(comment)
    db.session.commit()
    return jsonify({"code": RESPONSE_OK})


@app.route("/api/places/place_by_id", methods=["GET"])
def get_place_info_by_id():
    place_id = request.args.get('place_id')
    user_token = request.args.get('user_token')

    # найти пользователя по токену
    user = User.query.filter_by(user_token=user_token).first()
    if user is None:
        return ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found").to_json()

    # проверка, существует ли место с таким id
    place = Place.query.filter_by(id=place_id).first()
    if place is None:
        return ErrorResponse(code=CODE_ENTITY_NOT_FOUND, message="place was not found").to_json()

    photos = [{
        "photo_name": photo.photo_name,
        "photo_url": photo.photo_url,
        "id": photo.id,
        "is_main": photo.is_main
    } for photo in Photo.query.filter_by(place_id=place_id)]
    likes_count = Like.query.filter_by(place_id=place_id).count()
    comments = [{
        "place_id": comment.place_id,
        "comment_text": comment.text,
        "id": comment.id
    } for comment in Comment.query.filter_by(place_id=place_id)]

    response = {}
    response["code"] = RESPONSE_OK
    response["place"] = {}
    response["place"]["id"] = place.id
    response["place"]["place_name"] = place.place_name
    response["place"]["longitude"] = place.longitude
    response["place"]["latitude"] = place.latitude
    response["place"]["country"] = place.country
    response["place"]["address"] = place.address
    response["place"]["creator_id"] = place.creator_id
    response["place"]["place_desc"] = place.place_desc
    response["place"]["photos"] = photos
    response["place"]["likes_count"] = likes_count
    response["place"]["comments"] = comments

    return jsonify(response)


@app.route("/api/places/places_around", methods=["GET"])
def places_around():
    up_left_x = request.args.get('up_left_x')
    up_left_y = request.args.get('up_left_y')
    bottom_right_x = request.args.get('bottom_right_x')
    bottom_right_y = request.args.get('bottom_right_y')
    user_token = request.args.get('user_token')

    # найти пользователя по токену
    user = User.query.filter_by(user_token=user_token).first()
    if user is None:
        return ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found").to_json()
    place_query = Place.query.filter(bottom_right_y < Place.latitude).filter(Place.latitude < up_left_y).filter(up_left_x < Place.longitude).filter(Place.longitude < bottom_right_x)
    places = []
    for place in place_query:
        avatar = Photo.query.filter_by(place_id=place.id).filter_by(is_main=True).first()
        if avatar is not None:
            avatar_url = avatar.photo_url
        else:
            avatar_url = None;
        places.append({"id": place.id,
                   "place_name": place.place_name,
                   "avatar_url": avatar_url,
                   "latitude": place.latitude,
                   "longitude": place.longitude} )

    return jsonify({"code": RESPONSE_OK,
                    "places": places
                    })

@app.route("/api/places/favorite_places", methods=["GET"])
def favorite_places():
    token = request.args.get('user_token')
    # найти пользователя по токену
    user = User.query.filter_by(user_token=token).first()
    if user is None:
        return ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found").to_json()
    favorite_places = Like.query.filter_by(user_id=user.client_id)
    result = []

    for p in favorite_places:
        result.append({
            "id": p.id,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "creator_id": p.creator_id,
            "place_name": p.place_name,
            "place_desc": p.place_desc,
            "country": p.country,
            "address": p.address
        })
    return json.dumps(result)

@app.route("/api/places/search_places", methods=["GET"])
def search_places():
    token = request.args.get('user_token')
    query = request.args.get('query')
    # найти пользователя по токену
    user = User.query.filter_by(user_token=token).first()
    if user is None:
        return ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found").to_json()
    search_places = Place.query.filter(Place.place_name.startswith(query)).all()
    result = []

    for p in search_places:
        result.append({
            "id": p.id,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "creator_id": p.creator_id,
            "place_name": p.place_name,
            "place_desc": p.place_desc,
            "country": p.country,
            "address": p.address
        })
    return json.dumps(result)

# Test
@app.route("/", methods=["GET"])
def index():
    return "test"


if __name__ == "__main__":
    app.run("localhost", port=8080)
