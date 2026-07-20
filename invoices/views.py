from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Invoice, InvoiceItem
from .forms import InvoiceForm
from products.models import Product
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from django.shortcuts import get_object_or_404

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle

@login_required(login_url="login")
def invoice_list(request):

    invoices = Invoice.objects.all().order_by("-invoice_date")

    return render(
        request,
        "invoices/invoice_list.html",
        {
            "invoices": invoices
        }
    )


@login_required(login_url="login")
def add_invoice(request):

    products = Product.objects.all()

    if request.method == "POST":

        form = InvoiceForm(request.POST)

        if form.is_valid():

            invoice = form.save(commit=False)

            invoice.invoice_number = f"INV-{Invoice.objects.count() + 1:04d}"

            invoice.save()

            product_ids = request.POST.getlist("product[]")
            quantities = request.POST.getlist("quantity[]")
            prices = request.POST.getlist("price[]")
            totals = request.POST.getlist("total[]")

            subtotal = Decimal("0.00")

            for product_id, quantity, price, total in zip(
                product_ids,
                quantities,
                prices,
                totals
            ):

                if not product_id:
                    continue

                product = Product.objects.get(id=product_id)

                InvoiceItem.objects.create(
                    invoice=invoice,
                    product=product,
                    quantity=int(quantity),
                    price=Decimal(price),
                    gst=18,
                    total=Decimal(total)
                )

                subtotal += Decimal(total)

            gst_amount = subtotal * Decimal("0.18")
            total_amount = subtotal + gst_amount

            invoice.subtotal = subtotal
            invoice.gst_amount = gst_amount
            invoice.total_amount = total_amount

            invoice.save()

            messages.success(
                request,
                "Invoice created successfully."
            )

            return redirect("invoice_list")

    else:

        form = InvoiceForm()

    return render(
        request,
        "invoices/add_invoice.html",
        {
            "form": form,
            "products": products
        }
    )

@login_required(login_url="login")
def view_invoice(request, pk):

    invoice = get_object_or_404(
        Invoice,
        pk=pk
    )

    return render(
        request,
        "invoices/view_invoice.html",
        {
            "invoice": invoice
        }
    )

@login_required(login_url="login")
def edit_invoice(request, pk):

    invoice = get_object_or_404(
        Invoice,
        pk=pk
    )

    if request.method == "POST":

        form = InvoiceForm(
            request.POST,
            instance=invoice
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Invoice updated successfully."
            )

            return redirect("invoice_list")

    else:

        form = InvoiceForm(instance=invoice)

    return render(
        request,
        "invoices/edit_invoice.html",
        {
            "form": form,
            "invoice": invoice
        }
    )

@login_required(login_url="login")
def delete_invoice(request, pk):

    invoice = get_object_or_404(
        Invoice,
        pk=pk
    )

    if request.method == "POST":

        invoice.delete()

        messages.success(
            request,
            "Invoice deleted successfully."
        )

        return redirect("invoice_list")

    return render(
        request,
        "invoices/delete_invoice.html",
        {
            "invoice": invoice
        }
    )

@login_required(login_url="login")
def generate_invoice_pdf(request, pk):

    invoice = get_object_or_404(
        Invoice,
        pk=pk
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{invoice.invoice_number}.pdf"'
    )

    pdf = canvas.Canvas(response, pagesize=A4)

    width, height = A4

    # ===========================
    # Header
    # ===========================

    pdf.setFillColor(colors.darkblue)
    pdf.rect(0, height-70, width, 70, fill=1)

    pdf.setFillColor(colors.white)

    pdf.setFont("Helvetica-Bold", 24)

    pdf.drawString(40, height-45, "INVOXA")

    pdf.setFont("Helvetica", 11)

    pdf.drawRightString(
        width-40,
        height-45,
        "Invoice Management System"
    )

    # ===========================
    # Invoice Details
    # ===========================

    pdf.setFillColor(colors.black)

    pdf.setFont("Helvetica-Bold", 13)

    pdf.drawString(40, height-100, "Invoice Details")

    pdf.setFont("Helvetica", 11)

    pdf.drawString(
        40,
        height-120,
        f"Invoice No : {invoice.invoice_number}"
    )

    pdf.drawString(
        40,
        height-140,
        f"Date : {invoice.invoice_date}"
    )

    pdf.drawString(
        40,
        height-160,
        f"Status : {invoice.status}"
    )

    # ===========================
    # Customer Details
    # ===========================

    pdf.setFont("Helvetica-Bold", 13)

    pdf.drawString(
        320,
        height-100,
        "Customer"
    )

    pdf.setFont("Helvetica", 11)

    pdf.drawString(
        320,
        height-120,
        invoice.customer.name
    )

    pdf.drawString(
        320,
        height-140,
        invoice.customer.email
    )

    pdf.drawString(
        320,
        height-160,
        invoice.customer.phone
    )

    # ===========================
    # Product Table
    # ===========================

    data = [
        [
            "Product",
            "Qty",
            "Price",
            "GST",
            "Total"
        ]
    ]

    for item in invoice.items.all():

        data.append([
            item.product.name,
            str(item.quantity),
            f"₹ {item.price}",
            f"{item.gst}%",
            f"₹ {item.total}"
        ])

    table = Table(
        data,
        colWidths=[
            180,
            60,
            80,
            60,
            100
        ]
    )

    table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(-1,0),colors.darkblue),

            ("TEXTCOLOR",(0,0),(-1,0),colors.white),

            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

            ("GRID",(0,0),(-1,-1),1,colors.grey),

            ("BACKGROUND",(0,1),(-1,-1),colors.whitesmoke),

            ("BOTTOMPADDING",(0,0),(-1,0),10),

            ("ALIGN",(1,0),(-1,-1),"CENTER"),

        ])

    )

    table.wrapOn(pdf, width, height)

    table.drawOn(pdf, 40, height-420)

    # ===========================
    # Totals
    # ===========================

    pdf.setFont("Helvetica-Bold", 12)

    pdf.drawRightString(
        width-40,
        180,
        f"Subtotal : ₹ {invoice.subtotal}"
    )

    pdf.drawRightString(
        width-40,
        160,
        f"GST : ₹ {invoice.gst_amount}"
    )

    pdf.drawRightString(
        width-40,
        140,
        f"Grand Total : ₹ {invoice.total_amount}"
    )

    # ===========================
    # Footer
    # ===========================

    pdf.setFont("Helvetica-Oblique", 10)

    pdf.drawCentredString(
        width/2,
        50,
        "Thank you for choosing Invoxa!"
    )

    pdf.save()

    return response