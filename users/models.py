from django.contrib.auth.models import AbstractUser
from django.db import models

class RoleChoices(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    EVENT_MANAGER = 'EVENT_MANAGER', 'Event Manager'
    USHER = 'USHER', 'Usher'
    VISITOR = 'VISITOR', 'Visitor'

class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.VISITOR)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    title = models.TextField(blank=True, null=True )

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == RoleChoices.ADMIN

    @property
    def is_event_manager(self):
        return self.role == RoleChoices.EVENT_MANAGER

    @property
    def is_usher(self):
        return self.role == RoleChoices.USHER

    @property
    def is_visitor(self):
        return self.role == RoleChoices.VISITOR
