from django.urls import path
from . import views


urlpatterns = [
    path('AddProduct/',views.add_products,name='addproducts'),
    path('AddColour/',views.add_colour,name='addcolour'),
    
]
