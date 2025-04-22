from django.contrib import admin
from product.models import Product, Auction, Notification, Bid, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 3
    min_num = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    
    
admin.site.register(Product, ProductAdmin)
admin.site.register(Auction)
admin.site.register(Notification)
admin.site.register(Bid)

