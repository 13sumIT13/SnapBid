from django.shortcuts import render
from django.views.generic import ListView, DeleteView
from product.models import Product


class ProductList(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

class ProductDetail(DeleteView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    slug_field = 'p_id'  # Field in the model
    slug_url_kwarg = 'p_id'  # URL parameter 