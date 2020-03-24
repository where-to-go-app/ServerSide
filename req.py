import base64

import requests

ph1 = []
for i in range(1, 4):
    with open("test_ph/{}.png".format(i), "rb") as image_file:
        encoded_string = (base64.b64encode(image_file.read())).decode("utf-8")
        ph1.append(encoded_string)

req_create = {
    'latitude': 53.185389,
    'longitude': 45.013986,
    'creator_name': 'mister228',
    'place_name': 'true1',
    'country': 'Russia',
    'province': 'Penza',
    'description': 'bla-bla',
    'type': 'univer',
    'photos': ph1
}
req_create2 = {
    'latitude': 53.188227,
    'longitude':  45.011857,
    'creator_name': 'mister228',
    'place_name': 'true2',
    'country': 'Russia',
    'province': 'Penza',
    'description': 'bla-bla',
    'type': 'univer',
    'photos': ph1,
    'likes_count': 23
}

req_create3 = {
    'latitude': 59.959126,
    'longitude':  30.301043,
    'creator_name': 'mister228',
    'place_name': 'true1',
    'country': 'Russia',
    'province': 'Saints Petersburg',
    'description': 'bla-bla',
    'type': 'univer',
    'photos': []

}
req_delete = {
    'id': 58
}

req_find_near = {
    'latitude': 53.185453,
    'longitude': 45.013143,
    'radius': 2000,
    'limit': 3
}

req_find_interesting = {
    'limit': 2
}

req_get_info = {
    'id': 59
}

ans = requests.post("http://localhost:8080/api/places/create", json=req_create)
print(ans.text)
ans = requests.post("http://localhost:8080/api/places/create", json=req_create2)
print(ans.text)
ans = requests.post("http://localhost:8080/api/places/create", json=req_create3)
print(ans.text)

delete_place = requests.post("http://localhost:8080/api/places/delete", json=req_delete)
print(delete_place.text)

ans1 = requests.post("http://localhost:8080/api/places/get_info", json=req_get_info)
print(ans1.text)