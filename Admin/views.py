
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

from django.utils import timezone
from Userapp.models import CustomUser
from Userapp.urls import *
from django.utils.translation import gettext as _
from django.core.files.uploadedfile import UploadedFile
from PIL import Image

# Create your views here.
@never_cache
def login(request):
        if request.user.is_authenticated and request.user.is_superuser:
                
                
                return redirect('dashbord')
        

        if request.method == 'POST':
         
      
                username=request.POST["username"]
                password=request.POST["password"]

                try:
                        user = authenticate(request, username=username, password=password)
                        if user is not None and user.is_superuser==True:
                                log(request, user)
                                print(user.is_superuser)
                                return redirect('dashbord')
                        else :
                                 
                                messages.error(request,'incorrect username or password')  
                                return redirect('adminlogin')

                except Exception as e:
                        messages.error(request,e)  
                        return redirect('adminlogin')

                               
               

        return render(request,'login.html')
@never_cache
@login_required(login_url='AdminLogin/')
def dashbord(request):

        if request.user.is_superuser:


                return render(request,'dashbord.html')
        
        return redirect('adminlogin')
        
#_____________USERMANAGEMENT      

@never_cache
@login_required(login_url='adminlogin')
def view_user(request):
        
        if request.user.is_superuser:


                user=CustomUser.objects.all()
                
                return render(request,'userdetails.html',{'data':user})
        
        return redirect('adminlogin')


def block_user(request,u_id):
        
        try:

                data=CustomUser.objects.get(pk=u_id)
                data.is_active=False
                data.save()
                return redirect('userdetail')
        
        except:

                return redirect('userdetail')
        

def unblock_user(request,u_id):
       
                data=CustomUser.objects.get(pk=u_id)
                data.is_active=True
                data.save()
                return redirect('userdetail')

#______CATEGORYMANAGEMENT______
@never_cache
@login_required(login_url='adminlogin')
def category(request):

        if request.user.is_superuser: 


                if request.method=='POST':


                        try:

                                ca_name = request.POST.get('cat_name').strip()  
                                ca_description = request.POST.get('cat_description').strip()   
                                cover_photo = request.FILES.get('cover_image', None)  

                                if Catagory.objects.filter(cat_name__icontains=ca_name).exists():


                                        messages.error(request,'category already here')
                                        return redirect('category')
                                

                                elif not ca_name or not ca_name[0].isalpha():


                                        messages.error(request,'Field must start with a character')
                                        return redirect('category')
                                elif not is_valid_image(cover_photo):

                                        messages.error(request, 'Image  is an invalid image file')
                                        return redirect('category')
                                
                                item=Catagory(cat_name=ca_name,cat_description=ca_description,cover_image=cover_photo)
                                
                                item.save() 

                                return redirect('view_category')
                                
                                        
                        except Exception as e:
                                        
                                        messages.error(request,str(e))
                                        return redirect('category') 
                                                
                return render(request,'category.html')
        
        return redirect('adminlogin')

@never_cache
@login_required(login_url='adminlogin')   
def view_category(request):
        if request.user.is_superuser:
                try:
                        data=Catagory.objects.filter(is_listed=True)
                        
                
                        return render(request,'view_category.html',{'data':data})
                except :
                        return render(request,'view_category.html')

        return redirect('adminlogin')


@never_cache
@login_required(login_url='adminlogin')  
def edit_category(request,ca_id):
        try:
       
                
                data = Catagory.objects.get(id=ca_id)

                if request.method == 'POST':

                        ca_name = request.POST.get('cat_name').strip()  
                        ca_description = request.POST.get('cat_description').strip()   
                        cover_photo = request.FILES.get('cover_image') 
                        
                        
                        if not ca_name or not ca_name[0].isalpha():

                                messages.error(request, 'Field must start with a character')
                                return render(request, 'edit_category.html', {'data': data})
                        
                        if cover_photo:
                                
                                if not is_valid_image(cover_photo):

                                        messages.error(request, 'Image 1 is an invalid image file')
                                        return render(request, 'edit_category.html', {'data': data})
                                else:

                                        data.cover_image = cover_photo

                        if Catagory.objects.filter(cat_name__icontains=ca_name).exclude(id=ca_id).exists():

                                messages.error(request, 'Entered name already exists')
                                return render(request, 'edit_category.html', {'data': data})

                        data.cat_name = ca_name
                        data.cat_description = ca_description
                        data.save()

                        return redirect('view_category')  

                return render(request, 'edit_category.html', {'data': data})
        except:
                return redirect('view_category')

def category_unlist(request,ca_id):

        try:

                item=Catagory.objects.get(id=ca_id)
                item.is_listed=False
                item.save()
                return redirect('view_category')

        except:
               return redirect('view_category')

@never_cache
@login_required(login_url='adminlogin')  
def unlist_categories(request):

        if request.user.is_superuser:

                try:
                        data=Catagory.objects.filter(is_listed=False)
                        return render(request,'viewunlist_category.html',{'data':data})
                
                except:

                        return render(request,'viewunlist_category.html')
        return redirect('adminlogin')


def list_category(request,ca_id):
        
        try:
                item=Catagory.objects.get(id=ca_id)
                item.is_listed=True
                item.save()
                return redirect('view_category')

        except:
                return redirect('unlistcategory')



@never_cache
@login_required(login_url='adminlogin')             
def brand(request):
        if request.user.is_superuser:
                try:
                        if request.method=='POST':
                                b_name = request.POST.get('name').strip() 
                                cover_image = request.FILES.get('cover_image')
                                b_description = request.POST.get('description').strip() 
                                
                                if Brand.objects.filter(B_name__icontains=b_name).exists():
                                        messages.error(request,'brand already here')

                                        return render('brand')
                                
                                if not b_name or not b_name[0].isalpha():

                                        messages.error(request, 'Field must start with a character')

                                        return render('brand')
                                
                                if not is_valid_image(cover_image):

                                        messages.error(request, 'Image  is an invalid image file')
                                        return render('brand')
                                brand = Brand(
                                B_name=b_name,
                                cover_image=cover_image,
                                B_description=b_description,
                                )
                                brand.save()
                                return render('brand')
                        return render(request,'brand.html')
                
                
                except:
                        return render(request,'brand.html')
        return redirect('adminlogin')
    

       
        
       
def logout(request):
        authlogout(request)
        return redirect('adminlogin')
@never_cache
@login_required(login_url='adminlogin')  
def view_brands(request):
        if request.user.is_superuser:
                try:
                        return redirect('adminlogin')
                        data=Brand.objects.filter(is_listed=True)
                        return render(request,'view_brand.html',{'data':data})
                except :
                        return render(request,'view_brand.html')

        return redirect('adminlogin')
        
        
@never_cache
@login_required(login_url='adminlogin')  
def brand_delete(request,b_id):
        if request.user.is_superuser:
                try:
                        item=Brand.objects.get(id=b_id)
                        item.is_listed=False
                        item.save()
                        return render('viewbrand')
                except:
                        return render('viewbrand')
        return redirect('adminlogin')








        



       
def unlist_brand(request,b_id):
        try:
                data=Brand.objects.get(id=b_id)
                data.is_listed=False
                data.save()
                return redirect('viewbrand') 
        except:
                 return redirect('viewbrand') 

@never_cache
@login_required(login_url='adminlogin') 
def viewunlist_brands(request):
        try:
                data=Brand.objects.filter(is_listed=False)
                return render(request,'unlist_brand.html',{'data':data})
        except:
                return render(request,'unlist_brand.html')                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
def list_brand(request,b_id):
        try:
                data=Brand.objects.get(id=b_id)
                data.is_listed=True
                data.save()
                return redirect('viewbrand') 
        except:
                 return redirect('viewbrand') 
def is_valid_image(file):
    
    if not isinstance(file, UploadedFile):
        return False
    
    try:
        
        Image.open(file)
        return True
    except Exception as e:
        
        return False
    

