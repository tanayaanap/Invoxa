from django.shortcuts import render, redirect, get_object_or_404

from .models import Product
from .forms import ProductForm


def product_list(request):

    products = Product.objects.all()

    return render(
        request,
        "products/product_list.html",
        {"products": products}
    )


def add_product(request):

    if request.method == "POST":

        form = ProductForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("product_list")

    else:

        form = ProductForm()

    return render(
        request,
        "products/add_product.html",
        {"form": form}
    )


def edit_product(request, pk):

    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            instance=product
        )

        if form.is_valid():

            form.save()

            return redirect("product_list")

    else:

        form = ProductForm(instance=product)

    return render(
        request,
        "products/edit_product.html",
        {
            "form": form
        }
    )


def delete_product(request, pk):

    product = get_object_or_404(Product, pk=pk)

    product.delete()

    return redirect("product_list")
