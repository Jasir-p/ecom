from django.urls import path
from .views import Placed_order, order_management, order_details, Confirm, status,retry_payment

urlpatterns = [
    path("Placeorder/", Placed_order, name="placed_order"),
    path("OrderManagement/", order_management, name="order_management"),
    path("order_details/<int:id>", order_details, name="order_details"),
    path("Confirm/", Confirm, name="confirm"),
    path("UpdateStatus/<int:id>", status, name="update_status"),
    path("Retryamount/<int:id>",retry_payment,name="retry_payment")
  
   
    

]
