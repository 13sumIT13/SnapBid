from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from product.models import Product, Auction, Bid
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

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

    
    def get_context_data(self, **kwargs):
        """Pass product_id and auction_id to the template."""
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # Get the auction associated with this product (if it exists)
        auction = Auction.objects.filter(product=product, status="Live").first()

        if auction:
            context["auction_id"] = auction.id  
        else:
            context["auction_id"] = None  # Handle cases where no auction exists

        context["product_id"] = product.id
        return context
    
class PrdocutCreate(LoginRequiredMixin, CreateView):
    model = Product
    fields = "__all__"
    template_name = 'product/product_create.html'
    success_url = reverse_lazy("product-list")
    login_url = 'login'

    def set_owner(self, obj):
        obj.owner = self.request.user

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


class ProductAuction(LoginRequiredMixin, DetailView):
    model = Auction
    template_name = 'product/product_auction.html'
    context_object_name = 'auction'

    def get_context_data(self, **kwargs):
        """Pass product_id and auction_id to the template."""
        context = super().get_context_data(**kwargs)
        auction = self.get_object()

        # Get the auction associated with this product (if it exists)
        product = auction.product
        bid = Bid.objects.filter(auction=auction).reverse()

        context['product'] = product
        context['bid'] = bid

        return context
