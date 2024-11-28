from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.entity.models import User
from src.config import messages


user_data = {"username": "testuser", "email": "testuser@gmail.com", "password": "12345678"}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.app_users.routes_auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.app_users.routes_auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)

    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == messages.ACCOUNT_EXIST


def test_sigin_not_confirmed(client):
    response = client.post(
        "api/auth/signin",
        data={
            "username": "testuser@gmail.com",
            "password": "12345678",
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_CONFIRMED


@pytest.mark.asyncio
async def test_signin_user(client, session):
    user = user_data

    filter_user = select(User).filter(User.email == user_data.get("email"))
    user_db = await session.execute(filter_user)
    user_db = user_db.scalar_one_or_none()
    user_db.confirmed = True
    await session.commit()

    response = client.post(
        "/api/auth/signin",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data


def test_wrong_password_signin_user(client):
    response = client.post(
        "api/auth/signin", data={"username": user_data.get("email"), "password": "password"}
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_PASSWORD


def test_wrong_email_signin_user(client):
    response = client.post(
        "api/auth/signin", data={"username": "email", "password": user_data.get("password")}
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_EMAIL


def test_validation_error_signin_user(client):
    response = client.post("api/auth/signin", data={"password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data
