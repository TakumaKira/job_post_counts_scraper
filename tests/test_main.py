import pytest
from unittest.mock import MagicMock, patch

import sys
import os
from datetime import datetime

from const import STORE_FILE_NAME_HTML, STORE_FILE_NAME_HEADER_DATE
from models import ScrapeRawResult, ScrapeResult, ProxyScrapeResult
import scraper
import file_io
import utils
import repository
from repository import Target, Result
import job_search_page_analyzers
from main import get_raw_result, scrape, main


mock_verify = MagicMock()
mock_find_count = MagicMock()

class MockAnalyzer:
    def verify(self, html):
        return mock_verify(html)

    def find_count(self, html):
        return mock_find_count(html)

class TestMain:
    def setup_class(self):
        self.mock_proxy_scrape = MagicMock()
        self.patch_proxy_scrape = patch.object(scraper, 'proxy_scrape', new_callable=lambda: self.mock_proxy_scrape)
        self.patch_proxy_scrape.start()
        self.mock_store_text_as_file = MagicMock()
        self.patch_store_text_as_file = patch.object(file_io, 'store_text_as_file', new_callable=lambda: self.mock_store_text_as_file)
        self.patch_store_text_as_file.start()
        self.mock_restore_text_from_file = MagicMock()
        self.patch_restore_text_from_file = patch.object(file_io, 'restore_text_from_file', new_callable=lambda: self.mock_restore_text_from_file)
        self.patch_restore_text_from_file.start()
        self.mock_header_date_to_datetime = MagicMock()
        self.patch_header_date_to_datetime = patch.object(utils, 'header_date_to_datetime', new_callable=lambda: self.mock_header_date_to_datetime)
        self.patch_header_date_to_datetime.start()
        self.mock_get_targets = MagicMock()
        self.patch_get_targets = patch.object(repository, 'get_targets', new_callable=lambda: self.mock_get_targets)
        self.patch_get_targets.start()
        self.mock_create_analyzer = MagicMock()
        self.patch_create_analyzer = patch.object(job_search_page_analyzers, 'create_analyzer', new_callable=lambda: self.mock_create_analyzer)
        self.patch_create_analyzer.start()
        self.mock_store_results = MagicMock()
        self.patch_store_results = patch.object(repository, 'store_results', new_callable=lambda: self.mock_store_results)
        self.patch_store_results.start()

    def teardown_class(self):
        self.patch_proxy_scrape.stop()
        self.patch_store_text_as_file.stop()
        self.patch_restore_text_from_file.stop()
        self.patch_header_date_to_datetime.stop()
        self.patch_get_targets.stop()
        self.patch_create_analyzer.stop()
        self.patch_store_results.stop()


    def test_ScrapeRawResult_instance_has_correct_attributes(self):
        scrape_raw_result = ScrapeRawResult(html='html', header_date='header_date')
        assert scrape_raw_result.html == 'html'
        assert scrape_raw_result.header_date == 'header_date'

    def test_ScrapeResult_instance_has_correct_attributes(self):
        scrape_result = ScrapeResult(count=1, scrape_date=datetime(2024, 1, 13, 8, 17, 1))
        assert scrape_result.count == 1
        assert scrape_result.scrape_date == datetime(2024, 1, 13, 8, 17, 1)

    def test_ProxyScrapeResult_instance_has_correct_attributes(self):
        proxy_scrape_result = ProxyScrapeResult(html='html', header_date='header_date')
        assert proxy_scrape_result.html == 'html'
        assert proxy_scrape_result.header_date == 'header_date'

    def test_get_raw_result_calls_proxy_scrape_and_does_not_call_store_text_and_restore_text_from_file_when_passed_should_request_argument(self):
        test_id = 1
        self.mock_proxy_scrape.return_value = ProxyScrapeResult(html=f'html{test_id}', header_date=f'header_date{test_id}')
        raw_result = get_raw_result(
            scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
            scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
            target_url=f'target_url{test_id}',
            store_file_name_html=f'store_file_name_html{test_id}',
            store_file_name_header_date=f'store_file_name_header_date{test_id}',
            should_request=True
        )
        self.mock_proxy_scrape.assert_any_call(f'target_url{test_id}', f'scrape_ops_endpoint{test_id}', f'scrape_ops_api_key{test_id}')
        self.mock_store_text_as_file.assert_not_called()
        self.mock_restore_text_from_file.assert_not_called()
        assert isinstance(raw_result, ScrapeRawResult)
        assert raw_result.html == f'html{test_id}'
        assert raw_result.header_date == f'header_date{test_id}'

    def test_get_raw_result_calls_proxy_scrape_and_store_text_as_file_and_does_not_call_restore_text_from_file_when_passed_should_request_with_store_argument(self):
        test_id = 2
        self.mock_proxy_scrape.return_value = ProxyScrapeResult(html=f'html{test_id}', header_date=f'header_date{test_id}')
        raw_result = get_raw_result(
            scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
            scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
            target_url=f'target_url{test_id}',
            store_file_name_html=f'store_file_name_html{test_id}',
            store_file_name_header_date=f'store_file_name_header_date{test_id}',
            should_request_with_store=True
        )
        self.mock_proxy_scrape.assert_any_call(f'target_url{test_id}', f'scrape_ops_endpoint{test_id}', f'scrape_ops_api_key{test_id}')
        self.mock_store_text_as_file.assert_any_call(f'html{test_id}', f'store_file_name_html{test_id}')
        self.mock_store_text_as_file.assert_any_call(f'header_date{test_id}', f'store_file_name_header_date{test_id}')
        self.mock_restore_text_from_file.assert_not_called()
        assert isinstance(raw_result, ScrapeRawResult)
        assert raw_result.html == f'html{test_id}'
        assert raw_result.header_date == f'header_date{test_id}'

    def test_get_raw_result_calls_proxy_scrape_and_store_text_as_file_and_does_not_call_restore_text_from_file_when_passed_should_request_and_should_request_with_store_argument(self):
        test_id = 3
        self.mock_proxy_scrape.return_value = ProxyScrapeResult(html=f'html{test_id}', header_date=f'header_date{test_id}')
        raw_result = get_raw_result(
            scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
            scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
            target_url=f'target_url{test_id}',
            store_file_name_html=f'store_file_name_html{test_id}',
            store_file_name_header_date=f'store_file_name_header_date{test_id}',
            should_request=True,
            should_request_with_store=True
        )
        self.mock_proxy_scrape.assert_any_call(f'target_url{test_id}', f'scrape_ops_endpoint{test_id}', f'scrape_ops_api_key{test_id}')
        self.mock_store_text_as_file.assert_any_call(f'html{test_id}', f'store_file_name_html{test_id}')
        self.mock_store_text_as_file.assert_any_call(f'header_date{test_id}', f'store_file_name_header_date{test_id}')
        self.mock_restore_text_from_file.assert_not_called()
        assert isinstance(raw_result, ScrapeRawResult)
        assert raw_result.html == f'html{test_id}'
        assert raw_result.header_date == f'header_date{test_id}'

    def test_get_raw_result_does_not_call_proxy_scrape_and_store_text_as_file_and_calls_restore_text_from_file_when_not_passed_should_request_nor_should_request_with_store_argument(self):
        test_id = 4
        self.mock_proxy_scrape.return_value = ProxyScrapeResult(html=f'html{test_id}_false', header_date=f'header_date{test_id}_false')
        self.mock_restore_text_from_file.side_effect = lambda file_name: f'html{test_id}' if file_name == f'store_file_name_html{test_id}' else f'header_date{test_id}'
        raw_result = get_raw_result(
            scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
            scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
            target_url=f'target_url{test_id}',
            store_file_name_html=f'store_file_name_html{test_id}',
            store_file_name_header_date=f'store_file_name_header_date{test_id}'
        )
        with pytest.raises(AssertionError):
            self.mock_proxy_scrape.assert_any_call(f'target_url{test_id}', f'scrape_ops_endpoint{test_id}', f'scrape_ops_api_key{test_id}')
        with pytest.raises(AssertionError):
            self.mock_store_text_as_file.assert_any_call(f'html{test_id}', f'store_file_name_html{test_id}')
        with pytest.raises(AssertionError):
            self.mock_store_text_as_file.assert_any_call(f'header_date{test_id}', f'store_file_name_header_date{test_id}')
        self.mock_restore_text_from_file.assert_any_call(f'store_file_name_html{test_id}')
        self.mock_restore_text_from_file.assert_any_call(f'store_file_name_header_date{test_id}')
        assert isinstance(raw_result, ScrapeRawResult)
        assert raw_result.html == f'html{test_id}'
        assert raw_result.header_date == f'header_date{test_id}'

    def test_scrape_returns_expected_scrape_result_when_html_from_proxy_scrape_is_valid_and_contains_count(self):
        test_id = 5
        mock_get_raw_result = MagicMock(return_value=ScrapeRawResult(html=f'html{test_id}', header_date=f'header_date{test_id}'))
        mock_find_count.return_value = test_id
        self.mock_header_date_to_datetime.return_value = datetime(2024, test_id, test_id, test_id, test_id, test_id)
        mock_analyzer = MockAnalyzer()
        with patch('main.get_raw_result', new_callable=lambda: mock_get_raw_result):
            scrape_result = scrape(
                scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
                scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
                target_url=f'target_url{test_id}',
                analyzer=mock_analyzer,
                store_file_name_html=f'store_file_name_html{test_id}',
                store_file_name_header_date=f'store_file_name_header_date{test_id}',
            )
        mock_get_raw_result.assert_called_with(
            scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
            scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
            target_url=f'target_url{test_id}',
            store_file_name_html=f'store_file_name_html{test_id}',
            store_file_name_header_date=f'store_file_name_header_date{test_id}',
            should_request=False,
            should_request_with_store=False,
        )
        mock_verify.assert_called_with(f'html{test_id}')
        mock_find_count.assert_called_with(f'html{test_id}')
        self.mock_header_date_to_datetime.assert_called_with(f'header_date{test_id}')
        assert scrape_result.count == test_id
        assert scrape_result.scrape_date == datetime(2024, test_id, test_id, test_id, test_id, test_id)

    def test_scrape_raises_exception_when_analyzer_verify_raises_exception(self):
        test_id = 6
        mock_get_raw_result = MagicMock(return_value=ScrapeRawResult(html=f'html{test_id}', header_date=f'header_date{test_id}'))
        mock_verify.side_effect = Exception('Verification failed')
        mock_analyzer = MockAnalyzer()
        with patch('main.get_raw_result', new_callable=lambda: mock_get_raw_result):
            try:
                scrape(
                    scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
                    scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
                    target_url=f'target_url{test_id}',
                    analyzer=mock_analyzer,
                    store_file_name_html=f'store_file_name_html{test_id}',
                    store_file_name_header_date=f'store_file_name_header_date{test_id}',
                )
            except Exception as e:
                assert str(e) == 'Verification failed'
        mock_verify.side_effect = None

    def test_scrape_raises_exception_when_analyzer_find_count_raises_exception(self):
        test_id = 7
        mock_get_raw_result = MagicMock(return_value=ScrapeRawResult(html=f'html{test_id}', header_date=f'header_date{test_id}'))
        mock_find_count.side_effect = Exception('Find count failed')
        mock_analyzer = MockAnalyzer()
        with patch('main.get_raw_result', new_callable=lambda: mock_get_raw_result):
            try:
                scrape(
                    scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
                    scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
                    target_url=f'target_url{test_id}',
                    analyzer=mock_analyzer,
                    store_file_name_html=f'store_file_name_html{test_id}',
                    store_file_name_header_date=f'store_file_name_header_date{test_id}',
                )
            except Exception as e:
                assert str(e) == 'Find count failed'
        mock_find_count.side_effect = None

    def test_scrape_raises_exception_when_header_date_to_datetime_raises_exception(self):
        test_id = 7
        mock_get_raw_result = MagicMock(return_value=ScrapeRawResult(html=f'html{test_id}', header_date=f'header_date{test_id}'))
        mock_find_count.return_value = test_id
        self.mock_header_date_to_datetime.side_effect = Exception('Header date to datetime failed')
        mock_analyzer = MockAnalyzer()
        with patch('main.get_raw_result', new_callable=lambda: mock_get_raw_result):
            try:
                scrape(
                    scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
                    scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
                    target_url=f'target_url{test_id}',
                    analyzer=mock_analyzer,
                    store_file_name_html=f'store_file_name_html{test_id}',
                    store_file_name_header_date=f'store_file_name_header_date{test_id}',
                )
            except Exception as e:
                assert str(e) == 'Header date to datetime failed'
        self.mock_header_date_to_datetime.side_effect = None

    def test_main_store_results_into_database(self, capsys):
        test_id = 8
        self.mock_get_targets.return_value = [
            Target(url=f'target_url{test_id}-1', job_title=f'target_job_title{test_id}-1', job_location=f'target_job_location{test_id}-1'),
            Target(url=f'target_url{test_id}-2', job_title=f'target_job_title{test_id}-2', job_location=f'target_job_location{test_id}-2'),
        ]
        mock_analyzer1 = MockAnalyzer()
        mock_analyzer2 = MockAnalyzer()
        self.mock_create_analyzer.side_effect = [mock_analyzer1, mock_analyzer2]
        mock_scrape = MagicMock()
        mock_scrape.side_effect = [
            ScrapeResult(count=1, scrape_date=datetime(2024, test_id, test_id, test_id, test_id, 1)),
            ScrapeResult(count=2, scrape_date=datetime(2024, test_id, test_id, test_id, test_id, 2)),
        ]
        with patch.dict(
            os.environ, {'SCRAPE_OPS_ENDPOINT': f'scrape_ops_endpoint{test_id}', 'SCRAPE_OPS_API_KEY': f'scrape_ops_api_key{test_id}'}
        ), patch.object(sys, 'argv', ['', 'should_request']), patch('main.scrape', new_callable=lambda: mock_scrape):
            main()
        capsys.readouterr()
        self.mock_create_analyzer.assert_any_call(f'target_url{test_id}-1', f'target_job_title{test_id}-1', f'target_job_location{test_id}-1')
        self.mock_create_analyzer.assert_any_call(f'target_url{test_id}-2', f'target_job_title{test_id}-2', f'target_job_location{test_id}-2')
        mock_scrape.assert_any_call(
            should_request=True,
            should_request_with_store=False,
            scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
            scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
            target_url=f'target_url{test_id}-1',
            analyzer=mock_analyzer1,
            store_file_name_html=STORE_FILE_NAME_HTML,
            store_file_name_header_date=STORE_FILE_NAME_HEADER_DATE,
        )
        mock_scrape.assert_any_call(
            should_request=True,
            should_request_with_store=False,
            scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
            scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
            target_url=f'target_url{test_id}-2',
            analyzer=mock_analyzer2,
            store_file_name_html=STORE_FILE_NAME_HTML,
            store_file_name_header_date=STORE_FILE_NAME_HEADER_DATE,
        )
        self.mock_store_results.assert_called_with([
            Result(url=f'target_url{test_id}-1', job_title=f'target_job_title{test_id}-1', job_location=f'target_job_location{test_id}-1', count=1, scrape_date=datetime(2024, test_id, test_id, test_id, test_id, 1)),
            Result(url=f'target_url{test_id}-2', job_title=f'target_job_title{test_id}-2', job_location=f'target_job_location{test_id}-2', count=2, scrape_date=datetime(2024, test_id, test_id, test_id, test_id, 2)),
        ])

    def test_main_prints_exception_when_given_unsupported_target_url(self, capsys):
        test_id = 9
        self.mock_get_targets.return_value = [
            Target(url=f'target_url{test_id}-1', job_title=f'target_job_title{test_id}-1', job_location=f'target_job_location{test_id}-1'),
            Target(url=f'target_url{test_id}-2', job_title=f'target_job_title{test_id}-2', job_location=f'target_job_location{test_id}-2'),
       ]
        mock_analyzer1 = MockAnalyzer()
        mock_analyzer2 = MockAnalyzer()
        self.mock_create_analyzer.side_effect = [Exception('Unsupported target url'), mock_analyzer2]
        mock_scrape = MagicMock()
        mock_scrape.side_effect = [
            ScrapeResult(count=2, scrape_date=datetime(2024, test_id, test_id, test_id, test_id, 2)),
        ]
        with patch.dict(
            os.environ, {'SCRAPE_OPS_ENDPOINT': f'scrape_ops_endpoint{test_id}', 'SCRAPE_OPS_API_KEY': f'scrape_ops_api_key{test_id}'}
        ), patch.object(sys, 'argv', ['', 'should_request']), patch('main.scrape', new_callable=lambda: mock_scrape):
            main()
        self.mock_create_analyzer.assert_any_call(f'target_url{test_id}-2', f'target_job_title{test_id}-2', f'target_job_location{test_id}-2')
        assert 'Unsupported target url' in capsys.readouterr().out
        with pytest.raises(AssertionError):
            mock_scrape.assert_any_call(
                should_request=True,
                should_request_with_store=False,
                scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
                scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
                target_url=f'target_url{test_id}-1',
                analyzer=mock_analyzer1,
                store_file_name_html=STORE_FILE_NAME_HTML,
                store_file_name_header_date=STORE_FILE_NAME_HEADER_DATE,
            )
        mock_scrape.assert_any_call(
            should_request=True,
            should_request_with_store=False,
            scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
            scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
            target_url=f'target_url{test_id}-2',
            analyzer=mock_analyzer2,
            store_file_name_html=STORE_FILE_NAME_HTML,
            store_file_name_header_date=STORE_FILE_NAME_HEADER_DATE,
        )
        self.mock_store_results.assert_called_with([
            Result(url=f'target_url{test_id}-2', job_title=f'target_job_title{test_id}-2', job_location=f'target_job_location{test_id}-2', count=2, scrape_date=datetime(2024, test_id, test_id, test_id, test_id, 2)),
        ])

    def test_main_prints_exception_when_scrape_raises_exception(self, capsys):
        test_id = 10
        self.mock_get_targets.return_value = [
            Target(url=f'target_url{test_id}-1', job_title=f'target_job_title{test_id}-1', job_location=f'target_job_location{test_id}-1'),
            Target(url=f'target_url{test_id}-2', job_title=f'target_job_title{test_id}-2', job_location=f'target_job_location{test_id}-2'),
        ]
        mock_analyzer1 = MockAnalyzer()
        mock_analyzer2 = MockAnalyzer()
        self.mock_create_analyzer.side_effect = [mock_analyzer1, mock_analyzer2]
        mock_scrape = MagicMock()
        mock_scrape.side_effect = [
            Exception('Scrape failed'),
            ScrapeResult(count=2, scrape_date=datetime(2024, test_id, test_id, test_id, test_id, 2)),
        ]
        with patch.dict(
            os.environ, {'SCRAPE_OPS_ENDPOINT': f'scrape_ops_endpoint{test_id}', 'SCRAPE_OPS_API_KEY': f'scrape_ops_api_key{test_id}'}
        ), patch.object(sys, 'argv', ['', 'should_request']), patch('main.scrape', new_callable=lambda: mock_scrape):
            main()
        self.mock_create_analyzer.assert_any_call(f'target_url{test_id}-1', f'target_job_title{test_id}-1', f'target_job_location{test_id}-1')
        self.mock_create_analyzer.assert_any_call(f'target_url{test_id}-2', f'target_job_title{test_id}-2', f'target_job_location{test_id}-2')
        mock_scrape.assert_any_call(
            should_request=True,
            should_request_with_store=False,
            scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
            scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
            target_url=f'target_url{test_id}-1',
            analyzer=mock_analyzer1,
            store_file_name_html=STORE_FILE_NAME_HTML,
            store_file_name_header_date=STORE_FILE_NAME_HEADER_DATE,
        )
        mock_scrape.assert_any_call(
            should_request=True,
            should_request_with_store=False,
            scrape_ops_endpoint=f'scrape_ops_endpoint{test_id}',
            scrape_ops_api_key=f'scrape_ops_api_key{test_id}',
            target_url=f'target_url{test_id}-2',
            analyzer=mock_analyzer2,
            store_file_name_html=STORE_FILE_NAME_HTML,
            store_file_name_header_date=STORE_FILE_NAME_HEADER_DATE,
        )
        assert 'Scrape failed' in capsys.readouterr().out
        self.mock_store_results.assert_called_with([
            Result(url=f'target_url{test_id}-2', job_title=f'target_job_title{test_id}-2', job_location=f'target_job_location{test_id}-2', count=2, scrape_date=datetime(2024, test_id, test_id, test_id, test_id, 2)),
        ])
