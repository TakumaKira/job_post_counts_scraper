import os
import sqlalchemy
from unittest.mock import patch, MagicMock
from db import get_db_url, get_engine
import aws_secrets_manager_connector


class TestDB:
    def setup_class(self):
        self.mock_create_engine = MagicMock()
        self.patch_create_engine = patch.object(sqlalchemy, 'create_engine', new_callable=lambda: self.mock_create_engine)
        self.patch_create_engine.start()
        self.mock_get_secrets = MagicMock()
        self.patch_get_secrets = patch.object(aws_secrets_manager_connector, 'get_secrets', new_callable=lambda: self.mock_get_secrets)
        self.patch_get_secrets.start()

    def teardown_class(self):
        self.patch_create_engine.stop()
        self.patch_get_secrets.stop()


    @patch.dict(os.environ, {"ENV": "production", "DB_USER": "user", "DB_PASS": "pass", "DB_HOST": "host", "DB_PORT": "5432", "DB_NAME": "db"}, clear=True)
    def test_get_db_url_returns_correct_in_production(self):
        assert get_db_url() == 'postgresql://user:pass@host:5432/db'

    def test_get_db_url_returns_correct_in_development(self):
        assert get_db_url() == 'sqlite:///dev.db'

    @patch.dict(os.environ, {"FUNCTION_ENVIRONMENT": "aws_lambda", "AWS_RDS_PROXY_SECRET_NAME": "aws/secret/name", "AWS_REGION": "aws-region", "AWS_RDS_PROXY_HOST": "rds.proxy.host"})
    def test_get_db_url_returns_correct_in_aws_lambda_environment(self):
        self.mock_get_secrets.return_value = {'username': 'user', 'password': 'pass', 'port': '5432', 'dbname': 'db'}
        assert get_db_url() == 'postgresql://user:pass@rds.proxy.host:5432/db'
        self.mock_get_secrets.assert_called_with('aws/secret/name', 'aws-region')

    @patch.dict(os.environ, {"ENV": "production", "DB_USER": "user", "DB_PASS": "pass", "DB_HOST": "host", "DB_PORT": "5432", "DB_NAME": "db"}, clear=True)
    def test_create_engine_called_with_correct_url_in_production(self):
        get_engine()
        self.mock_create_engine.assert_called_with('postgresql://user:pass@host:5432/db')

    def test_create_engine_called_with_correct_url_in_development(self):
        get_engine()
        self.mock_create_engine.assert_called_with('sqlite:///dev.db')
