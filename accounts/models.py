from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'), 
        ('STUDENT', 'Student'),
        ('REPORTER', 'Reporter'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')

    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.username} - {self.role}"