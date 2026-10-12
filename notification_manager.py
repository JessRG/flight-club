import os
from twilio.rest import Client
from flight_data import FlightData
import smtplib

# Using a .env file to retrieve the phone numbers and tokens.

class NotificationManager:

    def __init__(self):
        self.email = os.getenv("FROM_EMAIL", "")
        self.password = os.getenv("TEST_PASS_CODE", "")
        self.twilio_virtual_number = os.getenv("TWILIO_VIRTUAL_NUMBER", "")
        self.twilio_verified_number = os.getenv("TWILIO_VERIFIED_NUMBER", "")
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "")
        self.client = Client(os.getenv('TWILIO_SID', ""), os.getenv("TWILIO_AUTH_TOKEN", ""))
        self.connection = smtplib.SMTP(host=os.getenv("TEST_SMTP_ADDRESS", ""), port=int(os.getenv("PORT", 2525)))

    def send_sms(self, message_body):
        message = self.client.messages.create(
            from_=self.twilio_virtual_number,
            body=message_body,
            to=self.twilio_verified_number
        )
        # Prints if successfully sent.
        print(message.sid)

    # Is SMS not working for you or prefer whatsapp? Connect to the WhatsApp Sandbox!
    # https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
    def send_whatsapp(self, message_body):
        message = self.client.messages.create(
            from_=f'whatsapp:{self.whatsapp_number}',
            body=message_body,
            to=f'whatsapp:{self.twilio_verified_number}'
        )
        print(message.sid)

    def send_emails(self, email_list, flight: FlightData):
        if flight.stops > 0:
            body_text = (
                f"Low price alert! Only ${flight.price} to fly "
                f"from {flight.origin_airport} to {flight.destination_airport}, "
                f"with {flight.stops} stop(s)"
                f"departing on {flight.out_date} and returning on {flight.return_date}. ✈️\n"
            )
        else:
            body_text = (
                f"Low price alert! Only ${flight.price} to fly direct "
                f"from {flight.origin_airport} to {flight.destination_airport}, "
                f"on {flight.out_date} until {flight.return_date}. ✈️\n"
            )

        with self.connection as smtp:
            smtp.starttls()
            smtp.login(self.email, self.password)
            for email in email_list:
                full_message = (
                    f"From: {self.email}\n"
                    f"To: {email}\n"
                    "Subject: Flight Deal\n"
                    "MIME-Version: 1.0\n"
                    "Content-Type: text/plain; charset=utf-8\n\n"
                    f"{body_text}"
                )
                smtp.sendmail(
                    from_addr=self.email,
                    to_addrs=email,
                    msg=full_message.encode('utf-8')
                )