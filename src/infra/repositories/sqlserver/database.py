from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from src.config.env import ConfigEnvs

Base = declarative_base()


class Database:

    _session_local: sessionmaker

    def __init__(self):
        url = f"mssql+pymssql://{ConfigEnvs.DATABASE_USER}:{ConfigEnvs.DATABASE_PASSWORD}@{ConfigEnvs.DATABASE_HOST}/{ConfigEnvs.DATABASE_NAME}"
        engine = create_engine(url=url)
        self._session_local = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )

        Base.metadata.create_all(engine)

    def get_session(self) -> Session:
        return next(self.create_session())

    def create_session(self) -> Generator[Any, Any, Session | None]:
        db: Session = self._session_local()
        try:
            yield db
        finally:
            db.close()

    def close(self):
        self._session_local.close_all()
