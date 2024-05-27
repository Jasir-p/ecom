from datetime import timedelta, timezone, datetime
from io import BytesIO

from django.core.exceptions import ValidationError


from django.shortcuts import render, HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.db.models import Sum, Case, When, Value, BooleanField
from django.shortcuts import render, redirect
from .models import Catagory, Brand
from django.contrib.auth import authenticate, login as log, logout as authlogout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control

from django.utils import timezone
from Userapp.models import CustomUser
from Userapp.urls import *
from django.utils.translation import gettext as _
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
from Order.models import *


# Create your views here.
@never_cache
def login(request):
    if request.user.is_authenticated and request.user.is_superuser:

        return redirect("dashbord")

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        try:
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_superuser:
                log(request, user)

                return redirect("dashbord")
            else:

                messages.error(request, "incorrect username or password")
                return redirect("adminlogin")

        except Exception as e:
            messages.error(request, e)
            return redirect("adminlogin")

    return render(request, "login.html")


@never_cache
@login_required(login_url="adminlogin")
def dashbord(request):

    if request.user.is_superuser:

        return render(request, "dashbord.html")

    return redirect("adminlogin")


# _____________USERMANAGEMENT


@never_cache
@login_required(login_url="adminlogin")
def view_user(request):

    if request.user.is_superuser:

        user = CustomUser.objects.all()

        return render(request, "userdetails.html", {"data": user})

    return redirect("adminlogin")


def block_user(request, u_id):

    try:

        data = CustomUser.objects.get(pk=u_id)
        data.is_active = False
        data.save()
        return redirect("userdetail")

    except CustomUser.DoesNotExist:

        return redirect("userdetail")


def unblock_user(request, u_id):

    data = CustomUser.objects.get(pk=u_id)
    data.is_active = True
    data.save()
    return redirect("userdetail")


# ______CATEGORYMANAGEMENT______


@never_cache
@login_required(login_url="adminlogin")
def category(request):

    if request.user.is_superuser:

        if request.method == "POST":

            try:

                ca_name = request.POST.get("cat_name").strip()
                ca_description = request.POST.get("cat_description").strip()
                cover_photo = request.FILES.get("cover_image", None)

                if Catagory.objects.filter(cat_name__iexact=ca_name).exists():

                    messages.error(request, "category already here")
                    return redirect("category")

                elif not ca_name or not ca_name[0].isalpha():

                    messages.error(request, "Field must start with a character")
                    return redirect("category")
                elif not is_valid_image(cover_photo):

                    messages.error(request, "Image  is an invalid image file")
                    return redirect("category")

                item = Catagory(
                    cat_name=ca_name,
                    cat_description=ca_description,
                    cover_image=cover_photo,
                )

                item.save()

                return redirect("view_category")

            except Exception as e:

                messages.error(request, str(e))
                return redirect("category")

        return render(request, "category.html")

    return redirect("adminlogin")


@never_cache
@login_required(login_url="adminlogin")
def view_category(request):
    if request.user.is_superuser:
        try:
            data = Catagory.objects.filter(is_listed=True)

            return render(request, "view_category.html", {"data": data})
        except Catagory.DoesNotExist:
            return render(request, "view_category.html")

    return redirect("adminlogin")


@never_cache
@login_required(login_url="adminlogin")
def edit_category(request, ca_id):
    try:

        data = Catagory.objects.get(id=ca_id)

        if request.method == "POST":

            ca_name = request.POST.get("cat_name").strip()
            ca_description = request.POST.get("cat_description").strip()
            cover_photo = request.FILES.get("cover_image")

            if not ca_name or not ca_name[0].isalpha():

                messages.error(request, "Field must start with a character")
                return render(request, "edit_category.html", {"data": data})

            if cover_photo:

                if not is_valid_image(cover_photo):

                    messages.error(request, "Image 1 is an invalid image file")
                    return render(request, "edit_category.html", {"data": data})
                else:

                    data.cover_image = cover_photo

            if (
                Catagory.objects.filter(cat_name__iexact=ca_name)
                .exclude(id=ca_id)
                .exists()
            ):

                messages.error(request, "Entered name already exists")
                return render(request, "edit_category.html", {"data": data})

            data.cat_name = ca_name
            data.cat_description = ca_description
            data.save()

            return redirect("view_category")

        return render(request, "edit_category.html", {"data": data})
    except Exception:
        return redirect("view_category")


def category_unlist(request, ca_id):

    try:

        item = Catagory.objects.get(id=ca_id)
        item.is_listed = False
        item.save()
        return redirect("view_category")

    except Catagory.DoesNotExist:
        return redirect("view_category")


@never_cache
@login_required(login_url="adminlogin")
def unlist_categories(request):

    if request.user.is_superuser:

        try:
            data = Catagory.objects.filter(is_listed=False)
            return render(request, "viewunlist_category.html", {"data": data})

        except:

            return render(request, "viewunlist_category.html")
    return redirect("adminlogin")


def list_category(request, ca_id):

    try:
        item = Catagory.objects.get(id=ca_id)
        item.is_listed = True
        item.save()
        return redirect("view_category")

    except Catagory.DoesNotExist:
        return redirect("unlistcategory")


@never_cache
@login_required(login_url="adminlogin")
def brand(request):
    if request.user.is_superuser:
        try:
            if request.method == "POST":
                b_name = request.POST.get("name").strip()
                cover_image = request.FILES.get("cover_image")
                b_description = request.POST.get("description").strip()

                if Brand.objects.filter(B_name__iexact=b_name).exists():
                    messages.error(request, "brand already here")

                    return render("brand")

                if not b_name or not b_name[0].isalpha():

                    messages.error(request, "Field must start with a character")

                    return render("brand")

                if not is_valid_image(cover_image):

                    messages.error(request, "Image  is an invalid image file")
                    return render("brand")
                brand = Brand(
                    B_name=b_name,
                    cover_image=cover_image,
                    B_description=b_description,
                )
                brand.save()
                return render("brand")
            return render(request, "brand.html")

        except:
            return render(request, "brand.html")
    return redirect("adminlogin")


def logout(request):
    authlogout(request)
    return redirect("adminlogin")


@never_cache
@login_required(login_url="adminlogin")
def view_brands(request):
    if request.user.is_superuser:
        try:

            data = Brand.objects.filter(is_listed=True)
            return render(request, "view_brand.html", {"data": data})
        except:
            return render(request, "view_brand.html")

    return redirect("adminlogin")


@never_cache
@login_required(login_url="adminlogin")
def brand_delete(request, b_id):
    if request.user.is_superuser:
        try:
            item = Brand.objects.get(id=b_id)
            item.is_listed = False
            item.save()
            return render("viewbrand")
        except:
            return render("viewbrand")
    return redirect("adminlogin")


def edit_brand(request, id):
    data = Brand.objects.get(id=id)
    try:
        if request.method == "POST":

            b_name = request.POST.get("b_name").strip()
            b_description = request.POST.get("B_description").strip()
            cover_photo = request.FILES.get("cover_image")

            if not b_name or not b_name[0].isalpha():

                messages.error(request, "Field must start with a character")
                return render(request, "edit_brand.html", {"data": data})

            if cover_photo:

                if not is_valid_image(cover_photo):

                    messages.error(request, "Image  is an invalid image file")
                    return render(request, "edit_brand.html", {"data": data})
                else:

                    data.cover_image = cover_photo

            if Brand.objects.filter(B_name__iexact=b_name).exclude(id=id).exists():

                messages.error(request, "Entered name already exists")
                return render(request, "edit_brand.html", {"data": data})

            data.B_name = b_name
            data.B_description = b_description
            data.save()

            return redirect("viewbrand")

        return render(request, "edit_brand.html", {"data": data})
    except:
        return redirect("viewbrand")


def unlist_brand(request, b_id):
    try:
        data = Brand.objects.get(id=b_id)
        data.is_listed = False
        data.save()
        return redirect("viewbrand")
    except:
        return redirect("viewbrand")


@never_cache
@login_required(login_url="adminlogin")
def viewunlist_brands(request):
    try:
        data = Brand.objects.filter(is_listed=False)
        return render(request, "unlist_brand.html", {"data": data})
    except:
        return render(request, "unlist_brand.html")


def list_brand(request, b_id):
    try:
        data = Brand.objects.get(id=b_id)
        data.is_listed = True
        data.save()
        return redirect("viewbrand")
    except:
        return redirect("viewbrand")


def is_valid_image(file):

    if not isinstance(file, UploadedFile):
        return False

    try:

        Image.open(file)
        return True
    except Exception:

        return False



def sales_report(request):
    if request.user.is_superuser:
             
        if request.method == "GET":
            orders = OrderProduct.objects.filter(status="Delivered").select_related('order', 'product').order_by("order__created_at")

            report_type = request.GET.get('report_type')
            day = request.GET.get('day')
            week = request.GET.get('week')
            month = request.GET.get('month')
            year = request.GET.get('year')

            if report_type == 'day' and day:
                orders = orders.filter(order__created_at__date=day)
            elif report_type == 'week' and week:
                today = datetime.today()
                start_of_week = today - timedelta(days=today.weekday())
                orders = orders.filter(order__created_at__date__gte=start_of_week, order__created_at__date__lte=today)
            elif report_type == 'month' and month and year:
                orders = orders.filter(order__created_at__year=year, order__created_at__month=month)
            elif report_type == 'year' and year:
                orders = orders.filter(order__created_at__year=year)

            orders = orders.annotate(
                coupon_applied=Case(
                    When(order__coupon_id__isnull=False, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )

            grouped_orders = {}
            for order_product in orders:
                order_id = order_product.order_id
                if order_id not in grouped_orders:
                    grouped_orders[order_id] = {
                            'order': order_product.order,
                            'products': [],
                            'coupon_applied': order_product.order.coupon_id is not None,
                            'discount_amount':Coupon.objects.get(code=order_product.order.coupon_id).discount_amount if order_product.order.coupon_id else None
                        }
                grouped_orders[order_id]['products'].append(order_product)

            order_ids = orders.values_list('order_id', flat=True).distinct()
            order_list = Order.objects.filter(id__in=list(order_ids))

            count = orders.count()
            total = order_list.aggregate(total=Sum("total_amount"))["total"]

            context = {
                'grouped_orders': grouped_orders.values(),
                'count': count,
                'total': total,
                'months': range(1, 13),
                'years': range(2020, datetime.now().year + 1),
            }

            return render(request, 'sales_report.html', context)

        else:
            messages.error(request, "You do not have permission to access this page.")
            return redirect("adminlogin")
    else:
        messages.error(request, "You do not have permission to access this page.")
        return redirect("adminlogin")


def download_sales_report(request):
    if request.user.is_superuser:
        if request.method == "GET":
            sales_data = OrderProduct.objects.filter(
                Q(cancel=False)
                & Q(return_product=False)
                & Q(status="Delivered")
            )

            overall_sales_count = request.session.get("overall_sales_count")
            overall_order_amount = request.session.get("overall_order_amount")
            overall_discount = request.session.get("overall_discount")

            if "format" in request.GET and request.GET["format"] == "pdf":
                buffer = BytesIO()

                doc = SimpleDocTemplate(buffer, pagesize=letter)

                styles = getSampleStyleSheet()
                centered_style = ParagraphStyle(
                    name="Centered", parent=styles["Heading1"], alignment=1
                )

                today_date = datetime.now().strftime("%Y-%m-%d")

                content = []

                company_details = f"<b>MELIOTIS</b><br/>Email: meliotis100@email.com<br/>Date: {today_date}"
                content.append(Paragraph(company_details, styles["Normal"]))
                content.append(Spacer(1, 0.5 * inch))

                content.append(Paragraph("<b>SALES REPORT</b><hr>", centered_style))
                content.append(Spacer(1, 0.5 * inch))

                data = [["Order ID", "Product", "Quantity", "Total Price", "Date"]]
                for sale in sales_data:
                    formatted_date = sale.order.created_at.strftime("%a, %d %b %Y")
                    data.append(
                        [sale.order.tracking_id,sale.product.product.name, sale.qty, sale.product.product.offer_price, formatted_date]
                    )

                table = Table(data, repeatRows=1)
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("TOPPADDING", (0, 0), (-1, 0), 12),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ]
                    )
                )

                content.append(table)

                content.append(Spacer(1, 0.5 * inch))

                overall_sales_count_text = f"<b>Overall Sales Count:</b> {overall_sales_count}"
                overall_order_amount_text = f"<b>Overall Order Amount:</b> {overall_order_amount}"
                overall_discount_amount_text = f"<b>Overall Discount:</b> {overall_discount}"

                content.append(Paragraph(overall_sales_count_text, styles["Normal"]))
                content.append(Paragraph(overall_order_amount_text, styles["Normal"]))
                content.append(Paragraph(overall_discount_amount_text, styles["Normal"]))

                doc.build(content)

                current_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                file_name = f"Sales_Report_{current_time}.pdf"

                response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
                response["Content-Disposition"] = f'attachment; filename="{file_name}"'

                return response

            elif "format" in request.GET and request.GET["format"] == "excel":
                output = BytesIO()
                workbook = xlsxwriter.Workbook(output, {"in_memory": True})
                worksheet = workbook.add_worksheet("Sales Report")

                headings = ["Product", "Quantity", "Total Price", "Date"]
                header_format = workbook.add_format({"bold": True})
                for col, heading in enumerate(headings):
                    worksheet.write(0, col, heading, header_format)

                for row, sale in enumerate(sales_data, start=1):
                    formatted_date = sale.order.created_at.strftime("%a, %d %b %Y")
                    worksheet.write(row, 0, sale.product.product.name)
                    worksheet.write(row, 1, sale.qty)
                    worksheet.write(row, 2, sale.product.product.offer_price)
                    worksheet.write(row, 3, formatted_date)

                workbook.close()

                output.seek(0)
                response = HttpResponse(
                    output.getvalue(),
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                current_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                file_name = f"Sales_Report_{current_time}.xlsx"
                response["Content-Disposition"] = f'attachment; filename="{file_name}"'

                return response

        else:
            return redirect("dashboard")
    else:
        return redirect("admin_login")