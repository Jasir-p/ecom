
from django.shortcuts import render,HttpResponse
from django.contrib import messages
from django.db.models import Q

from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth import authenticate, login,logout as authlogout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache,cache_control

# Create your views here.

def user_login(request):
    

   

    
    

    return render(request,'userlogin.html')
def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get('password')
        number=request.POST.get('number')
        email=request.POST.get('email')
        if username:
            CustomUser.objects.create_user(username=username, password=password,phone=number,email=email)

            c=CustomUser.objects.all()
            print(c)
        else:
            print('hi')
    return render(request,'userlogin.html')


def user_home(request):

    return render(request,'index.html')