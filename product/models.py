from django.db import models
import shortuuid

# Choices for product status
STATUS_CHOICES = [
    ('Available', 'Available'),
    ('Sold', 'Sold'),
]

class Product(models.Model):
    # Unique identifier for the product
    p_id = models.CharField(
        max_length=22,  # Default length for shortuuid
        unique=True,
        default=shortuuid.uuid  # Automatically generate a short UUID for new products
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    starting_price = models.IntegerField()
    image = models.ImageField(upload_to='product_images')
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='Available')

    def __str__(self):
        return self.name
