from django.urls import path
from . import views


urlpatterns = [
    path('Products/AddProduct/',views.add_products,name='addproducts'),
    
]
