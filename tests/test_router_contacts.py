from unittest.mock import AsyncMock, patch
import pytest


@pytest.mark.asyncio
async def test_get_contacts(async_client, get_token, mock_limiter, monkeypatch):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    monkeypatch.setattr(
        "src.app_users.services_cache.get_redis_client", AsyncMock(return_value=mock_redis)
    )

    response = await async_client.get("api/contacts", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_add_contact(async_client, get_token, mock_limiter):
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    with patch("src.app_users.services_cache.get_redis_client", return_value=mock_redis):
        response = await async_client.post(
            "api/contacts",
            headers=headers,
            json={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email_sec": "test@gmail.com",
            },
        )

        assert response.status_code == 201, response.text
        data = response.json()
        assert "id" in data
        assert data["first_name"] == "test_first_name"
        assert data["email_sec"] == "test@gmail.com"


@pytest.mark.asyncio
async def test_get_contact_id(async_client, get_token, monkeypatch, mock_limiter):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    monkeypatch.setattr(
        "src.app_users.services_cache.get_redis_client", AsyncMock(return_value=mock_redis)
    )

    response_w = await async_client.post(
        "api/contacts",
        headers=headers,
        json={
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "email_sec": "testr@gmail.com",
        },
    )
    assert response_w.status_code == 201, response_w.text
    data_w = response_w.json()
    contact_id = data_w["id"]

    response = await async_client.get(f"api/contacts/{contact_id}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == contact_id
    assert data["first_name"] == "test_first_name"

    contact_id += 1
    response = await async_client.get(f"api/contacts/{contact_id}", headers=headers)
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "CONTACT NOT FOUND"
