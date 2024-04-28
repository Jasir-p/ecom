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
# Create your views here.

class AddCart(View):
    
    def post(self,request,id):
        
        try:
            cart=Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            cart= Cart.objects.create(user=request.user)
            
        
        size=request.POST.get('size')
        
        
        product=Color_products.objects.get(id=id)
        try: 
            size_instance=size_variant.objects.get(id=size)
        except size_variant.DoesNotExist:
             messages.warning(request, 'Select a size')
             return redirect('shopdetails',id)

        existing_cart_item = CartItem.objects.filter(cart=cart, product=product)
        if  existing_cart_item:
                messages.warning(request,'Item already in the cart')
                return redirect('viewcart')
        
        cart_item=CartItem.objects.create(cart=cart,product=product,product_size_color=size_instance)
        cart_item.save()
        cart.save()
        messages.success(request,'Product succesfully added')
        return redirect('shopdetails',id)
        

        
class Viewcart(View):
    def get(self,request):
        cart1 = Cart.objects.get(user=request.user)
        print(cart1)
        cart=CartItem.objects.filter(cart__user=request.user).order_by('id')
        total=0
        for i in cart:
            total=0
            total+=i.product.product.price * i.quantity
            i.total_price=total
            i.save()
        
        cart1.total_amount =sum(item.total_price for item in cart)
        cart1.save()
        context={
            'cart1':cart1,
            'cart':cart
        }
        
        return render(request,'shopping-cart.html',context)
    






class UpdateCartView(View):
    def post(self, request):
        # Ensure the user is authenticated
        if request.user.is_authenticated:
            product_id = request.POST.get('product_id')
            quantity = request.POST.get('quantity')

            try:
                # Retrieve the cart and item
                cart = Cart.objects.get(user=request.user)
                item = CartItem.objects.get(cart=cart, id=product_id)

                # Check if the requested quantity is available
                available_quantity = item.product_size_color.quantity
                requested_quantity = int(quantity)

                if requested_quantity > available_quantity:
                    
                    return JsonResponse({'success': False, 'error': 'Insufficient quantity'})

                # Update quantity and save
                item.quantity = requested_quantity
                item.save()

                # Calculate updated total price based on the new quantity
                total_price = item.product.product.price * item.quantity
                item.total_price = total_price
                item.save()

                return JsonResponse({'success': True, 'total_price': total_price})
            
            except Cart.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Cart not found'})
            except CartItem.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'CartItem not found'})
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid quantity value'})
        
        else:
            return JsonResponse({'success': False, 'error': 'User not authenticated'})



def delete_cart(request,cart_id):
        try:
             cart = Cart.objects.get(user=request.user)
             item = CartItem.objects.get(cart=cart, id=cart_id)
             item.delete()
             return redirect('viewcart')
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Cart or item not found'})


def cart_total_view(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
        cart_item=CartItem.objects.filter(cart__user=request.user).order_by('id')
        subtotal =sum(item.total_price for item in cart_item)
        total = cart.Totel() # Assuming you have shipping cost
        return JsonResponse({'subtotal': subtotal, 'total': total})
    else:
        return JsonResponse({'error': 'User not authenticated'})
def checkout(request):
    cart= Cart.objects.get(user=request.user)
    
    print(cart)
    
    item=CartItem.objects.filter(cart__user=request.user).order_by('id')
    context={
            'item':item,
            'cart':cart
        }
        
        

    return render (request,'checkout.html',context)