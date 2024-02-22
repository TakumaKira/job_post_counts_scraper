import requests
from models import ProxyScrapeResult


def proxy_scrape(target_url: str, scrape_ops_endpoint: str, scrape_ops_api_key: str) -> ProxyScrapeResult:
    print('Sending scrape request...')
    print(f"target_url: {target_url}")
    print(f"scrape_ops_endpoint: {scrape_ops_endpoint}")
    print(f"scrape_ops_api_key: {scrape_ops_api_key}")
    response = requests.get(
        url=scrape_ops_endpoint,
        params={
            'api_key': scrape_ops_api_key,
            'url': target_url,
        },
        timeout=120,
    )
    print('Got response.')
    return ProxyScrapeResult(
        html=response.text,
        header_date=response.headers.get('date'), # Sat, 13 Jan 2024 08:17:01 GMT
    )
