from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from starlette.types import ASGIApp, Receive, Scope, Send

from utils.fetch_parking import fetch_parking
from utils.process import process_parking_data
from utils.db_connect import SessionLocal
from db import model

from datetime import datetime


# background getting parking data
def get_parking_data():
    db = SessionLocal()
    data = fetch_parking()
    parkinglot_li = process_parking_data(data)
    parkinglot_models = []
    for p in parkinglot_li:
        # get parkinglot id
        parking_id = db.query(model.ParkinglotInfo).filter(model.ParkinglotInfo.name == p.name).first().id
        p_dict = p.dict()
        p_dict["parkinglot_id"] = parking_id
        parkinglot_models.append(
            model.ParkinglotSpace(
                **{
                    k: v
                    for k, v in p_dict.items()
                    if k in model.ParkinglotSpace.__table__.columns
                }
            )
        )
    print(parkinglot_models[0].parkinglot_id)

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
