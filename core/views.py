from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

from .forms import EditProfileForm
from .decorators import allowed_roles

from customers.models import Customer
from products.models import Product
from invoices.models import Invoice
from payments.models import Payment


def login_view(request):

    # ===========================
    # Create Groups Automatically
    # ===========================

    admin_group, _ = Group.objects.get_or_create(name="Admin")
    accountant_group, _ = Group.objects.get_or_create(name="Accountant")
    staff_group, _ = Group.objects.get_or_create(name="Staff")

    # ===========================
    # Create Admin User
    # ===========================

    if not User.objects.filter(username="admin").exists():

        admin = User.objects.create_superuser(
            username="admin",
            email="admin@invoxa.com",
            password="Admin@123"
        )

    else:

        admin = User.objects.get(username="admin")

    if not admin.groups.filter(name="Admin").exists():
        admin.groups.add(admin_group)

    # ===========================
    # Create Accountant User
    # ===========================

    if not User.objects.filter(username="accountant").exists():

        accountant = User.objects.create_user(
            username="accountant",
            email="accountant@invoxa.com",
            password="Account@123"
        )

        accountant.groups.add(accountant_group)

    # ===========================
    # Create Staff User
    # ===========================

    if not User.objects.filter(username="staff").exists():

        staff = User.objects.create_user(
            username="staff",
            email="staff@invoxa.com",
            password="Staff@123"
        )

        staff.groups.add(staff_group)

    # ===========================
    # Already Logged In
    # ===========================

    if request.user.is_authenticated:
        return redirect("dashboard")

    # ===========================
    # Login
    # ===========================

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

            messages.error(
                request,
                "Invalid username or password."
            )

    return render(request, "login.html")


@login_required(login_url="login")
@allowed_roles(["Admin", "Accountant", "Staff"])
def dashboard(request):

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


@login_required(login_url="login")
def profile(request):

    return render(
        request,
        "core/profile.html",
        {
            "user": request.user
        }
    )


@login_required(login_url="login")
def edit_profile(request):

    if request.method == "POST":

        form = EditProfileForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully!"
            )

            return redirect("profile")

    else:

        form = EditProfileForm(
            instance=request.user
        )

    return render(
        request,
        "core/edit_profile.html",
        {
            "form": form
        }
    )