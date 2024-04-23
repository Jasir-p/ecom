from django.urls import path
from . import views





urlpatterns = [
        path('login/',views.user_login,name='login'),
       
        path('',views.user_home,name='user_home'),
        
        path('UserSignUp/',views.user_signup,name='SignUp'),
        path('otp',views.otp,name='otp'),
        path('ResendOtp/',views.resend_otp,name='resend'),
        path('UserLogout/',views.logout,name='userlogout'),
        path('Shop/',views.shop,name='shop'),
        path('ShopDetails/<int:p_id>/<int:id>',views.shopdetails,name='shopdetails'),
        path('filterd/<int:id>',views.filterd,name='filterd'),
        path('AddAddress/',views.add_address,name="add_address"),
        path('ViewAddress/',views.view_address,name='view_address'),
        path('DeleteAddress/<int:address_id>',views.delete_address,name="delete_address"),
        path('Wishlist/',views.wish_list,name='wishlist'),
        path('addwishlist/<int:product_id>',views.add_to_wishlist,name='addwishlist'),
    
        
    ]
