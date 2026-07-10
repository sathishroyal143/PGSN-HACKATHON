"""
Serializers for Users module.
Handles data validation and API representation.
"""

from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField

from .models import User, UserActivity, UserRole, Gender
from .validators import (
    validate_email,
    validate_phone_number,
    validate_date_of_birth,
    validate_profile_picture,
    validate_coordinates,
    validate_name,
)


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for UserActivity model"""
    
    class Meta:
        model = UserActivity
        fields = [
            'id',
            'activity_type',
            'description',
            'ip_address',
            'created_at',
        ]
        read_only_fields = fields


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for user list view"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'phone_number',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'gender',
            'age',
            'city',
            'state',
            'profile_picture',
            'is_active',
            'is_verified',
            'is_profile_complete',
            'created_at',
        ]
        read_only_fields = fields


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed user view"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    recent_activities = serializers.SerializerMethodField()

    def get_recent_activities(self, obj):
        qs = obj.activities.order_by('-created_at')[:10]
        return UserActivitySerializer(qs, many=True).data

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'phone_number',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'gender',
            'date_of_birth',
            'age',
            'profile_picture',
            'bio',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'postal_code',
            'country',
            'latitude',
            'longitude',
            'is_email_verified',
            'is_phone_verified',
            'is_profile_complete',
            'is_active',
            'is_blocked',
            'notification_enabled',
            'email_notification_enabled',
            'sms_notification_enabled',
            'push_notification_enabled',
            'created_at',
            'updated_at',
            'last_login_at',
            'recent_activities',
        ]
        read_only_fields = [
            'id',
            'full_name',
            'age',
            'is_email_verified',
            'is_phone_verified',
            'is_profile_complete',
            'is_active',
            'is_blocked',
            'created_at',
            'updated_at',
            'last_login_at',
            'recent_activities',
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user creation"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    phone_number = PhoneNumberField(required=True)
    
    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'confirm_password',
            'phone_number',
            'first_name',
            'last_name',
            'role',
            'gender',
            'date_of_birth',
        ]
    
    def validate_email(self, value):
        """Validate email"""
        validate_email(value)
        return value.lower()
    
    def validate_phone_number(self, value):
        """Validate phone number"""
        validate_phone_number(value)
        return value
    
    def validate_first_name(self, value):
        """Validate first name"""
        validate_name(value, 'First name')
        return value.strip()
    
    def validate_last_name(self, value):
        """Validate last name"""
        validate_name(value, 'Last name')
        return value.strip()
    
    def validate_date_of_birth(self, value):
        """Validate date of birth"""
        if value:
            validate_date_of_birth(value)
        return value
    
    def validate(self, data):
        """Validate password match"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match'
            })
        return data
    
    def create(self, validated_data):
        """Create user (handled by service layer)"""
        validated_data.pop('confirm_password')
        return validated_data


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for user profile update"""
    
    phone_number = PhoneNumberField(required=False)
    
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'gender',
            'date_of_birth',
            'bio',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'postal_code',
            'country',
            'latitude',
            'longitude',
            'phone_number',
        ]
    
    def validate_first_name(self, value):
        """Validate first name"""
        if value:
            validate_name(value, 'First name')
            return value.strip()
        return value
    
    def validate_last_name(self, value):
        """Validate last name"""
        if value:
            validate_name(value, 'Last name')
            return value.strip()
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number"""
        if value:
            validate_phone_number(value)
        return value
    
    def validate_date_of_birth(self, value):
        """Validate date of birth"""
        if value:
            validate_date_of_birth(value)
        return value
    
    def validate(self, data):
        """Validate coordinates together"""
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude is not None or longitude is not None:
            # If updating coordinates, validate them
            current_lat = self.instance.latitude if self.instance else None
            current_lon = self.instance.longitude if self.instance else None
            
            final_lat = latitude if latitude is not None else current_lat
            final_lon = longitude if longitude is not None else current_lon
            
            validate_coordinates(final_lat, final_lon)
        
        return data


class ProfilePictureUpdateSerializer(serializers.ModelSerializer):
    """Serializer for profile picture update"""
    
    profile_picture = serializers.ImageField(required=True)
    
    class Meta:
        model = User
        fields = ['profile_picture']
    
    def validate_profile_picture(self, value):
        """Validate profile picture"""
        validate_profile_picture(value)
        return value


class NotificationPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences"""
    
    class Meta:
        model = User
        fields = [
            'notification_enabled',
            'email_notification_enabled',
            'sms_notification_enabled',
            'push_notification_enabled',
        ]


class FCMTokenSerializer(serializers.Serializer):
    """Serializer for FCM token update"""
    
    fcm_token = serializers.CharField(required=True, max_length=500)


class UserRoleUpdateSerializer(serializers.Serializer):
    """Serializer for user role update (admin only)"""
    
    role = serializers.ChoiceField(choices=UserRole.choices, required=True)


class UserBlockSerializer(serializers.Serializer):
    """Serializer for blocking user"""
    
    reason = serializers.CharField(required=False, max_length=500)


class UserSearchSerializer(serializers.Serializer):
    """Serializer for user search parameters"""
    
    query = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(
        choices=UserRole.choices,
        required=False,
        allow_blank=True
    )
    city = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    is_verified = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    age_min = serializers.IntegerField(required=False, min_value=18)
    age_max = serializers.IntegerField(required=False, max_value=120)


class UserStatisticsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    
    total_activities = serializers.IntegerField()
    last_login = serializers.DateTimeField(allow_null=True)
    account_age_days = serializers.IntegerField()
    is_verified = serializers.BooleanField()
    profile_completion = serializers.BooleanField()


class UserEligibilitySerializer(serializers.Serializer):
    """Serializer for user eligibility checks"""
    
    can_book_service = serializers.BooleanField()
    can_accept_bookings = serializers.BooleanField()
    can_access_admin = serializers.BooleanField()
    requires_verification = serializers.BooleanField()
    requires_profile_completion = serializers.BooleanField()


class UserDashboardSerializer(serializers.Serializer):
    """Serializer for user dashboard statistics"""
    
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    verified_users = serializers.IntegerField()
    inactive_users = serializers.IntegerField()
    role_distribution = serializers.ListField()
    recent_registrations = serializers.IntegerField()


class NearbyUsersSerializer(serializers.Serializer):
    """Serializer for nearby users search"""
    
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=True
    )
    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=True
    )
    radius_km = serializers.IntegerField(
        required=False,
        default=10,
        min_value=1,
        max_value=100
    )
    role = serializers.ChoiceField(
        choices=UserRole.choices,
        required=False,
        allow_blank=True
    )
