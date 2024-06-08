from django.urls import path
from .views import *


urlpatterns = [
    path("AddCart/<int:id>", AddCart.as_view(), name="add_cart"),
    path("ViewCart/", Viewcart.as_view(), name="viewcart"),
    path("update-cart/", UpdateCartView.as_view(), name="update_cart"),
    path("Deletecart/<int:cart_id>", delete_cart, name="deletecart"),
    path("Updatetotal/", cart_total_view, name="update_total"),
    path("Checkout/", checkout, name="checkout"),
    path('AddCoupon/',add_coupon,name='add_coupon'),
    path('ChekAddress/<int:address_id>',check_update_address,name="check_address"),
    path('Viewcoupons/',view_admin_coupon,name="view_coupons"),
    path('ChekAddAddress/',check_add_address,name="check_add_address"),

    path('edit_coupon/<int:id>/', edit_coupon, name='edit_coupon'),
    path('ActiveCoupon/<int:id>',coupon_is_active,name='active_coupon')


]
