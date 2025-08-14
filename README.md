# alx_travel_app_0x02 — Milestone 4: Chapa Payment Integration

This repo duplicates the travel app and adds **Chapa** payment initiation + verification with a `Payment` model and simple Celery email notification.

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # put your real CHAPA_SECRET_KEY
python manage.py migrate
python manage.py runserver
```

### Create demo data
```bash
python manage.py shell <<'PY'
from listings.models import Listing, Booking
l = Listing.objects.create(title="Nairobi Getaway", price=250)
b = Booking.objects.create(user_email="alice@example.com", listing=l, start_date="2025-09-01", end_date="2025-09-05", amount=250)
print("Booking id:", b.id)
PY
```

### Initiate a payment
```bash
curl -X POST http://127.0.0.1:8000/api/payments/initiate/   -H "Content-Type: application/json"   -d '{"booking_id": 1, "email":"alice@example.com", "first_name":"Alice"}'
```
- You should receive Chapa `checkout_url` (in the JSON) where the user completes payment.
- A `Payment` row with `status="Pending"` is created.

### Verify a payment
After completing in sandbox, verify with:
```bash
curl "http://127.0.0.1:8000/api/payments/verify/?tx_ref=<the-tx-ref-returned>"
```
- `Payment.status` updates to `Completed` or `Failed`.
- On success, a **console email** is printed (Celery task).

## Notes
- Uses `.env` for `CHAPA_SECRET_KEY` via `python-decouple`.
- Email backend is console-only; swap in SMTP for production.
- Celery defaults to in-memory for demo; configure Redis/RabbitMQ in production.
- Endpoints:
  - `POST /api/payments/initiate/`
  - `GET  /api/payments/verify/?tx_ref=...`
