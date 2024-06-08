from datetime import timedelta, timezone, datetime
from io import BytesIO

from django.core.exceptions import ValidationError

from django.db.models.functions import ExtractYear, ExtractMonth
from django.shortcuts import render, HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.db.models import Sum, Case, When, Value, BooleanField,ExpressionWrapper, DecimalField,Count
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
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle 
from reportlab.lib.units import inch
import xlsxwriter
import calendar


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

    if request.user.is_authenticated and request.user.is_superuser:

             
        if request.method == "GET":
            orders = OrderProduct.objects.filter(status="Delivered").select_related('order', 'product').order_by("order__created_at")
            thismonth=OrderProduct.objects.filter(status="Delivered",order__created_at__month=timezone.now().month)
            distinct_order_ids = thismonth.values_list('order__id', flat=True).distinct()
            month_sale = thismonth.aggregate(
            month_sale=Sum(
                ExpressionWrapper(F("price") * F("quantity"), output_field=DecimalField())
            )
        )['month_sale']
            


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
                orders = orders.filter(order__created_at__month=month)
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
                            'discount_amount':order_product.order.coupon_amount if order_product.order.coupon_id else None
                        }
                grouped_orders[order_id]['products'].append(order_product)

            order_ids = orders.values_list('order_id', flat=True).distinct()
            order_list = Order.objects.filter(id__in=list(order_ids))
            thismonth_sum = Order.objects.filter(id__in=distinct_order_ids).aggregate(thismonth_sum=Sum('total_amount'))['thismonth_sum']
            count = orders.count()
            count_with_month=orders.values("order__created_at").annotate(count=Count("product__product__catagory")).order_by("-count")[:5]
            total = order_list.aggregate(total=Sum("total_amount"))["total"]
            total = total if total is not None else 0
            total_float = float(total)
            overall_discount=order_list.aggregate(overall_discount=Sum("coupon_amount"))['overall_discount']
            overall_discount=float(order_list.aggregate(overall_discount=Sum("coupon_amount"))['overall_discount']) if overall_discount is not None else 0
            request.session['overall_sales_count'] = count
            request.session['overall_order_amount'] =total_float
            request.session['overall_discount'] = overall_discount
            Totalsale=OrderProduct.objects.filter(status="Delivered")
            total_sale=Totalsale.aggregate(
            total_sale=Sum(ExpressionWrapper(F("price") * F("quantity"), output_field=DecimalField())
            ))['total_sale']
            Revanue=OrderProduct.objects.filter(status="Delivered")
            distinct_order=Revanue.values_list('order__id', flat=True).distinct()
            totel_revenue=Order.objects.filter(id__in=distinct_order).aggregate(totel_revenue=Sum('total_amount'))['totel_revenue']

            top_selling_categories = (
                    OrderProduct.objects.filter(status="Delivered")
                        .values("product__product__catagory__cat_name")
                        .annotate(category_count=Count("product__product__catagory"))
                        .order_by("-category_count")[:5]
)

            top_selling_brand = (
                    OrderProduct.objects.filter(status="Delivered")
                        .values("product__product__brand__B_name")
                        .annotate(brand_count=Count("product__product__brand"))
                        .order_by("-brand_count")[:5]
               )
            top_selling_product=(OrderProduct.objects.filter(status="Delivered").values("product__product__name").annotate(Product_count=Count("product__product"))
                                 .order_by("-Product_count")[:4])

            


            current_year = timezone.now().year
            current_month = timezone.now().month

            
            delivered_sales = list(get_monthly_sales("Delivered"))
            cancelled_sales = list(get_monthly_sales("Cancelled"))
            returned_sales = list(get_monthly_sales("Returned"))
            
            context = {
                'grouped_orders': grouped_orders.values(),
                'count': count,
                'total': total_float,
                'month': range(1, 13),
                'years': range(2020, datetime.now().year + 1),
                'discount':overall_discount,
                'thismonth':thismonth_sum,
                'monthsale':month_sale,
                'top_selling_categories': top_selling_categories,
                'top_selling_brand': top_selling_brand,
                'top_selling_product':top_selling_product,
                'total_sale':total_sale,
                'totel_revenue':totel_revenue,
                'delivered_sales': delivered_sales,
                'cancelled_sales': cancelled_sales,
                'returned_sales':returned_sales,
                'months': [calendar.month_name[month] for month in range(1, current_month + 1)],

            }
            return render(request, "dashbord.html",context)
            # return render(request, 'sales_report.html', context)

        else:
           
            return redirect("adminlogin")
    else:
         return redirect("adminlogin")


        

def get_monthly_sales(status):
        current_year = timezone.now().year
        current_month = timezone.now().month
        sales = OrderProduct.objects.filter(
            status=status,
            order__created_at__year=current_year
        ).annotate(
            month=ExtractMonth('order__created_at')
        ).values('month').annotate(
            sales_count=Count('id')
        ).order_by('month')
        

        sales_dict = {sale['month']: sale['sales_count'] for sale in sales}
        
        
        monthly_sales = []
        for month in range(1, current_month + 1):
            monthly_sales.append({
                'month': month,
                'sales_count': sales_dict.get(month, 0)
            })
        
        return monthly_sales

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

    if request.user.is_authenticated and request.user.is_superuser:

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
    if request.user.is_authenticated and request.user.is_superuser:
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

@never_cache
@login_required(login_url="adminlogin")
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

    if request.user.is_authenticated and request.user.is_superuser:

        try:
            data = Catagory.objects.filter(is_listed=False)
            return render(request, "viewunlist_category.html", {"data": data})

        except:

            return render(request, "viewunlist_category.html")
    return redirect("adminlogin")

@never_cache
@login_required(login_url="adminlogin")
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
    if request.user.is_authenticated and request.user.is_superuser:
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
    if  request.user.is_authenticated and request.user.is_superuser:
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

@never_cache
@login_required(login_url="adminlogin")
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


# @never_cache
# @login_required(login_url="adminlogin")
# def sales_report(request):
#     if request.user.is_authenticated and request.user.is_superuser:

             
#         if request.method == "GET":
#             orders = OrderProduct.objects.filter(status="Delivered").select_related('order', 'product').order_by("order__created_at")

#             report_type = request.GET.get('report_type')
#             day = request.GET.get('day')
#             week = request.GET.get('week')
#             month = request.GET.get('month')
#             year = request.GET.get('year')

#             if report_type == 'day' and day:
#                 orders = orders.filter(order__created_at__date=day)
#             elif report_type == 'week' and week:
#                 today = datetime.today()
#                 start_of_week = today - timedelta(days=today.weekday())
#                 orders = orders.filter(order__created_at__date__gte=start_of_week, order__created_at__date__lte=today)
#             elif report_type == 'month' and month and year:
#                 orders = orders.filter(order__created_at__month=month)
#             elif report_type == 'year' and year:
#                 orders = orders.filter(order__created_at__year=year)

#             orders = orders.annotate(
#                 coupon_applied=Case(
#                     When(order__coupon_id__isnull=False, then=Value(True)),
#                     default=Value(False),
#                     output_field=BooleanField()
#                 )
#             )

#             grouped_orders = {}
#             for order_product in orders:
#                 order_id = order_product.order_id
#                 if order_id not in grouped_orders:
#                     grouped_orders[order_id] = {
#                             'order': order_product.order,
#                             'products': [],
#                             'coupon_applied': order_product.order.coupon_id is not None,
#                             'discount_amount':Coupon.objects.get(code=order_product.order.coupon_id).discount_amount if order_product.order.coupon_id else None
#                         }
#                 grouped_orders[order_id]['products'].append(order_product)

#             order_ids = orders.values_list('order_id', flat=True).distinct()
#             order_list = Order.objects.filter(id__in=list(order_ids))

#             count = orders.count()
#             total = order_list.aggregate(total=Sum("total_amount"))["total"]
#             total = total if total is not None else 0
#             total_float = float(total)
#             request.session['overall_sales_count'] = count
#             request.session['overall_order_amount'] =total_float
#             # request.session['overall_discount'] = overall_discount
#             context = {
#                 'grouped_orders': grouped_orders.values(),
#                 'count': count,
#                 'total': total_float,
#                 'months': range(1, 13),
#                 'years': range(2020, datetime.now().year + 1),
#             }

#             return render(request, 'sales_report.html', context)

#         else:
           
#             return redirect("adminlogin")
#     else:
        
#         return redirect("adminlogin")



@login_required(login_url="adminlogin")
def download_sales_report(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == "GET":
            filters = request.session.get("filters", {})
            sales_data = OrderProduct.objects.filter(status="Delivered")

            # Apply filters if available
            if "from_date" in filters:
                sales_data = sales_data.filter(order__created_at__gte=filters["from_date"])
            if "to_date" in filters:
                sales_data = sales_data.filter(order__created_at__lte=filters["to_date"])
            if "month" in filters:
                year, month = map(int, filters["month"].split("-"))
                sales_data = sales_data.filter(order__created_at__year=year, order__created_at__month=month)
            if "year" in filters:
                sales_data = sales_data.filter(order__created_at__year=filters["year"])
            overall_sales_count =  request.session['overall_sales_count']
            overall_order_amount = request.session['overall_order_amount']
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

                company_details = f"<b>HipHopz</b><br/>Email:hiphopz831@gmail.com.<br/>Date: {today_date}"
                content.append(Paragraph(company_details, styles["Normal"]))
                content.append(Spacer(1, 0.5 * inch))

                content.append(Paragraph("<b>SALES REPORT</b><hr>", centered_style))
                content.append(Spacer(1, 0.5 * inch))

                data = [["Order ID", "Product", "Quantity", "Price","Total Price", "Date"]]
                for sale in sales_data:
                    formatted_date = sale.order.created_at.strftime("%a, %d %b %Y")
                    data.append([sale.order.order_id, sale.product.product.name, sale.quantity, sale.price,sale.totel_price() ,formatted_date])

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

                overall_sales_count_text = (
                    f"<b>Overall Sales Count:</b> {overall_sales_count}"
                )
                overall_order_amount_text = (
                    f"<b>Overall Order Amount:</b> {overall_order_amount}"
                )
                overall_discount_amount_text = (
                    f"<b>Overall Discount:</b> {overall_discount}"
                )

                content.append(Paragraph(overall_sales_count_text, styles["Normal"]))
                content.append(Paragraph(overall_order_amount_text, styles["Normal"]))
                content.append(
                    Paragraph(overall_discount_amount_text, styles["Normal"])
                )

                doc.build(content)

                current_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                file_name = f"Sales_Report_{current_time}.pdf"

                response = HttpResponse(
                    buffer.getvalue(), content_type="application/pdf"
                )
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
                    worksheet.write(row, 1, sale.quantity)
                    worksheet.write(row, 2, sale.price)
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
            return redirect("dashbord")
    else:
        return redirect("adminlogin")