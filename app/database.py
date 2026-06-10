from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Numeric, func
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

Base = declarative_base()

SQLALCHEMY_DATABASE_URL = 'sqlite:///./movies.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Session = SessionLocal
