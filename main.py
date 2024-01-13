import sys
import os
import re
from typing import List, TypedDict
import requests
from bs4 import BeautifulSoup


SCRAPE_OPS_ENDPOINT = os.environ['SCRAPE_OPS_ENDPOINT']
SCRAPE_OPS_API_KEY = os.environ['SCRAPE_OPS_API_KEY']

SHOULD_REQUEST_FLAG_STR = 'should_request'
SHOULD_REQUEST_WITH_STORE_FLAG_STR = 'should_request_with_store'

STORE_FILE_NAME = 'content.txt'


class Target(TypedDict):
    target_url: str
    job_title: str
    job_location: str

class Result(Target):
    count: int

class TitleException(Exception):
    pass

class FileException(Exception):
    pass

def main():
    should_request = sys.argv[1] == SHOULD_REQUEST_FLAG_STR if len(sys.argv) > 1 else False
    should_request_with_store = sys.argv[1] == SHOULD_REQUEST_WITH_STORE_FLAG_STR if len(sys.argv) > 1 else False

    targets: List[Target] = get_targets()
    results: List[Result] = []

    for target in targets:
        try:
            count = scrape(
                should_request=should_request,
                should_request_with_store=should_request_with_store,
                scrape_ops_endpoint=SCRAPE_OPS_ENDPOINT,
                scrape_ops_api_key=SCRAPE_OPS_API_KEY,
                target_url=target['url'],
                target_job_title=target['job_title'],
                target_job_location=target['job_location'],
                store_file_name=STORE_FILE_NAME,
            )
            results.append({"target_url": target['url'], "job_title": target['job_title'], "job_location": target['job_location'], "count": count})
        except Exception as e:
            print(f"Error while scraping target '{target['url']}': {str(e)}")
    store(results)

def get_targets() -> List[Target]:
    targets = [
        {
            "url": 'https://www.glassdoor.com/Job/germany-react-jobs-SRCH_IL.0,7_IN96_KO8,13.htm',
            "job_title": 'react',
            "job_location": 'Germany',
        },
    ]
    print(f"TODO: Get targets from database.\n{targets}")
    return targets

def scrape(
        should_request: bool,
        should_request_with_store: bool,
        scrape_ops_endpoint: str,
        scrape_ops_api_key: str,
        target_url: str,
        target_job_title: str,
        target_job_location: str,
        store_file_name: str,
    ):
    if should_request or should_request_with_store:
        html = proxy_scrape(target_url, scrape_ops_endpoint, scrape_ops_api_key)

    if should_request_with_store:
        store_html_as_file(html, store_file_name)

    if not should_request and not should_request_with_store:
        html = restore_html_from_file(store_file_name)

    title = get_page_title(html)

    verify_title(title, target_job_title, target_job_location)

    return extract_number_from_title(title)

def proxy_scrape(target_url: str, scrape_ops_endpoint: str, scrape_ops_api_key: str) -> str:
    response = requests.get(
        url=scrape_ops_endpoint,
        params={
            'api_key': scrape_ops_api_key,
            'url': target_url,
        },
        timeout=120,
    )
    return response.text

def store_html_as_file(html: str, file_name: str):
    with open(file_name, 'w') as file:
        file.write(html)

def restore_html_from_file(file_name: str) -> str:
    try:
        with open(file_name, 'r') as file:
            return file.read()
    except FileNotFoundError:
        raise FileException(f"Stored file does not exist. Please run this function with {SHOULD_REQUEST_WITH_STORE_FLAG_STR} to create it.")

def get_page_title(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    return soup.title.string

def verify_title(title: str, job_title: str, job_location: str):
    """
    Expects input strings like "3,051 react Jobs in Germany, January 2024 | Glassdoor"
    """
    if job_title.lower() not in title.lower() and job_location.lower() not in title.lower():
        raise TitleException(f"Title '{title}' does not include both job title '{job_title}' and job location '{job_location}'.")
    elif job_title.lower() not in title.lower():
        raise TitleException(f"Title '{title}' does not include job title '{job_title}'.")
    elif job_location.lower() not in title.lower():
        raise TitleException(f"Title '{title}' does not include job location '{job_location}'.")
    else:
        pass

def extract_number_from_title(title: str) -> int:
    """
    Expects input strings like "3,051 react Jobs in Germany, January 2024 | Glassdoor"
    """
    match = re.search(r'(\d+(,\d+)*)\s*.*jobs', title, re.IGNORECASE)
    if match:
        return int(match.group(1).replace(',', ''))
    else:
        raise TitleException(f"Title '{title}' does not include job counts.")

def store(results: List[Result]):
    print(f"TODO: Store results in database.\n{results}")


if __name__ == '__main__':
    main()
