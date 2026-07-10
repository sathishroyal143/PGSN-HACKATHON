"""
User models for CareBridge-AI.
Custom user model with role-based access control, profile management, and audit fields.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    """Custom manager for User model"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user"""
        if not email:
            raise ValueError('Email address is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class UserRole(models.TextChoices):
    """User role choices"""
    ADMIN = 'ADMIN', 'Admin'
    FAMILY = 'FAMILY', 'Family Member'
    COMPANION = 'COMPANION', 'Care Companion'
    SUPPORT = 'SUPPORT', 'Support Staff'


class Gender(models.TextChoices):
    """Gender choices"""
    MALE = 'MALE', 'Male'
    FEMALE = 'FEMALE', 'Female'
    OTHER = 'OTHER', 'Other'
    PREFER_NOT_TO_SAY = 'PREFER_NOT_TO_SAY', 'Prefer not to say'


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for CareBridge-AI.
    Supports multiple user roles: Family, Companion, Admin, Support.
    """
    
    # Authentication fields
    email = models.EmailField(
        unique=True,
        db_index=True,
        help_text='Unique email address for authentication'
    )
    phone_number = PhoneNumberField(
        unique=True,
        db_index=True,
        help_text='Unique phone number with country code'
    )
    
    # Role and permissions
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.FAMILY,
        db_index=True,
        help_text='User role in the system'
    )
    
    # Personal information
    first_name = models.CharField(max_length=100, help_text='First name')
    last_name = models.CharField(max_length=100, help_text='Last name')
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        blank=True,
        null=True,
        help_text='Gender'
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text='Date of birth'
    )
    
    # Profile information
    profile_picture = models.ImageField(
        upload_to='users/profiles/%Y/%m/',
        blank=True,
        null=True,
        help_text='Profile picture'
    )
    bio = models.TextField(
        blank=True,
        max_length=500,
        help_text='Short biography'
    )
    
    # Address information
    address_line_1 = models.CharField(
        max_length=255,
        blank=True,
        help_text='Address line 1'
    )
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        help_text='Address line 2'
    )
    city = models.CharField(max_length=100, blank=True, help_text='City')
    state = models.CharField(max_length=100, blank=True, help_text='State')
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        validators=[RegexValidator(r'^\d{6}$', 'Enter a valid 6-digit postal code')],
        help_text='6-digit postal code'
    )
    country = models.CharField(
        max_length=100,
        default='India',
        help_text='Country'
    )
    
    # Geolocation
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text='Latitude coordinate'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text='Longitude coordinate'
    )
    
    # Verification status
    is_email_verified = models.BooleanField(
        default=False,
        help_text='Email verification status'
    )
    is_phone_verified = models.BooleanField(
        default=False,
        help_text='Phone verification status'
    )
    is_profile_complete = models.BooleanField(
        default=False,
        help_text='Profile completion status'
    )
    
    # Account status
    is_active = models.BooleanField(
        default=True,
        help_text='Active status'
    )
    is_staff = models.BooleanField(
        default=False,
        help_text='Staff status'
    )
    is_blocked = models.BooleanField(
        default=False,
        help_text='Blocked status'
    )
    
    # Preferences
    notification_enabled = models.BooleanField(
        default=True,
        help_text='Enable notifications'
    )
    email_notification_enabled = models.BooleanField(
        default=True,
        help_text='Enable email notifications'
    )
    sms_notification_enabled = models.BooleanField(
        default=True,
        help_text='Enable SMS notifications'
    )
    push_notification_enabled = models.BooleanField(
        default=True,
        help_text='Enable push notifications'
    )
    
    # Device tokens for push notifications
    fcm_token = models.TextField(
        blank=True,
        help_text='Firebase Cloud Messaging token'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text='Creation timestamp')
    updated_at = models.DateTimeField(auto_now=True, help_text='Last update timestamp')
    last_login_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Last login timestamp'
    )
    email_verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Email verification timestamp'
    )
    phone_verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Phone verification timestamp'
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional metadata'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Return short name"""
        return self.first_name
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if not self.date_of_birth:
            return None
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def is_verified(self):
        """Check if user is fully verified"""
        return self.is_email_verified and self.is_phone_verified
    
    def mark_email_verified(self):
        """Mark email as verified"""
        self.is_email_verified = True
        self.email_verified_at = timezone.now()
        self.save(update_fields=['is_email_verified', 'email_verified_at'])
    
    def mark_phone_verified(self):
        """Mark phone as verified"""
        self.is_phone_verified = True
        self.phone_verified_at = timezone.now()
        self.save(update_fields=['is_phone_verified', 'phone_verified_at'])
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login_at = timezone.now()
        self.save(update_fields=['last_login_at'])
    
    def block_user(self, reason=None):
        """Block user account"""
        self.is_blocked = True
        self.is_active = False
        if reason:
            self.metadata['block_reason'] = reason
            self.metadata['blocked_at'] = timezone.now().isoformat()
        self.save(update_fields=['is_blocked', 'is_active', 'metadata'])
    
    def unblock_user(self):
        """Unblock user account"""
        self.is_blocked = False
        self.is_active = True
        if 'block_reason' in self.metadata:
            self.metadata['unblocked_at'] = timezone.now().isoformat()
        self.save(update_fields=['is_blocked', 'is_active', 'metadata'])
    
    def check_profile_completion(self):
        """Check and update profile completion status"""
        required_fields = [
            self.first_name,
            self.last_name,
            self.phone_number,
            self.email,
            self.date_of_birth,
            self.gender,
            self.address_line_1,
            self.city,
            self.state,
            self.postal_code,
        ]
        
        self.is_profile_complete = all(required_fields)
        self.save(update_fields=['is_profile_complete'])
        return self.is_profile_complete


class UserActivity(models.Model):
    """Track user activity for analytics and security"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        help_text='User'
    )
    activity_type = models.CharField(
        max_length=50,
        db_index=True,
        help_text='Type of activity'
    )
    description = models.TextField(help_text='Activity description')
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text='IP address'
    )
    user_agent = models.TextField(blank=True, help_text='User agent string')
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional metadata'
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text='Activity timestamp')
    
    class Meta:
        db_table = 'user_activities'
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.created_at}"
