import os
import uuid

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


RESPONSE_OK = "ok"

# коды ошибок, возращаемых сервером
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
    secret_string = request.args.get("auth_secret_string")
    if secret_string is None or secret_string != settings.auth_secret_string:
        return jsonify(ErrorResponse(code=CODE_AUTH_ERROR, message="Неверный секретный ключ"))

    client_id = request.args.get("client_id")
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")

    user = User.query.get(client_id)
    if user is None:
        user_token = uuid.uuid4()

        new_user = User(
            client_id=client_id,
            user_token=user_token,
            first_name=first_name,
            last_name=last_name)

        db.session.add(new_user)
        db.session.commit()
    else:
        user_token = user.user_token

    return user_token


# Places
@app.route("/api/places/create", methods=["POST"])
def create_place():
    # получаем параметры из запроса
    place_name = request.args.get('place_name')
    place_desc = request.args.get('place_desc')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    user_token = request.args.get('user_token')
    country = request.args.get('country')
    photos = request.files

    # найти пользователя по токену
    creator = User.query.filter_by(user_token=user_token)
    if creator is None:
        return jsonify(ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found"))

    # сохранить место
    place = Place(
        latitude=latitude,
        longitude=longitude,
        creator_id=creator.client_id,
        place_name=place_name,
        place_desc=place_desc,
        country=country
    )
    db.session.add(place)
    db.session.commit()

    # сохранить фотки
    for p in photos:
        if allowed_file(p.filename):
            continue
        name = "{}.png".format(uuid.uuid4())
        url = "https://{}/{}/{}".format(settings.site_hostname, settings.images_dir, name)
        photo = Photo(
            place_id=place.id,
            photo_url=url,
            photo_name=name
        )

        db.session.add(photo)
        db.session.commit()
        p.save(os.path.join(settings.images_dir, name))

    return RESPONSE_OK


@app.route("/api/places/update", methods=["POST"])
def update_place():
    # получаем параметры из запроса
    place_id = request.args.get('place_id')
    place_name = request.args.get('place_name')
    place_desc = request.args.get('place_desc')
    user_token = request.args.get('user_token')

    # Найти пользователя по токену
    creator = User.query.filter_by(user_token=user_token)
    if creator is None:
        return jsonify(ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found"))

    # если пользователь - не автор места, тогда вернуть ошибку
    place = Place.query.get(place_id)
    if place is None:
        return jsonify(ErrorResponse(code=CODE_ENTITY_NOT_FOUND, message="place was not found"))
    if place.creator_id != creator.client_id:
        return jsonify(
            ErrorResponse(code=CODE_NO_PERMISSION, message="user have not permission to edit this place"))

    place.place_name = place_name
    place.place_desc = place_desc
    db.session.commit()

    return RESPONSE_OK


@app.route("/api/places/delete", methods=["POST"])
def delete_place():
    # получаем параметры из запроса
    place_id = request.args.get('place_id')
    user_token = request.args.get('user_token')

    # Найти пользователя по токену
    creator = User.query.filter_by(user_token=user_token)
    if creator is None:
        return jsonify(ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found"))

    # если пользователь - не автор места, тогда вернуть ошибку
    place = Place.query.get(place_id)
    if place is None:
        return jsonify(ErrorResponse(code=CODE_ENTITY_NOT_FOUND, message="place was not found"))

    if place.creator_id != creator.client_id:
        return jsonify(
            ErrorResponse(code=CODE_NO_PERMISSION, message="user have not permission to edit this place"))

    # Удалить файлы
    photos = Photo.query.filter_by(place_id=place_id)
    for p in photos:
        os.remove(os.path.join(settings.images_dir, p.photo_name))

    # Удалить запись из бд
    db.session.delete(place)
    db.session.commit()

    return RESPONSE_OK


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Likes
@app.route("/api/likes/add_like", methods=["POST"])
def add_like():
    place_id = request.args.get('place_id')
    user_token = request.args.get('user_token')

    # найти пользователя по токену
    user = User.query.filter_by(user_token=user_token)
    if user is None:
        return jsonify(ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found"))

    new_like = Like(
        place_id=place_id,
        user_id=user.first().client_id
    )
    db.session.add(new_like)
    db.session.commit()
    return RESPONSE_OK


@app.route("/api/likes/delete_like", methods=["POST"])
def delete_like():
    like_id = request.args.get('like_id')
    user_token = request.args.get('user_token')

    # найти пользователя по токену
    user = User.query.filter_by(user_token=user_token)
    if user is None:
        return jsonify(ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found"))

    like = Like.query.filter_by(id=like_id)
    # может ли пользователь удалить лайк
    if like.first().user_id != user.first().client_id:
        return jsonify(
            ErrorResponse(code=CODE_NO_PERMISSION, message="user have not permission to edit this like"))

    db.session.delete(like)
    db.session.commit()
    return RESPONSE_OK


# Comments
@app.route("/api/comments/create", methods=["GET"])
def create_comment():
    place_id = request.args.get('place_id')
    user_token = request.args.get('user_token')
    comment_text = request.args.get('comment_text')

    # найти пользователя по токену
    user = User.query.filter_by(user_token=user_token)
    if user is None:
        return jsonify(ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found"))

    comment = Comment(
        place_id=place_id,
        text=comment_text,
        user_id=user.first().client_id
    )
    db.session.add(comment)
    db.session.commit()
    return RESPONSE_OK


@app.route("/api/comments/update", methods=["GET"])
def update_comment():
    comment_id = request.args.get('comment_id')
    user_token = request.args.get('user_token')
    new_comment_text = request.args.get('comment_text')

    # найти пользователя по токену
    user = User.query.filter_by(user_token=user_token)
    if user is None:
        return jsonify(ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found"))

    # проверка, существует ли комментарий с таким id
    comment = Comment.query.filter_by(id=comment_id)
    if comment is None:
        return jsonify(ErrorResponse(code=CODE_ENTITY_NOT_FOUND, message="comment was not found"))
    # проверка, может ли пользователь изменять данный комментарий
    if comment.user_id != user.client_id:
        return jsonify(ErrorResponse(code=CODE_NO_PERMISSION, message="user have no permission to update this comment"))

    comment.text = new_comment_text
    db.session.commit()
    return RESPONSE_OK


@app.route("/api/comments/delete", methods=["GET"])
def delete_comment():
    comment_id = request.args.get('comment_id')
    user_token = request.args.get('user_token')

    # найти пользователя по токену
    user = User.query.filter_by(user_token=user_token)
    if user is None:
        return jsonify(ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found"))

    # проверка, существует ли комментарий с таким id
    comment = Comment.query.filter_by(id=comment_id)
    if comment is None:
        return jsonify(ErrorResponse(code=CODE_ENTITY_NOT_FOUND, message="comment was not found"))
    # проверка, может ли пользователь изменять данный комментарий
    if comment.first().user_id != user.first().client_id:
        return jsonify(ErrorResponse(code=CODE_NO_PERMISSION, message="user have no permission to delete this comment"))

    db.session.delete(comment)
    db.session.commit()
    return RESPONSE_OK


@app.route("/api/places/get", methods=["GET"])
def get_place_info_by_id():
    place_id = request.args.get('comment_id')
    user_token = request.args.get('user_token')

    # найти пользователя по токену
    user = User.query.filter_by(user_token=user_token)
    if user is None:
        return jsonify(ErrorResponse(code=CODE_USER_NOT_FOUND, message="user was not found"))

    # проверка, существует ли место с таким id
    place = Comment.query.filter_by(id=place_id)
    if place is None:
        return jsonify(ErrorResponse(code=CODE_ENTITY_NOT_FOUND, message="place was not found"))

    photos = Photo.query.filter_by(place_id=place_id)
    likes_count = Like.query.filter_by(place_id=place_id).count()
    comments = Comment.query.filter_by(place_id=place_id)

    # TODO как-нибудь сделать отправку всей информации на клиент. Оставляю это тебе, так как пока не знаю, как будет лучше

    return RESPONSE_OK


# Test
@app.route("/", methods=["GET"])
def index():
    return "test"


if __name__ == "__main__":
    app.run("localhost", port=8080)
