import atexit
from contextlib import contextmanager
from enum import Enum
import os
from sshtunnel import SSHTunnelForwarder

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Environment(Enum):
    PROD = 1
    DEV = 2


CURRENT_ENV = Environment.PROD


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

        local_postgres_port = 5432
        if CURRENT_ENV == Environment.DEV:
            tunnel = SshTunnelFactory().start_tunnel()
            local_postgres_port = tunnel.local_bind_port

        engine = create_engine(f'postgresql://{db_user}:{db_password}@localhost:{local_postgres_port}/postgres')
        return sessionmaker(bind=engine, expire_on_commit=False), engine


class SshTunnelFactory:
    def __init__(self):
        self.remote_host = '127.0.0.1'
        self.remote_port = 5432
        self.ssh_host = os.environ.get('SSH_HOST')
        self.ssh_port = 22
        self.ssh_username = os.environ.get('SSH_USERNAME')
        self.ssh_pem_file = os.environ.get('SSH_KEY_FILE')
        if not (self.ssh_host and self.ssh_username and self.ssh_pem_file):
            raise Exception('SSH credentials not set')

    def start_tunnel(self):
        tunnel = SSHTunnelForwarder(
            ssh_address_or_host=(self.ssh_host, self.ssh_port),
            ssh_username=self.ssh_username,
            ssh_pkey=self.ssh_pem_file,
            remote_bind_address=(self.remote_host, self.remote_port)
        )
        tunnel.start()
        atexit.register(tunnel.stop)

        return tunnel
