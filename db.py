import psycopg2


def db_connection():
    """ function to open connection """
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='ghostStories',
        user='flask',
        password='flask'
    )
    return conn
