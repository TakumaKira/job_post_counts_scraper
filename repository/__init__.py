from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import Target, Result
from db import engine
from db.models import Target as TargetDB

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
    results_for_db = results # TODO: Convert results to results_for_db
    print(f"TODO: Store results in database.\n{results_for_db}")
