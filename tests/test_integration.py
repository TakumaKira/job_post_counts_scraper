from unittest.mock import patch, MagicMock
import os
import sys
import requests
import sqlalchemy
from main import main
from repository.models import Target
import db
from db.models import Result as ResultDB


mock_targets_to_get = [
    Target(url='https://www.glassdoor.com/Job/ocation-title-jobs-UNKNOWN_STRINGS.htm', job_title='react', job_location='germany'),
]
mock_Select = 'Select'
mock_Engine = 'Engine'
mock_MockSession_init = MagicMock(return_value=None)
mock_scalars = MagicMock(return_value=mock_targets_to_get)
mock_add_all = MagicMock(return_value=None)
mock_commit = MagicMock(return_value=None)
mock_select = MagicMock(return_value=mock_Select)
mock_get_engine = MagicMock(return_value=mock_Engine)

class MockSession:
    def __init__(self, engine):
        mock_MockSession_init(engine)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def scalars(self, *args, **kwargs):
        return mock_scalars(*args, **kwargs)

    def add_all(self, *args, **kwargs):
        return mock_add_all(*args, **kwargs)

    def commit(self, *args, **kwargs):
        return mock_commit(*args, **kwargs)

class TestIntegration:
    def setup_class(self):
        self.mock_get = MagicMock()
        self.patch_get = patch.object(requests, 'get', new_callable=lambda: self.mock_get)
        self.patch_get.start()
        self.patch_Session = patch.object(sqlalchemy.orm, 'Session', new_callable=lambda: MockSession)
        self.patch_select = patch.object(sqlalchemy, 'select', new_callable=lambda: mock_select)
        self.patch_get_engine = patch.object(db, 'get_engine', new_callable=lambda: mock_get_engine)
        self.patch_Session.start()
        self.patch_select.start()
        self.patch_get_engine.start()

    def teardown_class(self):
        self.patch_get.stop()
        self.patch_Session.stop()
        self.patch_select.stop()
        self.patch_get_engine.stop()


    def test_app_prints_meaningful_message_when_no_counts_found(self, capsys):
        test_id = 1
        self.mock_get.return_value = type('Response', (object,), {'text': '<html><head><title> react Jobs in Germany, January 2024 | Glassdoor</title></head><body></body></html>', 'headers': {'date': 'Sat, 13 Jan 2024 08:17:01 GMT'}})
        with patch.dict(
            os.environ, {'SCRAPE_OPS_ENDPOINT': f'scrape_ops_endpoint{test_id}', 'SCRAPE_OPS_API_KEY': f'scrape_ops_api_key{test_id}'}
        ):
            main()
        assert 'does not include job counts.' in capsys.readouterr().out
