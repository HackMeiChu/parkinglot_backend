import math


def cal_dist(
    source_lat: float, source_lng: float, target_lat: float, target_lng: float
) -> float:
    """
    calculate the distance between the target spot and the parking lot (source)
    """
    return math.sqrt(
        math.pow(source_lat - target_lat, 2) + math.pow(source_lng - target_lng, 2)
    )
