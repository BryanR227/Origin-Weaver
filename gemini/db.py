import os

from psycopg2 import pool

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("Warning: DATABASE_URL is not set. Add your Tiger connection string to .env")

# Tiger Cloud requires SSL. Include ?sslmode=require in your DATABASE_URL
# (Tiger's own connection strings already include this by default).
connection_pool = pool.SimpleConnectionPool(1, 10, dsn=DATABASE_URL)


def get_connection():
    return connection_pool.getconn()


def put_connection(conn):
    connection_pool.putconn(conn)
