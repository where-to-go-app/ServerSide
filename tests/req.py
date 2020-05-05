import os

import requests


def test_auth():
    response = requests.post("http://valer14356.pythonanywhere.com/api/users/auth", params={
        "auth_secret_string":"debug",
        "client_id": 1234454,
        "first_name": "alex",
        "last_name": "dom"
    })
    print(response.text)


def test_create_place(user_token, long, lat):
    response = requests.post("http://valer14356.pythonanywhere.com/api/places/create", params={
        "latitude": lat,
        "longitude": long,
        "place_name": "fffffffff",
        "place_desc": "Лffffffffffо на планете",
        "country": "Russia",
        "address": "Penza",
        "user_token": user_token
    },
                             files={
                                 "photo1": open("../test_ph/1.png", "rb"),
                                 "photo2": open("../test_ph/2.png", "rb")
                             })
    print(response.text)


def test_update_place(user_token):
    response = requests.post("http://localhost:8080/api/places/update", params={
        "place_id": 9,
        "place_name": "Polytech2",
        "place_desc": "lol1",
        "user_token": user_token
    })
    print(response.text)


def test_delete_place(user_token):
    response = requests.post("http://localhost:8080/api/places/delete", params={
        "place_id": 9,
        "user_token": user_token
    })
    print(response.text)


def test_add_like(user_token):
    response = requests.post("http://localhost:8080/api/likes/add_like", params={
        "place_id": 9,
        "user_token": user_token
    })
    print(response.text)


def test_delete_like(user_token):
    response = requests.post("http://localhost:8080/api/likes/delete_like", params={
        "like_id": 5,
        "user_token": user_token
    })
    print(response.text)


def test_create_comment(user_token):
    response = requests.post("http://localhost:8080/api/comments/create", params={
        "place_id": 9,
        "user_token": user_token,
        "comment_text": "fkeferkflnerjfrnjelf"
    })
    print(response.text)


def test_update_comment(user_token):
    response = requests.post("http://localhost:8080/api/comments/update", params={
        "comment_id": 1,
        "user_token": user_token,
        "comment_text": "fkefhgjgh"
    })
    print(response.text)


def test_delete_comment(user_token):
    response = requests.post("http://localhost:8080/api/comments/delete", params={
        "comment_id": 1,
        "user_token": user_token,

    })
    print(response.text)


def test_get_place_info_by_id(place_id, user_token):
    response = requests.get("http://localhost:8080/api/places/get_place_by_id", params={
        "place_id": place_id,
        "user_token": user_token,

    })
    print(response.text)


def test_find_places_by_bounding_box(up_left_x, up_left_y, bottom_right_x, bottom_right_y):
    response = requests.get("http://valer14356.pythonanywhere.com/api/places/places_around", params={
        "up_left_x": up_left_x,
        "up_left_y": up_left_y,
        "bottom_right_x": bottom_right_x,
        "bottom_right_y": bottom_right_y,
        "user_token": "12345"
    })
    print(response.text)


if __name__ == "__main__":
    USER_TOKEN_1 = "314790c3-fcf3-485d-87af-dd821e082c21"
    USER_TOKEN_2 = "1c470743-9c3d-4efb-88ff-e3530e1f97d4"
    test_auth()
    #test_create_place(USER_TOKEN_2, 54.526252, 41.959880)
    test_create_place("ed5040d0-fb0a-4b21-84c5-3c04f59fa1cb", 53.778152, 45.775179)
    # test_create_place("ed5040d0-fb0a-4b21-84c5-3c04f59fa1cb", 30.778152, 45.775179)
    # test_create_place("ed5040d0-fb0a-4b21-84c5-3c04f59fa1cb", 53.778152, 30.775179)
    # test_update_place()
    # test_add_like("314790c3-fcf3-485d-87af-dd821e082c21")
    # test_add_like("ed5040d0-fb0a-4b21-84c5-3c04f59fa1cb")
    # test_delete_like("ed5040d0-fb0a-4b21-84c5-3c0459fa1cb")
    # test_delete_comment("314790c3-fcf3-485d-87af-dd821e082c21")
    # test_delete_place()

