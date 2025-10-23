import os
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read environment variables
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def get_engine_for_db(database_name=None):
    """Create an SQLAlchemy engine for a specific database (or none)."""
    db_url = (
        f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/"
        f"{database_name if database_name else ''}?auth_plugin=mysql_native_password"
    )
    try:
        engine = create_engine(db_url, pool_pre_ping=True, echo=False)
        logging.debug(f"✅ Engine created for DB: {database_name or 'no specific DB'}")
        return engine
    except Exception as e:
        logging.error(f"❌ Error creating engine: {e}")
        raise


def test_connection():
    """Check if database connection works."""
    try:
        with get_engine_for_db(MYSQL_DATABASE).connect() as connection:
            logging.info("✅ Database connected successfully.")
    except Exception as e:
        logging.error(f"❌ Connection failed: {e}")
        raise


def list_databases():
    """Return list of all databases."""
    try:
        engine = get_engine_for_db()
        with engine.connect() as connection:
            result = connection.execute(text("SHOW DATABASES;"))
            databases = [row[0] for row in result.fetchall()]
        return databases
    except Exception as e:
        logging.error(f"❌ Error listing databases: {e}")
        return []


def list_tables(database_name):
    """Return list of tables in the given database."""
    try:
        engine = get_engine_for_db(database_name)
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES;"))
            tables = [row[0] for row in result.fetchall()]
        return tables
    except Exception as e:
        logging.error(f"❌ Error listing tables for {database_name}: {e}")
        return []


def list_columns(database_name, table_name):
    """Return list of columns for a given table."""
    try:
        engine = get_engine_for_db(database_name)
        query = text(f"SHOW COLUMNS FROM `{table_name}`;")
        with engine.connect() as connection:
            result = connection.execute(query)
            columns = [row[0] for row in result.fetchall()]
        return columns
    except Exception as e:
        logging.error(f"❌ Error listing columns for {database_name}.{table_name}: {e}")
        return []


def get_schema():
    """Return schema (table → [columns]) for current MYSQL_DATABASE."""
    try:
        engine = get_engine_for_db(MYSQL_DATABASE)
        query = text("""
            SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = :database;
        """)
        with engine.connect() as connection:
            result = connection.execute(query, {"database": MYSQL_DATABASE})
            schema_info = result.fetchall()

        schema_dict = {}
        for table, column, dtype in schema_info:
            schema_dict.setdefault(table, []).append(f"{column} ({dtype})")

        return schema_dict

    except Exception as e:
        logging.error(f"❌ Error retrieving schema: {e}")
        return {}


# ✅ Test manually
if __name__ == "__main__":
    test_connection()
    print("Databases:", list_databases())
    if MYSQL_DATABASE:
        print("Tables:", list_tables(MYSQL_DATABASE))
        print("Schema:", get_schema())
