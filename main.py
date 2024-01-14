import sys
import os
from typing import List, TypedDict
import requests

from job_search_page_analyzers import JobSearchPageAnalyzer, create_analyzer
from exceptions import FileException
from repository.models import Target, Result
from repository import get_targets, store_results


SCRAPE_OPS_ENDPOINT = os.environ['SCRAPE_OPS_ENDPOINT']
SCRAPE_OPS_API_KEY = os.environ['SCRAPE_OPS_API_KEY']

SHOULD_REQUEST_FLAG_STR = 'should_request'
SHOULD_REQUEST_WITH_STORE_FLAG_STR = 'should_request_with_store'

STORE_FILE_NAME_HTML = 'content.txt'
STORE_FILE_NAME_DATE = 'date.txt'


class ScrapeResult(TypedDict):
    count: int
    date: str

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
                store_file_name_date=STORE_FILE_NAME_DATE,
            )
            count = result['count']
            date = result['date']
            results.append({"target_url": target['url'], "job_title": target['job_title'], "job_location": target['job_location'], "count": count, "date": date})
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
        store_file_name_date: str,
    ) -> ScrapeResult:
    if should_request or should_request_with_store:
        result = proxy_scrape(target_url, scrape_ops_endpoint, scrape_ops_api_key)
        html = result['html']
        date = result['date']

    if should_request_with_store:
        store_text_as_file(html, store_file_name_html)
        store_text_as_file(date, store_file_name_date)

    if not should_request and not should_request_with_store:
        html = restore_text_from_file(store_file_name_html)
        date = restore_text_from_file(store_file_name_date)

    analyzer.verify(html)

    count = analyzer.find_count(html)

    return {"count": count, "date": date}

def proxy_scrape(target_url: str, scrape_ops_endpoint: str, scrape_ops_api_key: str) -> str:
    response = requests.get(
        url=scrape_ops_endpoint,
        params={
            'api_key': scrape_ops_api_key,
            'url': target_url,
        },
        timeout=120,
    )
    return {
        "html": response.text,
        "date": response.headers.get('date'), # Sat, 13 Jan 2024 08:17:01 GMT
    }

def store_text_as_file(html: str, file_name: str):
    with open(file_name, 'w') as file:
        file.write(html)

def restore_text_from_file(file_name: str) -> str:
    try:
        with open(file_name, 'r') as file:
            return file.read()
    except FileNotFoundError:
        raise FileException(f"Stored file does not exist. Please run this function with {SHOULD_REQUEST_WITH_STORE_FLAG_STR} to create it.")


if __name__ == '__main__':
    main()
