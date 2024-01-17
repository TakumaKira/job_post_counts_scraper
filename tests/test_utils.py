import datetime

import src.app.utils as utils


def test_header_date_to_datetime():
    header_date = 'Sat, 13 Jan 2024 08:17:01 GMT'
    expected_datetime = datetime.datetime(2024, 1, 13, 8, 17, 1)
    actual_datetime = utils.header_date_to_datetime(header_date)
    assert actual_datetime == expected_datetime
