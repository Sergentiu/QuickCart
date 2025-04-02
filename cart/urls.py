from django.urls import path
from .views import *

urlpatterns = [
    path("", cart_view, name="cart_url"),
    path("add/<productid>", add_to_cart_view, name="add_to_cart_url"),
    path("empty", empty_cart_view, name="empty_cart_url"),
    path("checkout/", checkout_view, name="checkout_url"),
    path("payment_success/", payment_success, name="payment_success"),
]