
from datetime import timedelta, timezone, datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

import random
from django.shortcuts import render,HttpResponse
from django.contrib import messages
from django.db.models import Q

from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth import authenticate, login as log,logout as authlogout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache,cache_control
from django.core.mail import send_mail
from shopifyproject.settings import EMAIL_HOST_USER
from django.core.validators import EmailValidator
from django.utils import timezone
from Userapp.models import *

# Create your views here.
def login(request):
    if request.method=='POST':
         
      
                username=request.POST["username"]
                password=request.POST["password"]

                try:
                        user = authenticate(request, username=username, password=password)
                        if user is not None:
                                log(request, user)
                                return redirect('dashbord')
                        else:
                                 print('helo')
                                 messages.error(request,'incorrect username or password')  


                except:
                        pass
                        
                        
               
               

    return render(request,'login.html')


def dashbord(request):
        return render(request,'dashbord.html')



def view_user(request):
        user=CustomUser.objects.all().order_by('-pk')
        return render(request,'userdetails.html',{'data':user})
