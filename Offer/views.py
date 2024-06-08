from django.shortcuts import render
from django.shortcuts import get_object_or_404

# Create your views here.
from django.shortcuts import render, redirect
from .models import Offer
from django.shortcuts import render
from datetime import timedelta, timezone, datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

import random
from django.shortcuts import render, HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login as log, logout as authlogout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control

from django.utils import timezone
from Userapp.models import CustomUser
from Userapp.urls import *
from django.utils.translation import gettext as _
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
from django.views import View


from Products.models import Product
from Admin.models import Catagory

@never_cache
@login_required(login_url="adminlogin")
def add_offer(request):
    if request.user.is_authenticated and request.user.is_superuser:
        products = Product.objects.all()
        categories = Catagory.objects.all()
        

        if request.method == 'POST':
            offer_type = request.POST.get('offer_type')
            category_id = request.POST.get('category')
            product_id = request.POST.get('product')
            discount_percentage = request.POST.get('discount_percentage')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            print(offer_type,category_id,product_id,discount_percentage,start_date,end_date)

            if discount_percentage <= 0:
                messages.error(request, "Discount percentage must be positive")
                return redirect("view_offer")


            if offer_type == 'category':
                if Offer.objects.filter(category__id=category_id).exists():
                    messages.error(request,"already Added")
                    return redirect("view_offer")
                
                category_instance = get_object_or_404(Catagory, id=category_id)
                
                Offer.objects.create(
                    offer_type=Offer.CATEGORY,
                    category=category_instance,
                    discount_percentage=discount_percentage,
                    start_date=start_date,
                    end_date=end_date
                )
                messages.success(request,"Offer added succesfully")
                return redirect('view_offer')
            elif offer_type == 'product':
                if Offer.objects.filter(product__id=product_id).exists():
                    messages.error(request,"already Added")
                    return redirect("view_offer")
                product = Product.objects.get(pk=product_id)
                Offer.objects.create(
                    offer_type=Offer.PRODUCT,
                    product=product,
                    discount_percentage=discount_percentage,
                    start_date=start_date,
                    end_date=end_date
                )
                messages.success(request,"Offer added succesfully")

            return redirect('view_offer')  # Redirect to the offer list page after successful addition
        
        return render(request, 'add_offer.html', {'products': products, 'categories': categories})
    else:
         return redirect("adminlogin")
    
@never_cache
@login_required(login_url="adminlogin")
def view_offers(request):
    if request.user.is_authenticated and request.user.is_superuser:
    
        offers = Offer.objects.all()
        
        return render(request, 'view_offer.html', {'offers': offers})
    else:
         return redirect("adminlogin")


@never_cache
@login_required(login_url="adminlogin")
def edit_offer(request, offer_id):
    if request.user.is_authenticated and request.user.is_superuser:

    
        offer = get_object_or_404(Offer, pk=offer_id)
        products = Product.objects.all()
        categories = Catagory.objects.all()
        
        if request.method == 'POST':
            offer_type = request.POST.get('offer_type')
            category_id = request.POST.get('category')
            product_id = request.POST.get('product')
            discount_percentage = request.POST.get('discount_percentage')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            if discount_percentage <= 0:
                messages.error(request, "Discount percentage must be positive")
                return redirect("view_offer")

            if offer_type == 'category':
                
                if Offer.objects.filter(category__id=category_id).exclude(id=offer_id).exists():
                    messages.error(request, "Offer already exists for this category.")
                    return redirect("view_offer")
                category_instance = get_object_or_404(Catagory, id=category_id)
                offer.offer_type = Offer.CATEGORY
                offer.category = category_instance
            elif offer_type == 'product':
            
                if Offer.objects.filter(product__id=product_id).exclude(id=offer_id).exists():
                    messages.error(request, "Offer already exists for this product.")
                    return redirect("view_offer")
                product = Product.objects.get(pk=product_id)
                offer.offer_type = Offer.PRODUCT
                offer.product = product
            
            offer.discount_percentage = discount_percentage
            offer.start_date = start_date
            offer.end_date = end_date
            offer.save()
            messages.success(request, "Offer updated successfully.")

        return render(request, 'edit_offer.html', {'offer': offer, 'products': products, 'categories': categories})
    else:
         return redirect("adminlogin")

def active_section(request,id):
    offer = get_object_or_404(Offer, pk=id)
    if offer.is_active == False:
         offer.is_active =True
         offer.save()
    else:
         offer.is_active=False
         offer.save()
    return redirect("view_offer")
    