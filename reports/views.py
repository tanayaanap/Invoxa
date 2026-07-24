from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from core.decorators import allowed_roles

from customers.models import Customer
from products.models import Product
from invoices.models import Invoice, InvoiceItem

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth

import json


@login_required(login_url="login")
@allowed_roles(["Admin"])
def report_dashboard(request):

    # ==========================================
    # Dashboard Counts
    # ==========================================

    total_customers = Customer.objects.count()

    total_products = Product.objects.count()

    total_invoices = Invoice.objects.count()

    paid_invoices = Invoice.objects.filter(
        status="Paid"
    ).count()

    pending_invoices = Invoice.objects.filter(
        status="Pending"
    ).count()

    overdue_invoices = Invoice.objects.filter(
        status="Overdue"
    ).count()

    # ==========================================
    # Revenue
    # ==========================================

    revenue = sum(
        invoice.total_amount
        for invoice in Invoice.objects.filter(status="Paid")
    )

    gst_collected = sum(
        invoice.gst_amount
        for invoice in Invoice.objects.filter(status="Paid")
    )

    # ==========================================
    # Monthly Revenue Chart
    # ==========================================

    monthly_data = (

        Invoice.objects.filter(status="Paid")

        .annotate(
            month=TruncMonth("invoice_date")
        )

        .values("month")

        .annotate(
            total=Sum("total_amount")
        )

        .order_by("month")

    )

    months = []
    revenues = []

    for item in monthly_data:

        months.append(
            item["month"].strftime("%b %Y")
        )

        revenues.append(
            float(item["total"])
        )

    # ==========================================
    # Top Selling Products
    # ==========================================

    top_products = (

        InvoiceItem.objects

        .values("product__name")

        .annotate(

            total_quantity=Sum("quantity"),

            total_revenue=Sum("total")

        )

        .order_by("-total_quantity")[:5]

    )

    # ==========================================
    # Top Customers
    # ==========================================

    top_customers = (

        Invoice.objects

        .values("customer__name")

        .annotate(

            invoices=Count("id"),

            total_purchase=Sum("total_amount")

        )

        .order_by("-total_purchase")[:5]

    )

    # ==========================================
    # Context
    # ==========================================

    context = {

        "total_customers": total_customers,

        "total_products": total_products,

        "total_invoices": total_invoices,

        "paid_invoices": paid_invoices,

        "pending_invoices": pending_invoices,

        "overdue_invoices": overdue_invoices,

        "revenue": float(revenue),

        "gst_collected": float(gst_collected),

        "months": json.dumps(months),

        "revenues": json.dumps(revenues),

        "top_products": top_products,

        "top_customers": top_customers,

    }

    return render(
        request,
        "reports/report_dashboard.html",
        context
    )