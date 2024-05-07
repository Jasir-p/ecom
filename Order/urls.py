from django.urls import path
from .views import place_order, order_management, order_details, Confirm, status

urlpatterns = [
    path("Placeorder/", place_order, name="placed_order"),
    path("OrderManagement/", order_management, name="order_management"),
    path("order_details/<int:id>", order_details, name="order_details"),
    path("Confirm/", Confirm, name="confirm"),
    path("UpdateStatus/<int:id>", status, name="update_status"),
    
]
