from django.urls import path
from . import views
from .views import*


urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("", views.user_home, name="user_home"),
    path("UserSignUp/", views.user_signup, name="SignUp"),
    path("otp", views.otp, name="otp"),
    path("ResendOtp/", views.resend_otp, name="resend"),
    path("UserLogout/", views.logout, name="userlogout"),
    path("Shop/", views.shop, name="shop"),
    path("ShopDetails/<int:p_id>", views.shopdetails, name="shopdetails"),
    path("filterd/", views.filterd, name="filterd"),
    path("AddAddress/", views.add_address, name="add_address"),
    path("ViewAddress/", views.view_address, name="view_address"),
    path("EditAddress/<int:address_id>",views.update_address,name="edit_adress"),
    path("DeleteAddress/<int:address_id>", views.delete_address, name="delete_address"),
    path("Wishlist/", views.wish_list, name="wishlist"),
    path("addwishlist/<int:product_id>", views.add_to_wishlist, name="addwishlist"),
    path("WishlistRemove/<int:id>", views.Remove_wishlist, name="wishlist_remove"),
    path("ChangePassword/", views.change_password, name="changepassword"),
    path("Userorder/", views.user_order, name="user_order"),
    path(
        "OrderViewDetails/<int:id>", views.view_order_details, name="view_order_details"
    ),
    path("OrderTracking/<int:id>", views.order_track, name="order_track"),
    path("error/", views.error_page, name="error"),
    path("RequestCancel/<int:id>", views.request_status_cancel, name="request_cancel"),
    path("RequestReturn/<int:id>", views.request_status_return, name="request_return"),
    path("Wallet/",views.wallet,name="wallet"),
    path("Add_to_Wallet/,",views.add_to_wallet,name="add_to_wallet"),
    path('ViewCoupon/',views.view_coupons,name="view_coupon"),
    path('api/products/<int:product_id>/sizes', views.get_product_sizes, name='get_sizes'),
    path('wishlist-to-cart/<int:id>/<int:size_id>/', views.wishlist_to_cart, name='wishlist_to_cart'),
    path("MyRefarels/",views.myrefrals,name='my_refarel'),
    path("Search/",views.search_shop,name="search"),
    path("Forgotpassword/",views.forgot_email,name='f_password'),
    path('Otppassword/',views.check_otp,name="otp_password"),
    path('Resendotppassword/',views.resend_otp_password,name="resend_otp_password"),
    path("PasswordSection/",views.set_password,name='password_section'),
    path('invoice/<int:order_id>/', views.generate_invoice, name='generate_invoice'),
]
