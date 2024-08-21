import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from flask import current_app

# This is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging. This sets up loggers.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Set the SQLAlchemy database URL from the current Flask app configuration.
# This ensures that the migrations use the correct database URL provided by Heroku.
config.set_main_option(
    'sqlalchemy.url', current_app.config.get('SQLALCHEMY_DATABASE_URI')
)

# The target_metadata is required for 'autogenerate' support.
# This pulls the metadata from the current app's SQLAlchemy extension.
target_metadata = current_app.extensions['migrate'].db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.
    This configures the context with just a URL and not an Engine.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.
    In this scenario, we create an Engine and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    try:
        # Attempt to connect to the database and run the migrations.
        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata
            )

            with context.begin_transaction():
                context.run_migrations()
    except Exception as e:
        # Log the error if the connection to the database fails.
        logger.error(f"Error connecting to the database: {e}")
        raise e


# Determine if the migrations should run in offline or online mode.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
