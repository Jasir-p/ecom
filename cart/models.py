from django.db import models
from Userapp.models import *
from Products.models import *


# Create your models here.


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
    
class CustomerCoupon(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Color_products, through='CartItem')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    coupon_applied = models.BooleanField(default=False,null=True,blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,null=True)

    def totel_amount(self):
        total_amount=0
        cart1=self.cartitem.all()
        for i in cart1:
       
            total_amount += self.products.product.price * i.quanttity

        return total_amount


   

class CartItem(models.Model):
    cart = models.ForeignKey(Cart,related_name="cart", on_delete=models.CASCADE)
    product = models.ForeignKey(Color_products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    product_size_color = models.ForeignKey(size_variant, on_delete=models.CASCADE, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0,null=True)


class Address(models.Model):
    user = models.ForeignKey(CustomUser ,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,blank=True,null=True)
    address = models.CharField(max_length=100)
    House_no = models.CharField(max_length=100, blank=True, null=True)
    
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    pincode = models.CharField(max_length=20)
    is_delete = models.BooleanField(default=False,null=True)
    


    def __str__(self):
        return f"{self.address}, {self.city}, {self.state}, {self.country}"

        
        


   