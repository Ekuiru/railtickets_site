import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'course_project_secret_key')
    DB_NAME = os.getenv('DB_NAME', 'train_tickets')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'admin')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    TESTING = False