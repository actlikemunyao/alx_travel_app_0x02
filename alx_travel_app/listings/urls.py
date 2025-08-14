from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, BookingViewSet, ListingViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'listings', ListingViewSet, basename='listing')

payment_initiate = PaymentViewSet.as_view({'post': 'initiate'})
payment_verify = PaymentViewSet.as_view({'get': 'verify'})

urlpatterns = [
    path('', include(router.urls)),
    path('payments/initiate/', payment_initiate, name='payments-initiate'),
    path('payments/verify/', payment_verify, name='payments-verify'),
]
