import sys
import os
import re
import requests
from bs4 import BeautifulSoup


SCRAPE_OPS_ENDPOINT = os.environ['SCRAPE_OPS_ENDPOINT']
SCRAPE_OPS_API_KEY = os.environ['SCRAPE_OPS_API_KEY']

TARGET_URL = os.environ['TARGET_URL']
TARGET_JOB_TITLE = os.environ['TARGET_JOB_TITLE']
TARGET_JOB_LOCATION = os.environ['TARGET_JOB_LOCATION']

SHOULD_REQUEST_FLAG_STR = 'should_request'
SHOULD_REQUEST_WITH_STORE_FLAG_STR = 'should_request_with_store'

STORE_FILE_NAME = 'content.txt'


class TitleException(Exception):
    pass

class FileException(Exception):
    pass

def main():
    should_request = sys.argv[1] == SHOULD_REQUEST_FLAG_STR if len(sys.argv) > 1 else False
    should_request_with_store = sys.argv[1] == SHOULD_REQUEST_WITH_STORE_FLAG_STR if len(sys.argv) > 1 else False

    if should_request or should_request_with_store:
        html = proxy_scrape(TARGET_URL, SCRAPE_OPS_ENDPOINT, SCRAPE_OPS_API_KEY)

    if should_request_with_store:
        store_html_as_file(html, STORE_FILE_NAME)

    if not should_request and not should_request_with_store:
        html = restore_html_from_file(STORE_FILE_NAME)

    title = get_page_title(html)

    verify_title(title, TARGET_JOB_TITLE, TARGET_JOB_LOCATION)

    result = extract_number_from_title(title)

    store(TARGET_URL, TARGET_JOB_TITLE, TARGET_JOB_LOCATION, result)

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

def store(target_url: str, target_job_title: str, target_job_location: str, result: int):
    print(f"TODO: Store result '{result}' with TARGET_URL '{target_url}', TARGET_JOB_TITLE '{target_job_title}', TARGET_JOB_LOCATION '{target_job_location}' in database.")


if __name__ == '__main__':
    main()
