
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


# Create your views here.

def user_login(request):
    

   

    
    

    return render(request,'userlogin.html')
def user_signup(request):
    try:
    
        if request.method == 'POST':
            print('hi')
            username = request.POST.get('name')
            password = request.POST.get('password')
            number = request.POST.get('number')
            email = request.POST.get('email')
        
            if not all([username , email, password,]):
                    messages.error(request,'Please fill up all the fields.')
                    return redirect('SignUp')
            elif CustomUser.objects.filter(username=username).exists():
                    messages.error(request, 'The username is already taken')
                    return redirect('SignUp')
            elif not username:
                    messages.error(request, 'Please provide a username')
                    return redirect('SignUp')
            elif not username.strip():
                    messages.error(request, 'The username is not valid')
                    return redirect('SignUp')
          
            elif CustomUser.objects.filter(username=username).exists():
                    messages.error(request, 'The username is already taken')
                    return redirect('SignUp')
            elif not is_valid_email(email):
                    messages.error(request, 'The email is not valid')
                    return redirect('SignUp')
            elif not validate_mobile_number(number):
                messages.error(request, 'The Mobail number is not valid')
                return redirect('SignUp')
                
            request.session['name']=username
            request.session['password']=password
            request.session['phone']=number
            request.session['email']=email
            
            generate_otp_and_send_email(request,email)
            
            return redirect(otp)
            
        return render(request,'usersignup.html')
    except Exception as e:
           messages.error(e)



def user_home(request):

    return render(request,'index.html')


def generate_otp_and_send_email(request,email):
    otp = random.randint(1000, 9999)
    otp_generated_at = datetime.now().isoformat()
    print(otp_generated_at)

    request.session['otp'] = otp
    request.session['time'] =otp_generated_at 
    print("hi")

    send_mail(
        subject='Welcome',
        message=f'Your OTP for verification is: {otp}',
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=True
    )
   

def otp(request):
        if request.method == 'POST':
               
                otp1 = request.POST.get('otp1')
                otp2 = request.POST.get('otp2')
                otp3 = request.POST.get('otp3')
                otp4 = request.POST.get('otp4')

                full_otp = otp1 + otp2 + otp3 + otp4
                print(full_otp)
                print(request.session['otp'])
                if 'otp' in request.session:
                       
                        otp=request.session['otp']
                        otp_generated=request.session['time']
                        delta=timedelta(minutes=2)
                        time=datetime.fromisoformat(otp_generated)
                        
                        print(time,time+delta)
                        
    
    
                        if datetime.now() <= time + delta :
                                
                                if int(full_otp) == otp:
                                        CustomUser.objects.create_user(username= request.session['name'],password= request.session['password'],email= request.session['email'],phone=request.session['phone'])
                                        request.session.pop('name')
                                        request.session.pop('password')
                                        request.session.pop('email')
                                        request.session.pop('phone')
        
                                
                                        return redirect('login')
                                else:

                                        messages.error("Incorrect OTP! Please try again.")
                                        
                                        return redirect('otp')
                        else:   
                                expired_status = True  
                                error_message = f"OTP has {'expired' if expired_status else 'not expired'}. Please request a new one."
                                messages.error(request, error_message)
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


      