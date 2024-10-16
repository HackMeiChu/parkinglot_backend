if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))


import requests

from db import schema


# URL of the JSON data
url_official = "https://hispark.hccg.gov.tw/OpenData/GetParkInfo?1111104155049"
url = "https://ocam.live/c_hsinchu_city_parkinglots.json"


def fetch_parking() -> schema.In_parking_lot_official_all:
    try:
        response = requests.get(url_official)
        response.raise_for_status()

        data = response.json()

        # Print or process the data as needed

        parkinglot_info = schema.In_parking_lot_official_all.model_validate({"data": data})

        return parkinglot_info

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Other error occurred: {err}")


if __name__ == "__main__":
    fetch_parking()

