
from datetime import timedelta, timezone, datetime
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
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
from django.http import JsonResponse
from Admin.models import *
from cart.models import *


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
            elif len(password) < 6:
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
   
        product=Color_products.objects.filter(is_listed=True).distinct('product')[:5]
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
               
                products = Color_products.objects.select_related('product').distinct('product')
                category = Catagory.objects.filter(is_listed=True)
                brand = Brand.objects.filter(is_listed=True)
                return render(request, 'shop.html', {'products': products, 'category': category, 'brand': brand})
        except Exception as e:       
                return render(request, 'shop.html', {'error': str(e)})

                
@never_cache
@login_required(login_url='login') 
def shopdetails(request,p_id,id):

        data=Color_products.objects.get(id=p_id)
        item=Color_products.objects.filter(product=id)
        return render(request,'shop-details.html',{'data':data,'item':item})
        
def filterd(request,id):
        try:
               
                products = Color_products.objects.select_related('product').filter(product__catagory=id).distinct('product')
                category = Catagory.objects.filter(is_listed=True)
                brand = Brand.objects.filter(is_listed=True)
                
                context={'products': products, 'category': category, 'brand': brand}
            
              

                        
                return render(request, 'shop.html',context)
                
        except Exception as e:       
                return render(request, 'shop.html',)
def view_address(request):
      address=Address.objects.filter(user=request.user)
      return render(request,'view_address.html' ,{'address': address})





@login_required
def add_address(request):
    if request.method == 'POST':
        user = request.user
        name = request.POST.get('name')
        address = request.POST.get('address')
        house_no = request.POST.get('house_no')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        pincode = request.POST.get('pincode')
        
        address_obj = Address.objects.create(
            user=user,
            name=name,
            address=address,
            House_no=house_no,
            city=city,
            state=state,
            country=country,
            pincode=pincode
        )
        address_obj.save()
        return JsonResponse({'message': 'Address added successfully'})
    return render(request, 'add_address.html')

@login_required
def update_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    if request.method == 'POST':
        address.name = request.POST.get('name')
        address.address = request.POST.get('address')
        address.House_no = request.POST.get('house_no')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.country = request.POST.get('country')
        address.pincode = request.POST.get('pincode')
        address.save()
        return JsonResponse({'message': 'Address updated successfully'})
    return render(request, 'update_address.html', {'address': address})

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    address.delete()
    return redirect('view_address')
        
def wish_list(request):

        try:
              wish_list=Wishlist.objects.get(customer=request.user)
              if wish_list:
                    wishlist=wish_list.products.all()
                    return render(request,"wishlist.html",{'wishlist':wishlist}) 
        except wish_list.DoesNotExist:
        
                return render(request,"wishlist.html") 

def add_to_wishlist(request, product_id):
     
    
    
        wishlist, created = Wishlist.objects.get_or_create(customer=request.user)
            
        product = get_object_or_404(Product, pk=product_id)
        

        if wishlist.products.filter(pk=product_id).exists():
            messages.info(request, 'This product is already in your wishlist.')
        else:
            
            wishlist.products.add(product)
            messages.success(request, 'Product added to wishlist successfully.')
            
    
        return redirect('wishlist') 
    
    
def change_password(request):
      if request.method=="POST":
           Current_password=request.POST.get("current_password")
           New_password=request.POST.get('new_password1')
           New_password2=request.POST.get('new_password2')
           if not  check_password(Current_password, request.user.password):
                 messages.error(request,'Current Password is error')
            elif not any(char.isupper() for char in password):
                messages.error(request, 'Password must contain at least one uppercase letter')
                return redirect('SignUp')
            elif not any(char.islower() for char in password):  # Corrected condition
                messages.error(request, 'Password must contain at least one lowercase letter')
                return redirect('SignUp')
            elif not any(char.isdigit() for char in password):
                messages.error(request, 'Password must contain at least one digit')
                return redirect('SignUp')
                 

      return render(request,"change_password.html")
                      

       
                      