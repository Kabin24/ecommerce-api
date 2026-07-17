"""
Accounts app models - Custom user model and user-related data.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import re


class User(AbstractUser):
    """
    Custom user model extending AbstractUser.
    - Uses email as the primary identifier instead of username
    - Adds phone number field for contact
    - Adds email verification tracking
    """
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False, help_text='Indicates if email is verified')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Keep username for Django compatibility
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return self.email
    
    def clean(self):
        super().clean()
        # Validate phone number format if provided
        if self.phone_number:
            if not re.match(r'^\+?1?\d{9,15}$', self.phone_number.replace('-', '').replace(' ', '')):
                raise ValidationError({'phone_number': 'Invalid phone number format.'})


class EmailVerificationToken(models.Model):
    """
    Model to store email verification tokens.
    Tokens are single-use and expire after a set time.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification_token')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Verification token for {self.user.email}"
    
    def is_valid(self):
        """Check if token is still valid."""
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()


class UserProfile(models.Model):
    """
    Extended user profile for additional information.
    Separated to keep User model clean and follow Django best practices.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/%Y/%m/%d/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Profile for {self.user.email}"
