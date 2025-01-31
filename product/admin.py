from django.contrib import admin
from product.models import Product, Auction, Notification


admin.site.register(Product)
admin.site.register(Auction)
admin.site.register(Notification)
