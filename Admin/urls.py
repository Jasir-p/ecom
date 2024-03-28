from django.urls import path
from . import views

urlpatterns = [
    path('AdminLogin/',views.login,name='adminlogin'),
    path('DashBord/',views.dashbord,name='dashbord'),
    path('UserDetails/',views.view_user,name='userdetail'),
    path('Category/',views.category,name='category'),
    path('Brand/',views.brand,name='brand'),
    path('ViewCategory/',views.view_category,name='view_category'),
    path('AdminLogout/',views.logout,name='adminlogout'),
    path('ViewBrand/',views.view_brands,name='viewbrand'),
    path('DelCategory/<int:ca_id>',views.category_unlist,name='delcategory'),
    path('ViewUnlistCategory/',views.unlist_categories,name='unlistcategory'),
    path('EditCategory/<int:ca_id>',views.edit_category,name='EditCatogory'),
    path('ListCategory/<int:ca_id>',views.list_category,name='listcategory')
       
    ]

   


