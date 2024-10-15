if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

from sqlalchemy import Column, Integer, String, Date, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ParkinglotOrigin(Base):
    __tablename__ = "parkinglotOrigin"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    startHour = Column(Integer, nullable=False)
    endHour = Column(Integer, nullable=False)
    carAvail = Column(Integer, nullable=False)
    carTotal = Column(Integer, nullable=False)
    motoAvail = Column(Integer, nullable=False)
    motoTotal = Column(Integer, nullable=False)
    carChargeFeeWeek = Column(Integer, nullable=False)
    carChargeFeeHoli = Column(Integer, nullable=False)
    motoChargeFeeWeek = Column(Integer, nullable=False)
    motoChargeFeeHoli = Column(Integer, nullable=False)
    latitude = Column(String, nullable=False)
    longitude = Column(String, nullable=False)
    updateDate = Column(Date, nullable=False)
    updateTime = Column(Time, nullable=False)
