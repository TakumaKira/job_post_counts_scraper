from datetime import datetime

def header_date_to_datetime(header_date: str) -> datetime:
    return datetime.strptime(header_date, "%a, %d %b %Y %H:%M:%S %Z")
