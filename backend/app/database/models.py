from sqlalchemy import (
    Column,
    Date,
    Integer,
    String,
    Float,
    DateTime,
    UniqueConstraint,
    func
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


class EconomicSurprise(Base):

    __tablename__ = "economic_surprises"

    __table_args__ = (
        UniqueConstraint(
            "category",
            "event_name",
            "release_date",
            name="uq_economic_surprises_release"
        ),
    )

    id = Column(
        Integer,
        primary_key=True
    )

    category = Column(
        String,
        index=True,
        nullable=False
    )

    event_name = Column(
        String,
        index=True,
        nullable=False
    )

    actual = Column(
        Float,
        nullable=False
    )

    forecast = Column(
        Float,
        nullable=False
    )

    previous = Column(
        Float,
        nullable=False
    )

    surprise = Column(
        Float,
        nullable=False
    )

    score = Column(
        Float,
        nullable=False
    )

    bias = Column(
        String,
        nullable=False
    )

    release_date = Column(
        Date,
        index=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
