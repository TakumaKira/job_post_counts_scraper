from unittest.mock import patch

from job_search_page_analyzers import create_analyzer
from job_search_page_analyzers.glassdoor import GlassdoorJobSearchPageAnalyzer


class TestCreateAnalyzer:
    def test_create_analyzer_returns_glassdoor_analyzer_when_target_url_is_glassdoor(self):
        target_url = 'https://www.glassdoor.com/Job/ocation-title-jobs-UNKNOWN_STRINGS.htm'
        target_job_title = 'title'
        target_job_location = 'location'

        with patch.object(GlassdoorJobSearchPageAnalyzer, '__init__', return_value=None) as mock_init:
            analyzer = create_analyzer(target_url, target_job_title, target_job_location)

        assert isinstance(analyzer, GlassdoorJobSearchPageAnalyzer)
        mock_init.assert_called_once_with(target_job_title, target_job_location)

    def test_create_analyzer_throws_when_target_url_is_unknown(self):
        target_url = 'https://www.unknown.com/Job/ocation-title-jobs-UNKNOWN_STRINGS.htm'
        target_job_title = 'title'
        target_job_location = 'location'

        try:
            create_analyzer(target_url, target_job_title, target_job_location)
        except Exception as e:
            assert target_url in str(e)
        else:
            assert False
