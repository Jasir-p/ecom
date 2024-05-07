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
from cart.urls import *
from Admin.urls import *

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

from django.db.models import F
import random
import time
import secrets
import string
import razorpay
from django.conf import settings
from decimal import Decimal
# Create your views here.


razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET)
)

def place_order(request):
    if request.method == "POST":
        try:
            address_id = request.POST.get("address")
        except:
            messages.error("please select an address")
            return redirect("checkout")

        selected_address = Address.objects.get(id=address_id)
        payment_mode = request.POST.get("payment_method")
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart__user=request.user)
        total_amount = cart.Totel()

        if payment_mode == 'Cash on Delivery':
            # Create Payment record for COD
            payment = Payment.objects.create(
                user=request.user, method=payment_mode, amount=total_amount
            )
            # Create Order
            order = Order.objects.create(
                user=request.user,
                payment=payment,
                total_amount=total_amount,
                payment_method=payment_mode,
                coupon_id=cart.coupon.discount if cart.coupon else None,
                order_id=generate_order_id(),
                name=selected_address.name,
                address=selected_address.address,
                House_no=selected_address.House_no,
                city=selected_address.city,
                state=selected_address.state,
                country=selected_address.country,
            )

            # Process Cart Items
            for cart_item in cart_items:
                product = cart_item.product
                prod = Color_products.objects.get(id=product.id)
                quantity_ordered = cart_item.quantity
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
                    quantity=quantity_ordered,
                    size=product_size_colors,
                    trackig_id=generate_tracking_id(),
                )

            cart_items.delete()
            # Redirect to confirmation page
            return redirect("confirm")

        elif payment_mode == 'Razorpay':
            currency = "INR"
            amount = total_amount * 100 
            amount_str = int(amount) # Convert to paisa (Razorpay expects amount in smallest currency unit)

            # Create a Razorpay Order
            razorpay_order = razorpay_client.order.create(
                dict(amount=amount_str, currency=currency, payment_capture="0")
            )

            # Order id of newly created order
            razorpay_order_id = razorpay_order["id"]
            callback_url = "paymenthandler/"

            # Pass these details to frontend
            context = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_merchant_key": "YOUR_KEY",
                "razorpay_amount": amount,
                "currency": currency,
                "callback_url": callback_url
            }

            return render(request, "checkout.html", context)



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
        data = Order.objects.all()
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
        print("hii")
        get_status = request.POST.get("status")
        print(get_status)
        item = OrderProduct.objects.get(id=id)
        item.status = get_status
        item.save()
        return redirect("order_details", item.order.id)






