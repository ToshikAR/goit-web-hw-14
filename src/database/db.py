import contextlib
import logging

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.config.config import conf


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session is not initialized")

        async with self._session_maker() as session:
            try:
                yield session
            except ValueError as err:
                await session.rollback()
                logging.error(f"Database error: {err}")
                raise HTTPException(status_code=500, detail="Database error occurred")
            finally:
                await session.close()


sessionmanager = DatabaseSessionManager(conf.SQLALCHEMY_DB_URL)
sessionmanager_mysql = DatabaseSessionManager(conf.MYSQ_DB_URL)


async def get_db():
    async with sessionmanager.session() as session:
        yield session


async def get_db_mysql():
    async with sessionmanager_mysql.session() as session_mysql:
        yield session_mysql
