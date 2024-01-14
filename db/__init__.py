import os
from sqlalchemy import create_engine


ENV = os.getenv('ENV', 'development')

DB_URL = f'postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}' if ENV == 'production' else 'sqlite:///dev.db'

print(DB_URL)
engine = create_engine(DB_URL)

if ENV == 'development':
    # Make sure the database exists and generate if not exists.
    conn = engine.connect()
    conn.close()
