from django.db import models
from Admin.models import *
from django.db.models.signals import pre_save,post_save,post_delete
from django.dispatch import receiver
from PIL import Image
from django.db.models import Sum

from Offer.models import *

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail = models.ImageField(upload_to="products/", null=True)
    description = models.TextField()
    catagory = models.ForeignKey(Catagory, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    offer_price=models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.thumbnail:
            img = Image.open(self.thumbnail.path)
            target_size = (260, 260)
            img = img.resize(target_size, Image.BICUBIC)
            img.save(self.thumbnail.path)
    
@receiver(post_save, sender=Catagory)
def update_color_products_listing_status(sender, instance, **kwargs):
    
        Product.objects.filter(catagory=instance).update(is_listed=instance.is_listed)


@receiver(post_save, sender=Brand)
def update_color_products_listing_status(sender, instance, **kwargs):
    
  Product.objects.filter(brand=instance).update(is_listed=instance.is_listed)


class Color_products(models.Model):

    product = models.ForeignKey(
        Product, related_name="color_product", on_delete=models.CASCADE
    )
    color_name = models.CharField(max_length=50)

    img1 = models.ImageField(upload_to="products/", null=True)
    img2 = models.ImageField(upload_to="products/", null=True)
    img3 = models.ImageField(upload_to="products/", null=True)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.color_name} ({self.product.name})"
    
    def is_in_stock(self):
        
        total_quantity = self.size.aggregate(total_quantity=Sum('quantity'))['total_quantity']
        
        if total_quantity is not None and total_quantity > 0:
            return True
        else:
            return False
    @receiver(post_save, sender=Product)
    def update_color_products_listing_status(sender, instance, **kwargs):
    
        Color_products.objects.filter(product=instance).update(is_listed=instance.is_listed)

    # def save(self, *args, **kwargs):
    #         super().save(*args, **kwargs)

    #         target_size = (300, 300)

    #         if self.img1:
    #             img = Image.open(self.img1.path)
    #             img = img.resize(target_size, Image.BICUBIC)
    #             img.save(self.img1.path)

    #         if self.img2:
    #             img = Image.open(self.img2.path)
    #             img = img.resize(target_size, Image.BICUBIC)
    #             img.save(self.img2.path)

    #         if self.img3:
    #             img = Image.open(self.img3.path)
    #             img = img.resize(target_size, Image.BICUBIC)
    #             img.save(self.img3.path)


class size_variant(models.Model):
    size = models.CharField(max_length=10)
    quantity = models.IntegerField()
    Color_products = models.ForeignKey(
        Color_products, related_name="size", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.size} ({self.Color_products.color_name})"


class Wishlist(models.Model):
    customer = models.OneToOneField('Userapp.CustomUser', on_delete=models.CASCADE)
    products = models.ManyToManyField(Color_products, related_name="wishlists")


@receiver([post_save, post_delete,pre_save], sender=Offer)
def update_product_price(sender, instance, **kwargs):

    product = instance.product
    category = instance.category
    if not instance.is_active and product:
        
        product.offer_price = 0
    
    if product and  instance.is_active :
        product_offers = Offer.objects.filter(product=product,is_active=True)
        max_discount = 0

        for offer in product_offers:
            if offer.discount_percentage > max_discount:
                max_discount = offer.discount_percentage
        
        final_price = product.price
        if max_discount > 0:
            final_price -= (final_price * max_discount / 100)
       
        product.offer_price = round(final_price)
        product.save()
    if not instance.is_active and category:
        products_in_category = Product.objects.filter(catagory=category)

        for product_in_category in products_in_category:
            product_in_category.offer_price = 0
            product_in_category.save()

    
    if category and instance.is_active:
        products_in_category = Product.objects.filter(catagory=category)

        for product_in_category in products_in_category:
            
            product_offers_in_category = Offer.objects.filter(product=product_in_category,is_active=True)

            if product_offers_in_category.exists():

                biggest_discount = max(offer.discount_percentage for offer in product_offers_in_category)
            else:
                biggest_discount = 0

            category_offers = Offer.objects.filter(category=category)
            biggest_discount_in_category = max((offer.discount_percentage for offer in category_offers), default=0)

            final_discount = max(biggest_discount, biggest_discount_in_category)

            final_price_in_category = product_in_category.price
            if final_discount > 0:
                final_price_in_category -= (final_price_in_category * final_discount / 100)

            product_in_category.offer_price = round(final_price_in_category)
            product_in_category.save()


