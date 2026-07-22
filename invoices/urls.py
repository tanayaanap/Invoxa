from django.urls import path
from . import views

urlpatterns = [

    # Invoice List
    path(
        "",
        views.invoice_list,
        name="invoice_list",
    ),

    # Add Invoice
    path(
        "add/",
        views.add_invoice,
        name="add_invoice",
    ),

    # View Invoice
    path(
        "view/<int:pk>/",
        views.view_invoice,
        name="view_invoice",
    ),

    # Edit Invoice
    path(
        "edit/<int:pk>/",
        views.edit_invoice,
        name="edit_invoice",
    ),

    # Delete Invoice
    path(
        "delete/<int:pk>/",
        views.delete_invoice,
        name="delete_invoice",
    ),

    # Download PDF
    path(
        "pdf/<int:pk>/",
        views.generate_invoice_pdf,
        name="generate_invoice_pdf",
    ),

    # Email Invoice
    path(
        "email/<int:pk>/",
        views.email_invoice,
        name="email_invoice",
    ),

]