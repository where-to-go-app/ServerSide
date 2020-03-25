import os
import pytest
from main import app
from database import db
from models import *


# Чтобы запустить тесты нужно в консоли ввести команду: pytest
# Все названия тестов, файлов с тестами должны начинаться с test_


@pytest.fixture
def init_app():
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


def test_home_page(init_app):
    response = init_app.get('/')
    assert response.status_code == 200
