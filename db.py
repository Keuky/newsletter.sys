import psycopg2
import psycopg2.extras
from config import DB_SETTINGS

def get_connection():
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        return conn
    except Exception as e:
        print("=== DATABASE CONNECTION ERROR ===")
        print(e)
        return None


def fetch(query, params=None):
    conn = get_connection()
    if conn is None:
        return []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    finally:
        conn.close()


def execute(query, params=None):
    conn = get_connection()
    if conn is None:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            conn.commit()
            return True
    except Exception as e:
        print("=== EXECUTE ERROR ===")
        print(e)
        conn.rollback()
        return False
    finally:
        conn.close()