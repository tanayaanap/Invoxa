from django import forms
from .models import Payment
from invoices.models import Invoice


class PaymentForm(forms.ModelForm):

    class Meta:

        model = Payment

        fields = [
            "invoice",
            "payment_method",
            "reference_number",
        ]

        widgets = {

            "invoice": forms.Select(attrs={
                "class": "form-control"
            }),

            "payment_method": forms.Select(attrs={
                "class": "form-control"
            }),

            "reference_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Transaction ID (Optional)"
            }),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["invoice"].queryset = Invoice.objects.all()