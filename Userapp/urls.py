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
        path('categoryfilter/',views.category_filter,name='category_filter')
        
    ]
