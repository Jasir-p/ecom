from django.db import models

from Products.models import Color_products, size_variant


# Create your models here.


class Coupon(models.Model):
    title = models.CharField(max_length=50, null=True, blank=True)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    discount_amount = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=2
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    min_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    active = models.BooleanField(default=True)
    created = models.DateField(auto_now_add=True,null=True)


class CustomerCoupon(models.Model):
    user = models.ForeignKey('Userapp.CustomUser', on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)


class Cart(models.Model):
    user = models.OneToOneField('Userapp.CustomUser', on_delete=models.CASCADE)
    products = models.ManyToManyField(Color_products, through="CartItem")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    coupon_applied = models.BooleanField(default=False, null=True, blank=True)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True
    )
    shipping_charge=models.BooleanField(default=False)

    def update_total_amount(self):
        total_amount = sum(item.total_price  for item in self.cartitem.all() ) 
        if self.coupon:
            self.total_amount = total_amount - self.coupon.discount_amount
        else:
            self.total_amount = total_amount
        self.save()

    def remove_coupon(self):
        if self.coupon:
            self.coupon = None
            self.update_total_amount()  

    def coupon_applied_in(self):
        total_amount = sum(item.total_price for item in self.cartitem.all())
        if self.coupon:
            if self.coupon.min_amount <= total_amount:
                total_amount -= self.coupon.discount_amount
        return total_amount
    
    def check_cart_items_exist(self):
        return self.cartitem.exists()

    def Totel(self):

        Total = 0
        if self.check_cart_items_exist() :
            if self.total_amount > 3000:
                Total = self.total_amount
            else:
                Total = self.total_amount + 50
                self.shipping_charge=True
        return Total


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="cartitem", on_delete=models.CASCADE)
    product = models.ForeignKey(Color_products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    product_size_color = models.ForeignKey(
        size_variant, on_delete=models.CASCADE, null=True
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True
    )

    def save(self, *args, **kwargs):
        if self.product_size_color and self.product_size_color.quantity is not None and self.quantity is not None:
            if self.product_size_color.quantity >= self.quantity:
                if self.product.product.offer_price is not None:
                    self.total_price = self.product.product.offer_price * self.quantity
                elif self.product.product.price is not None:
                    self.total_price = self.product.product.price * self.quantity
                
                super().save(*args, **kwargs)
                # Update the total_amount of the cart after saving the CartItem
                self.cart.update_total_amount()
             


class Address(models.Model):
    user = models.ForeignKey('Userapp.CustomUser', on_delete=models.CASCADE)
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
