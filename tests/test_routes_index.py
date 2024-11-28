import pytest
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_healthchecker_success(async_client, monkeypatch):
    mock_execute = AsyncMock()
    mock_execute.return_value.fetchone.return_value = (1,)
    monkeypatch.setattr("src.database.db.get_db", AsyncMock(return_value=mock_execute))

    response = await async_client.get("index/healthchecker")

    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI!"}
