from django.db import models
import shortuuid

STATUS_CHOICES = [
    ('A', 'Available'),
    ('S', 'Sold'),
]

class Product(models.Model):
    p_id = models.CharField(
        max_length=22, 
        unique=True, 
        default=shortuuid.uuid
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    starting_price = models.IntegerField()
    image = models.ImageField(upload_to='product_images')
    status = models.CharField(choices=STATUS_CHOICES, max_length=1)

    def __str__(self):
        return self.name
