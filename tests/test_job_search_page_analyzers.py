from unittest.mock import patch

from src.app.job_search_page_analyzers import create_analyzer
from src.app.job_search_page_analyzers.glassdoor import GlassdoorJobSearchPageAnalyzer

def test_create_analyzer_returns_glassdoor_analyzer_when_target_url_is_glassdoor():
    target_url = 'https://www.glassdoor.com/Job/ocation-title-jobs-UNKNOWN_STRINGS.htm'
    target_job_title = 'title'
    target_job_location = 'location'

    with patch.object(GlassdoorJobSearchPageAnalyzer, '__init__', return_value=None) as mock_init:
        analyzer = create_analyzer(target_url, target_job_title, target_job_location)

    assert isinstance(analyzer, GlassdoorJobSearchPageAnalyzer)
    mock_init.assert_called_once_with(target_job_title, target_job_location)
