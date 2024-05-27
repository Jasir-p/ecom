from django.urls import path
from .views import *


urlpatterns = [
    path("AddOffer/",add_offer,name="add_offer"),
    path('Viewoffer/',view_offers,name="view_offer"),
    path('EditOffer/<int:offer_id>',edit_offer,name="edit_offer"),
    path("toggle_offer/<int:id>",active_section,name="toggle_offer"),
]
