from django.urls import path
from product.views import ProductList, ProductDetail, PrdocutCreate, ProductUpdate, ProductDelete

urlpatterns = [
    path("", ProductList.as_view(), name="product-list"),
    path('<int:id>/', ProductDetail.as_view(), name='product-detail'),
    path('create/', PrdocutCreate.as_view(), name='product-create'),
    path('update/<int:id>/', ProductUpdate.as_view(), name='product-update'),
    path('delete/<int:id>/', ProductDelete.as_view(), name='product-delete'),
]

