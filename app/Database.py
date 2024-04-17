import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DBNAME = "typingtestDB"
USER = "typingtestadmin"
PASSWORD = "nutballs"
HOST = "localhost"

def init_db(name=DBNAME):
    conn = psycopg2.connect(dbname='postgres', user=USER, password=PASSWORD, host=HOST)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute(f'CREATE DATABASE "{name}"')
    conn.close()

    conn, cursor = open_connection(name)
    with open("./sql/TABLES.sql", 'r') as file:
        query = sql.SQL(file.read())
        cursor.execute(query)
    conn.commit()
    conn.close()

def drop_db(confirm=False, name=DBNAME):
    if confirm:
        conn = psycopg2.connect(dbname='postgres', user=USER, password=PASSWORD, host=HOST)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(f'DROP DATABASE "{name}"')
        conn.close()

def open_connection(name=DBNAME):
    conn = psycopg2.connect(dbname=name, user=USER, password=PASSWORD, host=HOST)
    cursor = conn.cursor()
    return conn, cursor

def run_query(query):
    conn, cursor = open_connection()
    cursor.execute(query)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    try:
        init_db()
    except Exception:
        conn, cursor = open_connection(DBNAME)
        with open("./sql/TABLES.sql", 'r') as file:
            query = sql.SQL(file.read())
            cursor.execute(query)
        conn.commit()
        conn.close()

