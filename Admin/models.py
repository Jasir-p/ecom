from django.db import models
from PIL import Image

# Create your models here.


class Catagory(models.Model):

    cat_name = models.CharField(max_length=60)
    cover_image = models.ImageField(upload_to="catagory/")
    cat_description = models.CharField(max_length=260)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.cat_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.cover_image:
            img = Image.open(self.cover_image.path)
            target_size = (300, 300)
            img = img.resize(target_size, Image.BICUBIC)
            img.save(self.cover_image.path)


class Brand(models.Model):
    B_name = models.CharField(max_length=60)
    cover_image = models.ImageField(upload_to="brand/")
    B_description = models.CharField(max_length=260)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.B_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.cover_image:
            img = Image.open(self.cover_image.path)
            target_size = (300, 300)
            img = img.resize(target_size, Image.BICUBIC)
            img.save(self.cover_image.path)
