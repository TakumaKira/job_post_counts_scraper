from unittest.mock import patch, MagicMock
import sqlalchemy.orm
from repository import get_targets, store_results
import db
from repository.models import Target
from db.models import Result as ResultDB


mock_targets_to_get = [
    Target(url='url1', job_title='job_title1', job_location='job_location1'),
    Target(url='url2', job_title='job_title2', job_location='job_location2'),
]
mock_results_to_store = [
    ResultDB(url='url1', job_title='job_title1', job_location='job_location1', count=1, scrape_date='scrape_date1'),
    ResultDB(url='url2', job_title='job_title2', job_location='job_location2', count=2, scrape_date='scrape_date2'),
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

class TestRepository:
    def setup_class(self):
        self.patch_Session = patch.object(sqlalchemy.orm, 'Session', new_callable=lambda: MockSession)
        self.patch_select = patch.object(sqlalchemy, 'select', new_callable=lambda: mock_select)
        self.patch_get_engine = patch.object(db, 'get_engine', new_callable=lambda: mock_get_engine)
        self.patch_Session.start()
        self.patch_select.start()
        self.patch_get_engine.start()

    def teardown_class(self):
        self.patch_Session.stop()
        self.patch_select.stop()
        self.patch_get_engine.stop()

    def test_get_targets_returns_targets(self):
        targets = get_targets()
        assert targets == mock_targets_to_get

    def test_store_results_stores_results(self):
        store_results(mock_results_to_store)
        calls = mock_add_all.call_args_list
        for result_index in range(len(mock_results_to_store)):
            for prop in vars(mock_results_to_store[result_index]):
                if prop == '_sa_instance_state':
                    continue
                assert getattr(calls[0][0][0][result_index], prop) == getattr(mock_results_to_store[result_index], prop)
