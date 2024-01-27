import os
import sqlalchemy


def get_db_url():
    env = os.getenv('ENV', 'development')
    return f'postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}' if env == 'production' else 'sqlite:///dev.db'

def get_engine():
    return sqlalchemy.create_engine(get_db_url())
