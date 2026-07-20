from django.db import models
from customers.models import Customer
from products.models import Product


class Invoice(models.Model):

    invoice_number = models.CharField(max_length=20, unique=True)

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    invoice_date = models.DateField(auto_now_add=True)

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("Paid", "Paid"),
            ("Pending", "Pending")
        ],
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_number


class InvoiceItem(models.Model):

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    gst = models.IntegerField(default=18)

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.product.name