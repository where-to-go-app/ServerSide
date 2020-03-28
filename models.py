from database import db


class User(db.Model):
    __tablename__ = "users"

    client_id = db.Column(db.Integer, primary_key=True)  # Идентификатор пользователя вк.
    user_token = db.Column(db.String(256))  # Этот токен есть на клиенте и он будет приходить вместе с запросом.
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))


class Place(db.Model):
    __tablename__ = "places"

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    creator_id = db.Column(db.Integer)
    place_name = db.Column(db.String(256))
    place_desc = db.Column(db.String(256))
    country = db.Column(db.String(256))
    # likes_count = db.Column(db.Integer(), default=0)    Мы можем каждый раз считать лайки из таблицы лайков
    # comments_count = db.Column(db.Integer(), default=0) То же самое с комментариями


class Like(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.ForeignKey(Place.id))
    user_id = db.Column(db.Integer())


class Photo(db.Model):
    __tablename__ = "photos"

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.ForeignKey(Place.id))
    photo_url = db.Column(db.String(256))
    photo_name = db.Column(db.String(256))


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.ForeignKey(Place.id))
    user_id = db.Column(db.Integer())
    text = db.Column(db.String(1024))


class ErrorResponse:
    def __init__(self, code, message):
        self.code = code
        self.message = message
