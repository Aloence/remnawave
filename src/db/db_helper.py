from sqlalchemy.ext.asyncio import create_async_engine

from config import settings

db_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
)
