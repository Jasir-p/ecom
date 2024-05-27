from django.shortcuts import render
from datetime import timedelta, timezone, datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from decimal import Decimal

import random
from django.shortcuts import render, HttpResponse
from django.contrib import messages
from django.db.models import Q,Count
from django.http import JsonResponse
from cart.models import *
from cart.urls import *
from Admin.urls import *

from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login as log, logout as authlogout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control

from django.shortcuts import get_object_or_404, redirect
from django.db import transaction

from django.utils import timezone
from Userapp.models import CustomUser,Wallet,Wallet_transaction
from Userapp.urls import *
from django.utils.translation import gettext as _
from django.core.files.uploadedfile import UploadedFile
from django.http import JsonResponse
import uuid
from django.db.models import F
import random
import time
import secrets
import string
import razorpay
from django.conf import settings

# Create your views here.
razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
def initiate_payment(items):
    data = {
        "currency": "INR",
        "payment_capture": "1",
        "amount": items[0]["amount"] * 100,
    }

    razorpay_order = razorpay_client.order.create(data=data)
    razorpay_order_id = razorpay_order["id"]
    for item in items:
        item_data = {
            "amount": item["amount"] * 100,
            "currency": "INR",
        }
    razorpay_client.order.create(data=item_data)
    return razorpay_order_id
        

def Placed_order(request):
    try:
        if request.method == "POST":
            try:
                address_id = request.POST.get("address")
            except:
                messages.error("please select a address")
                return redirect("checkout")
            

            selected_address = Address.objects.get(id=address_id)
            payment_mode = request.POST.get("payment_method")
            
            # payment_id = request.POST.get('payment_id')
            # coupon_id = request.POST.get('coupon_id')
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart__user=request.user)
            if payment_mode == 'Cash On Delivery':
                print("hi")
             
                total_amount = cart.Totel()
                
                payment = Payment.objects.create(
                    user=request.user, method=payment_mode, amount=total_amount
                )
                
                order = Order.objects.create(
                    user=request.user,
                    payment=payment,
                    total_amount=total_amount, 
                    payment_method=payment_mode,
                    coupon_id=cart.coupon.code if cart.coupon else None,
                    order_id=generate_order_id(),
                    name=selected_address.name,
                    address=selected_address.address,
                    House_no=selected_address.House_no,
                    city=selected_address.city,
                    state=selected_address.state,
                    country=selected_address.country,
                )

                for cart_item in CartItem.objects.filter(cart=cart):
                    product = cart_item.product
                    prod = Color_products.objects.get(id=product.id)
                    quantity_ordered = cart_item.quantity
                    
                    if prod.product.offer_price > 0:
                       prices = prod.product.offer_price
                    else:
                        prices = prod.product.price
                    
                    size = cart_item.product_size_color.id
                    
                    product_size_colors = size_variant.objects.get(id=size)

                    if product_size_colors.quantity < quantity_ordered:
                        messages.error(
                            request, f"Sorry, '{product.product.name}' is out of stock."
                        )
                        return redirect("viewcart")
                   
                    product_size_colors.quantity = F("quantity") - quantity_ordered
                    product_size_colors.save()
                    
                    OrderProduct.objects.create(
                        order=order,
                        product=prod,
                        price=prices,
                        quantity=quantity_ordered,
                        size=product_size_colors,
                        trackig_id=generate_tracking_id(),
                    )

                cart_items.delete()
                cart.delete()
                return redirect("confirm")

            
            elif payment_mode == "Razorpay":
                print(payment_mode)
                payment_status = request.POST.get('payment_status')
                failure_reason = request.POST.get('failure_reason')
                print(payment_status,failure_reason)
                total_amount = cart.Totel()
                if payment_status == "success":
                    items = [
                        {
                            "amount": int(total_amount) * 100,
                        }
                    ]
                    order_id = initiate_payment(items)
                    if order_id is None:
                        messages.error(request, "Payment initiation failed. Please try again.")
                        return redirect("checkout")
                
                    payment = Payment.objects.create(   
                        user=request.user, method=payment_mode, amount=total_amount,Transaction_id=order_id, status=payment_status 
                    )
                else:
                    payment = Payment.objects.create(   
                        user=request.user, method=payment_mode, amount=total_amount, status=payment_status 
                    )
                
                
            
                order = Order.objects.create(
                    user=request.user,
                    payment=payment,
                    total_amount=total_amount,
                    payment_method=payment_mode,
                    coupon_id=cart.coupon.code if cart.coupon else None,
                    order_id=generate_order_id(),
                    name=selected_address.name,
                    address=selected_address.address,
                    House_no=selected_address.House_no,
                    city=selected_address.city,
                    state=selected_address.state,
                    country=selected_address.country,
                )

                for cart_item in CartItem.objects.filter(cart=cart):
                    product = cart_item.product
                    prod = Color_products.objects.get(id=product.id)
                    quantity_ordered = cart_item.quantity
                    size = cart_item.product_size_color.id
                    if prod.product.offer_price > 0:
                       prices = prod.product.offer_price
                    else:
                        prices = prod.product.price

                    
                    product_size_colors = size_variant.objects.get(id=size)

                    if product_size_colors.quantity < quantity_ordered:

                        messages.error(
                            request, f"Sorry, '{product.product.name}' is out of stock."
                        )
                        return redirect("viewcart")
                    
                    product_size_colors.quantity = F("quantity") - quantity_ordered
                    product_size_colors.save()
                    OrderProduct.objects.create(
                        order=order,
                        product=prod,
                        quantity=quantity_ordered,
                        price=prices,
                        size=product_size_colors,
                        trackig_id=generate_tracking_id(),
                    )

                cart_items.delete()
                cart.delete()
                return redirect("confirm")
        
        return redirect("checkout")
    except Exception as e :
        print(str(e))
        messages.error(request,e)
        return redirect("checkout")
       
        


        


def generate_tracking_id():

    fixed_chars = "HP"
    max_unique_id_length = 20 - len(fixed_chars)
    unique_id = str(int(time.time())) + str(random.randint(10000, 99999))
    unique_id = unique_id[:max_unique_id_length]
    tracking_id = fixed_chars + unique_id
    return tracking_id


# Generate a tracking ID


def generate_order_id(length=8):

    digits = string.digits

    first_two_chars = "OID"

    remaining_chars = "".join(secrets.choice(digits) for i in range(length - 3))

    order_id = first_two_chars + remaining_chars
    while Order.objects.filter(order_id=order_id).exists():
        remaining_chars = "".join(secrets.choice(digits) for i in range(length - 3))
        order_id = first_two_chars + remaining_chars

    return order_id


@never_cache
@login_required(login_url="adminlogin")
def order_management(request):

    if request.user.is_superuser:
        data = Order.objects.all().order_by('-id')
        return render(request, "Order_management.html", {"data": data})
    return redirect("adminlogin")


@never_cache
@login_required(login_url="adminlogin")
def order_details(request, id):
    if request.user.is_superuser:
        data = OrderProduct.objects.filter(order__id=id)
        order = Order.objects.get(id=id)
        print(data)

        return render(request, "order_items.html", {"data": data, "Address": order})
    return redirect("adminlogin")


@never_cache
def Confirm(request):

    return render(request, "confirm.html")



def status(request, id):
    if request.method == "POST":
        get_status = request.POST.get("status")
        print(get_status)

        item = get_object_or_404(OrderProduct, id=id)
        order = item.order
        size = get_object_or_404(size_variant, id=item.size.pk)
        payment = get_object_or_404(Payment, pk=item.order.payment.pk)

        if get_status in ['Cancelled', 'Returned']:
            with transaction.atomic():

                size.quantity += item.quantity
                size.save()

                item_total = item.quantity * item.price

                Quantity = OrderProduct.objects.filter(order=order).exclude(status__in=['Cancelled', 'Returned']).count() == 1

               
                    

                if order.payment_method == "Razorpay" and payment.status=="success":
                    wallet = get_object_or_404(Wallet, user=order.user)

                    if Quantity:
                        
                        refund_amount = order.total_amount
                        order.total_amount =0
                        payment.amount=0
                        payment.status="Cancelled"
                    else:
                        order.total_amount -= item_total
                        payment.amount-=item_total
                        if order.coupon_id:
                            coupon = get_object_or_404(Coupon, code=order.coupon_id)
                            if order.total_amount < coupon.min_amount:
                                refund_amount = item_total - coupon.discount_amount
                            else:
                                refund_amount = item_total
                        else:
                            refund_amount = item_total
                        
                    wallet.balance += refund_amount
                    transaction_id = str(uuid.uuid4())

                    Wallet_transaction.objects.create(
                        wallet=wallet,
                        transaction_id=transaction_id,
                        money_deposit=refund_amount
                    )
                    wallet.save()
                else:
                    if Quantity:
                        
                        refund_amount = order.total_amount
                        order.total_amount =0
                        payment.amount=0
                        payment.status="Cancelled"
                    else:
                        order.total_amount -= item_total
                        payment.amount-=item_total
                        if order.coupon_id:
                            coupon = get_object_or_404(Coupon, code=order.coupon_id)
                            if order.total_amount < coupon.min_amount:
                                order.total_amount -= item_total-coupon.discount_amount
                                payment.amount-=order.total_amount
                                
                        



                order.save()
                payment.save()
        item.status = get_status
        item.save()

        return redirect("order_details", item.order.id)





def generate_short_uuid():
    uuid_str = str(uuid.uuid4())
    
    truncated_uuid = uuid_str[:8]  
    return truncated_uuid

def retry_payment(request,id):
    if request.method =="POST":
        print("hii")
        order=Order.objects.get(id=id)
        payment=Payment.objects.get(id=order.payment.pk)
        amount=int(order.total_amount)
        trans_id=razar_payment(amount)

        if  trans_id is not None:
            payment.status="success"
            payment.Transaction_id=trans_id
            payment.save()




    return redirect('user_order')
def razar_payment(items):
    data = {
        "currency": "INR",
        "payment_capture": "1",
        "amount": items * 100,
    }

    razorpay_order = razorpay_client.order.create(data=data)
    razorpay_order_id = razorpay_order["id"]
    
    item_data = {
            "amount": items * 100,
            "currency": "INR",
        }
    razorpay_client.order.create(data=item_data)
    return razorpay_order_id
