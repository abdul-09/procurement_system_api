from twilio.rest import Client
from django.conf import settings
from django.core.mail import send_mail

# # Twilio Configuration
# TWILIO_ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
# TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
# TWILIO_FROM_NUMBER = settings.TWILIO_PHONE_NUMBER

# client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# def send_sms_notification(to_number, message):
#     try:
#         client.messages.create(
#             body=message,
#             from_=TWILIO_FROM_NUMBER,
#             to=to_number
#         )
#     except Exception as e:
#         # Handle exceptions (e.g., log the error)
#         print(f"Error sending SMS: {e}")

def send_email_notification(to_email, subject, message):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )

