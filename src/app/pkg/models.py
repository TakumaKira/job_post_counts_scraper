from typing import TypedDict
from datetime import datetime


class ScrapeResult(TypedDict):
    count: int
    scrape_date: datetime

class ProxyScrapeResult(TypedDict):
    html: str
    header_date: str
