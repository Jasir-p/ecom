from django.db import models
from Userapp.models import CustomUser
from Products.models import Color_products, size_variant


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
    products = models.ManyToManyField(Color_products, through="CartItem")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    coupon_applied = models.BooleanField(default=False, null=True, blank=True)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True
    )

    def update_total_amount(self):
        total_amount = sum(item.total_price for item in self.cart.all())
        self.total_amount = total_amount
        self.save()

    def check_cart_items_exist(self):
        return self.cart.exists()

    def Totel(self):

        Total = 0
        if self.check_cart_items_exist():
            if self.total_amount > 3000:
                Total = self.total_amount
            else:
                Total = self.total_amount + 50
        return Total


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="cart", on_delete=models.CASCADE)
    product = models.ForeignKey(Color_products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    product_size_color = models.ForeignKey(
        size_variant, on_delete=models.CASCADE, null=True
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True
    )

    def save(self, *args, **kwargs):
        if self.product_size_color.quantity >= self.quantity:
            self.total_price = self.product.product.price * self.quantity
            super().save(*args, **kwargs)
            # Update the total_amount of the cart after saving the CartItem
            self.cart.update_total_amount()


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100)
    House_no = models.CharField(max_length=100, blank=True, null=True)

    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    pincode = models.CharField(max_length=20)
    is_delete = models.BooleanField(default=False, null=True)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state}, {self.country}"
