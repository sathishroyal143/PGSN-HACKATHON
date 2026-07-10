"""
Care Services serializers.
Covers ServiceCategory, CareService, and legacy ServiceType/ServicePackage/ServicePricing.
"""

from decimal import Decimal
from rest_framework import serializers
from .models import ServiceType, ServicePackage, ServicePricing, ServiceCategory, CareService
from .validators import (
    validate_base_price,
    validate_duration,
    validate_non_negative_money,
    validate_service_code,
)
from . import constants


# ── Legacy serializers (kept intact) ──────────────────────────────────────────

class ServicePricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePricing
        exclude = ['id', 'package', 'created_at', 'updated_at']


class CareServicePricingSerializer(serializers.ModelSerializer):
    """Serializer for prompt-required CareService pricing records."""

    class Meta:
        model = ServicePricing
        fields = [
            'id', 'base_price', 'emergency_charge', 'instant_charge',
            'tax', 'discount', 'total_price', 'effective_from', 'effective_to',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']

    def validate(self, attrs: dict) -> dict:
        for field in ['base_price', 'emergency_charge', 'instant_charge', 'tax', 'discount']:
            if field in attrs:
                validate_non_negative_money(attrs[field], field.replace('_', ' ').title())

        effective_from = attrs.get('effective_from')
        effective_to = attrs.get('effective_to')
        if effective_from and effective_to and effective_to < effective_from:
            raise serializers.ValidationError({
                'effective_to': 'Effective end date cannot be earlier than start date.'
            })
        return attrs


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = [
            'id', 'name', 'code', 'description', 'icon',
            'is_emergency', 'requires_companion', 'status', 'sort_order',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServicePackageListSerializer(serializers.ModelSerializer):
    service_type_name = serializers.CharField(source='service_type.name', read_only=True)
    base_price = serializers.DecimalField(
        source='pricing.base_price', max_digits=10, decimal_places=2, read_only=True, default=None
    )

    class Meta:
        model = ServicePackage
        fields = [
            'id', 'name', 'slug', 'service_type', 'service_type_name',
            'description', 'min_duration_hours', 'companion_count',
            'requires_vehicle', 'is_featured', 'status', 'base_price',
        ]


class ServicePackageDetailSerializer(serializers.ModelSerializer):
    service_type = ServiceTypeSerializer(read_only=True)
    pricing = ServicePricingSerializer(read_only=True)

    class Meta:
        model = ServicePackage
        fields = [
            'id', 'name', 'slug', 'service_type', 'description',
            'inclusions', 'exclusions', 'min_duration_hours', 'max_duration_hours',
            'companion_count', 'requires_vehicle', 'requires_medical_training',
            'is_featured', 'status', 'sort_order', 'pricing',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServicePackageWriteSerializer(serializers.ModelSerializer):
    pricing = ServicePricingSerializer(required=False)

    class Meta:
        model = ServicePackage
        fields = [
            'name', 'slug', 'service_type', 'description',
            'inclusions', 'exclusions', 'min_duration_hours', 'max_duration_hours',
            'companion_count', 'requires_vehicle', 'requires_medical_training',
            'is_featured', 'status', 'sort_order', 'pricing',
        ]

    def validate_name(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Package name cannot be blank.")
        return value


class PriceCalculationSerializer(serializers.Serializer):
    package_id = serializers.UUIDField()
    hours = serializers.FloatField(min_value=0.5, max_value=24.0, default=1.0)
    is_emergency = serializers.BooleanField(default=False)
    is_night = serializers.BooleanField(default=False)


# ── New serializers ────────────────────────────────────────────────────────────

class ServiceCategorySerializer(serializers.ModelSerializer):
    """Read/write serializer for ServiceCategory."""

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'code', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_code(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Category code cannot be blank.")
        return value.upper()


class CareServiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""

    category_name = serializers.CharField(source='service_category.name', read_only=True)
    category_code = serializers.CharField(source='service_category.code', read_only=True)
    estimated_duration_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = CareService
        fields = [
            'id', 'service_name', 'service_code', 'category_name', 'category_code',
            'base_price', 'estimated_duration', 'estimated_duration_hours',
            'home_visit_supported', 'hospital_visit_supported', 'emergency_supported',
            'ai_recommended', 'icon', 'status',
        ]


class CareServiceDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer including category and audit fields."""

    service_category = ServiceCategorySerializer(read_only=True)
    estimated_duration_hours = serializers.FloatField(read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True, default=None)
    updated_by_email = serializers.EmailField(source='updated_by.email', read_only=True, default=None)
    pricing = serializers.SerializerMethodField()

    class Meta:
        model = CareService
        fields = [
            'id', 'service_category', 'service_name', 'service_code', 'description',
            'estimated_duration', 'estimated_duration_hours', 'base_price',
            'home_visit_supported', 'hospital_visit_supported', 'emergency_supported',
            'ai_recommended', 'icon', 'status',
            'pricing',
            'created_by_email', 'updated_by_email', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_pricing(self, obj: CareService) -> dict | None:
        pricing = obj.pricing_history.filter(is_active=True).order_by('-effective_from').first()
        if not pricing:
            return None
        return CareServicePricingSerializer(pricing).data


class CareServiceCreateSerializer(serializers.ModelSerializer):
    """Write serializer for creating a CareService."""

    pricing = CareServicePricingSerializer(required=False)

    class Meta:
        model = CareService
        fields = [
            'service_category', 'service_name', 'service_code', 'description',
            'estimated_duration', 'base_price',
            'home_visit_supported', 'hospital_visit_supported', 'emergency_supported',
            'ai_recommended', 'icon', 'status', 'pricing',
        ]

    def validate_service_name(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Service name cannot be blank.")
        return value.strip()

    def validate_service_code(self, value: str) -> str:
        try:
            validate_service_code(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))
        return value.upper()

    def validate_base_price(self, value: Decimal) -> Decimal:
        try:
            validate_base_price(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def validate_estimated_duration(self, value: int) -> int:
        try:
            validate_duration(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))
        return value


class CareServiceUpdateSerializer(CareServiceCreateSerializer):
    """Write serializer for updating a CareService — all fields optional."""

    class Meta(CareServiceCreateSerializer.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


class ServiceSearchSerializer(serializers.Serializer):
    """Query parameter serializer for service search."""

    q = serializers.CharField(
        min_length=constants.SEARCH_MIN_LENGTH,
        max_length=100,
        help_text='Search query (min 2 characters)',
    )
