from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from product.models import Product
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class ProductList(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    
class ProductDetail(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'id'
    login_url = 'login'

class PrdocutCreate(LoginRequiredMixin, CreateView):
    model = Product
    fields = "__all__"
    template_name = 'product/product_create.html'
    success_url = reverse_lazy("product-list")
    login_url = 'login'

class ProductUpdate(LoginRequiredMixin, UpdateView):
    model = Product
    fields = "__all__"
    success_url = reverse_lazy("product-list")
    template_name = 'product/product_update.html'
    pk_url_kwarg = 'id'
    login_url = 'login'


class ProductDelete(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'product/product_delete.html'
    success_url = reverse_lazy("product-list")
    pk_url_kwarg = 'id'
    login_url = 'login'
    
