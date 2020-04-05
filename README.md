# ServerSide
### Server side for WhereToGo app
# Методы, поддерживаемые api:

### /api/users/auth [POST]
##### Параметры:
- secret_string - секретная строка
- client_id - id клиента вк
- first_name - имя пользователя
- last_name - фамилия пользователя
#### Описание
 - Аутентификация пользователя через ВК. Возвращает новый токен, если пользователь новый, иначе, возвращает старый.
#### Формат ответа
```json
{
  "code": 0, 
  "user_token": "USER_TOKEN"
}
```
#### Ошибки:
 - code: 2, wrong secret key - неверный секретный ключ

### /api/places/create [POST]
##### Параметры:
- place_name - название места
- place_desc - описание места
- latitude - широта
- longitude - долгота
- user_token - токен пользователя
 country - страна
- address - адрес
##### Файлы 
 - photos - ресурсы фотографий {"название": файл}
#### Описание
 - Создает новое место с указанными параметрами
#### Ошибки:
 - code: 1, user was not found - не существует пользователя с таким токеном
### /api/places/update [POST]
##### Параметры:
- place_id - id места, которое пытаются изменить
- place_name -  новое название места
- place_desc - новое описание места
- latitude - новая широта
- longitude - новая долгота
- country - новая страна
- address - новый адрес
- user_token - токен пользователя
ВСЕ ПАРАМЕТРЫ ДОЛЖНЫ БЫТЬ УКАЗАНЫ. ЕСЛИ КАКОЙ-ТО ПАРАМЕТР НЕ УКАЗАН, ЕГО ЗНАЧЕНИЕ МЕНЯЕТСЯ НА "" (БУДЕТ ИСПРАВЛЕНО В ДАЛЬНЕЙШЕМ)

#### Описание
 - Изменяет параметры указанного места
#### Ошибки:
 - code: 1, user was not found - не существует пользователя с таким токеном
 - code: 3, user has not permission to edit this place - данный пользователь не может изменить данное место
 - code: 4, place was not found - места с таким id не существует

### /api/places/delete [POST]
##### Параметры:
- place_id - id места, которое пытаются удалить
- user_token - токен пользователя

#### Описание
 - Удаляет место с id=place_id
#### Ошибки:
 - code: 1, user was not found - не существует пользователя с таким токеном
 - code: 3, user has not permission to edit this place - данный пользователь не может удалить данное место
 - code: 4, place was not found - места с таким id не существует

### /api/places/get_place_by_id [GET]
##### Параметры:
- place_id - id места
- user_token - токен пользователя

#### Описание
 - Возвращает полную информацию о месте с id=place_id
#### Формат ответа
```json
{
  "code": "0", 
  "place": {
    "address": "address", 
    "country": "Russia", 
    "place_desc": "WOW", 
    "place_name": "GOOD_PLACE",
    "creator_id": 12344, 
    "id": 9, 
    "latitude": 54.4444, 
    "likes_count": 2, 
    "longitude": 45.4444, 
    "photos": [
      {
        "id": 13, 
        "photo_name": "63d7bd9f-6687-4097-93dd-3487a7032465.png", 
        "photo_url": "https://SITENAME/photos/63d7bd9f-6687-4097-93dd-3487a7032465.png"
      }, 
      {
        "id": 14, 
        "photo_name": "e6e15eb8-032b-48e6-bb3e-345ce9eb4968.png", 
        "photo_url": "https://SITENAME/photos/e6e15eb8-032b-48e6-bb3e-345ce9eb4968.png"
      }
    ], 
"comments": [
      {
        "comment_text": "WOW", 
        "id": 2, 
        "place_id": 9
      }
    ]
  }
}
```
#### Ошибки:
 - code: 1, user was not found - не существует пользователя с таким токеном
 - code: 4, place was not found - места с таким id не существует

### /api/places/get_places_by_bounding_box [GET]
##### Параметры:
- up_left_x - долгота левой верхней точки
- up_left_y - широта левой верхней точки
- bottom_right_x - долгота правой нижней точки
- bottom_right_y - широта правой нижней точки
- user_token - токен пользователя 

#### Описание
 - Возвражает JSON с id мест, попадающие в заданную область
#### Формат ответа
```json
{
  "code": "0", 
  "places": [
    {
      "id": 10
    }, 
    {
      "id": 11
    }
  ]
}
```
#### Ошибки:
code: 1, user was not found - не существует пользователя с таким токеном

### /api/likes/add_like [POST]
##### Параметры:
- place_id - id места
- user_token - токен пользователя 

#### Описание
 - Добавляет лайк от пользователя с user_token к месту с id=place_id
#### Ошибки:
 - code: 1, user was not found - не существует пользователя с таким токеном
 - code: 4, place was not found - места с таким id не существует

### /api/likes/delete_like [POST]
##### Параметры:
- like_id - id лайка
- user_token - токен пользователя 

#### Описание
 - Удаляет лайк c id=like_id
#### Ошибки:
 - code: 1, user was not found - не существует пользователя с таким токеном
- code: 4, like with such id was not found - лайка с таким id не существует
- code: 3, user has not permission to delete this like - пользователь с таким user_token не может удалить этот лайк

### /api/comments/create [POST]
##### Параметры:
- place_id  - id места
- comment_text - текст комментария
- user_token - токен пользователя 

#### Описание
 - Добавляет лайк от пользователя с токеном user_token к месту с id=place_id
#### Ошибки:
 - code: 1, user was not found - не существует пользователя с таким токеном
 - code: 4, place was not found - места с таким id не существует

### /api/likes/update_comment [POST]
##### Параметры:
- comment_id - id комментария
- new_comment_text - новый текст комментария
- user_token - токен пользователя 

#### Описание
 - Изменяет комментарий c id=comment_id
#### Ошибки:
 - code: 1, user was not found - не существует пользователя с таким токеном
- code: 4, comment was not found - комментария с таким id не существует
- code: 3, user has no permission to update this comment - пользователь с таким user_token не может изменить этот комментарий

### /api/likes/delete_like [POST]
##### Параметры:
- comment_id - id комментария
- user_token - токен пользователя 

#### Описание
 - Удаляет комментарий c id=comment_id
#### Ошибки:
 - code: 1, user was not found - не существует пользователя с таким токеном
- code: 4, comment was not found - комментария с таким id не существует
- code: 3, user has no permission to delete this comment - пользователь с таким user_token не может удалить этот комментарий


