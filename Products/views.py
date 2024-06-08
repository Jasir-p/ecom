from django.core.exceptions import ValidationError

import random

from django.contrib import messages
from django.db.models import Q

from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import authenticate, login as log, logout as authlogout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control

from Userapp.models import *
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
from .models import *
from Admin.urls import *
from django.http import JsonResponse

# Create your views here.


@never_cache
@login_required(login_url="adminlogin")
def add_products(request):
    if request.user.is_authenticated and request.user.is_superuser:
        categories = Catagory.objects.all()
        brands = Brand.objects.all()

        if request.method == "POST":
            name = request.POST.get("name").strip()
            price = request.POST.get("price")
            description = request.POST.get("description").strip()
            category_id = request.POST.get("category")
            brand = request.POST.get("brand")
            Thumbnail = request.FILES.get("thumbnail")

            if Product.objects.filter(name__iexact=name).exists():
                messages.error(request, "product already exist")
                return redirect("addproducts")
            if not name or not name[0].isalpha():
                messages.error(request, "Field must start with a character")
                return redirect("addproducts")
            if len(name) < 2:
                messages.error(request, "Field must atleast two character")
                return redirect("addproducts")

            elif int(price) < 0:
                messages.error(request, "price must be postive number")
                return redirect("addproducts")
            elif not is_valid_image(Thumbnail):
                messages.error(request, "Thumbnail is an invalid image file ")
                return redirect("addproducts")

            product = Product(
                name=name,
                price=price,
                description=description,
                catagory_id=category_id,
                brand_id=brand,
                thumbnail=Thumbnail,
            )
            product.save()
            messages.success(request, "Product added successfully")
            return redirect("addproducts")

        return render(
            request, "add_products.html", {"categories": categories, "brands": brands}
        )
    else:
         return redirect("adminlogin")

@never_cache
@login_required(login_url="adminlogin")
def add_colour(request, id):
    if request.user.is_authenticated and request.user.is_superuser:
        try:

            products = Product.objects.get(is_listed=True, id=id)

            if request.method == "POST":

                name = request.POST.get("color_name").strip()

                img1 = request.FILES.get("img1")
                img2 = request.FILES.get("img2")
                img3 = request.FILES.get("img3")
                product_id = request.POST.get("product")

                if Color_products.objects.filter(
                    product_id=product_id, color_name__iexact=name
                ).exists():

                    messages.error(request, "Color already exists for this product")
                    return render("addcolour")

                elif not name:

                    messages.error(request, "Please provide color name")
                    return render("addcolour")
                if not name or not name[0].isalpha():
                    messages.error(request, "Field must start with a character")
                    return render("addcolour")

                elif not is_valid_image(img1):
                    messages.error(request, "Image 1 is an invalid image file")
                    return render("addcolour")
                elif not is_valid_image(img2):
                    messages.error(request, "Image 2 is an invalid image file")
                    return render("addcolour")

                elif not is_valid_image(img3):
                    messages.error(request, "Image 3 is an invalid image file")
                    return render("addcolour")

                else:

                    product = Product.objects.get(id=product_id)
                    data = Color_products(
                        color_name=name, img1=img1, img2=img2, img3=img3, product=product
                    )
                    data.save()
                    messages.success(request, "Color added successfully")

            return render(request, "add_colour.html", {"products": products})

        except Exception as e:

            # messages.error(request,str(e))
            return render(request, "add_colour.html")
    else:
         return redirect("adminlogin")


@never_cache
@login_required(login_url="adminlogin")
def add_size(request, id):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            color_products = Color_products.objects.get(id=id, is_listed=True)
            if request.method == "POST":
                color_id = request.POST.get("color_product")
                size = request.POST.get("size").strip()
                quantity = int(request.POST.get("quantity"))
                if size not in ["S", "M", "L", "XL", "XXL"]:

                    messages.error(
                        request, "Invalid size. Please choose from S, M, L, XL, XXL."
                    )
                    return redirect("addsize", id)

                if quantity <= 0:
                    messages.error(request, "Quantity must be a positive number")
                    return redirect("addsize", id)

                color_product = Color_products.objects.get(id=color_id)

                if color_product.size.filter(size__iexact=size).exists():
                    messages.error(request, "Size already exists for this color")
                    return redirect("addsize", id)

                size_instance = size_variant(
                    size=size, quantity=quantity, Color_products=color_product
                )
                size_instance.save()

                
                return redirect(product_variant,id)

            return render(request, "add_size.html", {"color_products": color_products})
        except Exception as e:
            messages.error(request, str(e))
            return render(request, "add_size.html")
    else:
         return redirect("adminlogin")

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
@login_required(login_url="adminlogin")
def view_product(request):
    if request.user.is_authenticated and request.user.is_superuser:

        products = Product.objects.filter(is_listed=True)

        context = {"products": products}
        return render(request, "product.html", context)
    else:
         return redirect("adminlogin")


# except:
#     return render(request,'product.html')


def unlist_product(request, id):
    try:
        products = Product.objects.get(id=id)
        products.is_listed = False
        products.save()
        return redirect("viewproducts")

    except:

        return redirect("viewproducts")


def edit_product(request, id):
    if request.user.is_authenticated and request.user.is_superuser:

        product = Product.objects.get(id=id)

        categories = Catagory.objects.all()
        brands = Brand.objects.all()
        context = {"categories": categories, "brands": brands, "product": product}

        if request.method == "POST":
            name = request.POST.get("name").strip()
            price = request.POST.get("price")
            description = request.POST.get("description").strip()
            category_id = request.POST.get("Category")
            brand = request.POST.get("Brand")
            Thumbnail = request.FILES.get("Thumbnail")

            if Product.objects.filter(name__iexact=name).exclude(id=id).exists():
                messages.error(request, "product already exist")
                return redirect("editproduct", id)
            if not name or not name[0].isalpha():
                messages.error(request, "Field must start with a character")
                return redirect("editproduct", id)
            if len(name) < 2:
                messages.error(request, "Field must atleast two character")
                return redirect("editproduct", id)

            elif float(price) < 0:
                messages.error(request, "price must be postive number")
                return redirect("editproduct", id)
            elif Thumbnail:
                if not is_valid_image(Thumbnail):
                    messages.error(request, "Thumbnail is an invalid image file ")
                    return redirect("editproduct", id)
                else:
                    product.thumbnail = Thumbnail

            product.name = name
            product.price = price
            product.catagory = Catagory.objects.get(id=category_id)
            product.brand = Brand.objects.get(id=brand)
            product.description = description
            product.save()

        return render(request, "edit_product.html", context)

    else:
         return redirect("adminlogin")
# except:
#      return render(request,"edit_product.html")


def view_unlist(request):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            products = Product.objects.filter(is_listed=False)

            context = {"products": products}
            return render(request, "unlist_product.html", context)
        except:
            return render(request, "unlist_product.html")
    else:
        return redirect("adminlogin")


def list_product(request, id):
    try:
        products = Product.objects.get(id=id)
        products.is_listed = True
        products.save()
        return redirect("viewproducts")

    except:

        return redirect("viewproducts")


def product_variant(request, id):
    if request.user.is_authenticated and request.user.is_superuser:
        product_id = id

        products = Color_products.objects.filter(product__id=id, is_listed=True)

        return render(
            request, "variants.html", {"products": products, "product_id": product_id}
        )
    else:
         return redirect("adminlogin")

def edit_variant(request, id):
    if request.user.is_authenticated and request.user.is_superuser:
        variants = get_object_or_404(size_variant, id=id)
        

        if request.method == "POST":
            color_products = Color_products.objects.get(id=variants.Color_products.id)
            

            name = request.POST.get("color_name").strip()

            img1 = request.FILES.get("img1")
            img2 = request.FILES.get("img2")
            img3 = request.FILES.get("img3")
            
            size = request.POST.get("size")
            quantity = request.POST.get("quantity")
            product_id = color_products.product.id
        
            cat = Color_products.objects.filter(
                product__id=product_id, color_name__iexact=name
            ).exclude(id=color_products.pk)
            

            if (
                Color_products.objects.filter(
                    product__id=product_id, color_name__iexact=name
                )
                .exclude(id=color_products.pk)
                .exists()
            ):
                messages.error(request, "The color already exists")
                return render(request, "edit_variant.html", {"variants": variants})

            if not name or not name[0].isalpha():
                messages.error(request, "Field must start with a character")
                return render(request, "edit_variant.html", {"variants": variants})

            if len(name) < 2:
                messages.error(request, "Field must atleast two character")
                return render(request, "edit_variant.html", {"variants": variants})

            if img1:
                if not is_valid_image(img1):
                    messages.error(request, "Image 1 is an invalid image file")
                    return render(request, "edit_variant.html", {"variants": variants})
                else:

                    color_products.img1 = img1
            if img2:
                if not is_valid_image(img2):
                    messages.error(request, "Image 2 is an invalid image file")
                    return render(request, "edit_variant.html", {"variants": variants})
                else:
                    color_products.img2 = img2

            if img3:
                if not is_valid_image(img3):
                    messages.error(request, "Image 3 is an invalid image file")
                    return render(request, "edit_variant.html", {"variants": variants})
                else:
                    color_products.img3 = img3

            elif (
                size_variant.objects.filter(
                    Color_products__id=color_products.pk, size__iexact=size
                )
                .exclude(id=variants.id)
                .exists()
            ):
                print(
                    size_variant.objects.filter(
                        Color_products__id=color_products.pk, size__iexact=size
                    ).exclude(id=variants.id)
                )
                messages.error(request, "The Size already exists")
                return render(request, "edit_variant.html", {"variants": variants})
            elif size not in ["S", "M", "L", "XL", "XXL"]:

                messages.error(
                    request, "Invalid size. Please choose from S, M, L, XL, XXL."
                )
                return render(request, "edit_variant.html", {"variants": variants})
            elif int(quantity) <= 0:

                messages.error(request, "Quantity must be a positive number")
                return render(request, "edit_variant.html", {"variants": variants})
            else:
                color_products.color_name = name
                variants.size = size
                variants.quantity = int(quantity)
                variants.save()
                color_products.save()
                return redirect(product_variant, product_id)

        return render(request, "edit_variant.html", {"variants": variants})
    else:
         return redirect("adminlogin")

def unlist_variant(request, id):
    item = get_object_or_404(Color_products, id=id)
    item.is_listed = False
    item.save()
    return redirect(product_variant, item.product.pk)

def unlisted_variants_view(request, product_id):
    if request.user.is_authenticated and request.user.is_superuser: 
        product = get_object_or_404(Product, id=product_id)
        unlisted_variants = Color_products.objects.filter(product=product, is_listed=False).prefetch_related('size')

        context = {
            'product': product,
            'unlisted_variants': unlisted_variants,
        }
        return render(request, 'unlist_variant.html', context)
    else:
         return redirect("adminlogin")
    
def list_variant(request, id):
    item = get_object_or_404(Color_products, id=id)
    item.is_listed = True
    item.save()
    return redirect(product_variant, item.product.pk)