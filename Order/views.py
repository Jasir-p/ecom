from django.shortcuts import render
from datetime import timedelta, timezone, datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

import random
from django.shortcuts import render, HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from cart.models import *

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


# Create your views here.

def Placed_order(request):
     if request.method == 'POST':
        address_id  = request.POST.get('selectedAddress')
        selected_address =Address.objects.get(id=address_id)
        payment_mode = request.POST.get('payment_mode')
        payment_id = request.POST.get('payment_id')
        # coupon_id = request.POST.get('coupon_id')
        cart = Cart.objects.get(user=request.user)

        cart_items = CartItem.objects.filter(cart__user=request.user)
        total_amount=cart.Totel()

        payment = Payment.objects.create(
            user=request.user, 
            method=payment_mode, 
            amount=total_amount
        )
        for cart_item in CartItem.objects.filter(cart=cart):
            product = cart_item.product
            quantity_ordered = cart_item.quantity

            # Retrieve product size color
            product_size_colors = ProductSizeColor.objects.filter(product=product)
            if product_size_colors.exists():
                product_size_color = product_size_colors.first()
                if product_size_color.Stock < quantity_ordered:
                    messages.error(request, f"Sorry, '{product.product_name}' is out of stock.")
                    return redirect('Cart:view_cart')
                # Update product stock
                product_size_color.Stock = F('Stock') - quantity_ordered
                product_size_color.save()
                OrderProduct.objects.create(order=order, product=product, quantity=quantity_ordered)

        cart.delete()

        # Optionally, you can return a success response
        return JsonResponse({'status': 'success'})
    return render
