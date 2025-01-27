from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from product.models import Product
from django.urls import reverse_lazy

class ProductList(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

class ProductDetail(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'id'

class PrdocutCreate(CreateView):
    model = Product
    fields = "__all__"
    template_name = 'product/product_create.html'
    success_url = reverse_lazy("product-list")

class ProductUpdate(UpdateView):
    model = Product
    fields = "__all__"
    success_url = reverse_lazy("product-list")
    template_name = 'product/product_update.html'
    pk_url_kwarg = 'id'


class ProductDelete(DeleteView):
    model = Product
    template_name = 'product/product_delete.html'
    success_url = reverse_lazy("product-list")
    pk_url_kwarg = 'id'
    
