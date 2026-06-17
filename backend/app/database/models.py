from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime
)

from app.database.connection import Base



class MacroSeries(Base):

    __tablename__ = "macro_series"


    id = Column(
        Integer,
        primary_key=True
    )


    indicator = Column(
        String,
        index=True
    )


    date = Column(
        DateTime,
        index=True
    )


    value = Column(
        Float
    )


    source = Column(
        String
    )
