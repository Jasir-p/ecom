from django.urls import path
from . import views

urlpatterns = [
        path('login/',views.user_login,name='login'),
        path('',views.user_home,name='user_home'),
        
        path('UserSignUp/',views.user_signup,name='SignUp'),
        path('otp',views.otp,name='otp'),
        path('ResendOtp/',views.generate_otp_and_send_email,name='resend')
        
    ]
