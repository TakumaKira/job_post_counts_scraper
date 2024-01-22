import os
import sqlalchemy
from unittest.mock import patch, MagicMock
from db import get_db_url, get_engine


class TestDB:
    def setup_class(self):
        self.mock_create_engine = MagicMock()
        self.patch_create_engine = patch.object(sqlalchemy, 'create_engine', new_callable=lambda: self.mock_create_engine)
        self.patch_create_engine.start()

    @patch.dict(os.environ, {"ENV": "production", "DB_USER": "user", "DB_PASS": "pass", "DB_HOST": "host", "DB_PORT": "5432", "DB_NAME": "db"}, clear=True)
    def test_get_db_url_returns_correct_in_production(self):
        assert get_db_url() == 'postgresql://user:pass@host:5432/db'

    def test_get_db_url_returns_correct_in_development(self):
        assert get_db_url() == 'sqlite:///dev.db'

    @patch.dict(os.environ, {"ENV": "production", "DB_USER": "user", "DB_PASS": "pass", "DB_HOST": "host", "DB_PORT": "5432", "DB_NAME": "db"}, clear=True)
    def test_create_engine_called_with_correct_url_in_production(self):
        get_engine()
        self.mock_create_engine.assert_called_with('postgresql://user:pass@host:5432/db')

    def test_create_engine_called_with_correct_url_in_development(self):
        get_engine()
        self.mock_create_engine.assert_called_with('sqlite:///dev.db')

    def teardown_class(self):
        self.patch_create_engine.stop()
