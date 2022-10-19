import os
import requests

SHEETY_USERS_ENDPOINT = os.environ.get("SHEETY_USERS_ENDPOINT")
SHEET_ID = os.environ.get("SHEET_ID")

if SHEET_ID:
    SHEETS_API = f"https://api.sheety.co/{SHEET_ID}/flightDeals/prices/"
else:
    raise Exception("Sheety API requires a sheet id for requests")


class DataManager:

    def __init__(self):
        self.destination_data = {}
        self.customer_data = []

    def get_customer_emails(self):
        users_res = requests.get(url=SHEETY_USERS_ENDPOINT)
        data = users_res.json()
        self.customer_data = data["users"]
        return self.customer_data

    def get_sheet_prices(self):
        get_sheet_res = requests.get(url=SHEETS_API)
        get_sheet_res.raise_for_status()
        json = get_sheet_res.json()
        self.destination_data = json["prices"]
        return self.destination_data

    def update_destination_codes(self):
        for city in self.destination_data:
            new_data = {
                "price": {
                    "iataCode": city["iataCode"]
                }
            }
            put_res = requests.put(url=f"{SHEETS_API}/{city['id']}", json=new_data)
            put_res.raise_for_status()

    def update_price(self, price, row_id):
        new_data = {
            "price": {
                "lowestPrice": price
            }
        }
        put_res = requests.put(url=f"{SHEETS_API}/{row_id}", json=new_data)
        put_res.raise_for_status()
