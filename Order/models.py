from django.db import models

from Products.models import *
from cart.models import *

# Create your models here.


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("COD", "Cash on Delivery"),
        ("Razorpay", "Razorpay"),
    ]
    user = models.ForeignKey('Userapp.CustomUser', on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="pending", null=True)
    Transaction_id= models.CharField(max_length=20, blank=True, null=True)


class Order(models.Model):
    user = models.ForeignKey('Userapp.CustomUser', on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    coupon_id = models.CharField(max_length=100, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    payment_method = models.CharField(
        max_length=20,
        choices=[("COD", "Cash on Delivery"), ("Razorpay", "Razorpay")],
        null=True,
        default=True,
    )
    order_id = models.CharField(max_length=20, unique=True, default=None, null=True)

    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    House_no = models.CharField(max_length=100, blank=True, null=True)

    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)


class OrderProduct(models.Model):
    ORDER_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
        ("Returned", "Returned"),
    ]

    order = models.ForeignKey(Order, related_name="order", on_delete=models.CASCADE)
    product = models.ForeignKey(Color_products, on_delete=models.CASCADE)
    price=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default="Pending", null=True
    )
    review = models.TextField(
        blank=True, null=True
    )
    rating = models.IntegerField(
        default=0, null=True
    )  
    user = models.ForeignKey(
        'Userapp.CustomUser', on_delete=models.SET_NULL, null=True, blank=True
    ) 
    delivery_date = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    trackig_id = models.CharField(max_length=20, unique=True, default=None, null=True)
    size = models.ForeignKey(
        size_variant, on_delete=models.CASCADE, default=None, null=True
    )
    request_status = models.CharField(max_length=30, default="None", null=True)
    def totel(self):
        return self.quantity * self.price

    def set_expected_delivery_date(self):
     
        if self.order and self.order.created_at:

            expected_delivery_date = self.order.created_at + timezone.timedelta(
                days=7
            )
            self.delivery_date = expected_delivery_date.date()
    def save(self, *args, **kwargs):
        if self.delivery_date is None:
            self.set_expected_delivery_date()
        super().save(*args, **kwargs)