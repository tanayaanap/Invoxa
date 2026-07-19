from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Customer
from .forms import CustomerForm


@login_required(login_url="login")
def customer_list(request):

    customers = Customer.objects.all()

    return render(
        request,
        "customers/customer_list.html",
        {
            "customers": customers
        }
    )


@login_required(login_url="login")
def add_customer(request):

    if request.method == "POST":

        form = CustomerForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Customer added successfully."
            )

            return redirect("customer_list")

    else:

        form = CustomerForm()

    return render(
        request,
        "customers/add_customer.html",
        {
            "form": form
        }
    )