import os
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.fetch_parking import fetch_parking
from utils.process import process_parking_data
from db import model

DB_HOST = str(os.getenv("DB_HOST"))
DB_PORT = str(os.getenv("DB_PORT"))
DB_NAME = str(os.getenv("DB_NAME"))
DB_USERNAME = str(os.getenv("DB_USERNAME"))
DB_PASSWORD = str(os.getenv("DB_PASSWORD"))

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def insert_parking_info(target, connection, **kw):
    # Create a new session.
    Session = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    db = Session()

    data = fetch_parking()
    parkinglot_li = process_parking_data(data)
    parkinglot_models = []
    for p in parkinglot_li:
        parkinglot_models.append(
            model.ParkinglotInfo(
                **{
                    k: v
                    for k, v in p.dict().items()
                    if k in model.ParkinglotInfo.__table__.columns
                }
            )
        )

    db.add_all(parkinglot_models)
    db.commit()

    print("Fetch parkinglot info and save at: ", datetime.now())
