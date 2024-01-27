from unittest.mock import patch, MagicMock
import requests
from scraper import proxy_scrape
from models import ProxyScrapeResult


class TestScraper:
    def setup_class(self):
        self.mock_get = MagicMock(return_value=type('Response', (object,), {'text': 'html', 'headers': {'date': 'header_date'}}))
        self.patch_get = patch.object(requests, 'get', new_callable=lambda: self.mock_get)
        self.patch_get.start()

    def teardown_class(self):
        self.patch_get.stop()


    def test_proxy_scrape_returns_correct_ProxyScrapeResult_instance(self):
        result = proxy_scrape('target_url', 'scrape_ops_endpoint', 'scrape_ops_api_key')
        self.mock_get.assert_called_with(url='scrape_ops_endpoint', params={'api_key': 'scrape_ops_api_key', 'url': 'target_url'}, timeout=120)
        assert isinstance(result, ProxyScrapeResult)
        assert result.html == 'html'
        assert result.header_date == 'header_date'
