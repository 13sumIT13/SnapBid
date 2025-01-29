from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from userauth.models import User

STATUS_CHOICES = [
    ('A', 'Available'),
    ('S', 'Sold'),
]

BID_CHOICES = [
    ('Live', 'Live'),
    ('Closed', 'Closed'),
]


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    starting_price = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/')
    status = models.CharField(choices=STATUS_CHOICES, max_length=1, default='A')

    def __str__(self):
        return self.name


class Auction(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="auction")
    current_bid = models.PositiveIntegerField(null=True, blank=True)
    bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(choices=BID_CHOICES, max_length=10, default='Live')

    def __str__(self):
        return f"Auction for {self.product.name} - {self.status}"


# 🔥 Signal for auto-creating an Auction when a Product is created
@receiver(post_save, sender=Product)
def create_or_update_auction(sender, instance, created, **kwargs):
    """Ensure an auction is created or updated when a product is saved."""
    auction, created_auction = Auction.objects.get_or_create(product=instance)

    # If auction was just created, set the starting price
    if created_auction:
        auction.current_bid = instance.starting_price
        auction.status = 'Live'
    else:
        # If product is updated, sync starting price only if auction is live
        if auction.status == 'Live':
            auction.current_bid = instance.starting_price

    auction.save()
