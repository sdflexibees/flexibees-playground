from twilio.rest import Client

from flexibees_finance.settings import TWILIO_SID, TWILIO_AUTH

client = Client(TWILIO_SID, TWILIO_AUTH)


def send_sms(country_code, phone, message):
    message = client.messages.create(
        # from_='FLXBEE',
        messaging_service_sid='MG1b02569adccfacaa6227a63daca7221c',
        body=message,
        to='+' + country_code + phone
    )
    print(message.sid)
    return True
