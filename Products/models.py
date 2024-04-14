from django.db import models
from Admin.models import *
from django.db.models.signals import pre_save
from django.dispatch import receiver
from PIL import Image

# Create your models here.

class Product(models.Model):
    name=models.CharField(max_length=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail=models.ImageField(upload_to='products/',null=True)
    description = models.TextField()
    catagory=models.ForeignKey(Catagory,on_delete=models.CASCADE)
    brand=models.ForeignKey(Brand,on_delete=models.CASCADE)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_listed=models.BooleanField(default=True)

    
    def __str__(self):
        return self.name
    

class Color_products(models.Model):
    
    product = models.ForeignKey(Product,related_name = 'color_product', on_delete=models.CASCADE)
    color_name = models.CharField(max_length=50)
   
    img1=models.ImageField(upload_to='products/',null=True)
    img2=models.ImageField(upload_to='products/',null=True)
    img3=models.ImageField(upload_to='products/',null=True)
    is_listed=models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.color_name} ({self.product.name})"

    def save(self, *args, **kwargs):
            super().save(*args, **kwargs)
        
       
            target_size = (50, 50)
            
            
            if self.img1:
                img = Image.open(self.img1.path)
                img = img.resize(target_size, Image.BICUBIC)
                img.save(self.img1.path)
                print('hi')

            
            if self.img2:
                img = Image.open(self.img2.path)
                img = img.resize(target_size, Image.BICUBIC)
                img.save(self.img2.path)

        
            if self.img3:
                img = Image.open(self.img3.path)
                img = img.resize(target_size, Image.BICUBIC)
                img.save(self.img3.path)



class size_variant(models.Model):
    size = models.CharField(max_length=10)
    quantity = models.IntegerField()
    
    Color_products=models.ForeignKey(Color_products,related_name = 'size',on_delete=models.CASCADE)   
    def __str__(self):
        return f"{self.size} ({self.Color_products.color_name})"