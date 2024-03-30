from django.urls import path
from . import views

urlpatterns = [
        path('login/',views.user_login,name='login'),
        path('',views.user_home,name='user_home'),
        
        path('UserSignUp/',views.user_signup,name='SignUp'),
        path('otp',views.otp,name='otp'),
        path('ResendOtp/',views.resend_otp,name='resend'),
        path('UserLogout/',views.logout,name='userlogout')
        
    ]
