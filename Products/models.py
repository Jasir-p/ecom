from django.db import models
from Admin.models import *

# Create your models here.

class Product(models.Model):
    p_name=models.CharField(max_length=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    catagory=models.ForeignKey(Catagory,on_delete=models.CASCADE,)
    brand=models.ForeignKey(Brand,on_delete=models.CASCADE,)
    thumbnail=models.ImageField(upload_to='products/')
    img1=models.ImageField(upload_to='products/',null=True)
    img2=models.ImageField(upload_to='products/',null=True)
    img3=models.ImageField(upload_to='products/',null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_listed=models.BooleanField(default=True)

    
    def __str__(self):
        return self.p_name
    

class Color_products(models.Model):
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color_name = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.color_name} ({self.product.p_name})"
class size_variant(models.Model):
    size = models.CharField(max_length=10)
    quantity = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE,default=None)
    Color_products=models.ForeignKey(Color_products,on_delete=models.CASCADE)   
    def __str__(self):
        return f"{self.size} ({self.Color_products.color_name})"