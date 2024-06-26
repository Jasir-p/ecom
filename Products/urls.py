from django.urls import path
from . import views


urlpatterns = [
    path("AddProduct/", views.add_products, name="addproducts"),
    path("AddColour/<int:id>", views.add_colour, name="addcolour"),
    path("AddSize/<int:id>", views.add_size, name="addsize"),
    path("ViewProducts/", views.view_product, name="viewproducts"),
    path("UnlistProduct/<int:id>", views.unlist_product, name="unlist_product"),
    path("Editproduct/<int:id>", views.edit_product, name="editproduct"),
    path("Unlistproduct/", views.view_unlist, name="unlist_products"),
    path("Listproduct/<int:id>", views.list_product, name="List_product"),
    path("ProductVariant/<int:id>", views.product_variant, name="product_variant"),
    path("Edit_variant/<int:id>", views.edit_variant, name="edit_variant"),
    path("Unlistvariant/<int:id>", views.unlist_variant, name="unlist_variant"),
    path('unlisted_variants/<int:product_id>/', views.unlisted_variants_view, name='unlisted_variants'),
    path("listvariant/<int:id>", views.list_variant, name="list_variant"),
]
