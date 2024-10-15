import os
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends

sys.path.append(os.path.dirname(__file__))

from utils.db_connect import engine, get_db
from utils.scheduler import get_parking_data
from schemas.parkinglog_db import Base, ParkinglotOrigin

scheduler = BackgroundScheduler(timezone="Asia/Taipei")
app = FastAPI()


# database
Base.metadata.create_all(bind=engine)


# background
scheduler.add_job(
    get_parking_data, IntervalTrigger(minutes=1), id="data"
)


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
