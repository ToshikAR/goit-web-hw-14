from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.database.db import get_db
from src.app_contacts import repository_contacts
from src.app_contacts.schemas_contact import ContactSchema, ContactResponse, ContactUpdateSchema
from src.app_users.services_auth import auth_service
from src.app_users.services_roles import access_to_route_am

router = APIRouter(prefix="/contacts", tags=["contacts"])
TIMES_LIMIT = 3
SECONDS_LIMIT = 10


@router.get(
    "/",
    response_model=list[ContactResponse],
    dependencies=[Depends(RateLimiter(times=TIMES_LIMIT, seconds=SECONDS_LIMIT))],
)
async def get_contacts(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contacts = await repository_contacts.get_contacts(limit, offset, db, user)
    return contacts


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    dependencies=[Depends(RateLimiter(times=TIMES_LIMIT, seconds=SECONDS_LIMIT))],
)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contact = await repository_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CONTACT NOT FOUND")
    return contact


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=TIMES_LIMIT, seconds=SECONDS_LIMIT))],
)
async def add_contact(
    body: ContactSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contact = await repository_contacts.add_contact(body, db, user)
    return contact


@router.put(
    "/{contact_id}",
    dependencies=[Depends(RateLimiter(times=TIMES_LIMIT, seconds=SECONDS_LIMIT))],
)
async def update_contact(
    body: ContactUpdateSchema,
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contact_updata = await repository_contacts.update_contact(contact_id, body, db, user)
    if contact_updata is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact_updata


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contact = await repository_contacts.delete_contact(contact_id, db, user)
    return contact


# =================================================================================
@router.get(
    "/contacts/all/",
    response_model=list[ContactResponse],
    dependencies=[
        Depends(RateLimiter(times=TIMES_LIMIT, seconds=SECONDS_LIMIT)),
        Depends(access_to_route_am),
    ],
)
async def contacts_all(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contacts = await repository_contacts.get_contacts_all(limit, offset, db, user)
    return contacts


@router.get(
    "/upcoming-birthdays/all",
    response_model=list[ContactResponse],
    dependencies=[
        Depends(RateLimiter(times=TIMES_LIMIT, seconds=SECONDS_LIMIT)),
        Depends(access_to_route_am),
    ],
)
async def upcoming_birthdays_all(
    days: int = Query(7, gt=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contacts = await repository_contacts.get_upcoming_birthdays_all(days, db, user)
    return contacts


@router.get(
    "/search/all",
    response_model=list[ContactResponse],
    dependencies=[
        Depends(RateLimiter(times=TIMES_LIMIT, seconds=SECONDS_LIMIT)),
        Depends(access_to_route_am),
    ],
)
async def search_contacts_all(
    FirstName: Optional[str] = Query(None, description="Contact name to search for"),
    LastName: Optional[str] = Query(None, description="Contact's last name to search for"),
    Email: Optional[str] = Query(None, description="Contact email to search"),
    EmailSec: Optional[str] = Query(None, description="Contact email second to search"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    params = [FirstName, LastName, EmailSec, Email]
    contacts = await repository_contacts.get_search_contacts_all(params, db, user)
    if contacts is None or not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts
