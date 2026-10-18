
import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# Loads database settings from the project's .env file.
load_dotenv(override=True)


@pytest.fixture
def db_engine():
    # Builds the database URL using the connection settings.
    db_url = (
        f"postgresql+psycopg2://{os.getenv('username')}:"
        f"{os.getenv('password')}@{os.getenv('host')}:"
        f"{os.getenv('port')}/{os.getenv('database')}"
    )

    # Creates an engine for connecting to PostgreSQL.
    engine = create_engine(db_url)

    try:
        # Makes the engine available to the test.
        yield engine
    finally:
        # Closes the engine's connections after the test.
        engine.dispose()


def test_pipeline_table_row_counts(db_engine):
    # Expected row counts from the last successful pipeline run.
    expected_counts = {
        "customers": 793,
        "locations": 632,
        "products": 1894,
        "orders": 9994,
    }

    # Opens a database connection and checks each table.
    with db_engine.connect() as conn:
        for table, expected_count in expected_counts.items():

            # Counts the records without changing the table.
            result = conn.execute(
                text(f'SELECT COUNT(*) FROM "{table}"')
            ).scalar_one()

            # Fails the test if the actual count is incorrect.
            assert result == expected_count, (
                f"{table} has {result} rows; expected {expected_count}"
            )
