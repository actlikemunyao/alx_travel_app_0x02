import uuid, requests
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Booking, Payment, Listing
from .serializers import PaymentSerializer, BookingSerializer, ListingSerializer
from .tasks import send_payment_confirmation

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

class PaymentViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["post"])
    def initiate(self, request):
        booking_id = request.data.get("booking_id")
        email = request.data.get("email")
        first_name = request.data.get("first_name", "Guest")
        last_name = request.data.get("last_name", "")

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        tx_ref = str(uuid.uuid4())
        payload = {
            "amount": str(booking.amount),
            "currency": "ETB",
            "email": email or booking.user_email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "callback_url": settings.FRONTEND_CALLBACK_URL,
        }
        headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
        try:
            resp = requests.post(f"{settings.CHAPA_BASE_URL}/transaction/initialize", json=payload, headers=headers, timeout=30)
            data = resp.json()
        except Exception as e:
            return Response({"error": f"Failed to reach Chapa: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

        if resp.status_code in (200, 201) and data.get("status") in ("success", True):
            Payment.objects.create(booking=booking, transaction_id=tx_ref, amount=booking.amount, status="Pending")
            return Response(data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def verify(self, request):
        tx_ref = request.query_params.get("tx_ref")
        if not tx_ref:
            return Response({"error": "tx_ref is required"}, status=status.HTTP_400_BAD_REQUEST)

        headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
        try:
            resp = requests.get(f"{settings.CHAPA_BASE_URL}/transaction/verify/{tx_ref}", headers=headers, timeout=30)
            data = resp.json()
        except Exception as e:
            return Response({"error": f"Failed to reach Chapa: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

        try:
            payment = Payment.objects.get(transaction_id=tx_ref)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        status_value = data.get("status")
        success = status_value in ("success", True)
        payment.status = "Completed" if success else "Failed"
        payment.save()

        if success:
            # fire-and-forget email
            send_payment_confirmation.delay(payment.booking.user_email, payment.booking.id, str(payment.amount))

        serializer = PaymentSerializer(payment)
        return Response({"chapa": data, "payment": serializer.data}, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)
