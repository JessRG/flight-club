import os
import requests
from requests.auth import HTTPBasicAuth

class DataManager:

    def __init__(self):
        self._user = os.getenv("SHEETY_USERNAME", "")
        self._password = os.getenv("SHEETY_PASSWORD", "")
        self._authorization = HTTPBasicAuth(self._user, self._password)
        self.prices_endpoint = os.getenv("SHEETY_PRICES_ENDPOINT", "")
        self.users_endpoint = os.getenv("SHEETY_USERS_ENDPOINT", "")
        self.destination_data = {}
        self.customer_emails = []

    def get_destination_data(self):
        response = requests.get(url=self.prices_endpoint, auth=self._authorization)
        data = response.json()
        self.destination_data = data["prices"]
        return self.destination_data

    def get_customer_emails(self):
        response = requests.get(url=self.users_endpoint, auth=self._authorization)
        data = response.json()
        self.customer_emails = data["users"]
        return self.customer_emails

    # ==================== Updated the price in the spreadsheet ====================

    def update_lowest_price(self, row_id, new_price):
        new_data = {
            "price": {
                "lowestPrice": new_price
            }
        }
        requests.put(
            url=f"{self.prices_endpoint}/{row_id}",
            json=new_data,
            auth=self._authorization
        )
