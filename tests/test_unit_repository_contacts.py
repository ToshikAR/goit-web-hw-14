from datetime import datetime, timedelta
import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy import extract, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app_contacts.schemas_contact import ContactSchema, ContactUpdateSchema
from src.entity.models import Contact, User
from src.app_contacts.repository_contacts import (
    get_contacts,
    get_contact,
    add_contact,
    update_contact,
    delete_contact,
    get_search_contacts_all,
    get_upcoming_birthdays_all,
)


class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(
            username="test_user", email="test@gmail.com", password="qwer", confirmed=True
        )
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(first_name="Lika", last_name="Lola", user=self.user),
            Contact(first_name="Rita", last_name="Kola", user=self.user),
        ]
        mock_contact = MagicMock()
        mock_contact.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mock_contact
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contacts = [Contact(first_name="Lika", last_name="Lola", user=self.user)]
        mock_contact = MagicMock()
        mock_contact.scalar_one_or_none.return_value = contacts
        self.session.execute.return_value = mock_contact

        result = await get_contact(1, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_add_contact(self):
        body = ContactSchema(
            first_name="Lika",
            last_name="Lola",
            email_sec="test@test.com",
            description="test_description",
        )
        result = await add_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.description, body.description)

    async def test_update_contact(self):
        body = ContactUpdateSchema(
            first_name="Lika",
            last_name="Lola",
            email_sec="test@test.com",
            description="test_description",
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            first_name="Lika",
            last_name="Lola",
            email_sec="test@test.com",
            description="test_description",
            user=self.user,
        )
        self.session.execute.return_value = mocked_contact
        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.description, body.description)

    async def test_delete_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            first_name="Lika",
            last_name="Lola",
            email_sec="test@test.com",
            description="test_description",
            user=self.user,
        )

        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()

        self.assertIsInstance(result, Contact)

    # ----------------------------------------------------------------------------
    async def test_get_contacts_all(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(first_name="Lika", last_name="Lola", user=self.user),
            Contact(first_name="Rita", last_name="Kola", user=self.user),
        ]

        mock_contact = MagicMock()
        mock_contact.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mock_contact
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_search_contacts_all(self):
        params = ["Rita", None, None, "test@test.com"]
        contacts = [
            Contact(
                first_name="Lika",
                last_name="Lola",
                email_sec="test@test.com",
                user=self.user,
            ),
            Contact(
                first_name="Rita",
                last_name="Kola",
                email_sec="test@test1.com",
                user=self.user,
            ),
        ]

        mock_contact = MagicMock()
        mock_contact.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mock_contact

        result = await get_search_contacts_all(params, self.session, self.user)
        self.assertEqual(result, contacts)
        expected_filters = [
            Contact.first_name.ilike("%Rita%"),
            User.email.ilike("%test@test.com%"),
        ]

        expected_query = (
            select(Contact)
            .join(User, Contact.user_id == User.id, isouter=True)
            .where(or_(*expected_filters))
        )
        actual_query = self.session.execute.call_args[0][0]
        self.assertEqual(str(actual_query), str(expected_query))

    async def get_upcoming_birthdays_all(self):
        days = 4
        today = datetime(2024, 11, 19).date()

        expected_days = [
            (today.month, today.day),
            ((today + timedelta(days=1)).month, (today + timedelta(days=1)).day),  # 20 ноября
            ((today + timedelta(days=2)).month, (today + timedelta(days=2)).day),  # 21 ноября
            ((today + timedelta(days=3)).month, (today + timedelta(days=3)).day),  # 22 ноября
            ((today + timedelta(days=4)).month, (today + timedelta(days=4)).day),  # 23 ноября
        ]

        contacts = [
            Contact(
                first_name="Lika",
                last_name="Lola",
                email_sec="test@test.com",
                date_birth=datetime(2024, 11, 19).date(),
                user=self.user,
            ),
            Contact(
                first_name="Rita",
                last_name="Kola",
                email_sec="test@test1.com",
                date_birth=datetime(2024, 11, 23).date(),
                user=self.user,
            ),
        ]
        mock_contact = MagicMock()
        mock_contact.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mock_contact

        result = await get_upcoming_birthdays_all(days, self.session, self.user)
        self.assertEqual(result, contacts)
        expected_conditions = [
            (extract("month", Contact.date_birth) == month)
            & (extract("day", Contact.date_birth) == day)
            for month, day in expected_days
        ]
        expected_query = select(Contact).where(or_(*expected_conditions))
        self.session.execute.assert_called_once_with(expected_query)
