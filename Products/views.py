

from django.core.exceptions import ValidationError

import random

from django.contrib import messages
from django.db.models import Q

from django.shortcuts import render,redirect

from django.contrib.auth import authenticate, login as log,logout as authlogout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache,cache_control

from Userapp.models import *
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
from .models import *
from Admin.urls import *

# Create your views here.

@never_cache
@login_required(login_url='adminlogin') 
def add_products(request):
    
        categories = Catagory.objects.all()
        brands = Brand.objects.all()
        
        if request.method == 'POST':
            name = request.POST.get('name').strip() 
            price = request.POST.get('price')
            description = request.POST.get('description').strip() 
            category_id = request.POST.get('category')
            brand = request.POST.get('brand')
            Thumbnail = request.FILES.get('thumbnail')

          
            if Product.objects.filter(name__icontains=name).exists():
                messages.error(request,'product already exist')
                return redirect('addproducts')
            if not name or not name[0].isalpha():
                messages.error(request, 'Field must start with a character')
                return redirect('addproducts')
            if len(name) < 2:
                messages.error(request, 'Field must atleast two character')
                return redirect('addproducts')

            elif int(price)<0:
                messages.error(request,'price must be postive number')
                return redirect('addproducts')
            elif not is_valid_image(Thumbnail):
                messages.error(request, 'Thumbnail is an invalid image file ')
                return redirect('addproducts')

           
            product = Product(
                name=name,
                price=price,
                description=description,
                catagory_id=category_id,
                brand_id=brand,
                thumbnail=Thumbnail,
                
            )
            product.save()
            messages.success(request, 'Product added successfully')
            return redirect('addproducts')

        return render (request,'add_products.html',{'categories': categories, 'brands': brands})
    

@never_cache
@login_required(login_url='adminlogin') 
def add_colour(request):
    try:
   
    
        products = Product.objects.filter(is_listed=True)
        
        if request.method == 'POST':

            name = request.POST.get('color_name').strip() 
            
            img1 = request.FILES.get('img1')
            img2 = request.FILES.get('img2')
            img3 = request.FILES.get('img3')
            product_id = request.POST.get('product')  

            if Color_products.objects.filter(product_id=product_id, color_name__icontains=name).exists():
                    
                    messages.error(request, 'Color already exists for this product')
                    return render('addcolour')

            elif not name:

                messages.error(request, 'Please provide color name')
                return render('addcolour') 
          
            elif not is_valid_image(img1):
                messages.error(request, 'Image 1 is an invalid image file')
                return render('addcolour')
            elif not is_valid_image(img2):
                messages.error(request, 'Image 2 is an invalid image file')
                return render('addcolour') 

            elif not is_valid_image(img3):
                messages.error(request, 'Image 3 is an invalid image file')
                return render('addcolour') 

            else:
                
              
                    product = Product.objects.get(id=product_id)
                    data = Color_products(color_name=name,img1=img1, img2=img2, img3=img3, product=product)
                    data.save()
                    messages.success(request, 'Color added successfully')
        
        return render(request, 'add_colour.html', {'products': products})
    
    except Exception as e:

        messages.error(request,str(e))
   

@never_cache
@login_required(login_url='adminlogin') 
def add_size(request):
    try:
        color_products=Color_products.objects.all()
        if request.method == 'POST':
            color_id = request.POST.get('color_product')
            size = request.POST.get('size').strip() 
            quantity = int(request.POST.get('quantity'))
            if size not in ['S', 'M', 'L', 'XL', 'XXL']:
                 
                messages.error(request,"Invalid size. Please choose from S, M, L, XL, XXL.")
                return redirect('addsize')
            

            if quantity <= 0:
                    messages.error(request,'Quantity must be a positive number')
                    return redirect('addsize')

              
            color_product = Color_products.objects.get(id=color_id)
            
            if color_product.size.filter(size__icontains=size).exists():
                    messages.error(request,'Size already exists for this color')
                    return redirect('addsize')

                
            size_instance = size_variant(size=size, quantity=quantity, Color_products=color_product)
            size_instance.save()
            
            messages.success(request,'Size added')

        return render(request,'add_size.html',{'color_products':color_products})
    except Exception as e:
        messages.error(request,str(e))
        return render(request,'add_size.html')

def is_valid_image(file):
    # Check if the file is an image
    if not isinstance(file, UploadedFile):
        return False
    
    try:
        
        Image.open(file)
        return True
    except Exception as e:
        
        return False

@never_cache
@login_required(login_url='adminlogin') 
def view_product(request):
    
    try:
        products=Product.objects.filter(is_listed=True).prefetch_related('color_product__size')
        
        context={
             
              'products':products

             
        }
        return render(request,'product.html',context)
    except:
        return render(request,'product.html')
        

def unlist_product(request,id):
    try:
            products=Product.objects.get(id=id)
            products.is_listed=False
            products.save()
            return redirect('viewproducts')
         
    except:
         
           return redirect('viewproducts')

def edit_product(request,id):
    try:
         
        product = Color_products.objects.prefetch_related('size').get(id=id)
        categories = Catagory.objects.all()
        brands = Brand.objects.all()
        context={
                'categories':categories,
                'brands':brands,
                'product':product

                
            }
        
        
        return render(request,"edit_product.html",context)
    except:
         return render(request,"edit_product.html")
         
def view_unlist(request):
    try:
        products=Product.objects.filter(is_listed=False)
        
        context={
             
              'products':products

             
        }
        return render(request,'unlist_product.html',context)
    except:
        return render(request,'unlist_product.html')
        
def list_product(request,id):
    try:
            products=Product.objects.get(id=id)
            products.is_listed=True
            products.save()
            return redirect('viewproducts')
         
    except:
         
           return redirect('viewproducts')               
        
     