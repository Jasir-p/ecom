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
from django.urls import reverse

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
    # try:
        if request.method == "POST":
            try:
                address_id = request.POST.get("address")
                selected_address = Address.objects.get(id=address_id)
                
            except:
                messages.error(request,"please select a address")
                return redirect("checkout")
            

            
            payment_mode = request.POST.get("payment_method")
            
            # payment_id = request.POST.get('payment_id')
            # coupon_id = request.POST.get('coupon_id')
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart__user=request.user)
            if payment_mode == 'Cash On Delivery':
                
             
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
                    coupon_amount=cart.coupon.discount_amount if cart.coupon else None,
                    min_amount=cart.coupon.min_amount if cart.coupon else None,
                    shipping_charge=cart.shipping_charge,
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
                    
                    if prod.product.offer_price  is not None:
                       prices = prod.product.offer_price
                    else:
                        prices = prod.product.price
                    
                    size = cart_item.product_size_color.id
                    
                    product_size_colors = size_variant.objects.get(id=size)

                    if product_size_colors.quantity < quantity_ordered or prod.is_listed == False:
                        order.delete()
                        payment.delete()
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
                        status= 'Processing',
                        trackig_id=generate_tracking_id(),
                    )

                cart_items.delete()
                cart.delete()
                return render(request, "confirm.html",{'order':order})

            
            elif payment_mode == "Razorpay":

                
                payment_status = request.POST.get('payment_status')
                failure_reason = request.POST.get('failure_reason')
                payment_failed=True if payment_status =="failed" else False
                
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
                    coupon_amount=cart.coupon.discount_amount if cart.coupon else None,
                    min_amount=cart.coupon.min_amount if cart.coupon else None,
                    shipping_charge=cart.shipping_charge,
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
                    if prod.product.offer_price  is not None :
                       prices = prod.product.offer_price
                    else:
                        prices = prod.product.price

                    
                    product_size_colors = size_variant.objects.get(id=size)

                    if product_size_colors.quantity < quantity_ordered:
                        order.delete()
                        payment.delete()
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
                        status='Processing' if not payment_failed else 'Pending',
                        size=product_size_colors,
                        trackig_id=generate_tracking_id(),
                    )

                cart_items.delete()
                cart.delete()
                
                return render(request, "confirm.html",{'payment_failed': payment_failed,'order':order})
            elif payment_mode == "Wallet":

                
                wallet=Wallet.objects.get(user=request.user)
                wallet_user, created = Wallet.objects.get_or_create(user=request.user)
           
            

            
           
                
                
                total_amount = cart.Totel()
                if wallet.balance >= total_amount:
                    wallet_user.balance -= total_amount
                    
            
                
                    payment = Payment.objects.create(   
                            user=request.user, method=payment_mode, amount=total_amount, status='success' 
                        )
                    
                    
                
                    order = Order.objects.create(
                        user=request.user,
                        payment=payment,
                        total_amount=total_amount,
                        payment_method=payment_mode,
                        coupon_id=cart.coupon.code if cart.coupon else None,
                        coupon_amount=cart.coupon.discount_amount if cart.coupon else None,
                        min_amount=cart.coupon.min_amount if cart.coupon else None,
                        shipping_charge=cart.shipping_charge,
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
                        if prod.product.offer_price  is not None :
                            prices = prod.product.offer_price
                        else:
                            prices = prod.product.price

                        
                        product_size_colors = size_variant.objects.get(id=size)

                        if product_size_colors.quantity < quantity_ordered:
                            order.delete()
                            payment.delete()

                            messages.error(
                                request, f"Sorry, '{product.product.name}' is out of stock."
                            )
                            return redirect("viewcart")
                        
                        product_size_colors.quantity = F("quantity") - quantity_ordered
                        product_size_colors.save()
                        order_item=OrderProduct(
                            order=order,
                            product=prod,
                            quantity=quantity_ordered,
                            price=prices,
                            status='Processing',
                            size=product_size_colors,
                            trackig_id=generate_tracking_id(),
                        )
                        transaction_id = str(uuid.uuid4())
                        Wallet_transaction.objects.create(
                        wallet=wallet_user,
                        transaction_id=transaction_id,
                        money_withdrawn=total_amount

                        )
                        order_item.save()
                        order.save()
                        wallet_user.save()
                        
                    
                    cart_items.delete()
                    cart.delete()
                    
                    return render(request, "confirm.html",{'order':order})
                messages.error(request,'Wallet has insufficient funds')
        
        return redirect("checkout")
    # except Exception as e :
    #     print(e)
        
    #     messages.error(request,e)
    #     return redirect("checkout")
       
        


        


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
        order_products = OrderProduct.objects.filter(order__id=id).exclude(status__in=['Cancelled', 'Returned'])
   
        totel_amount=order_products.annotate(totel_price=F('quantity')* F('price')).aggregate(totel_sum=Sum('totel_price'))['totel_sum'] or 0
        

        return render(request, "order_items.html", {"data": data, "Address": order,'totel_amount':totel_amount})
    return redirect("adminlogin")


@never_cache
def Confirm(request):

    return render(request, "confirm.html")



def status(request, id):
    if request.method == "POST":
        get_status = request.POST.get("status")
        

        item = get_object_or_404(OrderProduct, id=id)
        order = item.order
        size = get_object_or_404(size_variant, id=item.size.pk)
        payment = get_object_or_404(Payment, pk=item.order.payment.pk)
        print(order.shipping_charge)

        if get_status in ['Cancelled', 'Returned']:
            with transaction.atomic():
                print(size.quantity)
                size.quantity += item.quantity
                
                

                item_total = item.quantity * item.price

                Quantity = OrderProduct.objects.filter(order__id=order.id).exclude(status__in=['Cancelled', 'Returned']).count() == 1

                print(Quantity)
                    

                if order.payment_method == "Razorpay" or order.payment_method == "Wallet" or get_status=='Returned':
                    wallet = get_object_or_404(Wallet, user=order.user)
                    if payment.status=="success":
                        if Quantity:
                            print("hiii")
                            print(order.total_amount)
                            refund_amount = order.total_amount
                            order.total_amount =0
                            payment.amount=0
                            payment.status="Cancelled"
                            if order.coupon_id:
                                coupon = get_object_or_404(Coupon, code=order.coupon_id)
                                order.coupon_id=None
                                CustomerCoupon.objects.get(user=order.user,coupon__id=coupon.pk).delete()
                        else:
                            order.total_amount -= item_total
                            payment.amount-=item_total
                            if order.coupon_id:
                                coupon = get_object_or_404(Coupon, code=order.coupon_id)
                                shipping=50 if order.shipping_charge else 0
                                print(shipping)
                                
                                if order.total_amount -shipping < order.min_amount:
                                    order.coupon_id=None
                                    refund_amount = item_total - order.coupon_amount
                                    order.total_amount +=  order.coupon_amount
                                    payment.amount+=item_total
                                
                                    CustomerCoupon.objects.get(user=order.user,coupon__id=coupon.pk).delete()
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
                            if order.coupon_id:

                                coupon = get_object_or_404(Coupon, code=order.coupon_id)
                                CustomerCoupon.objects.get(user=order.user,coupon__id=coupon.pk).delete()
                                order.coupon_id=None
                        else:
                            order.total_amount -= item_total
                            payment.amount-=item_total
                            if order.coupon_id:
                                coupon = get_object_or_404(Coupon, code=order.coupon_id)
                                if order.total_amount < order.min_amount:
                                    refund_amount = item_total - order.coupon_amount
                                    order.total_amount +=  order.coupon_amount
                                    payment.amount+=item_total
                                    
                                    CustomerCoupon.objects.get(user=order.user,coupon__id=coupon.pk).delete()
                                    order.coupon_id=None
                                    
                                    payment.amount-=order.total_amount

                    order.save()
                    payment.save()
                    item.status = get_status
                    item.save()
                   
        
                
        else:
            if get_status =='Delivered':
                payment.status="success"
                payment.save()     
            item.status = get_status
            item.save()
        print(size.quantity)
            

        return redirect("order_details", item.order.id)





def generate_short_uuid():
    uuid_str = str(uuid.uuid4())
    
    truncated_uuid = uuid_str[:8]  
    return truncated_uuid

def retry_payment(request,id):
    
        print(id)
        
        order=Order.objects.get(id=id)
        
        payment=Payment.objects.get(id=order.payment.pk)
        amount=int(order.total_amount)
        print(amount)
        trans_id=razar_payment(amount)

        if  trans_id is not None:
            payment.status="success"
            payment.Transaction_id=trans_id
            OrderProduct.objects.filter(order__id=order.id).update(status='Processing')
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
