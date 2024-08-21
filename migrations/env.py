from alembic import context
from flask import current_app
from logging.config import fileConfig
import os
print("DATABASE_URL:", os.environ.get('DATABASE_URL'))


# this is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Override the sqlalchemy.url setting in Alembic config with the DATABASE_URL from environment
config.set_main_option('sqlalchemy.url', os.environ.get('DATABASE_URL'))


def get_engine():
    try:
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        return current_app.extensions['migrate'].db.engine


def get_metadata():
    return current_app.extensions['migrate'].db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=get_metadata(),
                      literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=get_metadata())

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
