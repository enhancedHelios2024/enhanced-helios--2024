from django.db import models

from helios_auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos', blank=True)
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.user.user_id
