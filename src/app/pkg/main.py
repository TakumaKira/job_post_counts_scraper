import sys
import os
from typing import List

from job_search_page_analyzers import JobSearchPageAnalyzer, create_analyzer
from repository.models import Target, Result
from repository import get_targets, store_results
from file_io import store_text_as_file, restore_text_from_file
from const import SHOULD_REQUEST_FLAG_STR, SHOULD_REQUEST_WITH_STORE_FLAG_STR, STORE_FILE_NAME_HTML, STORE_FILE_NAME_HEADER_DATE
from models import ScrapeResult
from scraper import proxy_scrape
from utils import header_date_to_datetime


SCRAPE_OPS_ENDPOINT = os.environ['SCRAPE_OPS_ENDPOINT']
SCRAPE_OPS_API_KEY = os.environ['SCRAPE_OPS_API_KEY']


def main():
    should_request = sys.argv[1] == SHOULD_REQUEST_FLAG_STR if len(sys.argv) > 1 else False
    should_request_with_store = sys.argv[1] == SHOULD_REQUEST_WITH_STORE_FLAG_STR if len(sys.argv) > 1 else False

    targets: List[Target] = get_targets()
    results: List[Result] = []

    for target in targets:
        try:
            analyzer = create_analyzer(target['url'], target['job_title'], target['job_location'])
            result = scrape(
                should_request=should_request,
                should_request_with_store=should_request_with_store,
                scrape_ops_endpoint=SCRAPE_OPS_ENDPOINT,
                scrape_ops_api_key=SCRAPE_OPS_API_KEY,
                target_url=target['url'],
                analyzer=analyzer,
                store_file_name_html=STORE_FILE_NAME_HTML,
                store_file_name_header_date=STORE_FILE_NAME_HEADER_DATE,
            )
            count = result['count']
            scrape_date = result['scrape_date']
            results.append({"url": target['url'], "job_title": target['job_title'], "job_location": target['job_location'], "count": count, "scrape_date": scrape_date})
        except Exception as e:
            print(f"Error while scraping target '{target['url']}': {str(e)}")
    store_results(results)

def scrape(
        should_request: bool,
        should_request_with_store: bool,
        scrape_ops_endpoint: str,
        scrape_ops_api_key: str,
        target_url: str,
        analyzer: JobSearchPageAnalyzer,
        store_file_name_html: str,
        store_file_name_header_date: str,
    ) -> ScrapeResult:
    if should_request or should_request_with_store:
        result = proxy_scrape(target_url, scrape_ops_endpoint, scrape_ops_api_key)
        html = result['html']
        header_date = result['header_date']

    if should_request_with_store:
        store_text_as_file(html, store_file_name_html)
        store_text_as_file(header_date, store_file_name_header_date)

    if not should_request and not should_request_with_store:
        html = restore_text_from_file(store_file_name_html)
        header_date = restore_text_from_file(store_file_name_header_date)

    analyzer.verify(html)

    count = analyzer.find_count(html)

    return {"count": count, "scrape_date": header_date_to_datetime(header_date)}


if __name__ == '__main__':
    main()
