from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "price",
        "gst",
        "stock",
        "created_at",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "gst",
        "created_at",
    )

    ordering = (
        "-created_at",
    )