from typing import List
from sqlalchemy.orm import Session
from .models import Target, Result
from db import engine

def get_targets() -> List[Target]:
    raw_targets = [
        {
            "url": 'https://www.glassdoor.com/Job/germany-react-jobs-SRCH_IL.0,7_IN96_KO8,13.htm',
            "job_title": 'react',
            "job_location": 'Germany',
        },
    ]
    print(f"TODO: Get targets from database.\n{raw_targets}")
    with Session(engine) as session:
        print(session)
    targets = raw_targets # TODO: Convert raw_targets to targets
    return targets

def store_results(results: List[Result]):
    results_for_db = results # TODO: Convert results to results_for_db
    print(f"TODO: Store results in database.\n{results_for_db}")
