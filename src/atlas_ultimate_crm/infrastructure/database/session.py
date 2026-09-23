from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker


class SessionFactory:
    def __init__(self, engine: Engine) -> None:
        self._factory = sessionmaker(bind=engine, expire_on_commit=False)

    def __call__(self) -> Session:
        return self._factory()
