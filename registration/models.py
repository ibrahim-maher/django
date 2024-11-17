from django.db import models
from django.conf import settings
from events.models import Event
import json


class Ticket(models.Model):
    """
    Defines different types of tickets for an event, e.g., General, VIP, Early Bird.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="ticket_types")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use AUTH_USER_MODEL
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    capacity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.event.name}"


class RegistrationField(models.Model):
    """
    Allows customization of registration forms with dynamic fields like text, email, etc.
    """
    FIELD_TYPES = [
        ('text', 'Text'),
        ('email', 'Email'),
        ('number', 'Number'),
        ('dropdown', 'Dropdown'),
        ('checkbox', 'Checkbox'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="custom_fields")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use AUTH_USER_MODEL
    field_name = models.CharField(max_length=50)  # e.g., "Company Name"
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    is_required = models.BooleanField(default=True)
    options = models.TextField(null=True, blank=True)  # For dropdown (comma-separated)

    def __str__(self):
        return f"{self.field_name} - {self.event.name}"


class Registration(models.Model):
    """
    Represents a registration for an event.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ticket_type = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, blank=True)
    registration_data = models.TextField(default='{}')  # To store dynamic form data as JSON
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"

    def get_registration_data(self):
        """
        Deserialize registration_data into a Python dictionary.
        """
        try:
            return json.loads(self.registration_data)
        except json.JSONDecodeError:
            return {}

    def set_registration_data(self, data):
        """
        Serialize a Python dictionary into registration_data.
        """
        self.registration_data = json.dumps(data)


class QRCode(models.Model):
    """
    Represents a QR code generated for a ticket.
    """
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name="qrcode")
    registration = models.ForeignKey(
        Registration,
        on_delete=models.SET_NULL,
        null=True,  # Allow null values
        blank=True  # Optional for admin forms
    )
    qr_image = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    def __str__(self):
        return f"QR Code for {self.ticket.user.username} - {self.ticket.event.name}"
