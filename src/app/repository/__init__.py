from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from db import engine
from db.models import Result as ResultDB, Target as TargetDB
from repository.models import Target, Result


def get_targets() -> List[Target]:
    targets: List[Target] = []
    with Session(engine) as session:
        raw_targets = session.scalars(select(TargetDB))
        for raw_target in raw_targets:
          targets.append({
              "url": raw_target.url,
              "job_title": raw_target.job_title,
              "job_location": raw_target.job_location,
          })
    return targets

def store_results(results: List[Result]):
    results_for_db: List[ResultDB] = []
    for result in results:
        results_for_db.append(ResultDB(
            url=result["url"],
            job_title=result["job_title"],
            job_location=result["job_location"],
            scrape_date=result["scrape_date"],
            count=result["count"],
        ))
    with Session(engine) as session:
        session.add_all(results_for_db)
        session.commit()
