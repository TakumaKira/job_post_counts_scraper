import os
import sqlalchemy
import aws_secrets_manager_connector


def get_db_url():
    if os.getenv('FUNCTION_ENVIRONMENT') == 'aws_lambda':
        secrets = aws_secrets_manager_connector.get_secrets(os.environ['AWS_RDS_PROXY_SECRET_NAME'], os.environ['AWS_REGION'])
        return f"postgresql+psycopg2://{secrets['username']}:{secrets['password']}@{os.environ['AWS_RDS_PROXY_HOST']}:{secrets['port']}/{secrets['dbname']}?sslmode=require"
    if os.getenv('ENV') == 'production':
        return f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
    return 'sqlite:///dev.db'

def get_engine():
    return sqlalchemy.create_engine(get_db_url())
