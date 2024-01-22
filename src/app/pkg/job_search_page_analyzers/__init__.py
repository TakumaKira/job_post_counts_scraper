from abc import ABC, abstractmethod
import re


class JobSearchPageAnalyzer(ABC):
    @abstractmethod
    def verify(self, html:str):
        pass

    @abstractmethod
    def find_count(self, html: str) -> int:
        pass

def create_analyzer(target_url: str, target_job_title: str, target_job_location: str) -> JobSearchPageAnalyzer:
    is_glassdoor = re.match(r"^https://www\.glassdoor\.com/Job/", target_url)
    if is_glassdoor:
        from job_search_page_analyzers.glassdoor import GlassdoorJobSearchPageAnalyzer
        return GlassdoorJobSearchPageAnalyzer(target_job_title, target_job_location)
    else:
        raise Exception(f"Unsupported target URL: {target_url}")
