from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session, aliased
from sqlalchemy import event, func
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from typing import List

from db import schema, model
from utils.scheduler import get_parking_data
from utils.db_connect import engine, get_db, insert_parking_info
from utils.nearby import cal_dist
from utils.prediction import pred_spaces_change


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
@app.get("/parking/space/{parking_id}", response_model=List[schema.ParkinglotSpace])
def get_parkingspace(parking_id: int, db: Session = Depends(get_db)):
    return (
        db.query(model.ParkinglotSpace)
        .filter(model.ParkinglotSpace.parkinglot_id == parking_id)
        .all()
    )


# get parking space for specific parking lot
@app.get(
    "/parking/space/{parking_id}/latest",
    summary="get latest space for one id",
    response_model=schema.ParkinglotSpace,
)
def get_each_latest_parkingspace(parking_id: int, db: Session = Depends(get_db)):
    return (
        db.query(model.ParkinglotSpace)
        .filter(model.ParkinglotSpace.parkinglot_id == parking_id)
        .order_by(
            model.ParkinglotSpace.updateDate.desc(),
            model.ParkinglotSpace.updateTime.desc(),
        )
        .first()
    )


# get parking space for specific parking lot
@app.get(
    "/parking/space",
    summary="get all latest space",
    response_model=List[schema.ParkinglotSpace],
)
def get_all_latest_parkingspace(db: Session = Depends(get_db)):
    """
    get the latest data for all parkinglots
    """
    subquery = db.query(
        model.ParkinglotSpace,
        func.row_number()
        .over(
            partition_by=model.ParkinglotSpace.parkinglot_id,
            order_by=(
                model.ParkinglotSpace.updateDate.desc(),
                model.ParkinglotSpace.updateTime.desc(),
            ),
        )
        .label("row_number"),
    ).subquery()

    # Alias the subquery for easier referencing
    aliased_parkinglot_space = aliased(model.ParkinglotSpace, subquery)

    return db.query(aliased_parkinglot_space).filter(subquery.c.row_number == 1).all()


# return nearby parking lot by given lat and lng
@app.get(
    "/parking/nearby",
    summary="get all nearby parking space",
    response_model=List[schema.ParkinglotSpace],
)
def get_nearby_parkinglot_space(lat: float, lng: float, db: Session = Depends(get_db)):
    """
    Provide the latitude(lat) and longitude(lng) of the site
    get the space of the parking lot within 500m (0.005 for lat and lng)
    for testing: lat: 24.807, lng: 120.969783
    """
    distance: float = 0.005  # 500m
    min_lat, max_lat = lat - distance, lat + distance
    min_lng, max_lng = lng - distance, lng + distance

    # get all parking lots
    nearby_parkinglot = (
        db.query(model.ParkinglotInfo)
        .filter(
            model.ParkinglotInfo.latitude >= min_lat,
            model.ParkinglotInfo.latitude <= max_lat,
            model.ParkinglotInfo.longitude >= min_lng,
            model.ParkinglotInfo.longitude <= max_lng,
        )
        .all()
    )

    # calculate their distance
    id_dist_dict: dict = {
        x.id: cal_dist(x.latitude, x.longitude, lat, lng) for x in nearby_parkinglot
    }

    sorted_id_li = [
        k for k, _ in sorted(id_dist_dict.items(), key=lambda item: item[1])
    ]

    # get the latest space info of the nearby parkinglot
    subquery = db.query(
        model.ParkinglotSpace,
        func.row_number()
        .over(
            partition_by=model.ParkinglotSpace.parkinglot_id,
            order_by=(
                model.ParkinglotSpace.updateDate.desc(),
                model.ParkinglotSpace.updateTime.desc(),
            ),
        )
        .label("row_number"),
    ).subquery()

    # Alias the subquery for easier referencing
    aliased_parkinglot_space = aliased(model.ParkinglotSpace, subquery)

    nearby_space = (
        db.query(aliased_parkinglot_space)
        .filter(subquery.c.row_number == 1, subquery.c.parkinglot_id.in_(sorted_id_li))
        .all()
    )

    id_space_dict = {x.parkinglot_id: x for x in nearby_space}
    print(id_space_dict)

    return [id_space_dict[i] for i in sorted_id_li]


@app.get(
    "/parking/predict",
    summary="get parking info (including predicted space) for the parking lot near target",
    response_model=List[schema.ParkinglotSpacePredict],
)
def get_nearby_parkinglot_space(lat: float, lng: float, minutes: int, db: Session = Depends(get_db)):
    """
    Provide the latitude(lat) and longitude(lng) of the site and the time (minutes)
    to reach the spot. Get the info and the predicted space for the nearby parking lot
    (within 500m)

    for testing: lat: 24.807, lng: 120.969783
    """
    distance: float = 0.005  # 500m
    min_lat, max_lat = lat - distance, lat + distance
    min_lng, max_lng = lng - distance, lng + distance

    # get all parking lots
    nearby_parkinglot = (
        db.query(model.ParkinglotInfo)
        .filter(
            model.ParkinglotInfo.latitude >= min_lat,
            model.ParkinglotInfo.latitude <= max_lat,
            model.ParkinglotInfo.longitude >= min_lng,
            model.ParkinglotInfo.longitude <= max_lng,
        )
        .all()
    )

    # calculate their distance
    id_dist_dict: dict = {
        x.id: cal_dist(x.latitude, x.longitude, lat, lng) for x in nearby_parkinglot
    }

    sorted_id_li = [
        k for k, _ in sorted(id_dist_dict.items(), key=lambda item: item[1])
    ]

    # get the latest space info of the nearby parkinglot
    subquery = db.query(
        model.ParkinglotSpace,
        func.row_number()
        .over(
            partition_by=model.ParkinglotSpace.parkinglot_id,
            order_by=(
                model.ParkinglotSpace.updateDate.desc(),
                model.ParkinglotSpace.updateTime.desc(),
            ),
        )
        .label("row_number"),
    ).subquery()

    # Alias the subquery for easier referencing
    aliased_parkinglot_space = aliased(model.ParkinglotSpace, subquery)

    nearby_space_li = (
        db.query(aliased_parkinglot_space)
        .filter(subquery.c.row_number == 1, subquery.c.parkinglot_id.in_(sorted_id_li))
        .all()
    )


    pred_parkinglot_li = []
    for curr_p in nearby_space_li:
        pred_change = pred_spaces_change(curr_p.parkinglot_id, minutes)

        p_dict = {k: v for k, v in curr_p.__dict__.items() if k in curr_p.__table__.columns}
        p_dict["carAvailPred"] = max(curr_p.carAvail - pred_change, 0)
        p_dict["motoAvailPred"] = curr_p.motoAvail
        pred_parkinglot = schema.ParkinglotSpacePredict(**p_dict)

        pred_parkinglot_li.append(pred_parkinglot)

    id_space_dict = {x.parkinglot_id: x for x in pred_parkinglot_li}

    return [id_space_dict[i] for i in sorted_id_li]
