from django.db import models
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
    starting_price = models.IntegerField()
    image = models.ImageField(upload_to='product_images')
    status = models.CharField(choices=STATUS_CHOICES, max_length=1)

    def __str__(self):
        return self.name

class Auction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    current_bid = models.IntegerField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(choices=BID_CHOICES, max_length=10)