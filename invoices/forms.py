from django import forms
from .models import Invoice


class InvoiceForm(forms.ModelForm):

    class Meta:
        model = Invoice

        fields = [
            "customer",
            "due_date",
        ]

        widgets = {

            "due_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            )

        }