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

            "customer": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "due_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            )

        }