from django.contrib import admin
from product.models import Product, Auction, Notification, Bid


admin.site.register(Product)
admin.site.register(Auction)
admin.site.register(Notification)
admin.site.register(Bid)

