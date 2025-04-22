from django.urls import path
from product.views import ProductList, ProductDetail, ProductCreate, ProductUpdate, ProductDelete, ProductAuction, AuctionUpdate

urlpatterns = [
    path("", ProductList.as_view(), name="product-list"),
    path('<int:id>/', ProductDetail.as_view(), name='product-detail'),
    path('create/', ProductCreate.as_view(), name='product-create'),
    path('update/<int:id>/', ProductUpdate.as_view(), name='product-update'),
    path('delete/<int:id>/', ProductDelete.as_view(), name='product-delete'),
    path('auction/<int:pk>/', ProductAuction.as_view(), name='product-auction'),
    path('auction/update/<int:id>/', AuctionUpdate.as_view(), name='product-auction-update'),
]

