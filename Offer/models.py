from django.db import models
from django.utils import timezone

# from Products.models import Product

class Offer(models.Model):
    CATEGORY = 'category'
    PRODUCT = 'product'
    OFFER_TYPE_CHOICES = [
        (CATEGORY, 'Category'),
        (PRODUCT, 'Product'),
    ]

    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)
    category = models.ForeignKey('Admin.Catagory', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey('Products.Product', on_delete=models.CASCADE, null=True, blank=True)
    discount_percentage = models.PositiveIntegerField()
    
    start_date = models.DateField(default=timezone.now)
    is_active=models.BooleanField(default=True)
    end_date = models.DateField()

    def __str__(self):
        if self.offer_type == self.CATEGORY and self.category:
            return f"{self.category.cat_name} - {self.discount_percentage}% DISCOUNT FROM {self.start_date} TO {self.end_date}"
        elif self.offer_type == self.PRODUCT and self.product:
            return f"{self.product.name} - {self.discount_percentage}% DISCOUNT FROM {self.start_date} TO {self.end_date}"
        else:
            return "Invalid offer"
