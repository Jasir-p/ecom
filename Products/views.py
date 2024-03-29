

from django.core.exceptions import ValidationError

import random

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


def add_products(request):
    try:
        categories = Catagory.objects.all()
        brands = Brand.objects.all()
        print('hi')

        print(brands)
       


        
        if request.method == 'POST':
            name = request.POST.get('name')
            price = request.POST.get('price')
            description = request.POST.get('description')
            category_id = request.POST.get('category')
            brand = request.POST.get('brand')

            print(category_id)


            
            
            if Product.objects.filter(name=name).exists():
                messages.error('product already exist')
            
           
           
           
            product = Product(
                name=name,
                price=price,
                description=description,
                catagory_id=category_id,
                brand_id=brand,
                
            )
            product.save()

        return render (request,'add_products.html',{'categories': categories, 'brands': brands})
    except:
        return render (request,'add_products.html')



def add_colour(request):
    try:
        products=Product.objects.all()
        print(products)
    
        return render(request,'add_colour.html',{'products':products})
    except:
        return render(request,'add_colour.html')