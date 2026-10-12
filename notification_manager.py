import os
from twilio.rest import Client
from flight_data import FlightData
import smtplib

# Using a .env file to retrieve the phone numbers and tokens.

class NotificationManager:

    def __init__(self):
        self.client = Client(os.environ['TWILIO_SID'], os.environ["TWILIO_AUTH_TOKEN"])

    def send_sms(self, message_body):
        message = self.client.messages.create(
            from_=os.environ["TWILIO_VIRTUAL_NUMBER"],
            body=message_body,
            to=os.environ["TWILIO_VERIFIED_NUMBER"]
        )
        # Prints if successfully sent.
        print(message.sid)

    # Is SMS not working for you or prefer whatsapp? Connect to the WhatsApp Sandbox!
    # https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
    def send_whatsapp(self, message_body):
        message = self.client.messages.create(
            from_=f'whatsapp:{os.environ["TWILIO_WHATSAPP_NUMBER"]}',
            body=message_body,
            to=f'whatsapp:{os.environ["TWILIO_VERIFIED_NUMBER"]}'
        )
        print(message.sid)

    def send_email(self, flight_data: FlightData):
        message_text = (
            "Subject: Flight Deal\n"
            "MIME-Version: 1.0\n"
            "Content-Type: text/plain; charset=utf-8\n\n"
            f"Low price alert! Only ${flight_data.price} to fly from {flight_data.origin_airport} to "
            f"{flight_data.destination_airport}, on {flight_data.out_date} until {flight_data.return_date} ✈️\n"
        )
        with smtplib.SMTP(os.getenv("SMTP_GMAIL", ""), port=int(os.getenv("PORT", 2525))) as smtp:
            smtp.starttls()
            smtp.login(os.getenv("FROM_EMAIL", ""), os.getenv("PASS_CODE", ""))
            smtp.sendmail(
                from_addr=os.getenv("FROM_EMAIL", ""),
                to_addrs=os.getenv("TO_EMAIL", ""),
                msg=message_text.encode('utf-8')
            )
