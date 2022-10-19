import os
import smtplib

from twilio.rest import Client

FROM_PHONE = os.environ.get("FROM_PHONE")
TO_PHONE = os.environ.get("TO_PHONE")
ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
EMAIL = os.environ.get("SMTP_EMAIL")
EMAIL_PASSWORD = os.environ.get("SMTP_EMAIL_PASSWORD")
SMTP_EMAIL_PROVIDER = os.environ.get("SMTP_EMAIL_PROVIDER")
SMTP_PORT = int(os.environ.get("SMTP_PORT"))


class NotificationManager:
    def __init__(self):
        self.client = Client(ACCOUNT_SID, AUTH_TOKEN)

    def notify(self, body):
        message = self.client.messages.create(
            body=body,
            from_=FROM_PHONE,
            to=TO_PHONE
        )
        print(message.sid)

    def send_emails(self, emails, body, link):
        with smtplib.SMTP(SMTP_EMAIL_PROVIDER, SMTP_PORT) as connection:
            connection.starttls()
            connection.login(user=EMAIL, password=EMAIL_PASSWORD)
            for email in emails:
                connection.sendmail(
                    from_addr=EMAIL,
                    to_addrs=email,
                    msg=f"Subject:Flight Checker\n\n{body}\n{link}".encode("utf-8")
                )
