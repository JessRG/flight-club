from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import requests_cache
from pprint import pprint
from datetime import datetime, timedelta
from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import find_cheapest_flight
from notification_manager import NotificationManager
import calendar

# Use this function to help calculate appropriate month, year, and day if not using relativedelta
def calculate_month_year_day(base_datetime, months_to_add):
    """
        Calculates a new datetime shifted by a specific number of calendar months.

        This function adjusts the year, month, and day safely, clamping the
        resulting day to the maximum valid calendar day of the target month
        (e.g., handles leap years and shorter months) while preserving the
        original time components.

        Args:
            base_datetime (datetime): The starting datetime object.
            months_to_add (int): The number of months to advance (can be negative).

        Returns:
            datetime: A new datetime object formatted identically to datetime.now().
        """
    month = base_datetime.month - 1 + months_to_add
    year = base_datetime.year + month // 12
    month = month % 12 + 1

    # monthrange returns a tuple: (day_of_week, num_days_in_month)
    _, max_days = calendar.monthrange(year, month)

    # Returns either the original day, or sets it to 28/29/30/31
    safe_day = min(base_datetime.day, max_days)
    return base_datetime.replace(year=year, month=month, day=safe_day)


# ==================== Conserve requests and preserve your free plan ====================
requests_cache.install_cache(
    "flight_cache",
    urls_expire_after={
        "*.sheety.co*": requests_cache.DO_NOT_CACHE,
        "*": 3600,
    }
)
# ==================== Setup ====================
data_manager = DataManager()
sheet_data = data_manager.get_destination_data()
# pprint(sheet_data)
customer_data = data_manager.get_customer_emails()
customer_email_list = [row.get("whatIsYourEmail?") for row in customer_data]
# pprint(f"Your email list includes {customer_email_list}")
flight_search = FlightSearch()
# Create an instance of the NotificationManager
notification_manager = NotificationManager()

# ==================== Set the Dates and Origin Airport ====================
six_month_from_today = calculate_month_year_day(datetime.now(), 6)
vacation_days = timedelta(days=12)
ORIGIN_CITY_IATA = "LHR"  # London Heathrow

# ==================== Find Cheap Flights ====================

for destination in sheet_data:
    pprint(f"Getting direct flights for {destination['city']}...")
    flights = flight_search.check_flights(
        ORIGIN_CITY_IATA,
        destination["iataCode"],
        from_time=six_month_from_today,
        to_time=six_month_from_today + vacation_days,
    )
    cheapest_flight = find_cheapest_flight(flights, return_date=six_month_from_today.strftime("%Y-%m-%d"))

    if cheapest_flight.price == "N/A":
        pprint(f"No direct flight to {destination['city']}. Looking for indirect flights...")
        flights = flight_search.check_flights(
            ORIGIN_CITY_IATA,
            destination["iataCode"],
            from_time=six_month_from_today,
            to_time=six_month_from_today + vacation_days,
            is_direct = False,
        )
        cheapest_flight = find_cheapest_flight(flights, return_date=six_month_from_today.strftime("%Y-%m-%d"))
    pprint(f"{destination['city']}: USD {cheapest_flight.price}")

    if cheapest_flight.price != "N/A" and cheapest_flight.price < destination["lowestPrice"]:
        pprint(f"Lower price flight found to {destination['city']}!")
        data_manager.update_lowest_price(destination["id"], cheapest_flight.price)
        # notification_manager.send_sms(
        #     message_body=f"Low price alert! Only GBP {cheapest_flight.price} to fly "
        #                  f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, "
        #                  f"on {cheapest_flight.out_date} until {cheapest_flight.return_date}."
        # )
        # SMS not working? Try whatsapp instead.
        # notification_manager.send_whatsapp(
        #     message_body=f"Low price alert! Only GBP {cheapest_flight.price} to fly "
        #                  f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, "
        #                  f"on {cheapest_flight.out_date} until {cheapest_flight.return_date}."
        # )
        notification_manager.send_emails(email_list=customer_email_list, flight=cheapest_flight)