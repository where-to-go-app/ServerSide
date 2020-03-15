import base64

import requests

ph1 = []
for i in range(1, 4):
    with open("test_ph/{}.png".format(i), "rb") as image_file:
        encoded_string = (base64.b64encode(image_file.read())).decode("utf-8")
        ph1.append(encoded_string)

req_create = {
    'latitude': -78.5656555,
    'longitude': -128.568555,
    'creator_name': 'mister228',
    'place_name': 'POLYTECH',
    'country': 'Russia',
    'province': 'Saints Petersburg',
    'description': 'bla-bla',
    'type': 'univer',
    'photos': ph1
}
req_create2 = {
    'latitude': -78.5656555,
    'longitude': -128.568555,
    'creator_name': 'mister228',
    'place_name': 'POLYweTECH',
    'country': 'Russia',
    'province': 'Saints Petersburg',
    'description': 'bla-bla',
    'type': 'univer',
    'photos': []
}
req_delete = {
    'place_name': 'POLYTECH'
}

ans = requests.post("http://localhost:8080/api/places/create", json=req_create)
print(ans.text)
# ans = requests.post("http://localhost:8080/api/places/create", json=req_create2)
# print(ans.text)
#
delete_place = requests.post("http://localhost:8080/api/places/delete", json=req_delete)
print(delete_place.text)