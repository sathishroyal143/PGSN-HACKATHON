"""
Family module models.

FamilyProfile  — extended profile for a FAMILY role user.
FamilyMember   — additional members linked to the primary family account.
EmergencyContact — emergency contacts stored per family profile.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()


class RelationshipType(models.TextChoices):
    SELF        = 'SELF',        'Self'
    SPOUSE      = 'SPOUSE',      'Spouse'
    PARENT      = 'PARENT',      'Parent'
    CHILD       = 'CHILD',       'Child'
    SIBLING     = 'SIBLING',     'Sibling'
    GRANDPARENT = 'GRANDPARENT', 'Grandparent'
    GRANDCHILD  = 'GRANDCHILD',  'Grandchild'
    UNCLE_AUNT  = 'UNCLE_AUNT',  'Uncle / Aunt'
    NEPHEW_NIECE= 'NEPHEW_NIECE','Nephew / Niece'
    FRIEND      = 'FRIEND',      'Friend'
    CAREGIVER   = 'CAREGIVER',   'Caregiver'
    OTHER       = 'OTHER',       'Other'


class FamilyProfile(models.Model):
    """
    Extended profile for a user with role=FAMILY.
    One-to-one with User. Created automatically on registration.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='family_profile',
    )

    # Preferred language / communication
    preferred_language = models.CharField(max_length=50, default='English')
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[('EMAIL', 'Email'), ('SMS', 'SMS'), ('CALL', 'Call'), ('WHATSAPP', 'WhatsApp')],
        default='SMS',
    )

    # Subscription / plan
    is_premium = models.BooleanField(default=False)
    premium_expires_at = models.DateTimeField(null=True, blank=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'family_profiles'
        verbose_name = 'Family Profile'
        verbose_name_plural = 'Family Profiles'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_deleted']),
        ]

    def __str__(self):
        return f"FamilyProfile — {self.user.get_full_name()}"


class FamilyMember(models.Model):
    """
    Additional family members linked to a FamilyProfile.
    These are the patients / dependants who will receive care.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family_profile = models.ForeignKey(
        FamilyProfile,
        on_delete=models.CASCADE,
        related_name='members',
    )

    # Personal details
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')],
        blank=True,
    )
    relationship = models.CharField(
        max_length=20,
        choices=RelationshipType.choices,
        default=RelationshipType.OTHER,
    )
    phone_number = PhoneNumberField(blank=True)
    profile_picture = models.ImageField(
        upload_to='family/members/%Y/%m/',
        blank=True,
        null=True,
    )

    # Medical quick-reference
    blood_group = models.CharField(max_length=5, blank=True)
    known_allergies = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)

    # Status
    is_primary_patient = models.BooleanField(
        default=False,
        help_text='Marks the main patient for this family account.',
    )
    is_active = models.BooleanField(default=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'family_members'
        verbose_name = 'Family Member'
        verbose_name_plural = 'Family Members'
        ordering = ['-is_primary_patient', 'first_name']
        indexes = [
            models.Index(fields=['family_profile', 'is_deleted']),
            models.Index(fields=['is_primary_patient']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.relationship})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class EmergencyContact(models.Model):
    """
    Emergency contacts for a FamilyProfile.
    Multiple contacts allowed; one can be marked primary.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family_profile = models.ForeignKey(
        FamilyProfile,
        on_delete=models.CASCADE,
        related_name='emergency_contacts',
    )

    name         = models.CharField(max_length=200)
    relationship = models.CharField(
        max_length=20,
        choices=RelationshipType.choices,
        default=RelationshipType.OTHER,
    )
    phone_number = PhoneNumberField()
    alternate_phone = PhoneNumberField(blank=True)
    email        = models.EmailField(blank=True)
    is_primary   = models.BooleanField(default=False)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'family_emergency_contacts'
        verbose_name = 'Emergency Contact'
        verbose_name_plural = 'Emergency Contacts'
        ordering = ['-is_primary', 'name']
        indexes = [
            models.Index(fields=['family_profile', 'is_primary']),
        ]

    def __str__(self):
        return f"{self.name} ({self.relationship}) — {self.phone_number}"
