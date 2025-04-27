from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from product.models import Product, Auction, Bid
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views import View
from .forms import ProductForm, ProductImageFormSet, AuctionForm, AuctionUpdateForm
from django.contrib import messages

class ProductList(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    paginate_by = 6 

    
    
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
        product.views += 1  # Increment the view count
        product.save()  # Save the updated view count
        # Get the auction associated with this product (if it exists)
        auction = Auction.objects.filter(product=product, status="Live").first()
        bid_count = Bid.objects.filter(auction=auction).count() if auction else 0


        context['bid_count'] = bid_count
        if auction:
            context["auction_id"] = auction.id  
        else:
            context["auction_id"] = None  # Handle cases where no auction exists

        context["product_id"] = product.id
        return context
    
class ProductCreate(LoginRequiredMixin, View):
    template_name = 'product/product_create.html'
    login_url = 'login'
    success_message = "Product created successfully!"

    def get(self, request):
        return render(request, self.template_name, {
            'form': ProductForm(),
            'formset': ProductImageFormSet(),
        })

    def post(self, request):
        form = ProductForm(request.POST, request.FILES)
        formset = ProductImageFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()

            formset.instance = product
            formset.save()

            return redirect('product-auction-update', id=product.auction.id)


        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
        })


class ProductUpdate(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['name', 'description', 'starting_price', 'image', 'status']
    success_url = reverse_lazy("product-list")
    template_name = 'product/product_update.html'
    pk_url_kwarg = 'id'
    login_url = 'login'
    success_message = "Product updated successfully!"

    

class AuctionUpdate(LoginRequiredMixin, UpdateView):
    model = Auction
    form_class = AuctionUpdateForm
    success_url = reverse_lazy("product-list")
    template_name = 'product/auction_update.html'
    pk_url_kwarg = 'id'
    login_url = 'login'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Auction updated successfully!")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "There was an error updating the auction.")
        return response
    

class ProductDelete(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'product/product_delete.html'
    success_url = reverse_lazy("product-list")
    pk_url_kwarg = 'id'
    login_url = 'login'
    success_message = "Product deleted successfully!"


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
