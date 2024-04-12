
from datetime import timedelta, timezone, datetime
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

import random
from django.shortcuts import render,HttpResponse
from django.contrib import messages
from django.db.models import Q

from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth import authenticate, login,logout as authlogout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache,cache_control
from django.core.mail import send_mail
from shopifyproject.settings import EMAIL_HOST_USER
from django.core.validators import EmailValidator
from django.utils import timezone
from Products.models import *
from Admin.models import *


# Create your views here.
@never_cache
def user_login(request):
        if request.user.is_authenticated:
                return redirect('user_home')
        if request.method=='POST':
         
      
                username=request.POST.get("username")
                password=request.POST.get("password")

                try:
                        user = authenticate(request, username=username, password=password)
                        if user is not None :
                                login(request, user)
                                return redirect('user_home')
                        else:
                                 
                                 messages.error(request,'incorrect username or password')  


                except Exception as e:
                        messages.error(str(e))
        return render(request,'userlogin.html')

def user_signup(request):
    try:
    
        if request.method == 'POST':
            
            username = request.POST.get('name')
            password = request.POST.get('password')
            number = request.POST.get('number')
            email = request.POST.get('email')
        
            
            if CustomUser.objects.filter(username=username).exists():
                    messages.error(request, 'The username is already taken')
                    return redirect('SignUp')
            
            elif not username.strip():
                    messages.error(request, 'The username is not valid')
                    return redirect('SignUp')
          
            elif CustomUser.objects.filter(email=email).exists():
                    messages.error(request, 'The username is already taken')
                    return redirect('SignUp')
            elif not is_valid_email(email):
                    messages.error(request, 'The email is not valid')
                    return redirect('SignUp')
            elif not validate_mobile_number(number):
                messages.error(request, 'The Mobail number is not valid')
                return redirect('SignUp')
            elif len(password) < 8:
                messages.error(request, 'The password should be at least 6 characters')
                return redirect('SignUp')
           
                
            elif not any(char.isupper() for char in password):
                messages.error(request, 'Password must contain at least one uppercase letter')
                return redirect('SignUp')
            elif not any(char.islower() for char in password):  # Corrected condition
                messages.error(request, 'Password must contain at least one lowercase letter')
                return redirect('SignUp')
            elif not any(char.isdigit() for char in password):
                messages.error(request, 'Password must contain at least one digit')
                return redirect('SignUp')
          
            else:    
                request.session['name']=username
                request.session['password']=password
                request.session['phone']=number 
                request.session['email']=email
                
                generate_otp_and_send_email(request,email)
                
                return redirect(otp)
            
        return render(request,'usersignup.html')
    except Exception as e:
           messages.error(request,e)
           return redirect('SignUp')



@never_cache

def user_home(request):
   
        product=Color_products.objects.filter(is_listed=True).order_by('-id')[:5]
        print(product)

        return render(request,'index.html',{'product':product})


def generate_otp_and_send_email(request,email):
    otp = random.randint(1000, 9999)
    otp_generated_at = datetime.now().isoformat()
    print(otp_generated_at)

    request.session['otp'] = otp
    request.session['time'] =otp_generated_at 
    
   
    send_mail(
            subject='Welcome',
            message=f'Your OTP for verification is: {otp}',
            from_email=EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )
   
          
   

def otp(request):
        if request.method == 'POST':
               
                otp1 = request.POST.get('otp1')
                otp2 = request.POST.get('otp2')
                otp3 = request.POST.get('otp3')
                otp4 = request.POST.get('otp4')

                full_otp = otp1 + otp2 + otp3 + otp4
               
                if 'otp' in request.session:
                       
                        otp=request.session['otp']
                        otp_generated=request.session['time']
                        delta=timedelta(minutes=2)
                        time=datetime.fromisoformat(otp_generated)
                        
                       
                        
    
    
                        if datetime.now() <= time + delta :
                                
                                if int(full_otp) == otp:
                                        CustomUser.objects.create_user(username= request.session['name'],password= request.session['password'],email= request.session['email'],phone=request.session['phone'])
                                        request.session.pop('name')
                                        request.session.pop('password')
                                        request.session.pop('email')
                                        request.session.pop('phone')
        
                                        messages.success(request, 'Registerd as successfully')
                                        return redirect('login')
                                else:

                                        messages.error(request,"Incorrect OTP! Please try again.")
                                        
                                        return redirect('otp')
                        else:   
                                expired_status = True  
                                error_message = f"OTP has {'expired' if expired_status else 'not expired'}. Please request a new one."
                                messages.error(request, f"OTP has {'expired' if expired_status else 'not expired'}. Please request a new one." )
                                return redirect('otp')
                
        else:
                return render(request,'otp.html')
        

def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
        


def validate_mobile_number(mobile_number):
   
    pattern = re.compile(r'^[6-9]\d{9}$')

    if pattern.match(mobile_number):
        return True
    else:
        return False


def logout(request):
       authlogout(request)
       return redirect('user_home')


def resend_otp(request):
        
        otp = random.randint(1000, 9999)
        otp_generated_at = datetime.now().isoformat()
        print(otp_generated_at)

        request.session['otp'] = otp
        request.session['time'] =otp_generated_at 
        email= request.session['email']
        
        
        send_mail(
                subject='Welcome',
                message=f'Your OTP for verification is: {otp}',
                from_email=EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False
                )
        return redirect('otp')
@never_cache
@login_required(login_url='login') 
def shop(request):
        try:
                category_id = request.GET.get('category_id')
                print(category_id)
                
                products=Color_products.objects.select_related('product')
                category=Catagory.objects.filter(is_listed=True)
                brand=Brand.objects.filter(is_listed=True)
                print(products)
                return render(request,'shop.html',{'products':products,'category':category,'brand':brand})
        except:       
                 return render(request,'shop.html')
        
        
@never_cache
@login_required(login_url='login') 
def shopdetails(request,p_id,id):
        data=Color_products.objects.get(id=p_id)
        item=Color_products.objects.filter(product=id)
        

        
        return render(request,'shop-details.html',{'data':data,'item':item})
        
def category_filter(request):
        category_id = request.GET.get('category_id')
        print(category_id)
        category=Catagory.objects.filter(is_listed=True)
        brand=Brand.objects.filter(is_listed=True)
        data=Product.objects.filter(catagory=category_id)
        print('hii')

        return render(request,'shop.html',{'products':data,'category':category,'brand':brand})