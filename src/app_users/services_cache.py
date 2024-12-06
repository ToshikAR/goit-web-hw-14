import redis
import logging
import pickle

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from src.database.db import get_db
from src.config.config import conf
from src.app_users import repository_users


# Создание клиента Redis async
async def get_redis_client():
    cl_redis = await redis.asyncio.Redis(
        host=conf.REDIS_HOST,
        port=conf.REDIS_PORT,
        db=0,
        password=conf.REDIS_PASSWORD,
    )
    return cl_redis


# Создание клиента Redis
def redis_client():
    cl_redis = redis.Redis(
        host=conf.REDIS_HOST,
        port=conf.REDIS_PORT,
        db=0,
        password=conf.REDIS_PASSWORD,
    )
    return cl_redis


# создаем хешь юзира async ---------------------------------------
async def user_cache(email: str, db: AsyncSession = Depends(get_db)):
    user_hash = email
    try:
        cache = await get_redis_client()
        user = await cache.get(user_hash)
        if user is None:
            print("User from database")
            user = await repository_users.get_user_by_email(email, db)
            await cache.set(user_hash, pickle.dumps(user))
            await cache.expire(user_hash, 300)
        else:
            print("User from cache")
            user = pickle.loads(user)
    except ValueError as err:
        logging.error(f"Cache Error: {err}")
    finally:
        return user


# создаем хешь юзира sync ---------------------------------------
def user_cache_sync(email: str, db: AsyncSession = Depends(get_db)):
    user_hash = email
    cache = redis_client()

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = cache.get(user_hash)
    user = None
    if user is None:
        print("User from database")
        user = repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        cache.set(user_hash, pickle.dumps(user))
        cache.expire(user_hash, 300)
    else:
        print("User from cache")
        user = pickle.loads(user)

    return user
