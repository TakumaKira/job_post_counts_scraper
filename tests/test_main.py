import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from models import ScrapeRawResult, ScrapeResult, ProxyScrapeResult
import scraper
import file_io
import utils
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

    def teardown_class(self):
        self.patch_proxy_scrape.stop()
        self.patch_store_text_as_file.stop()
        self.patch_restore_text_from_file.stop()
        self.patch_header_date_to_datetime.stop()


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

    def test_main_prints_exception_when_given_unsupported_target_url(self):
        pass

    def test_main_prints_exception_when_scrape_raises_exception(self):
        pass

    def test_main_store_results_into_database(self):
        pass

    # Integration tests for expected scenarios

    def test_main_prints_meaningful_message_when_scrape_results_has_minor_problem(self):
        pass
