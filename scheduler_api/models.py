from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, time
from django.utils import timezone
import zoneinfo
from django.conf import settings


class User(AbstractUser):

    '''
        User model with user type - Candidate, client

    '''
    class Types(models.TextChoices):
        CANDIDATE = "CANDIDATE","Candidate"
        CLIENT = "CLIENT", "Client"

    type = models.CharField(max_length=20, choices=Types.choices, default=Types.CANDIDATE)
    name = models.CharField(max_length=50) #Name of the user

    def get_absolute_url(self):
        return reverse("user_detail", kwargs={"username":self.username})


# Creates Model Manager class for Proxy model
class CandidateManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.CANDIDATE)

class ClientManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.CLIENT)
    
class Candidate(User):
    '''
        Proxy model - Candidate
    '''
    objects = CandidateManager()
    class Meta:
        proxy = True

    def save(self,*args, **kwargs):
        if not self.pk:
            self.type = User.Types.CANDIDATE
        return super().save(*args,**kwargs)


class Client(User):
    '''
        Proxy model - Client
    '''
    objects = ClientManager()
    class Meta:
        proxy = True

    def save(self,*args, **kwargs):
        if not self.pk:
            self.type = User.Types.CLIENT
        return super().save(*args,**kwargs)
    

TIMEZONE_CHOICES = ((x, x) for x in sorted(zoneinfo.available_timezones(), key=str.lower))

STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rescheduled', 'Reschedule'),
    )

class Interview(models.Model):
    '''
        Represents Interview details - client & candidate, time slot, status

    '''
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='candidate_detail')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="client_detail")
    date = models.DateField()
    time = models.TimeField()
    time_zone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default=timezone.get_default_timezone)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Interview - {self.candidate.username} with {self.client.username} on {self.date} at {self.time} {self.time_zone} ; Status: {self.get_status_display()}"

