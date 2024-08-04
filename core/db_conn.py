import psycopg2
from psycopg2.extras import RealDictCursor


def connect():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database='fastapi',
            user='postgres',
            password='',
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        # print("DB connection successfully")
        return conn, cursor
    except Exception as err:
        print("DB connection failed with error: ", err)
