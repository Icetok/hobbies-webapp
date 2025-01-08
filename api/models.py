
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Hobby(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    hobbies = models.ManyToManyField(Hobby, related_name='users')


    def __str__(self):
        return self.username
    

    
class PageView(models.Model):
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"Page view count: {self.count}"



    