import re
from django.shortcuts import render
from datetime import date, timedelta, timezone, datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction

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

    def post(self, request, id):

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=request.user)

        size = request.POST.get("size")

        product = Color_products.objects.get(id=id)
        try:
            size_instance = size_variant.objects.get(id=size)
        except size_variant.DoesNotExist:
            messages.warning(request, "Select a size")
            return redirect("shopdetails", id)

        existing_cart_item = CartItem.objects.filter(cart=cart, product=product)
        if existing_cart_item:
            messages.warning(request, "Item already in the cart")
            return redirect("viewcart")

        cart_item = CartItem.objects.create(
            cart=cart, product=product, product_size_color=size_instance
        )
        cart_item.save()
        cart.save()
        messages.success(request, "Product succesfully added")
        return redirect("shopdetails", id)


class Viewcart(View):
    def get(self, request):
        try:
            cart1 = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            cart1 = Cart.objects.create(user=request.user)

       
        if cart1.coupon_applied:
            coupon_instance = cart1.coupon
            with transaction.atomic():
                if coupon_instance:
                    
                    current_total = cart1.update_total_amount()
                    if current_total != cart1.total_amount:
                        CustomerCoupon.objects.get(coupon__id=coupon_instance.pk).delete()
                       
                        coupon_instance.is_active = False
                        coupon_instance.save()
                        cart1.coupon_applied = False
                        cart1.coupon = None
                        cart1.save()
                        
 
        cart = CartItem.objects.filter(cart__user=request.user).order_by("id")
        total = 0
        for i in cart:
            total = 0
            if i.product.product.offer_price>0:
                    total= i.product.product.offer_price * i.quantity
            else:
                    total += i.product.product.price * i.quantity
            
            i.total_price = total
            i.save()

        cart1.total_amount = sum(item.total_price for item in cart)
        cart1.save()
        context = {"cart1": cart1, "cart": cart}

        return render(request, "shopping-cart.html", context)


class UpdateCartView(View):
    def post(self, request):
        # Ensure the user is authenticated
        if request.user.is_authenticated:
            product_id = request.POST.get("product_id")
            quantity = request.POST.get("quantity")

            try:
                # Retrieve the cart and item
                cart = Cart.objects.get(user=request.user)
                item = CartItem.objects.get(cart=cart, id=product_id)

                # Check if the requested quantity is available
                available_quantity = item.product_size_color.quantity
                requested_quantity = int(quantity)
                print(available_quantity, requested_quantity)

                if requested_quantity > available_quantity:
                    print("aksjnf")
                    return JsonResponse(
                        {"success": False, "error": "Insufficient quantity"}
                    )

                # Update quantity and save
                item.quantity = requested_quantity
                item.save()

                # Calculate updated total price based on the new quantity
                if item.product.product.offer_price>0:
                    total_price = item.product.product.offer_price * item.quantity
                else:
                    total_price = item.product.product.price * item.quantity
                
                
                item.total_price = total_price
                item.save()

                return JsonResponse({"success": True, "total_price": total_price})

            except Cart.DoesNotExist:
                return JsonResponse({"success": False, "error": "Cart not found"})
            except CartItem.DoesNotExist:
                return JsonResponse({"success": False, "error": "CartItem not found"})
            except ValueError:
                return JsonResponse(
                    {"success": False, "error": "Invalid quantity value"}
                )

        else:
            return JsonResponse({"success": False, "error": "User not authenticated"})


def delete_cart(request, cart_id):
    try:
        cart = Cart.objects.get(user=request.user)
        item = CartItem.objects.get(cart=cart, id=cart_id)
        item.delete()
        return redirect("viewcart")
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return JsonResponse({"success": False, "error": "Cart or item not found"})


def cart_total_view(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.filter(cart__user=request.user).order_by("id")
        subtotal = sum(item.total_price for item in cart_item)
        total = cart.Totel()  # Assuming you have shipping cost
        return JsonResponse({"subtotal": subtotal, "total": total})
    else:
        return JsonResponse({"error": "User not authenticated"})




def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
        address = Address.objects.filter(user=request.user)
        existing_coupons = CustomerCoupon.objects.filter(user=request.user)
        cart.update_total_amount()
        
        if request.method == "POST":
            coupon_code = request.POST.get("coupon_code")
            print(coupon_code)
            print(cart.coupon_applied)
            if not cart.coupon_applied:
                try:
                    coupon = Coupon.objects.get(
                                                    code=coupon_code, 
                                                    start_date__lte=date.today(), 
                                                    end_date__gte=timezone.now()
        )
                    print(coupon)
                    
                except Coupon.DoesNotExist:
                    messages.error(request,"Couopn Does nort exist")
                    return redirect('checkout')

                if coupon and coupon.min_amount<= cart.total_amount:
                    cart.update_total_amount()
                    
                    if not CustomerCoupon.objects.filter(user=request.user, coupon=coupon).exists():
                        cart.total_amount-=coupon.discount_amount
                            
                        cart.coupon = coupon
                        cart.coupon_applied=True
                            
                        cart.save()
                        print(cart.total_amount)
                        CustomerCoupon.objects.create(user=request.user, coupon=coupon)
                            
                        cart.Totel()
                            
                            
                        messages.success(request,"Coupon applyed")
                        return redirect('checkout')
                    else:
                        messages.error(request,"This Coupon already applyed ")
                        return redirect('checkout')
                else:
                    messages.error(request, f"Pls Purchase More than '{str(coupon.min_amount)}'")
                    return redirect('checkout')   
            else:
                messages.error(request,"Only one coupon aplly at a order")
                return redirect('checkout')


        

        item = CartItem.objects.filter(cart__user=request.user).order_by("id")
        context = {
            "item": item,
            "cart": cart,
            "existing_addresses": address,
            "existing_coupons": existing_coupons,
            
        }

        return render(request, "checkout.html", context)
    except:
        return redirect('viewcart')

def coupon_applay(request):
    return redirect('checkout')

def add_coupon(request):

   

        now_date = timezone.now().date()

        if request.method == "POST":
            title = request.POST.get("title")
            code = request.POST.get("code")
            start_date_str = request.POST.get("start_date")
            end_date_str = request.POST.get("end_date")
            quantity = request.POST.get("quantity")
            min_amount = request.POST.get("min_amount")
            discount_amount = request.POST.get("discount_amount")
            active_check = request.POST.get("active")

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if active_check == "1":
                active = True
            else:
                active = False

            if title.isdigit():
                messages.error(request, "Title should not be numbers only")
                return redirect(add_coupon)

            if title.strip() == "":
                messages.error(request, "Please enter Your Coupon title")
                return redirect(add_coupon)

            if code.strip() == "":
                messages.error(request, "Please enter your Coupon code")
                return redirect(add_coupon)

            if end_date < start_date:
                messages.error(request, "End date must be after start date.")
                return redirect(add_coupon)

            if now_date > end_date:
                messages.error(request, "The end date for the coupon cannot be in the past.")
                return redirect(add_coupon)

            if quantity.strip() == "":
                messages.error(request, "Please enter your Quantity")
                return redirect(add_coupon)

            if min_amount.strip() == "":
                messages.error(request, "Please enter your Minimum Amount")
                return redirect(add_coupon)

            if discount_amount.strip() == "":
                messages.error(request, "Please enter your Discount Amount")
                return redirect(add_coupon)
            
            if float(quantity) < 1:
                messages.error(request,'Quantity should be  minimum 1')
                return redirect(add_coupon)
            
            if float(min_amount) < 1:
                messages.error(request,'Not Valid Minimum amount ')
                return redirect(add_coupon)

            if float(discount_amount) < 1:
                messages.error(request,'Not Valid Minimum Discount amount')
                return redirect(add_coupon)
            
            if Coupon.objects.filter(code=code).exists():
                messages.error(request,f'Coupon code "{code}" is already exists!')
                return redirect(add_coupon)
            
            obj = Coupon(
                title=title,
                code=code,
                discount_amount=discount_amount,
                start_date=start_date,
                end_date=end_date,
                quantity=quantity,
                min_amount=min_amount,
                active=active,
            )
            obj.save()
            messages.success(request, f'Coupon "{title}" added successfuly')
            return redirect("add_coupon")

        return render(request, "add_coupon.html")
    

@login_required
def check_update_address(request, address_id):
    
    user = request.user
    address_obj = Address.objects.filter(user=user, id=address_id).first()

    if not address_obj:
        messages.error(request, "Address not found")
        return redirect('checkout')

    if request.method == 'POST':
        name = request.POST.get("name", "").strip()
        address = request.POST.get("address", "").strip()
        house_no = request.POST.get("house_no", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        country = request.POST.get("country", "").strip()
        pincode = request.POST.get("pincode", "").strip()

        if not all([name, address, house_no, city, state, country, pincode]):
            messages.error(request, "Please provide all fields")
            return redirect('edit_adress', address_id=address_id)

        indian_state = [
            "Andaman and Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh",
            "Assam", "Bihar", "Chandigarh", "Chhattisgarh", "Dadra and Nagar Haveli and Daman and Diu",
            "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand",
            "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
            "Mizoram", "Nagaland", "Odisha", "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
            "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        ]

        if state.casefold() not in [state_name.casefold() for state_name in indian_state]:
            messages.error(request, "Please provide a valid state")
            return redirect('edit_adress', address_id=address_id)

        if not re.match(r'^[1-9][0-9]{5}$', pincode):
            messages.error(request, 'Invalid pincode format. Please enter a valid Indian pincode.')
            return redirect('edit_adress', address_id=address_id)

        address_obj.name = name
        address_obj.address = address
        address_obj.House_no = house_no
        address_obj.city = city
        address_obj.state = state
        address_obj.country = country
        address_obj.pincode = pincode
        address_obj.save()

        messages.success(request, "Address updated successfully")
        return redirect('checkout')

    return render(request, 'edit_check_address.html', {'address': address_obj})
def view_admin_coupon(request):
    coupons=Coupon.objects.all()
    return render(request,'view_coupons.html',{'coupons':coupons})
def check_add_address(request):
    if request.method == "POST":
        user = request.user
        name = request.POST.get("name", "").strip()
        address = request.POST.get("address", "").strip()
        house_no = request.POST.get("house_no", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        country = request.POST.get("country", "").strip()
        pincode = request.POST.get("pincode", "").strip()

        print(name,address,house_no,city,state)
        
        if not all([name, address, house_no, city, state, country, pincode]):
            print('hi')
            messages.error(request, "pls provide all field ")
            return redirect('check_add_address')
        indian_state=[
                "Andaman and Nicobar Islands","Andhra Pradesh","Arunachal Pradesh",
                "Assam","Bihar","Chandigarh","Chhattisgarh","Dadra and Nagar Haveli and Daman and Diu",
                "Delhi","Goa","Gujarat","Haryana","Himachal Pradesh","Jammu and Kashmir","Jharkhand",
                "Karnataka","Kerala","Ladakh","Lakshadweep","Madhya Pradesh","Maharashtra","Manipur","Meghalaya",
                "Mizoram","Nagaland","Odisha","Puducherry","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana",
                "Tripura","Uttar Pradesh","Uttarakhand","West Bengal",
            ]
        if state.casefold() not in [state_name.casefold() for state_name in indian_state]:
            messages.error(request, "pls provide valid state ")
            return redirect('check_add_address')
        if not re.match(r'^[1-9][0-9]{5}$', pincode):
            messages.error(request,'Invalid pincode format. Please enter a valid Indian pincode.')
            return redirect('check_add_address')
        address_obj = Address.objects.create(
            user=user,
            name=name,
            address=address,
            House_no=house_no,
            city=city,
            state=state,
            country=country,
            pincode=pincode,
        )
        address_obj.save()
        messages.success(request, "Address added successfully")
        print("hiiiiiii")
        return redirect('checkout')
    
    
    

    return render(request,'checkout_add_adress.html')