import sys
import os
from typing import List

from job_search_page_analyzers import JobSearchPageAnalyzer
import job_search_page_analyzers
from repository.models import Target, Result
import repository
import file_io
from const import SHOULD_REQUEST_FLAG_STR, SHOULD_REQUEST_WITH_STORE_FLAG_STR, STORE_FILE_NAME_HTML, STORE_FILE_NAME_HEADER_DATE
from models import ScrapeResult, ScrapeRawResult
import scraper
import utils


def main():
    print('Starting scraping...')
    SCRAPE_OPS_ENDPOINT = os.environ['SCRAPE_OPS_ENDPOINT']
    SCRAPE_OPS_API_KEY = os.environ['SCRAPE_OPS_API_KEY']

    should_request = sys.argv[1] == SHOULD_REQUEST_FLAG_STR if len(sys.argv) > 1 else False
    should_request_with_store = sys.argv[1] == SHOULD_REQUEST_WITH_STORE_FLAG_STR if len(sys.argv) > 1 else False

    targets: List[Target] = repository.get_targets()
    print('Got targets...')
    results: List[Result] = []

    for i, target in enumerate(targets):
        print(f"Scraping target {i+1}/{len(targets)}: '{target.url}'...")
        try:
            analyzer = job_search_page_analyzers.create_analyzer(target.url, target.job_title, target.job_location)
            result = scrape(
                should_request=should_request,
                should_request_with_store=should_request_with_store,
                scrape_ops_endpoint=SCRAPE_OPS_ENDPOINT,
                scrape_ops_api_key=SCRAPE_OPS_API_KEY,
                target_url=target.url,
                analyzer=analyzer,
                store_file_name_html=STORE_FILE_NAME_HTML,
                store_file_name_header_date=STORE_FILE_NAME_HEADER_DATE,
            )
            count = result.count
            scrape_date = result.scrape_date
            results.append(Result(url=target.url, job_title=target.job_title, job_location=target.job_location, count=count, scrape_date=scrape_date))
        except Exception as e:
            print(f"Error while scraping target '{target.url}': {str(e)}")

    print('Storing results...')
    repository.store_results(results)
    print('Scraping finished.')

def scrape(
        scrape_ops_endpoint: str,
        scrape_ops_api_key: str,
        target_url: str,
        analyzer: JobSearchPageAnalyzer,
        store_file_name_html: str,
        store_file_name_header_date: str,
        should_request: bool = False,
        should_request_with_store: bool = False,
    ) -> ScrapeResult:
    raw_result = get_raw_result(
        scrape_ops_endpoint=scrape_ops_endpoint,
        scrape_ops_api_key=scrape_ops_api_key,
        target_url=target_url,
        store_file_name_html=store_file_name_html,
        store_file_name_header_date=store_file_name_header_date,
        should_request=should_request,
        should_request_with_store=should_request_with_store,
    )
    html = raw_result.html
    header_date = raw_result.header_date
    analyzer.verify(html)
    count = analyzer.find_count(html)
    return ScrapeResult(count=count, scrape_date=utils.header_date_to_datetime(header_date))

def get_raw_result(
        scrape_ops_endpoint: str,
        scrape_ops_api_key: str,
        target_url: str,
        store_file_name_html: str,
        store_file_name_header_date: str,
        should_request: bool = False,
        should_request_with_store: bool = False
    ) -> ScrapeRawResult:
    """
    If both `should_request` and `should_request_with_store` are `True`, then it has the same effect with when only `should_request_with_store` is True.
    """
    if should_request or should_request_with_store:
        result = scraper.proxy_scrape(target_url, scrape_ops_endpoint, scrape_ops_api_key)
        html = result.html
        header_date = result.header_date

    if should_request_with_store:
        file_io.store_text_as_file(html, store_file_name_html)
        file_io.store_text_as_file(header_date, store_file_name_header_date)

    if not should_request and not should_request_with_store:
        html = file_io.restore_text_from_file(store_file_name_html)
        header_date = file_io.restore_text_from_file(store_file_name_header_date)

    return ScrapeRawResult(html=html, header_date=header_date)


if __name__ == '__main__':
    main()
