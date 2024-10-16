from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import event
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers.background import BackgroundScheduler
import os
import sys
from dotenv import load_dotenv
from typing import List

sys.path.append(os.path.dirname(__file__))

# load .env file
load_dotenv()

from db import schema, model
from utils.scheduler import get_parking_data
from utils.db_connect import engine, get_db, insert_parking_info


scheduler = BackgroundScheduler(timezone="Asia/Taipei")
app = FastAPI()


# database
# insert data right after the table creation
event.listen(model.ParkinglotInfo.__table__, "after_create", insert_parking_info)

model.Base.metadata.create_all(bind=engine)


# background
scheduler.add_job(get_parking_data, IntervalTrigger(minutes=1), id="data")


@app.on_event("startup")
async def startup_event():
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


@app.get("/")
async def root(db: Session = Depends(get_db)):
    return {"message": "Hello World"}


@app.get("/jobs")
def get_jobs():
    jobs = scheduler.get_jobs()
    return [{"id": job.id, "next_run_time": job.next_run_time} for job in jobs]


# get parking info
@app.get("/parking", response_model=List[schema.ParkinglotInfo])
def get_parkinglot(db: Session = Depends(get_db)):
    return db.query(model.ParkinglotInfo).all()


# get parking space for specific parking lot
@app.get("/parking/space", response_model=List[schema.ParkinglotInfo])
def get_parkingspace(parking_id: int, db: Session = Depends(get_db)):
    return (
        db.query(model.ParkinglotSpace)
        .filter(model.ParkinglotSpace.parkinglot_id == parking_id)
        .all()
    )
