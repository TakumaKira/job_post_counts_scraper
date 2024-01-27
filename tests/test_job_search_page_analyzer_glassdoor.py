from unittest.mock import patch

from job_search_page_analyzers.glassdoor import GlassdoorJobSearchPageAnalyzer


class TestGlassdoorJobSearchPageAnalyzerVerify:
    def test_GlassdoorJobSearchPageAnalyzer_verifies_valid_html(self):
        target_job_title = 'react'
        target_job_location = 'germany'
        analyzer = GlassdoorJobSearchPageAnalyzer(target_job_title=target_job_title, target_job_location=target_job_location)
        try:
            analyzer.verify('<html><head><title>3,051 react Jobs in Germany, January 2024 | Glassdoor</title></head><body></body></html>')
        except Exception as e:
            assert False, f"Exception raised: {e}"

    def test_GlassdoorJobSearchPageAnalyzer_raise_exception_when_missing_job_title_in_html_title(self):
        target_job_title = 'react'
        target_job_location = 'germany'
        analyzer = GlassdoorJobSearchPageAnalyzer(target_job_title=target_job_title, target_job_location=target_job_location)
        try:
            analyzer.verify('<html><head><title>3,051  Jobs in Germany, January 2024 | Glassdoor</title></head><body></body></html>')
        except Exception as e:
            assert target_job_title in str(e)

    def test_GlassdoorJobSearchPageAnalyzer_raise_exception_when_missing_job_location_in_html_title(self):
        target_job_title = 'react'
        target_job_location = 'germany'
        analyzer = GlassdoorJobSearchPageAnalyzer(target_job_title=target_job_title, target_job_location=target_job_location)
        try:
            analyzer.verify('<html><head><title>3,051 react Jobs in , January 2024 | Glassdoor</title></head><body></body></html>')
        except Exception as e:
            assert target_job_location in str(e)

    def test_GlassdoorJobSearchPageAnalyzer_raise_exception_when_missing_job_title_and_job_location_in_html_title(self):
        target_job_title = 'react'
        target_job_location = 'germany'
        analyzer = GlassdoorJobSearchPageAnalyzer(target_job_title=target_job_title, target_job_location=target_job_location)
        try:
            analyzer.verify('<html><head><title>3,051  Jobs in , January 2024 | Glassdoor</title></head><body></body></html>')
        except Exception as e:
            assert target_job_title in str(e)
            assert target_job_location in str(e)

class TestGlassdoorJobSearchPageAnalyzerFindCount:
    def test_GlassdoorJobSearchPageAnalyzer_returns_count_when_valid_html(self):
        target_job_title = 'react'
        target_job_location = 'germany'
        analyzer = GlassdoorJobSearchPageAnalyzer(target_job_title=target_job_title, target_job_location=target_job_location)
        count = analyzer.find_count('<html><head><title>3,051 react Jobs in Germany, January 2024 | Glassdoor</title></head><body></body></html>')
        assert count == 3051

    def test_GlassdoorJobSearchPageAnalyzer_throws_when_count_was_not_found_in_html_title(self):
        target_job_title = 'react'
        target_job_location = 'germany'
        html_title = ' react Jobs in Germany, January 2024 | Glassdoor'
        analyzer = GlassdoorJobSearchPageAnalyzer(target_job_title=target_job_title, target_job_location=target_job_location)
        try:
            analyzer.find_count(f"<html><head><title>{html_title}</title></head><body></body></html>")
        except Exception as e:
            assert html_title in str(e)
        else:
            assert False
