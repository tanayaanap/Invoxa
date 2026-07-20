from django.urls import path
from . import views

urlpatterns = [
    path("", views.invoice_list, name="invoice_list"),
    path("add/", views.add_invoice, name="add_invoice"),
    path("view/<int:pk>/", views.view_invoice, name="view_invoice"),
    path("edit/<int:pk>/", views.edit_invoice, name="edit_invoice"),
    path("delete/<int:pk>/", views.delete_invoice, name="delete_invoice"),
    path("pdf/<int:pk>/", views.generate_invoice_pdf, name="generate_invoice_pdf"),
]