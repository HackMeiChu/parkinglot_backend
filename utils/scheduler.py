from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from starlette.types import ASGIApp, Receive, Scope, Send

from utils.fetch_parking import fetch_parking
from utils.process import process_parking_data
from utils.db_connect import SessionLocal
from schemas.parkinglog_db import ParkinglotOrigin

from datetime import datetime


# background getting parking data
def get_parking_data():
    db = SessionLocal()
    data = fetch_parking()
    parkinglot_li = process_parking_data(data)
    parkinglot_models = []
    for p in parkinglot_li:
        parkinglot_models.append(ParkinglotOrigin(**p.dict()))

    db.add_all(parkinglot_models)
    db.commit()

    print("Fetch data and save at: ", datetime.now())


class SchedulerMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        scheduler: BackgroundScheduler,
    ) -> None:
        self.app = app
        self.scheduler = scheduler

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async with self.scheduler:
            await self.scheduler.add_job(
                get_parking_data, IntervalTrigger(seconds=1), id="data"
            )
            await self.scheduler.start()
            await self.app(scope, receive, send)
