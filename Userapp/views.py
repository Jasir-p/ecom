from datetime import date, timedelta, timezone, datetime
import http
from django.template.loader import render_to_string
import re
import time
import uuid
from django.core.paginator import Paginator

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
import random
from django.shortcuts import render, HttpResponse
from django.contrib import messages
from django.db.models import Q

from django.shortcuts import render, redirect

from shopifyproject import settings
from .models import *
from django.contrib.auth import authenticate, login, logout as authlogout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control
from django.core.mail import send_mail
from shopifyproject.settings import EMAIL_HOST_USER
from django.core.validators import EmailValidator
from django.utils import timezone
from Products.models import *
from django.http import JsonResponse
from Admin.models import *
from cart.models import *
from django.contrib.auth.hashers import check_password
from django.db.models import Sum, F, Case, When, Value
from django.db.models.functions import Coalesce
from Order.models import *
from Offer.models import Offer
import razorpay
from weasyprint import HTML
import os

# Create your views here.
@never_cache
def user_login(request):
    if request.user.is_authenticated:
        return redirect("user_home")
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("user_home")
            else:

                messages.error(request, "incorrect username or password")

        except Exception as e:
            messages.error(str(e))
    return render(request, "userlogin.html")


def user_signup(request):
    try:

        if request.method == "POST":

            username = request.POST.get("name")
            password = request.POST.get("password")
            number = request.POST.get("number")
            email = request.POST.get("email")
            refarel=request.POST.get("referral_code")

            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, "The username is already taken")
                return redirect("SignUp")

            elif not username.strip():
                messages.error(request, "The username is not valid")
                return redirect("SignUp")

            elif CustomUser.objects.filter(email=email).exists():
                messages.error(request, "The email is already taken")
                return redirect("SignUp")
            elif not is_valid_email(email):
                messages.error(request, "The email is not valid")
                return redirect("SignUp")
            elif not validate_mobile_number(number):
                messages.error(request, "The Mobail number is not valid")
                return redirect("SignUp")
            elif len(password) < 6:
                messages.error(request, "The password should be at least 6 characters")
                return redirect("SignUp")

            elif not any(char.isupper() for char in password):
                messages.error(
                    request, "Password must contain at least one uppercase letter"
                )
                return redirect("SignUp")
            elif not any(char.islower() for char in password):  # Corrected condition
                messages.error(
                    request, "Password must contain at least one lowercase letter"
                )
                return redirect("SignUp")
            elif not any(char.isdigit() for char in password):
                messages.error(request, "Password must contain at least one digit")
                return redirect("SignUp")

            else:
                request.session["name"] = username
                request.session["password"] = password
                request.session["phone"] = number
                request.session["email"] = email
                request.session["refaral"]=refarel

                generate_otp_and_send_email(request, email)

                return redirect(otp)

        return render(request, "usersignup.html")
    except Exception as e:
        messages.error(request, e)
        return redirect("SignUp")


@never_cache
def user_home(request):

    product = Color_products.objects.filter(is_listed=True).distinct("product")[:4]
    product_new=Color_products.objects.filter(is_listed=True).order_by('-id')[:4]

    new=product_new
    context={
        "product": product,
        "new":new,


    }
    

    return render(request, "index.html",context)


def generate_otp_and_send_email(request, email):
    otp = random.randint(1000, 9999)
    otp_generated_at = datetime.now().isoformat()
    print(otp)

    request.session["otp"] = otp
    request.session["time"] = otp_generated_at

    send_mail(
        subject="Welcome",
        message=f"Your OTP for verification is: {otp}",
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )


def otp(request):
    if request.method == "POST":
        otp1 = request.POST.get("otp1")
        otp2 = request.POST.get("otp2")
        otp3 = request.POST.get("otp3")
        otp4 = request.POST.get("otp4")

        full_otp = otp1 + otp2 + otp3 + otp4
        print("Full OTP entered:", full_otp)

        if "otp" in request.session:
            otp = request.session["otp"]
            otp_generated = request.session["time"]
            delta = timedelta(minutes=2)
            time = datetime.fromisoformat(otp_generated)

            print("Current time:", datetime.now())
            print("OTP generated time:", time)
            
            if datetime.now() <= time + delta:
                print("OTP is within the valid time frame.")

                if int(full_otp) == otp:
                    print("OTP is correct.")

                    try:
                        
                        # print("Generated referral code:", referral_code)
                        print('11')
                        ref=refreal_genarate()
                        print(ref)
                        new_user = CustomUser.objects.create_user(
                            username=request.session["name"],
                            password=request.session["password"],
                            email=request.session["email"],
                            phone=request.session["phone"],
                            referal_code=ref,
                        )
                        print('11')
                        print("New user created:", new_user)
                        refaral=request.session["refaral"]
                        if refaral:

                            Ref_user = CustomUser.objects.get(referal_code=request.session["refaral"])
                            print("Referral user found:", Ref_user)

                            if Ref_user is not None:
                                new_user_wallet = Wallet.objects.get(user=new_user)
                                print("New user wallet found:", new_user_wallet)
                                
                                new_user_wallet.balance += 30
                                new_user_wallet.save()
                                print("New user wallet updated with referral deposit.")

                                Wallet_transaction.objects.create(
                                    wallet=new_user_wallet,
                                    transaction_id=generate_unique_transaction_id(),
                                    referral_deposit=30
                                )
                                print("New user wallet transaction created.")

                                ref_user_wallet = Wallet.objects.get(user=Ref_user)
                                print("Referral user wallet found:", ref_user_wallet)

                                ref_user_wallet.balance += 50
                                ref_user_wallet.save()
                                print("Referral user wallet updated with referral deposit.")

                                Wallet_transaction.objects.create(
                                    wallet=ref_user_wallet,
                                    transaction_id=generate_unique_transaction_id(),
                                    referral_deposit=50
                                )
                                Myrefaral.objects.create(
                                    user=Ref_user,
                                    user_name=new_user.username,

                                )

                                print("Referral user wallet transaction created.")

                        # Clean up session data
                        request.session.pop("name")
                        request.session.pop("password")
                        request.session.pop("email")
                        request.session.pop("phone")

                        messages.success(request, "Registered successfully")
                        return redirect("login")

                    except CustomUser.DoesNotExist:
                        print("Referral user does not exist.")
                        messages.error(request, "Referral user does not exist.")
                        return redirect("otp")

                    except Wallet.DoesNotExist:
                        print("Wallet does not exist for the user.")
                        messages.error(request, "Wallet does not exist for the user.")
                        return redirect("otp")

                    except Exception as e:
                        print("Error occurred:", e)
                        messages.error(request, "An error occurred during registration. Please try again.")
                        return redirect("otp")

                else:
                    messages.error(request, "Incorrect OTP! Please try again.")
                    return redirect("otp")
            else:
                print("OTP has expired.")
                messages.error(request, "OTP has expired. Please request a new one.")
                return redirect("otp")
        else:
            print("OTP not found in session.")
            messages.error(request, "OTP session has expired or not set. Please request a new one.")
            return redirect("otp")
    else:
        return render(request, "otp.html")

def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def validate_mobile_number(mobile_number):

    pattern = re.compile(r"^[6-9]\d{9}$")

    if pattern.match(mobile_number):
        return True
    else:
        return False


def logout(request):
    authlogout(request)
    return redirect("user_home")


def resend_otp(request):

    otp = random.randint(1000, 9999)
    otp_generated_at = datetime.now().isoformat()
    print(otp)
    
    request.session["otp"] = otp
    request.session["time"] = otp_generated_at
    email = request.session["email"]

    send_mail(
        subject="Welcome",
        message=f"Your OTP for verification is: {otp}",
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )
    return redirect("otp")

def refreal_genarate():
    fixed_chars = "HP"
    max_unique_id_length = 6 - len(fixed_chars)
    check = True
    
    while check:
        # Generate a unique ID using UUID and get a part of it
        unique_id = str(uuid.uuid4().int)[:max_unique_id_length]
        referral_code = fixed_chars + unique_id
        
        
        
        if not CustomUser.objects.filter(referal_code=referral_code).exists():
            check = False
            return referral_code

    return None

        

def generate_unique_transaction_id():
    fixed_chars = "RF"
    max_unique_id_length = 8 - len(fixed_chars)
    
    while True:
        # Generate a unique ID using UUID and get a part of it
        unique_id = str(uuid.uuid4().int)[:max_unique_id_length]
        transaction_id = fixed_chars + unique_id
        
        
        if not Wallet_transaction.objects.filter(transaction_id=transaction_id).exists():
            return transaction_id
    
@never_cache
@login_required(login_url="login")
def shop(request):

    try:
        products = (
            Color_products.objects.select_related("product")
            .filter(is_listed=True)
            .distinct("product")
        )


        page_number = request.GET.get('page')
        paginator = Paginator(products, 9) 
        page_obj = paginator.get_page(page_number)

        category = Catagory.objects.filter(is_listed=True)
        brand = Brand.objects.filter(is_listed=True)

        return render(
            request,
            "shop.html",
            {"page_obj": page_obj, "category": category, "brand": brand},
        )
    except Exception as e:
        return render(request, "shop.html", {"error": str(e)})


@never_cache
@login_required(login_url="login")
def shopdetails(request, p_id):
    
    data = Color_products.objects.get(id=p_id)
    products=Product.objects.get(id=data.product.id)

    item = Color_products.objects.filter(product=data.product.id, is_listed=True)
    total_quantity = data.size.aggregate(total_quantity=Sum("quantity"))["total_quantity"] or 0
    
    return render(
        request,
        "shop-details.html",
        {
            "data": data,
            "item": item,
            "total_quantity": total_quantity,
            # "final_price": final_price,
        },
    )

from django.db.models import OuterRef, Subquery, F

def filterd(request):
    try:
        selected_categories = []
        selected_brands = []
        sort = request.GET.get('option')
        page_number = request.GET.get('page')
       

        # Ensure ordering is initialized
        ordering = 'product__price'

        if request.method == "GET":
            if sort:
                ordering = 'product__price' if sort == 'L' else '-product__price'
            
            selected_category = request.GET.getlist("category")
            selected_brand = request.GET.getlist("brand")

            products = Color_products.objects.filter(is_listed=True)

            if selected_category or selected_brand:
                products = products.filter(
                    Q(product__catagory__in=selected_category) |
                    Q(product__brand__in=selected_brand)
                )

            if selected_category and selected_brand:
                products = products.filter(
                    Q(product__catagory__in=selected_category) &
                    Q(product__brand__in=selected_brand)
                )

            for category_id in selected_category:
                selected_categories.append(int(category_id))
            for brand_id in selected_brand:
                selected_brands.append(int(brand_id))

            subquery = Color_products.objects.filter(
                product_id=OuterRef('product_id')
            ).order_by(ordering).values('id')[:1]

            products = products.filter(id__in=Subquery(subquery)).order_by(ordering)
            paginator = Paginator(products, 9) 
            page_obj = paginator.get_page(page_number)
            categories = Catagory.objects.filter(is_listed=True)
            brands = Brand.objects.filter(is_listed=True)

            context = {
                "page_obj": page_obj,
                "category": categories,
                "brand": brands,
                "selected_categories": selected_categories,
                "selected_brands": selected_brands,
                "sort": sort,
            }

            return render(request, "shop.html", context)
        else:
            return redirect('shop')



    except Exception as e:
        
        return redirect('shop')



    

# def selected_category(request,category):
#       sele
#       if category not
#       return selected_list

@never_cache
@login_required(login_url="login")
def view_address(request):
    address = Address.objects.filter(user=request.user)
    data = CustomUser.objects.get(id=request.user.pk)
    return render(request, "view_address.html", {"Address": address, "data": data})


@never_cache
@login_required(login_url="login")
def add_address(request):

    if request.method == "POST":
        user = request.user
        name = request.POST.get("name", "").strip()
        address = request.POST.get("address", "").strip()
        house_no = request.POST.get("house_no", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        country = request.POST.get("country", "").strip()
        pincode = request.POST.get("pincode", "").strip()

        
        
        if not all([name, address, house_no, city, state, country, pincode]):
            
            messages.error(request, "pls provide all field ")
            return redirect('add_address')
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
            return redirect('add_address')
        if not re.match(r'^[1-9][0-9]{5}$', pincode):
            messages.error(request,'Invalid pincode format. Please enter a valid Indian pincode.')
            return redirect('add_address')
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
    
    
    return render(request, "add_address.html",)


@never_cache
@login_required(login_url="login")
def update_address(request, address_id):
    
    user = request.user
    address_obj = Address.objects.filter(user=user, id=address_id).first()

    if not address_obj:
        messages.error(request, "Address not found")
        return redirect('view_address')

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
        return redirect('view_address')

    return render(request, 'edit_address.html', {'address': address_obj})

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    address.delete()
    return redirect("view_address")

@never_cache
@login_required(login_url="login")
def wish_list(request):
    try:
        
        wish_list = Wishlist.objects.get(customer=request.user)
        wishlist = wish_list.products.annotate(
            total_quantity=Coalesce(Sum("size__quantity"), Value(0)),
            in_stock=Sum(Case(When(size__quantity__gt=0, then=1), default=0, output_field=models.IntegerField())),
        ).annotate(
            stock_status=Case(
                When(in_stock__gt=0, then=Value("In Stock")),
                default=Value("Out of Stock"),
                output_field=models.CharField(),
            ),
        ).filter(is_listed=True).distinct()
        
        return render(request, "wishlist.html", {"wishlist": wishlist})
    except Wishlist.DoesNotExist:
        return render(request, "wishlist.html", {"wishlist": None})

def get_product_sizes(request, product_id):
    product = get_object_or_404(Color_products, id=product_id)
    sizes = product.size.filter(quantity__gt=0)
    size_data = [{"id": size.id, "size": size.size, "quantity": size.quantity} for size in sizes]

    return JsonResponse({"sizes": size_data})



def add_to_wishlist(request, product_id):
    try:
        wishlist= Wishlist.objects.get(customer=request.user)
    except:
        wishlist = Wishlist.objects.create(customer=request.user)
    product = get_object_or_404(Color_products, pk=product_id)

    if wishlist.products.filter(pk=product_id).exists():
        messages.info(request, "This product is already in your wishlist.")
    else:
        wishlist.products.add(product)
        messages.success(request, "Product added to wishlist successfully.")

    return redirect("wishlist")

def Remove_wishlist(request, id):
    wishlist = Wishlist.objects.get(customer=request.user)
    product = Color_products.objects.get(pk=id)
    wishlist.products.remove(product)

    return redirect("wishlist")

def wishlist_to_cart(request, id,size_id):
    if request.method == 'POST':
       
        
        

        

        product = get_object_or_404(Color_products, id=id)
        
        size_instance = get_object_or_404(size_variant, id=size_id)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        

        if CartItem.objects.filter(cart=cart, product=product).exists():
            messages.warning(request, "Item already in the cart")
            return redirect("viewcart")

        CartItem.objects.create(cart=cart, product=product,product_size_color=size_instance)
        
        
        # Return a JSON response indicating success
        return JsonResponse({'success': True})

    else:
        return render(request, "wishlist.html")



@never_cache
@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        Current_password = request.POST.get("old_password")
        New_password = request.POST.get("new_password1")
        New_password2 = request.POST.get("new_password2")

        if not check_password(Current_password, request.user.password):
            messages.error(request, "Current Password is error")
            return redirect("changepassword")
        if not New_password == New_password2:
            messages.error(request, "give passwords missmatch")
            return redirect("changepassword")

        elif not any(char.isupper() for char in New_password2):
            messages.error(
                request, "Password must contain at least one uppercase letter"
            )
            return redirect("changepassword")
        elif not any(char.islower() for char in New_password2):  # Corrected condition
            messages.error(
                request, "Password must contain at least one lowercase letter"
            )
            return redirect("changepassword")
        elif not any(char.isdigit() for char in New_password2):
            messages.error(request, "Password must contain at least one digit")
            return redirect("changepassword")

        request.user.set_password(New_password)
        request.user.save()
        user = authenticate(
            request, username=request.user.username, password=New_password
        )
        login(request, user)

        messages.success(request, "Changed successfully")

    return render(request, "change_password.html")

@never_cache
@login_required(login_url="login")
def user_order(request):
    orders = Order.objects.filter(user=request.user).order_by("-id")
    return render(request, "user_order.html", {"orders": orders})

@never_cache
@login_required(login_url="login")
def view_order_details(request, id):
    data = OrderProduct.objects.filter(order__id=id)
    order_products = OrderProduct.objects.filter(order__id=id).exclude(status__in=['Cancelled', 'Returned'])
    order = Order.objects.get(id=id)
    totel_amount=order_products.annotate(totel_price=F('quantity')* F('price')).aggregate(totel_sum=Sum('totel_price'))['totel_sum'] or 0
    context = {"order": order,'totel_amount':totel_amount}

    return render(request, "view_order_details.html", context)

@never_cache
@login_required(login_url="login")
def order_track(request, id):
    data = OrderProduct.objects.get(id=id)

    return render(request, "order_tracking.html", {"data": data})


def request_status_cancel(request, id):
    if request.method == "POST":
        reason=request.POST.get('reason')
        data = OrderProduct.objects.get(id=id)
        data.request_status = "Cancellation Requested"
        data.cancellation_reason=reason
        data.save()
        return redirect("view_order_details", data.order.id)


def request_status_return(request, id):
    if request.method == "POST":
        data = OrderProduct.objects.get(id=id)
        data.request_status = "Return Requested"
        data.save()
        return redirect("view_order_details", data.order.id)


def error_page(request, exception):
    return render(request, "error_page.html")

@never_cache
@login_required(login_url="login")
def wallet(request):
    try:
        wallet_user=Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        wallet_user=Wallet.objects.create(user=request.user)

    wallet_transc=Wallet_transaction.objects.filter(wallet=wallet_user).order_by("-id")
    return render(request,"wallet.html",{'wallets':wallet_transc,'wallet':wallet_user})

def add_to_wallet(request):
    # try:
        if request.method == "POST":
            amount = float(request.POST.get('amount'))

            
            wallet_user, created = Wallet.objects.get_or_create(user=request.user)
            wallet_user = wallet_user if not created else wallet_user[0]
            wallet_user.balance += amount
            wallet_user.save()

            transaction_id = initiate_payment(amount)
            Wallet_transaction.objects.create(
                wallet=wallet_user,
                transaction_id=transaction_id,
                money_deposit=amount
            )

            return redirect('wallet')
    # except Exception as e:
    #     print(e)  # Log the exception for debugging
    # return HttpResponse("An error occurred while adding money to the wallet.", status=500)

    
razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
def initiate_payment(items):
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

@never_cache
@login_required(login_url="login")
def view_coupons(request):
    custom_used = CustomerCoupon.objects.filter(user=request.user).values_list('coupon_id', flat=True)

    coupons = Coupon.objects.filter(active=True,start_date__lte=date.today(),end_date__gte=timezone.now()).exclude(id__in=custom_used)
    
    
    

    return render(request,'view_coupon.html',{'coupon':coupons})

@never_cache
@login_required(login_url="login")
def myrefrals(request):
    data=Myrefaral.objects.filter(user=request.user)
    user=CustomUser.objects.get(id=request.user.id)
    url="http://127.0.0.1:8000/"
    message=f'''
           explore now on HipHopz.

        🌟 Join the App Community Now! 🌟

        🚀 Get exclusive access to amazing deals and discounts when you join our app!

        💰 Plus, when you sign up using my referral code, you'll receive special benefits.

        🔗 Click to download the app and join now:{url} [{user.referal_code}]

        🎁 Hurry, limited time offer! *Terms and conditions apply.'''
    
    
    
    context={
        'data':data,
        'user':user,
        'message':message

    }
    return render(request,'my_refarel.html',context)




def search_shop(request):
    input=request.GET.get("Search",'').strip()

    products=Color_products.objects.filter(is_listed=True)

    if input:
        products=products.filter(Q(product__name__icontains=input)| Q(product__name__iexact=input))

    categories = Catagory.objects.filter(is_listed=True)
    brands = Brand.objects.filter(is_listed=True)

    context = {
                "products": products,
                "category": categories,
                "brand": brands,
    }

    return render(request, "shop.html", context)


def forgot_email(request):
    if request.method=="POST":
        email=request.POST.get('email')
        try:
            users=CustomUser.objects.get(email=email)
            email=users.email
            request.session['emails']=email
            
            generate_otp_and_send_email_for_forgot(request,email)
            messages.success(request,'Otp sent Succesfully')
            return redirect('otp_password')
        except CustomUser.objects.get(email=email).DoesNotExist:
            messages.error(request,"email doesnot exist")
    return render(request,"forgot_passsword.html")
def generate_otp_and_send_email_for_forgot(request,email):
    otp = random.randint(1000, 9999)
    otp_generated_at = datetime.now().isoformat()
    print(otp)

    request.session["otp_email"] = otp
    request.session["time_email"] = otp_generated_at

    send_mail(
        subject="Welcome",
        message=f"Your OTP for verification is: {otp}",
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )
def check_otp(request):
    if request.method == "POST":
        otp1 = request.POST.get("otp1")
        otp2 = request.POST.get("otp2")
        otp3 = request.POST.get("otp3")
        otp4 = request.POST.get("otp4")

        full_otp = otp1 + otp2 + otp3 + otp4
        

        if "otp_email" in request.session:
            otp = request.session["otp_email"]
            otp_generated = request.session["time_email"]
            delta = timedelta(minutes=2)
            time = datetime.fromisoformat(otp_generated)

           
            
            if datetime.now() <= time + delta:
                

                if int(full_otp) == otp:
                    messages.success(request,"You Enterd Successfully")

                    return redirect("password_section")

                   

                else:
                    messages.error(request, "Incorrect OTP! Please try again.")
                    return redirect("otp_password")
            else:
                
                messages.error(request, "OTP has expired. Please request a new one.")
                return redirect("otp_password")
        else:
            
            messages.error(request, "OTP session has expired or not set. Please request a new one.")
            return redirect("otp_password")
    else:
        return render(request,'password_otp.html')

    
def resend_otp_password(request):

    otp = random.randint(1000, 9999)
    otp_generated_at = datetime.now().isoformat()
    
    request.session["otp_email"]=otp
    request.session["time_email"]=otp_generated_at
    email = request.session["emails"]

    send_mail(
        subject="Welcome",
        message=f"Your OTP for verification is: {otp}",
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )
    return redirect("otp_password")

def set_password(request):
        if request.method=="POST":
            New_password = request.POST.get("new_password1")
            New_password2 = request.POST.get("new_password2")
            if not New_password == New_password2:
                messages.error(request, "give passwords missmatch")
                return redirect("password_section")

            elif not any(char.isupper() for char in New_password2):
                messages.error(
                    request, "Password must contain at least one uppercase letter"
                )
                return redirect("password_section")
            elif not any(char.islower() for char in New_password2):  # Corrected condition
                messages.error(
                    request, "Password must contain at least one lowercase letter"
                )
                return redirect("password_section")
            elif not any(char.isdigit() for char in New_password2):
                messages.error(request, "Password must contain at least one digit")
                return redirect("password_section")
            users=CustomUser.objects.get(email=request.session["emails"])
            users.set_password(New_password)
            users.save()
            

            messages.success(request, "Changed successfully")
            return redirect('login')
        
        return render(request,'password_section.html')


def generate_invoice(request, order_id):
    # Fetch the order details
    order = get_object_or_404(Order, id=order_id)

    order_products = OrderProduct.objects.filter(order__id=order_id).exclude(status__in=['Cancelled', 'Returned'])
    
    totel_amount=order_products.annotate(totel_price=F('quantity')* F('price')).aggregate(totel_sum=Sum('totel_price'))['totel_sum'] or 0
    html_string = render_to_string('invoice_template.html', {'order': order,'totel_amount':totel_amount})

    # Generate PDF from HTML
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    # Create a response object
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=invoice_{order_id}.pdf'

    return response