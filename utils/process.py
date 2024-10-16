if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

import re
from datetime import datetime
from typing import Tuple, List

from utils.fetch_parking import fetch_parking
from db import schema


def match_price(charge_des: str, carTotal: int, motoTotal: int) -> Tuple:
    carChargeFee, motoChargeFee = 0, 0

    assert carTotal + motoTotal > 0, "No parking space exist for both car and moto"

    match_str_li = re.findall(r"(\d+)元(?![^()]*\))", charge_des)
    assert len(match_str_li) > 0, "No price information exists"

    if carTotal != 0:
        carChargeFee = match_str_li[0]
    if motoTotal != 0:
        if len(match_str_li) > 1:
            motoChargeFee = match_str_li[-1]
        elif carTotal == 0:
            motoChargeFee = match_str_li[0]

    return carChargeFee, motoChargeFee


def extract_business_hours(hour_str: str) -> Tuple[int]:
    # check if is 24H
    if len(re.findall(r"24H", hour_str)) > 0:
        return 0, 24

    # capture the start and the end hours
    hours = re.findall(r"(\d{2}):\d{2}", hour_str)
    assert len(hours) == 2, "Should only have start and end hours"

    return int(hours[0]), int(hours[1])


def extract_date_time(dateTime: str) -> Tuple[datetime.date, datetime.time]:

    try:
        parsed_datetime = datetime.strptime(dateTime, "%Y-%m-%dT%H:%M:%S.%f")
    except:
        parsed_datetime = datetime.strptime(dateTime, "%Y-%m-%dT%H:%M:%S")

    date = parsed_datetime.date()
    time = parsed_datetime.time().replace(second=0, microsecond=0)

    return date, time


def transform_each_data(source: schema.In_parking_lot_official) -> schema.Out_parking_lot:
    # process charge fee for weekdays and holidays
    carChargeFeeWeek = 0
    carChargeFeeHoli = 0
    motoChargeFeeWeek = 0
    motoChargeFeeHoli = 0

    carChargeFeeWeek, motoChargeFeeWeek = match_price(
        source.weekdays, source.totalquantity, source.totalquantitymot
    )
    carChargeFeeHoli, motoChargeFeeHoli = match_price(
        source.holiday, source.totalquantity, source.totalquantitymot
    )

    date, time = extract_date_time(source.updatetime)
    startHour, endHour = extract_business_hours(source.businesshours)

    out = schema.Out_parking_lot(
        name=source.parkingname,
        address=source.address,
        startHour=startHour,
        endHour=endHour,
        carAvail=source.freequantity,
        carTotal=source.totalquantity,
        motoAvail=source.freequantitymot,
        motoTotal=source.totalquantitymot,
        carChargeFeeWeek=carChargeFeeWeek,
        carChargeFeeHoli=carChargeFeeHoli,
        motoChargeFeeWeek=motoChargeFeeWeek,
        motoChargeFeeHoli=motoChargeFeeHoli,
        latitude=source.latitude,
        longitude=source.longitude,
        updateDate=date,
        updateTime=time,
    )

    return out


def process_parking_data(
    source_data: schema.In_parking_lot_official_all,
) -> List[schema.Out_parking_lot]:

    out_li = []
    for source_datum in source_data.data:
        out_li.append(transform_each_data(source_datum))

    return out_li


if __name__ == "__main__":
    # test things out
    data = fetch_parking()
    print(process_parking_data(data)[0])
