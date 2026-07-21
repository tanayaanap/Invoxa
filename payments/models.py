from django.db import models
from invoices.models import Invoice


class Payment(models.Model):

    invoice = models.OneToOneField(
        Invoice,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("Cash","Cash"),
            ("UPI","UPI"),
            ("Card","Card"),
            ("Net Banking","Net Banking"),
        ]
    )

    payment_date = models.DateField(auto_now_add=True)

    reference_number = models.CharField(
        max_length=100,
        blank=True
    )

    def __str__(self):
        return self.invoice.invoice_number