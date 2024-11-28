from datetime import datetime, timezone
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.app_users.shemas_user import ChangePassword, UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    stmt = select(User).filter_by(email=email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    new_user = User(**body.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    user.refresh_token = token
    await db.commit()
    await db.refresh(user)
    return user


async def visit_user(user: User, db: AsyncSession = Depends(get_db)):
    user.last_visit = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_token(user: User, db: AsyncSession = Depends(get_db)):
    user.refresh_token = None
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as err:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update the user")


# ------------------- email если подтвердил ------------------------------------
async def confirmed_email(email: str, db: AsyncSession):
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()
    await db.refresh(user)
    return user


# ------------------------------------------------------------------------------
async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user


# async def reset_password(email: str, db: AsyncSession) -> None:
#     user = await get_user_by_email(email, db)
#     user.password = "3333"
#     await db.commit()


async def change_password(body: ChangePassword, db: AsyncSession):
    user = await get_user_by_email(body.email, db)
    user.password = body.password
    await db.commit()
    await db.refresh(user)
    return user
