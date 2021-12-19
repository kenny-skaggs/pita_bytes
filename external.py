from contextlib import contextmanager
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Database:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            instance = super(Database, cls).__new__(cls)
            session_factory, engine = cls._build_session_factory()
            instance.session_factory = session_factory
            instance.engine = engine
            cls._instance = instance

        return getattr(cls, '_instance')

    @contextmanager
    def get_new_session(self):
        session = self.session_factory()
        try:
            yield session
            session.commit()
        finally:
            session.close()

    @classmethod
    def _build_session_factory(cls) -> sessionmaker:
        db_user = os.environ.get('DB_USERNAME')
        db_password = os.environ.get('DB_PASSWORD')
        if not (db_user and db_password):
            raise Exception('Database credentials not set')

        engine = create_engine(f'postgresql://{db_user}:{db_password}@localhost:8967/postgres')
        return sessionmaker(bind=engine, expire_on_commit=False), engine
