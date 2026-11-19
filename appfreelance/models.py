from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    is_client=models.BooleanField(default=False)
    is_freelancer=models.BooleanField(default=False)
    email=models.EmailField(max_length=50)
    is_email_verified=models.BooleanField(default=False)
    def __str__(self):
        return self.username

class FreelancerProfile(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    biography=models.TextField(blank=True)
    skills=models.TextField(blank=True)
    experience=models.TextField(blank=True)
    hourly_rate=models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    def __str__(self):
        return self.user.username

class PortfolioItem(models.Model):
    freelancer = models.ForeignKey(
        FreelancerProfile,
        on_delete=models.CASCADE,
        related_name='portfolio_items'
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    project_url = models.URLField(blank=True)

    def __str__(self):
        return self.title