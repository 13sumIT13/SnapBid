from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from userauth.models import User
from django.utils import timezone
from datetime import timedelta



STATUS_CHOICES = [
    ('Available', 'Available'),
    ('Sold', 'Sold'),
]

BID_CHOICES = [
    ('Live', 'Live'),
    ('Closed', 'Closed'),
]


class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    starting_price = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/')
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='A')
    views = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"
    
class Auction(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="auction")
    current_bid = models.PositiveIntegerField(null=True, blank=True)
    bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(choices=BID_CHOICES, max_length=10, default='Live')

    end_time = models.DateTimeField(null=True, blank=True)    
    def __str__(self):
        return f"Auction for {self.product.name} - {self.status}"

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid by {self.user.username} for {self.auction.product.name} - {self.bid_amount}"
    
    
# 🔥 Signal for auto-creating an Auction when a Product is created
@receiver(post_save, sender=Product)
def create_auction(sender, instance, created, **kwargs):
    if created:
        Auction.objects.create(
            product=instance,
            current_bid=instance.starting_price,
            status='Live',
        )


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message}"
    
