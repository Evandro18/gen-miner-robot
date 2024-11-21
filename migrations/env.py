from logging.config import fileConfig
import os

from openai import BaseModel
from pydantic import Field, StrictStr
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


class ConfigModel(BaseModel):
    DATABASE_HOST: StrictStr = Field(default="", min_length=3, max_length=255)
    DATABASE_NAME: StrictStr = Field(default="", min_length=3, max_length=255)
    DATABASE_USER: StrictStr = Field(default="", min_length=3, max_length=255)
    DATABASE_PASSWORD: StrictStr = Field(default="", min_length=3, max_length=255)
    DATABASE_PORT: int = Field(default=5432)


ConfigEnvs = ConfigModel(
    DATABASE_HOST=os.getenv("DATABASE_HOST", "localhost"),
    DATABASE_NAME=os.getenv("DATABASE_NAME", "postgres"),
    DATABASE_USER=os.getenv("DATABASE_USER", "postgres"),
    DATABASE_PASSWORD=os.getenv("DATABASE_PASSWORD", "postgres"),
    DATABASE_PORT=int(os.getenv("DATABASE_PORT", "5432")),
)
connection_str = f"mssql+pymssql://{ConfigEnvs.DATABASE_USER}:{ConfigEnvs.DATABASE_PASSWORD}@{ConfigEnvs.DATABASE_HOST}/{ConfigEnvs.DATABASE_NAME}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """

    context.configure(
        url=connection_str,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    config_alembic = config.get_section(config.config_ini_section, {})
    config_alembic["sqlalchemy.url"] = connection_str
    connectable = engine_from_config(
        config_alembic,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
