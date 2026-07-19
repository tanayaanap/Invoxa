from django import forms
from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = [
            "name",
            "description",
            "price",
            "gst",
            "stock",
        ]

        widgets = {

            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Product Name"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter Product Description"
            }),

            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Price"
            }),

            "gst": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter GST (%)"
            }),

            "stock": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Available Stock"
            }),

        }