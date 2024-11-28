from datetime import datetime, timezone
import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.app_users.repository_users import (
    get_user_by_email,
    create_user,
    update_token,
    delete_token,
    visit_user,
    confirmed_email,
    change_password,
    update_avatar_url,
)
from src.app_users.shemas_user import UserSchema, ChangePassword


class TestAsyncUser(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(
            username="test_user", email="test@gmail.com", password="qwer", confirmed=False
        )
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_user_by_email(self):
        email = "test@gmail.com"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mock_result

        result = await get_user_by_email(email, self.session)
        self.assertEqual(result, self.user)

    async def test_create_user(self):
        body = UserSchema(
            username="test_user",
            email="test@gmail.com",
            password="qwerqwer",
        )

        result = await create_user(body, self.session)

        self.assertIsInstance(result, User)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)

    async def test_update_token(self):
        token = "qwertyuuiop"

        result = await update_token(self.user, token, self.session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mock_result

        self.assertIsInstance(result, User)
        self.assertEqual(result.refresh_token, token)

    async def test_visit_user(self):
        visit = datetime.now(timezone.utc)

        result = await visit_user(self.user, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.last_visit, visit)

    async def test_delete_token(self):
        token = "qwertyuuiop"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mock_result

        result = await update_token(self.user, token, self.session)
        result = await delete_token(result, self.session)

        self.assertIsInstance(result, User)
        self.assertEqual(result.refresh_token, None)

    async def test_confirmed_email(self):
        email = "test@gmail.com"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mock_result

        result = await confirmed_email(email, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.confirmed, True)

    async def test_change_password(self):
        body = ChangePassword(
            email="test@gmail.com",
            password="12345678",
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mock_result

        result = await change_password(body, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.password, body.password)

    async def test_update_avatar_url(self):
        email = "test@gmail.com"
        url = "http://test-cloudinary.com/avatar.jpg"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mock_result

        result = await update_avatar_url(email, url, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.avatar, url)

    async def test_delete_token(self):
        email = "test@gmail.com"
        url = "http://test-cloudinary.com/avatar.jpg"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mock_result

        result = await update_avatar_url(email, url, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.avatar, url)
