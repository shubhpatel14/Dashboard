from app.database.connection import (
    engine,
    Base
)

from app.database import models



def create_database():


    Base.metadata.create_all(
        bind=engine
    )



if __name__ == "__main__":


    create_database()


    print(
        "TRISHULA DATABASE READY"
    )
