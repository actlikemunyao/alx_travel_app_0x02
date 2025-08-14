from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_payment_confirmation(email, booking_id, amount):
    subject = "Payment Confirmation"
    message = f"Your payment for booking #{booking_id} of amount {amount} was successful."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True)
