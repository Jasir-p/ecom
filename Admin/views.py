
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
                        if user is not None and user.is_superuser:
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
 
 try:
        user=CustomUser.objects.all().order_by('-pk')
        return render(request,'userdetails.html',{'data':user})
 except :
        return render(request,'userdetails.html')
 
def category(request):
        try:

                 if request.method=='POST':

               
                      

                      
                        ca_name = request.POST.get('cat_name', '') 
                        ca_description = request.POST.get('cat_description', '')  
                        cover_photo = request.FILES.get('cover_image', None)  


                      
                        if Catagory.objects.filter(cat_name=ca_name).exists():


                             
                                messages.error(request,'category already here')
                                return redirect('category')
                
                        item=Catagory(cat_name=ca_name,cat_description=ca_description,cover_image=cover_photo)
                        print("hi")
                        item.save()     

                        
                        

        except Exception as e:
                      messages.error(request,str(e))
                      return redirect('category')
                

               
        return render(request,'category.html')
       
              
def brand(request):
    
    
    return render(request,'brand.html')
    
def view_category(request):
        return render(request,'')
       
