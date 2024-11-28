from unittest.mock import AsyncMock, MagicMock
import pytest

from fastapi.datastructures import UploadFile
from io import BytesIO

from src.app_users.shemas_user import ChangePassword
from src.app_users.services_auth import auth_service


@pytest.mark.asyncio
async def test_get_current_user(async_client, get_token, monkeypatch, mock_limiter):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    test_file = UploadFile(filename="test.png", file=BytesIO(b"test image data"))
    expected_url = "http://test-cloudinary.com/avatar.jpg"

    mock_upload = AsyncMock(return_value={"version": "12345"})
    monkeypatch.setattr("cloudinary.uploader.upload", mock_upload)
    mock_build_url = MagicMock(return_value=expected_url)
    monkeypatch.setattr("cloudinary.CloudinaryImage.build_url", mock_build_url)

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    monkeypatch.setattr(
        "src.app_users.services_cache.get_redis_client", AsyncMock(return_value=mock_redis)
    )

    response = await async_client.patch(
        "api/user/avatar",
        files={"file": ("test.png", test_file.file, "image/png")},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["avatar"] == expected_url


@pytest.mark.asyncio
async def test_change_password(async_client, get_token, monkeypatch):
    body = ChangePassword(
        email="deadpool@example.com",
        password="123qwe",
    )

    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    # Выполняем запрос
    response = await async_client.post(
        "api/user/change_password", json=body.model_dump(), headers=headers
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert auth_service.verify_password(body.password, data["password"]) == True
    assert data["email"] == "deadpool@example.com"

    response = await async_client.post(
        "api/user/change_password",
        json=ChangePassword(
            email="test5@example.com",
            password="123qwe",
        ).model_dump(),
        headers=headers,
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "CONTACT NOT FOUND"
