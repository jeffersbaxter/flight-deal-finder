from datetime import datetime, timedelta

from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager

flight_search = FlightSearch()
data_manager = DataManager()
notification_manager = NotificationManager()

ORIGIN_CITY_CODE = "SEA"

sheet_data = data_manager.get_sheet_prices()

if sheet_data[0]["iataCode"] == "":
    for row in sheet_data:
        row["iataCode"] = flight_search.get_destination_code(row["city"])
    data_manager.destination_data = sheet_data
    data_manager.update_destination_codes()

destinations = {
    data["iataCode"]: {
        "id": data["id"],
        "city": data["city"],
        "price": data["lowestPrice"]
    } for data in sheet_data}

tomorrow = datetime.now() + timedelta(days=1)
six_months_out = datetime.now() + timedelta(days=(6 * 30))

for destination_code in destinations:
    flight = flight_search.check_flights(
        ORIGIN_CITY_CODE,
        destination_code,
        from_time=tomorrow,
        to_time=six_months_out,
        stopovers=0
    )

    if flight is None:
        continue

    if flight.price < destinations[destination_code]["price"]:

        users = data_manager.get_customer_emails()
        emails = [row["email"] for row in users]
        names = [row["firstName"] for row in users]

        body = f"""Low price alert! Only ${flight.price} to fly from {flight.origin_airport} to {flight.destination_airport}, departing {flight.out_date} and returning {flight.return_date}"""

        if flight.stopovers > 0:
            body += f"\nFlight has {flight.stopovers} stop over, via {flight.via_city}"

        link = f"""https://www.google.com/flights?hl=en#flt={flight.origin_airport}.{flight.destination_airport}.{flight.out_date}*{flight.destination_airport}.{flight.origin_airport}.{flight.return_date}"""

        notification_manager.send_emails(emails, body, link)

        data_manager.update_price(flight.price, destinations[destination_code]["id"])
