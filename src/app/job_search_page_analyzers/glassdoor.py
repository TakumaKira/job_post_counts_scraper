import re

from bs4 import BeautifulSoup

from exceptions import TitleException
from job_search_page_analyzers import JobSearchPageAnalyzer


class GlassdoorJobSearchPageAnalyzer(JobSearchPageAnalyzer):
    def __init__(self, target_job_title: str, target_job_location: str):
        self.title = None
        self.target_job_title = target_job_title
        self.target_job_location = target_job_location

    def verify(self, html: str):
        self.verify_title(self.get_page_title(html))

    def find_count(self, html: str) -> int:
        return self.extract_number_from_title(self.get_page_title(html))


    def verify_title(self, title: str):
        """
        Expects title is something like "3,051 react Jobs in Germany, January 2024 | Glassdoor"
        """
        if self.target_job_title.lower() not in title.lower() and self.target_job_location.lower() not in title.lower():
            raise TitleException(f"Title '{title}' does not include both job title '{self.target_job_title}' and job location '{self.target_job_location}'.")
        elif self.target_job_title.lower() not in title.lower():
            raise TitleException(f"Title '{title}' does not include job title '{self.target_job_title}'.")
        elif self.target_job_location.lower() not in title.lower():
            raise TitleException(f"Title '{title}' does not include job location '{self.target_job_location}'.")
        else:
            pass

    def extract_number_from_title(self, title: str) -> int:
        """
        Expects input strings like "3,051 react Jobs in Germany, January 2024 | Glassdoor"
        """
        match = re.search(r'(\d+(,\d+)*)\s*.*jobs', title, re.IGNORECASE)
        if match:
            return int(match.group(1).replace(',', ''))
        else:
            raise TitleException(f"Title '{title}' does not include job counts.")

    def get_page_title(self, html: str) -> str:
        if self.title:
            return self.title
        soup = BeautifulSoup(html, 'html.parser')
        self.title = soup.title.string
        return self.title
