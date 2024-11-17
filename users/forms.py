# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from .models import CustomUser
import datetime


class CustomUserCreationForm(UserCreationForm):
    phone_validator = RegexValidator(
        regex=r'^\+?\d{10,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    email_validator = EmailValidator(message="Please enter a valid email address.")

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'title', 'email', 'role', 'phone_number', 'address', 'date_of_birth')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].required = True
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].required = True
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].required = True
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['title'].required = True
        self.fields['title'].widget.attrs.update({'class': 'form-control'})

        self.fields['role'].required = True
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        self.fields['phone_number'].required = True
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['address'].required = True
        self.fields['address'].widget.attrs.update({'class': 'form-control'})
        self.fields['date_of_birth'].required = True
        self.fields['date_of_birth'].widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise ValidationError("Phone number is required.")
        self.phone_validator(phone_number)
        return phone_number

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth:
            today = datetime.date.today()
            age = today.year - date_of_birth.year - (
                        (today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            if age < 18:
                raise ValidationError("You must be at least 18 years old to register.")
        return date_of_birth

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username


class EditProfileForm(forms.ModelForm):
    phone_validator = RegexValidator(
        regex=r'^\+?\d{10,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

    class Meta:
        model = CustomUser
        fields = ['phone_number', 'address', 'date_of_birth']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply attributes to ensure consistent styling and edit behavior
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control edit-mode d-none'})
        self.fields['address'].widget.attrs.update({'class': 'form-control edit-mode d-none'})
        self.fields['date_of_birth'].widget.attrs.update({'class': 'form-control edit-mode d-none', 'type': 'date'})

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        self.phone_validator(phone_number)
        return phone_number

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth:
            today = datetime.date.today()
            age = today.year - date_of_birth.year - (
                        (today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            if age < 18:
                raise ValidationError("You must be at least 18 years old.")
        return date_of_birth
