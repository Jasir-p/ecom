from django.urls import path
from . import views


urlpatterns = [
    path('AddProduct/',views.add_products,name='addproducts'),
    path('AddColour/',views.add_colour,name='addcolour'),
    path('AddSize/',views.add_size,name='addsize'),
    path('ViewProducts/',views.view_product,name='viewproducts'),
    path('UnlistProduct/<int:id>',views.unlist_product,name='unlist_product')
    
]
