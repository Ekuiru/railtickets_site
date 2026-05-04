import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app


def get_connection():
    return psycopg2.connect(
        dbname=current_app.config['DB_NAME'],
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PASSWORD'],
        host=current_app.config['DB_HOST'],
        port=current_app.config['DB_PORT'],
        cursor_factory=RealDictCursor
    )