from typing import TypedDict

class Target(TypedDict):
    target_url: str
    job_title: str
    job_location: str

class Result(Target):
    count: int
    date: str
