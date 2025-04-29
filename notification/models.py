from django.db import models
from userauth.models import User
# Create your models here.
  
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    heading = models.CharField(max_length=100, default="Notification")
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True) 

    def __str__(self):
        return f"{self.user.username} - {self.message}"