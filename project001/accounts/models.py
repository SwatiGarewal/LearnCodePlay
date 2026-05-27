from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics/', default='default.png')
    mobile = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    dob = models.DateField(null=True)
    profession = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username