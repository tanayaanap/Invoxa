from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum

from invoices.models import Invoice
from payments.models import Payment

from customers.models import Customer
from products.models import Product


def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


def dashboard(request):

    if not request.user.is_authenticated:
        return redirect("login")

    total_customers = Customer.objects.count()

    total_products = Product.objects.count()

    total_invoices = Invoice.objects.count()

    total_revenue = Invoice.objects.filter(
        status="Paid"
    ).aggregate(
        Sum("total_amount")
    )["total_amount__sum"] or 0

    recent_invoices = Invoice.objects.select_related(
        "customer"
    ).order_by("-created_at")[:5]

    paid_amount = Payment.objects.aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    pending_amount = Invoice.objects.filter(
        status="Pending"
    ).aggregate(
        Sum("total_amount")
    )["total_amount__sum"] or 0

    paid_invoices = Invoice.objects.filter(
    status="Paid"
    ).count()

    pending_invoices = Invoice.objects.filter(
    status="Pending"
    ).count()

    context = {

        "total_customers": total_customers,

        "total_products": total_products,

        "total_invoices": total_invoices,

        "total_revenue": total_revenue,

        "recent_invoices": recent_invoices,

        "paid_amount": paid_amount,

        "pending_amount": pending_amount,

        "paid_invoices": paid_invoices,

        "pending_invoices": pending_invoices,


    }

    return render(
        request,
        "dashboard.html",
        context
    )


def logout_view(request):
    logout(request)
    return redirect("login")