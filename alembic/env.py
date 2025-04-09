import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool


from app.config.database import engine
from app.config.database import Base
from app.models import (
    Mission, ordre_mission, financement, hebergement, ligne_budgetaire,
    rapport_mission, remboursement, justificatif, voyage
)

config = context.config

# Configure logging from .ini file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the metadata for 'autogenerate'
target_metadata = Base.metadata

# Offline migrations (just emit SQL)
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Online migrations (execute against DB)
async def run_migrations_online() -> None:
    connectable: AsyncEngine = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=NullPool,
    )

    async with connectable.connect() as connection:
        def do_run_migrations(connection):
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
            )
            with context.begin_transaction():
                context.run_migrations()

        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
