from typing import TypedDict
import datetime

class Target(TypedDict):
    url: str
    job_title: str
    job_location: str

class Result(Target):
    count: int
    scrape_date: datetime
