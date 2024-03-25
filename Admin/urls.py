from django.urls import path
from . import views

urlpatterns = [
    path('AdminLogin/',views.login,name='adminlogin'),
    path('DashBord/',views.dashbord,name='dashbord'),
    path('UserDetails/',views.view_user,name='userdetail')
       
    ]

   


