import contextlib
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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


# print(conf.RENDER_DB_URL)
sessionmanager = DatabaseSessionManager(conf.SQLALCHEMY_DB_URL)
sessionmanager_mysql = DatabaseSessionManager(conf.MYSQ_DB_URL)


async def get_db():
    async with sessionmanager.session() as session:
        yield session


async def get_db_mysql():
    async with sessionmanager_mysql.session() as session_mysql:
        yield session_mysql


# class DatabaseSessionManager:
#     def __init__(self, url: str):
#         self._engine = create_engine(url)
#         self._session_maker = sessionmaker(
#             autoflush=False, autocommit=False, bind=self._engine
#         )

#     @contextlib.contextmanager
#     def session(self):
#         if self._session_maker is None:
#             raise Exception("Session is not initialized")

#         with self._session_maker() as session:
#             try:
#                 yield session
#             except ValueError as err:
#                 session.rollback()
#                 logging.error(f"Database error: {err}")
#                 raise HTTPException(status_code=500, detail="Database error occurred")
#             finally:
#                 session.close()


# # Инициализация менеджеров с использованием синхронного движка
# sessionmanager = DatabaseSessionManager(conf.KOYEB_DB_URL)
# # sessionmanager_mysql = DatabaseSessionManager(conf.MYSQ_DB_URL)


# # Заменяем асинхронный `get_db` на синхронный
# def get_db():
#     with sessionmanager.session() as session:
#         yield session


# # def get_db_mysql():
# #     with sessionmanager_mysql.session() as session_mysql:
# #         yield session_mysql
