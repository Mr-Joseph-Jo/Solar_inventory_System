import mysql.connector
from mysql.connector import pooling
from flask import g
from config import DB_CONFIG

# One pool shared across all threads — connections are reused, not recreated
_pool = pooling.MySQLConnectionPool(
    pool_name="solar_pool",
    pool_size=10,           # tune to your expected concurrency
    pool_reset_session=True,
    **DB_CONFIG
)


def get_db():
    """Return the connection for this request, creating it once if needed."""
    if "db" not in g:
        g.db = _pool.get_connection()
    return g.db


def close_db(e=None):
    """Return the connection to the pool at the end of every request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()  # returns to pool, does not actually disconnect
