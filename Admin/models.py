from django.db import models

# Create your models here.


class Catagory(models.Model):
    
    cat_name=models.CharField(max_length=60)
    cover_image=models.ImageField(upload_to='catagory/')
    cat_description=models.CharField(max_length=260)
    is_listed=models.BooleanField(default=True)
    

    def __str__(self):
        return self.cat_name

    
class Brand(models.Model):

    B_name=models.CharField(max_length=60)
    cover_image=models.ImageField(upload_to='brand/')
    B_description=models.CharField(max_length=260)
    is_listed=models.BooleanField(default=True)
    
    def __str__(self):
        return self.B_name