import sys
import os
from typing import List

from job_search_page_analyzers import JobSearchPageAnalyzer
import job_search_page_analyzers
from repository.models import Target, Result
import repository
import file_io
from const import NO_REQUEST_FLAG_STR, STORE_RESULTS_FLAG_STR, STORE_FILE_NAME_HTML, STORE_FILE_NAME_HEADER_DATE
from models import ScrapeResult, ScrapeRawResult
import scraper
import utils
import aws_secrets_manager_connector


def main(*args):
    print('Starting scraping...')
    SCRAPE_OPS_ENDPOINT = os.environ['SCRAPE_OPS_ENDPOINT']
    if os.getenv('FUNCTION_ENVIRONMENT') == 'aws_lambda':
        secrets = aws_secrets_manager_connector.get_secrets(os.environ['AWS_API_KEYS_SECRET_NAME'], os.environ['AWS_REGION'])
        SCRAPE_OPS_API_KEY = secrets['SCRAPE_OPS_API_KEY']
    else:
        SCRAPE_OPS_API_KEY = os.environ['SCRAPE_OPS_API_KEY']

    no_request = sys.argv[1] == NO_REQUEST_FLAG_STR if len(sys.argv) > 1 else False
    store_results = sys.argv[1] == STORE_RESULTS_FLAG_STR if len(sys.argv) > 1 else False

    print('Getting targets...')
    targets: List[Target] = repository.get_targets()
    print(targets)
    print('Got targets...')
    results: List[Result] = []

    for i, target in enumerate(targets):
        print(f"Scraping target {i+1}/{len(targets)}: '{target.url}'...")
        try:
            analyzer = job_search_page_analyzers.create_analyzer(target.url, target.job_title, target.job_location)
            result = scrape(
                no_request=no_request,
                store_results=store_results,
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
        no_request: bool = False,
        store_results: bool = False,
    ) -> ScrapeResult:
    raw_result = get_raw_result(
        scrape_ops_endpoint=scrape_ops_endpoint,
        scrape_ops_api_key=scrape_ops_api_key,
        target_url=target_url,
        store_file_name_html=store_file_name_html,
        store_file_name_header_date=store_file_name_header_date,
        no_request=no_request,
        store_results=store_results,
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
        no_request: bool = False,
        store_results: bool = False
    ) -> ScrapeRawResult:
    """
    If both `no_request` is `False` and `store_results` is `True`, then it has the same effect with when only `store_results` is True.
    """
    if not no_request or store_results:
        result = scraper.proxy_scrape(target_url, scrape_ops_endpoint, scrape_ops_api_key)
        html = result.html
        header_date = result.header_date

    if not no_request and store_results:
        file_io.store_text_as_file(html, store_file_name_html)
        file_io.store_text_as_file(header_date, store_file_name_header_date)

    if no_request and not store_results:
        html = file_io.restore_text_from_file(store_file_name_html)
        header_date = file_io.restore_text_from_file(store_file_name_header_date)

    return ScrapeRawResult(html=html, header_date=header_date)


if __name__ == '__main__':
    main()
