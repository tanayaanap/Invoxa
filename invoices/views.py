from decimal import Decimal

from core.decorators import allowed_roles

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Invoice, InvoiceItem
from .forms import InvoiceForm
from products.models import Product
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.http import HttpResponse
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from payments.models import Payment
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from django.utils import timezone
from reportlab.platypus import (
    Table,
    TableStyle,
)

from reportlab.pdfbase.pdfmetrics import stringWidth


def format_currency(amount):
    # FIX: "₹" (U+20B9) has no glyph in ReportLab's built-in Helvetica font
    # (Base-14 PDF fonts), so it was rendering as a missing-glyph box (■).
    # "Rs." renders correctly with Helvetica without needing a custom TTF font.
    return f"Rs. {amount:,.2f}"


@login_required(login_url="login")
@allowed_roles(["Admin", "Accountant", "Staff"])
def invoice_list(request):

    invoices = Invoice.objects.all().order_by("-invoice_date")

    today = timezone.now().date()

    for invoice in invoices:

        if (
            invoice.status == "Pending"
            and invoice.due_date
            and invoice.due_date < today
        ):

            invoice.status = "Overdue"
            invoice.save()

    return render(
        request,
        "invoices/invoice_list.html",
        {
            "invoices": invoices
        }
    )


@login_required(login_url="login")
@allowed_roles(["Admin", "Accountant"])
def add_invoice(request):

    products = Product.objects.all()

    if request.method == "POST":

        form = InvoiceForm(request.POST)

        if form.is_valid():

            invoice = form.save(commit=False)

            invoice.invoice_number = (
                f"INV-{Invoice.objects.count()+1:04d}"
            )

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

            invoice.subtotal = subtotal

            invoice.gst_amount = subtotal * Decimal("0.18")

            invoice.total_amount = (
                invoice.subtotal +
                invoice.gst_amount
            )

            invoice.save()

            messages.success(
                request,
                "Invoice created successfully."
            )

            return redirect("invoice_list")

        else:

            print("========== FORM ERRORS ==========")
            print(form.errors)
            print("=================================")

            messages.error(
                request,
                "Please correct the form errors."
            )

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
@allowed_roles(["Admin", "Accountant"])
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
@allowed_roles(["Admin"])
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
@allowed_roles(["Admin", "Accountant", "Staff"])
def generate_invoice_pdf(request, pk):
    invoice = get_object_or_404(
        Invoice,
        pk=pk
    )

    payment = Payment.objects.filter(
        invoice=invoice
    ).first()

    # FIX: recompute each line's total as quantity * price instead of
    # trusting the stored InvoiceItem.total field. If an item was ever
    # saved with a bad/zero total (e.g. a front-end bug at creation time),
    # summing the stored values still produces 0.00. quantity * price is
    # always correct regardless of what got persisted.
    items = list(invoice.items.all())

    line_totals = []
    subtotal = Decimal("0.00")

    for item in items:
        line_total = (item.price * item.quantity).quantize(Decimal("0.01"))
        line_totals.append(line_total)
        subtotal += line_total

    gst_amount = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))
    total_amount = subtotal + gst_amount

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{invoice.invoice_number}.pdf"'
    )

    pdf = canvas.Canvas(response, pagesize=A4)

    width, height = A4

    # Load Company Logo
    logo = ImageReader("static/images/logo.png")

    pdf.drawImage(
        logo,
        40,
        height - 72,
        width=42,
        height=42,
        mask="auto"
    )

    # =====================================
    # COLORS
    # =====================================

    PRIMARY = colors.HexColor("#1E3A8A")
    LIGHT = colors.HexColor("#F8FAFC")
    BORDER = colors.HexColor("#CBD5E1")
    TEXT = colors.HexColor("#1F2937")
    GREEN = colors.HexColor("#16A34A")
    RED = colors.HexColor("#DC2626")
    ORANGE = colors.HexColor("#F59E0B")

    # =====================================
    # HEADER
    # =====================================

    pdf.setFillColor(PRIMARY)
    pdf.rect(0, height - 80, width, 80, fill=1)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawString(40, height - 45, "INVOXA")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, height - 63, "Professional Invoice Management System")
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawRightString(width - 40, height - 45, "INVOICE")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString(width - 40, height - 62, invoice.invoice_number)

    # =====================================
    # COMPANY INFORMATION
    # =====================================

    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, height - 110, "From")
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, height - 130, "Invoxa Technologies")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, height - 148, "Pune, Maharashtra")
    pdf.drawString(40, height - 163, "Phone : +91 9876543210")
    pdf.drawString(40, height - 178, "support@invoxa.com")
    pdf.drawString(40, height - 193, "GSTIN : 27ABCDE1234F1Z5")

    # =====================================
    # BILL TO CARD
    # =====================================

    pdf.setFillColor(LIGHT)
    pdf.roundRect(320, height - 220, 235, 115, 8, fill=1, stroke=0)
    pdf.setStrokeColor(BORDER)
    pdf.roundRect(320, height - 220, 235, 115, 8)
    pdf.setFillColor(PRIMARY)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(335, height - 125, "Bill To")
    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(335, height - 145, invoice.customer.name)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(335, height - 160, invoice.customer.email)
    pdf.drawString(335, height - 175, invoice.customer.phone)
    address = invoice.customer.address or "-"
    pdf.drawString(335, height - 190, address[:40])

    # =====================================
    # INVOICE DETAILS BOX
    # =====================================

    pdf.setFillColor(PRIMARY)
    pdf.rect(40, height - 255, width - 80, 28, fill=1)

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(
    50,
    height - 237,
    "Invoice Details"
)

    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica", 10)

    pdf.drawString(
    50,
    height - 275,
    f"Invoice No : {invoice.invoice_number}"
)

    pdf.drawString(
    220,
    height - 275,
    f"Date : {invoice.invoice_date}"
)

# NEW LINE
    pdf.drawString(
    50,
    height - 292,
    f"Due Date : {invoice.due_date}"
)

# Status
    if invoice.status == "Paid":
        pdf.setFillColor(GREEN)

    elif invoice.status == "Pending":
        pdf.setFillColor(ORANGE)

    else:
        pdf.setFillColor(RED)

    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawRightString(
    width - 55,
    height - 292,
    invoice.status
)

    pdf.setFillColor(TEXT)

    # =====================================
    # PRODUCT TABLE
    # =====================================

    data = [["Sr.", "Product", "Qty", "Price", "GST", "Total"]]

    for sr, (item, line_total) in enumerate(zip(items, line_totals), start=1):
        data.append([
            sr,
            item.product.name,
            item.quantity,
            format_currency(item.price),
            f"{item.gst} %",
            format_currency(line_total)
        ])

    # =====================================
    # WATERMARK
    # =====================================
    pdf.saveState()
    pdf.setFont("Helvetica-Bold", 70)
    pdf.setFillColorRGB(0.95, 0.95, 0.95)
    pdf.translate(220, 380)
    pdf.rotate(35)
    pdf.drawCentredString(0, 0, "INVOXA")
    pdf.restoreState()

    table = Table(
        data,
        colWidths=[40, 180, 55, 80, 55, 100]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("TOPPADDING", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )

    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, 40, height - 370)

    # =====================================
    # GST SUMMARY  (FIX: moved up so it clears the totals box below)
    # totals box top edge = box_y (120) + box_height (95) = 215
    # so this block must end comfortably above y=215
    # =====================================

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(340, 270, "GST Summary")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(340, 250, f"Taxable : {format_currency(subtotal)}")
    pdf.drawString(340, 233, f"GST : {format_currency(gst_amount)}")

    # =====================================
    # TOTALS BOX
    # =====================================

    box_x = 340
    box_y = 120

    pdf.setFillColor(LIGHT)
    pdf.roundRect(box_x, box_y, 200, 95, 6, fill=1, stroke=0)
    pdf.setStrokeColor(BORDER)
    pdf.roundRect(box_x, box_y, 200, 95, 6)
    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica", 10)

    pdf.drawString(box_x + 15, box_y + 70, "Subtotal")
    pdf.drawRightString(box_x + 185, box_y + 70, format_currency(subtotal))

    pdf.drawString(box_x + 15, box_y + 48, "GST (18%)")
    pdf.drawRightString(box_x + 185, box_y + 48, format_currency(gst_amount))

    pdf.setStrokeColor(colors.grey)
    pdf.line(box_x + 10, box_y + 35, box_x + 190, box_y + 35)

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(box_x + 15, box_y + 15, "Grand Total")
    pdf.drawRightString(box_x + 185, box_y + 15, format_currency(total_amount))

    # =====================================
    # PAYMENT STATUS
    # =====================================

    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(TEXT)
    pdf.drawString(40, 175, "Payment Status")

    if invoice.status == "Paid":
        pdf.setFillColor(GREEN)
    else:
        pdf.setFillColor(RED)

    pdf.roundRect(40, 145, 100, 22, 5, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.drawCentredString(90, 152, invoice.status)

    # =====================================
    # PAYMENT DETAILS
    # =====================================

    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, 120, "Payment Details")
    pdf.setFont("Helvetica", 10)

    if payment:
        pdf.drawString(40, 102, f"Method : {payment.payment_method}")
        pdf.drawString(40, 86, f"Reference : {payment.reference_number}")
    else:
        pdf.drawString(40, 102, "Payment Pending")

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, 58, "Bank Details")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, 42, "Bank : HDFC Bank")
    pdf.drawString(40, 28, "A/C : 123456789012")

    # =====================================
    # SIGNATURE
    # =====================================

    pdf.setFillColor(TEXT)
    pdf.line(420, 85, 540, 85)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(430, 70, "Authorized Signatory")

    # =====================================
    # FOOTER
    # =====================================

    pdf.setStrokeColor(BORDER)
    pdf.line(40, 50, width - 40, 50)
    pdf.setFillColor(colors.grey)
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawCentredString(width / 2, 35, "This is a computer generated invoice. No signature required.")
    pdf.drawCentredString(width / 2, 20, "Thank you for choosing INVOXA.")

    pdf.save()

    return response

@login_required(login_url="login")
def email_invoice(request, pk):
    

    invoice = get_object_or_404(
        Invoice,
        pk=pk
    )
    

    customer_email = invoice.customer.email

    if not customer_email:

        messages.error(
            request,
            "Customer email not found."
        )

        return redirect(
            "view_invoice",
            pk=pk
        )
 

    # Generate PDF
    pdf_response = generate_invoice_pdf(request, pk)
    

    pdf_bytes = pdf_response.content

    email = EmailMessage(

        subject=f"Invoice {invoice.invoice_number}",

        body=f"""
Hello {invoice.customer.name},

Please find your invoice attached.

Invoice Number : {invoice.invoice_number}

Amount : ₹{invoice.total_amount}

Thank you for choosing Invoxa.

Regards,
Invoxa Team
""",

        from_email=settings.EMAIL_HOST_USER,

        to=[customer_email]

    )

    email.attach(

        f"{invoice.invoice_number}.pdf",

        pdf_bytes,

        "application/pdf"

    )
    print("Sending email to:", customer_email)

    email.send(fail_silently=False)
    print("Email sent successfully")

    messages.success(

        request,

        "Invoice emailed successfully."

    )

    # THIS IS THE FIX
    return redirect("invoice_list")