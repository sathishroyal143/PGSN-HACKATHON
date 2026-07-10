"""
Care Services models.

Existing models (migration 0001):
  ServiceType     — legacy service type categories
  ServicePackage  — bookable packages under a ServiceType
  ServicePricing  — pricing rules for a ServicePackage

New models (migration 0002):
  ServiceCategory — three care modes: Scheduled, Instant, Emergency
  CareService     — individual services under a category
"""

import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone
from . import constants


# ── Legacy models (kept intact — referenced by bookings, existing migration) ──


class ServiceType(models.Model):
    """
    Legacy service type category.
    e.g. Hospital Visit, Home Care, Emergency.
    Retained for backward compatibility with existing bookings.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(
        max_length=30,
        choices=constants.SERVICE_TYPE_CHOICES,
        unique=True,
        db_index=True,
    )
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text='Icon class or URL')
    is_emergency = models.BooleanField(default=False, db_index=True)
    requires_companion = models.BooleanField(default=True)
    status = models.CharField(
        max_length=10,
        choices=constants.STATUS_CHOICES,
        default=constants.STATUS_ACTIVE,
        db_index=True,
    )
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service_types'
        verbose_name = 'Service Type'
        verbose_name_plural = 'Service Types'
        ordering = ['sort_order', 'name']

    def __str__(self) -> str:
        return self.name


class ServicePackage(models.Model):
    """
    A bookable service package under a ServiceType.
    Defines inclusions, duration, and companion requirements.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.CASCADE,
        related_name='packages',
        db_index=True,
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    inclusions = models.JSONField(default=list, help_text='List of included services')
    exclusions = models.JSONField(default=list, help_text='List of excluded services')
    min_duration_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1)
    max_duration_hours = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    companion_count = models.PositiveSmallIntegerField(default=1)
    requires_vehicle = models.BooleanField(default=False)
    requires_medical_training = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10,
        choices=constants.STATUS_CHOICES,
        default=constants.STATUS_ACTIVE,
        db_index=True,
    )
    is_featured = models.BooleanField(default=False, db_index=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service_packages'
        verbose_name = 'Service Package'
        verbose_name_plural = 'Service Packages'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['service_type', 'status']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self) -> str:
        return f"{self.service_type.name} — {self.name}"


class ServicePricing(models.Model):
    """
    Pricing rules for a ServicePackage.
    Supports hourly, fixed, and package pricing with surge multipliers.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.OneToOneField(
        ServicePackage,
        on_delete=models.CASCADE,
        related_name='pricing',
        null=True,
        blank=True,
    )
    service = models.ForeignKey(
        'CareService',
        on_delete=models.CASCADE,
        related_name='pricing_history',
        null=True,
        blank=True,
        db_index=True,
    )
    pricing_type = models.CharField(
        max_length=10,
        choices=constants.PRICING_TYPE_CHOICES,
        default=constants.PRICING_TYPE_HOURLY,
    )
    base_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text='Base price in INR',
    )
    price_per_hour = models.DecimalField(
        max_digits=8, decimal_places=2,
        null=True, blank=True,
        help_text='Per-hour rate for HOURLY pricing',
    )
    emergency_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Flat emergency charge in INR',
    )
    instant_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Flat instant booking charge in INR',
    )
    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Flat tax amount in INR',
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Flat discount amount in INR',
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Computed final service price in INR',
    )
    emergency_surcharge_pct = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal('50.00'),
        help_text='Emergency surcharge percentage',
    )
    night_surcharge_pct = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal('20.00'),
        help_text='Night-time surcharge percentage (10 PM – 6 AM)',
    )
    platform_commission_pct = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal('15.00'),
        help_text='Platform commission percentage',
    )
    gst_pct = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal('18.00'),
        help_text='GST percentage',
    )
    is_active = models.BooleanField(default=True, db_index=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    effective_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service_pricing'
        verbose_name = 'Service Pricing'
        verbose_name_plural = 'Service Pricing'
        indexes = [
            models.Index(
                fields=['service', 'is_active', 'effective_from'],
                name='service_pri_service_175329_idx',
            ),
        ]

    def __str__(self) -> str:
        return f"Pricing — {self.package.name} ({self.pricing_type})"

    def __str__(self) -> str:
        if self.service_id:
            return f"Pricing - {self.service.service_name}"
        return f"Pricing - {self.package.name} ({self.pricing_type})"

    def save(self, *args, **kwargs) -> None:
        """Keep service-level total_price synchronized."""
        self.total_price = self.calculate_service_total()
        super().save(*args, **kwargs)

    def calculate_service_total(self) -> Decimal:
        """Calculate final service price from flat pricing components."""
        total = (
            self.base_price
            + self.emergency_charge
            + self.instant_charge
            + self.tax
            - self.discount
        )
        return max(total, Decimal('0.00'))

    def calculate_total(
        self,
        hours: float = 1.0,
        is_emergency: bool = False,
        is_night: bool = False,
    ) -> dict:
        """
        Calculate full price breakdown for given parameters.

        Args:
            hours: Number of service hours requested.
            is_emergency: Whether emergency surcharge applies.
            is_night: Whether night surcharge applies.

        Returns:
            dict with base_price, surcharges, gst, and total.
        """
        h = Decimal(str(hours))
        base = self.base_price
        if self.pricing_type == constants.PRICING_TYPE_HOURLY and self.price_per_hour:
            base = self.price_per_hour * h

        emergency_surcharge = (
            base * self.emergency_surcharge_pct / Decimal('100')
        ) if is_emergency else Decimal('0')
        night_surcharge = (
            base * self.night_surcharge_pct / Decimal('100')
        ) if is_night else Decimal('0')

        subtotal = base + emergency_surcharge + night_surcharge
        commission = subtotal * self.platform_commission_pct / Decimal('100')
        gst = subtotal * self.gst_pct / Decimal('100')
        total = subtotal + gst

        return {
            'base_price': float(base),
            'emergency_surcharge': float(emergency_surcharge),
            'night_surcharge': float(night_surcharge),
            'subtotal': float(subtotal),
            'platform_commission': float(commission),
            'gst': float(gst),
            'total': float(total),
        }


# ── New models ─────────────────────────────────────────────────────────────────


class ServiceCategory(models.Model):
    """
    Top-level care category representing one of the three care modes:
    Scheduled Care, Instant Care, Emergency Care.

    Each category groups CareService records and defines the booking
    behaviour, priority, and availability rules for that mode.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(
        max_length=30,
        choices=constants.CATEGORY_CODE_CHOICES,
        unique=True,
        db_index=True,
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service_categories'
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['code', 'is_active'], name='service_cat_code_is_active_idx'),
        ]

    def __str__(self) -> str:
        return self.name


class CareService(models.Model):
    """
    An individual care service offered under a ServiceCategory.

    Supports three care modes:
      - Scheduled Care  — advance booking with preferred date/time
      - Instant Care    — immediate request with auto companion matching
      - Emergency Care  — highest priority with emergency escalation

    Soft-deleted via is_deleted flag; never hard-deleted.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name='care_services',
        db_index=True,
    )
    service_name = models.CharField(max_length=200, unique=True)
    service_code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)

    # Duration (stored in minutes for precision)
    estimated_duration = models.PositiveIntegerField(
        help_text='Estimated service duration in minutes',
    )

    # Pricing
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Base price in INR',
    )

    # Visit type support
    home_visit_supported = models.BooleanField(default=False, db_index=True)
    hospital_visit_supported = models.BooleanField(default=False, db_index=True)
    emergency_supported = models.BooleanField(default=False, db_index=True)

    # Feature flags
    ai_recommended = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Surfaced by AI matching engine',
    )
    icon = models.CharField(max_length=100, blank=True, help_text='Icon class or URL')

    # Status
    status = models.CharField(
        max_length=10,
        choices=constants.STATUS_CHOICES,
        default=constants.STATUS_ACTIVE,
        db_index=True,
    )

    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Audit
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_care_services',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_care_services',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'care_services'
        verbose_name = 'Care Service'
        verbose_name_plural = 'Care Services'
        ordering = ['service_name']
        indexes = [
            models.Index(
                fields=['service_category', 'status', 'is_deleted'],
                name='care_svc_cat_stat_del_idx',
            ),
            models.Index(fields=['service_code'], name='care_svc_code_idx'),
            models.Index(
                fields=['emergency_supported', 'status'],
                name='care_svc_emergency_status_idx',
            ),
            models.Index(fields=['ai_recommended', 'status'], name='care_svc_ai_status_idx'),
        ]

    def __str__(self) -> str:
        return f"{self.service_name} ({self.service_category.code})"

    @property
    def estimated_duration_hours(self) -> float:
        """Return estimated duration in hours."""
        return round(self.estimated_duration / 60, 2)

    def soft_delete(self, deleted_by=None) -> None:
        """Soft-delete this service. Never hard-deletes."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.status = constants.STATUS_INACTIVE
        if deleted_by:
            self.updated_by = deleted_by
        self.save(update_fields=['is_deleted', 'deleted_at', 'status', 'updated_by', 'updated_at'])

    def activate(self, updated_by=None) -> None:
        """Activate this service."""
        self.status = constants.STATUS_ACTIVE
        if updated_by:
            self.updated_by = updated_by
        self.save(update_fields=['status', 'updated_by', 'updated_at'])

    def deactivate(self, updated_by=None) -> None:
        """Deactivate this service without deleting it."""
        self.status = constants.STATUS_INACTIVE
        if updated_by:
            self.updated_by = updated_by
        self.save(update_fields=['status', 'updated_by', 'updated_at'])
