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

class ClientProfile(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    company_name=models.CharField(max_length=100,blank=True)
    organization_details=models.TextField(blank=True)
    website=models.URLField(blank=True)
    location=models.CharField(max_length=100,blank=True)
    def __str__(self):
        return self.user.username

class Project(models.Model):
    STATUS_CHOICES=[
        ('draft','Draft'),
        ('published','Published'),
        ('paused','Paused'),
        ('closed','Closed'),
        ('archived','Archived'),]
    client=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='projects')
    title=models.CharField(max_length=100)
    description=models.TextField()
    budget=models.DecimalField(max_digits=10,decimal_places=2)
    deadline=models.DateField()
    required_skills=models.TextField()
    status=models.CharField(choices=STATUS_CHOICES,default='draft')
    created_url=models.DateTimeField(auto_now_add=True)
    updated_url=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title

class Proposal(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='proposals')
    freelancer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    cover_letter = models.TextField()
    proposed_budget = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_duration = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),],
        default='pending')
    def __str__(self):
        return self.project.title

class Contract(models.Model):
    proposal=models.OneToOneField(Proposal,on_delete=models.CASCADE,related_name='contract')
    status=models.CharField(max_length=20,choices=[
        ('active','Active'),
        ('completed','Completed'),
        ('cancelled','Cancelled'),],
        default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.proposal.project.title

class Message(models.Model):
    contract=models.ForeignKey(Contract,on_delete=models.CASCADE,related_name='messages')
    sender=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    content=models.TextField()
    timestamp=models.DateTimeField(auto_now_add=True)
    is_read=models.BooleanField(default=False)
    def __str__(self):
        return self.sender.username