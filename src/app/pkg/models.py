from datetime import datetime
from dataclasses import dataclass


@dataclass
class ScrapeRawResult:
    html: str
    header_date: str

@dataclass
class ScrapeResult:
    count: int
    scrape_date: datetime

@dataclass
class ProxyScrapeResult:
    html: str
    header_date: str
