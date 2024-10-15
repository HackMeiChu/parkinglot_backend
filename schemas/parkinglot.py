from datetime import date, time

from typing import List
from pydantic import BaseModel, Field


class In_parking_lot_official(BaseModel):
    parkno: str = Field(..., validation_alias="PARKNO")
    parkingname: str = Field(..., validation_alias="PARKINGNAME")
    address: str = Field(..., validation_alias="ADDRESS")
    businesshours: str = Field(..., validation_alias="BUSINESSHOURS")
    weekdays: str = Field(..., validation_alias="WEEKDAYS")
    holiday: str = Field(..., validation_alias="HOLIDAY")
    freequantitybig: int = Field(..., validation_alias="FREEQUANTITYBIG")
    totalquantitybig: int = Field(..., validation_alias="TOTALQUANTITYBIG")
    freequantity: int = Field(..., validation_alias="FREEQUANTITY")
    totalquantity: int = Field(..., validation_alias="TOTALQUANTITY")
    freequantitymot: int = Field(..., validation_alias="FREEQUANTITYMOT")
    totalquantitymot: int = Field(..., validation_alias="TOTALQUANTITYMOT")
    freequantitydis: int = Field(..., validation_alias="FREEQUANTITYDIS")
    totalquantitydis: int = Field(..., validation_alias="TOTALQUANTITYDIS")
    freequantitycw: int = Field(..., validation_alias="FREEQUANTITYCW")
    totalquantitycw: int = Field(..., validation_alias="TOTALQUANTITYCW")
    freequantityecar: int = Field(..., validation_alias="FREEQUANTITYECAR")
    totalquantityecar: int = Field(..., validation_alias="TOTALQUANTITYECAR")
    longitude: str = Field(..., validation_alias="LONGITUDE")
    latitude: str = Field(..., validation_alias="LATITUDE")
    updatetime: str = Field(..., validation_alias="UPDATETIME")


class In_parking_lot_official_all(BaseModel):
    data: List[In_parking_lot_official]


class In_parking_lot(BaseModel):
    name: str
    address: str
    carSpace: str
    motoSpace: str
    chargeFee: str
    lat: str
    lng: str
    update_time: str
    zone: str


class Out_parking_lot(BaseModel):
    name: str
    address: str
    startHour: int
    endHour: int
    carAvail: int
    carTotal: int
    motoAvail: int
    motoTotal: int
    carChargeFeeWeek: int
    carChargeFeeHoli: int
    motoChargeFeeWeek: int
    motoChargeFeeHoli: int
    latitude: str
    longitude: str
    updateDate: date
    updateTime: time
