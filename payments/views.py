from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from core.decorators import allowed_roles

from .models import Payment
from .forms import PaymentForm
from invoices.models import Invoice



@login_required(login_url="login")
@allowed_roles(["Admin", "Accountant"])
def payment_list(request):

    payments = Payment.objects.select_related(
        "invoice",
        "invoice__customer"
    ).order_by("-payment_date")

    return render(
        request,
        "payments/payment_list.html",
        {
            "payments": payments
        }
    )


@login_required(login_url="login")
@allowed_roles(["Admin", "Accountant"])
def add_payment(request):

    if request.method == "POST":

        form = PaymentForm(request.POST)

        if form.is_valid():

            payment = form.save(commit=False)

            invoice = payment.invoice

            # Automatically use invoice total
            payment.amount = invoice.total_amount

            payment.save()

            # Update invoice status
            invoice.status = "Paid"
            invoice.save()

            messages.success(
                request,
                "Payment recorded successfully."
            )

            return redirect("payment_list")

    else:

        form = PaymentForm()

    return render(
        request,
        "payments/add_payment.html",
        {
            "form": form
        }
    )


@login_required(login_url="login")
@allowed_roles(["Admin", "Accountant"])
def get_invoice_details(request, invoice_id):

    invoice = get_object_or_404(Invoice, id=invoice_id)

    data = {

        "customer": invoice.customer.name,

        "amount": str(invoice.total_amount),

        "status": invoice.status,

    }

    return JsonResponse(data)