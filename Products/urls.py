from django.urls import path
from . import views


urlpatterns = [
    path('AddProduct/',views.add_products,name='addproducts'),
    path('AddColour/',views.add_colour,name='addcolour'),
    path('AddSize/',views.add_size,name='addsize'),
    path('ViewProducts/',views.view_product,name='viewproducts'),
    path('UnlistProduct/<int:id>',views.unlist_product,name='unlist_product'),
    path('Editproduct/<int:id>',views.edit_product,name='editproduct'),
    path('Unlistproduct/',views.view_unlist,name="unlist_products"),
    path('Listproduct/<int:id>',views.list_product,name='List_product'),
    
    path('ProductVariant/<int:id>',views.product_variant,name="product_variant"),
    path('Edit_variant/<int:id>',views.edit_variant,name="edit_variant"),
    path('UnlistBrand/<int:id>',views.unlist_variant,name="unlist_variant"),
    
]
