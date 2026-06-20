from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from urllib.parse import quote_plus


PASSWORD = quote_plus(
    "Shubh@11"
)


DATABASE_URL = (
    f"postgresql://postgres:{PASSWORD}"
    "@localhost:5432/trishula"
)


engine = create_engine(
    DATABASE_URL
)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


Base = declarative_base()