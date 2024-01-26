from typing import TypedDict
import datetime
from dataclasses import dataclass


@dataclass
class Target:
    url: str
    job_title: str
    job_location: str

@dataclass
class Result(Target):
    count: int
    scrape_date: datetime
