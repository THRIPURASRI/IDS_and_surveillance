# alerts/sms_alert.py
from twilio.rest import Client
from flask import current_app

def send_sms_alert(to_number, message):
    """
    Sends an SMS alert using Twilio API.
    """
    account_sid = current_app.config.get("TWILIO_ACCOUNT_SID")
    auth_token = current_app.config.get("TWILIO_AUTH_TOKEN")
    from_number = current_app.config.get("TWILIO_FROM_NUMBER")

    client = Client(account_sid, auth_token)

    try:
        client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        print("SMS sent successfully.")
    except Exception as e:
        print("Failed to send SMS:", e)
