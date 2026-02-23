from contextlib import asynccontextmanager
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

ISOLATION_LEVEL = Literal[
    "READ COMMITTED",
    "SERIALIZABLE",
]


class BaseRepository:
    def __init__(self, db_engine: AsyncEngine):
        self._db_engine = db_engine

    def async_session_maker(
        self,
        autoflush: bool = False,
        autocommit: bool = False,
        expire_on_commit: bool = False,
        isolation_level: ISOLATION_LEVEL = "READ COMMITTED",
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=self._db_engine.execution_options(isolation_level=isolation_level),
            autoflush=autoflush,
            autocommit=autocommit,
            expire_on_commit=expire_on_commit,
        )

    @asynccontextmanager
    async def session(self):
        async with self.async_session_maker().begin() as session:
            yield session
