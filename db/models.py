from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    pass

class Target(Base):
    __tablename__ = "targets"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String)
    job_title: Mapped[str] = mapped_column(String)
    job_location: Mapped[str] = mapped_column(String)
    def __repr__(self) -> str:
        return f"Target(id={self.id!r}, url={self.url!r}, job_title={self.job_title!r}, job_location={self.job_location!r})"

class Result(Base):
    __tablename__ = "results"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String)
    job_title: Mapped[str] = mapped_column(String)
    job_location: Mapped[str] = mapped_column(String)
    scrape_date: Mapped[str] = mapped_column(DateTime)
    count: Mapped[int] = mapped_column(Integer)
    def __repr__(self) -> str:
        return f"Result(id={self.id!r}, url={self.url!r}, job_title={self.job_title!r}, job_location={self.job_location!r}, scrape_date={self.scrape_date!r}, count={self.count!r})"
