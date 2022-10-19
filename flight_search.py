import os
from pprint import pprint

import requests

from flight_data import FlightData

TEQUILA_ENDPOINT = os.environ.get("TEQUILA_ENDPOINT")
TEQUILA_API_KEY = os.environ.get("TEQUILA_API_KEY")

class FlightSearch:
    def get_destination_code(self, city):
        location_endpoint = f"{TEQUILA_ENDPOINT}/locations/query"
        headers = {"apiKey": TEQUILA_API_KEY}
        query = {
            "term": city,
            "location_types": "city"
        }
        code_res = requests.get(url=location_endpoint, params=query, headers=headers)
        results = code_res.json()["locations"]
        iata_code = results[0]["code"]
        return iata_code

    def check_flights(self, origin_city_code, destination_city_code, from_time, to_time, stopovers=0):
        headers = { "apiKey": TEQUILA_API_KEY }
        query = {
            "fly_from": origin_city_code,
            "fly_to": destination_city_code,
            "date_from": from_time.strftime("%d/%m/%Y"),
            "date_to": to_time.strftime("%d/%m/%Y"),
            "nights_in_dst_from": 7,
            "nights_in_dst_to": 28,
            "flight_type": "round",
            "one_for_city": 1,
            "max_stopovers": stopovers,
            "curr": "USD"
        }

        search_res = requests.get(
            url=f"{TEQUILA_ENDPOINT}/v2/search",
            headers=headers,
            params=query
        )

        try:
            data = search_res.json()["data"][0]
        except IndexError:
            query["max_stopovers"] = 1
            search_res = requests.get(
                url=f"{TEQUILA_ENDPOINT}/v2/search",
                headers=headers,
                params=query
            )

            try:
                data = search_res.json()["data"][0]
                pprint(data)
            except IndexError:
                return None
            else:
                first_route = data["route"][0]
                second_route = data["route"][1]

                flight_data = FlightData(
                    price=data["price"],
                    origin_city=first_route["cityFrom"],
                    origin_airport=first_route["flyFrom"],
                    destination_city=second_route["cityTo"],
                    destination_airport=second_route["flyTo"],
                    out_date=first_route["local_departure"].split("T")[0],
                    return_date=data["route"][2]["local_departure"].split("T")[0],
                    stopovers=1,
                    via_city=first_route["cityTo"]
                )
                return flight_data
        else:
            first_route = data["route"][0]

            flight_data = FlightData(
                price=data["price"],
                origin_city=first_route["cityFrom"],
                origin_airport=first_route["flyFrom"],
                destination_city=first_route["cityTo"],
                destination_airport=first_route["flyTo"],
                out_date=first_route["local_departure"].split("T")[0],
                return_date=data["route"][1]["local_departure"].split("T")[0]
            )
            return flight_data

