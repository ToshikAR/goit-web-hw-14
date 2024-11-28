from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy import select, or_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact
from src.app_contacts.schemas_contact import ContactSchema, ContactUpdateSchema, ContactResponse
from src.entity.models import User


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """get_contacts

    Args:
        limit (int): [description]
        offset (int): [description]
        db (AsyncSession): [description]
        user (User): [description]

    Returns:
        [type]: [description]
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """get_contact

    Args:
        contact_id (int): [description]
        db (AsyncSession): [description]
        user (User): [description]

    Returns:
        [type]: [description]
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def add_contact(body: ContactSchema, db: AsyncSession, user: User):
    """add_contact

    Args:
        body (ContactSchema): [description]
        db (AsyncSession): [description]
        user (User): [description]

    Returns:
        [type]: [description]
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User):
    """update_contact

    Args:
        contact_id (int): [description]
        body (ContactUpdateSchema): [description]
        db (AsyncSession): [description]
        user (User): [description]

    Returns:
        [type]: [description]
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email_sec = "null" if body.email_sec == "user@example.com" else body.email_sec
        contact.phone = body.phone
        contact.description = body.description
        contact.date_birth = body.date_birth
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """delete_contact

    Args:
        contact_id (int): [description]
        db (AsyncSession): [description]
        user (User): [description]

    Returns:
        [type]: [description]
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


# ================================================================================
async def get_contacts_all(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_upcoming_birthdays_all(days: int, db: AsyncSession, user: User):
    today = datetime.now().date()
    months_days = [(today.month, today.day)]
    for i in range(1, days + 1):
        next_day = today + timedelta(days=i)
        months_days.append((next_day.month, next_day.day))

    conditions = [
        (extract("month", Contact.date_birth) == month)
        & (extract("day", Contact.date_birth) == day)
        for month, day in months_days
    ]

    stmt = select(Contact).where(or_(*conditions))
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts


async def get_search_contacts_all(params: List[Optional[str]], db: AsyncSession, user: User):
    first_name, last_name, email_sec, email = params

    filters = []
    if first_name:
        filters.append(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        filters.append(Contact.last_name.ilike(f"%{last_name}%"))
    if email_sec:
        filters.append(Contact.email_sec.ilike(f"%{email_sec}%"))
    if email:
        filters.append(User.email.ilike(f"%{email}%"))

    if filters:
        stmt = (
            select(Contact)
            .join(User, Contact.user_id == User.id, isouter=True)
            .where(or_(*filters))
        )

    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts
