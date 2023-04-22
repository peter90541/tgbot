import psycopg2
from typing import List, Optional, Tuple
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST


def create_db_conn() -> psycopg2.extensions.connection:
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn


def insert_into_db(connc: psycopg2.extensions.connection, table_name: str, column_names: List[str], values: Tuple) -> None:
    try:
        cur = connc.cursor()
        query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({', '.join(['%s' for _ in values])})"
        cur.execute(query, values)
        connc.commit()
        cur.close()
    except Exception as e:
        print(e)


def get_last_values_from_db(connc: psycopg2.extensions.connection, table_name: str, column_names: List[str]) -> Optional[Tuple]:
    try:
        cur = connc.cursor()
        query = f"SELECT {', '.join(column_names)} FROM {table_name} ORDER BY api_id DESC LIMIT 1"
        cur.execute(query)
        row = cur.fetchone()
        cur.close()
        return tuple(row)
    except Exception as e:
        print(e)
        return None
