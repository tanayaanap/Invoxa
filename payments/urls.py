from django.urls import path
from . import views

urlpatterns = [

    path("", views.payment_list, name="payment_list"),

    path("add/", views.add_payment, name="add_payment"),

     path("invoice/<int:invoice_id>/", views.get_invoice_details, name="get_invoice_details"
    ),

]