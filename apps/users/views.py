"""
Views for Users module.
REST API endpoints for user management.
"""

import logging
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from common.responses import (
    success_response,
    error_response,
    created_response,
    updated_response,
    paginated_response,
)
from .models import User, UserRole
from .serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ProfilePictureUpdateSerializer,
    NotificationPreferencesSerializer,
    FCMTokenSerializer,
    UserRoleUpdateSerializer,
    UserBlockSerializer,
    UserSearchSerializer,
    UserStatisticsSerializer,
    UserEligibilitySerializer,
    UserDashboardSerializer,
    NearbyUsersSerializer,
)
from .services import UserService
from .selectors import UserSelector, UserActivitySelector
from .repositories import UserRepository
from .permissions import (
    IsOwnerOrAdmin,
    IsAdminUser,
    CanViewAllUsers,
    CanModifyUser,
    CanBlockUser,
    CanChangeRole,
)
from .exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    UserBlockedException,
)

logger = logging.getLogger('carebridge.users')


@extend_schema_view(
    list=extend_schema(
        summary="List all users",
        description="Get paginated list of all users with optional filters",
        tags=['Users']
    ),
    retrieve=extend_schema(
        summary="Get user details",
        description="Get detailed information about a specific user",
        tags=['Users']
    ),
    create=extend_schema(
        summary="Create new user",
        description="Create a new user account",
        tags=['Users']
    ),
    update=extend_schema(
        summary="Update user",
        description="Update user profile information",
        tags=['Users']
    ),
    partial_update=extend_schema(
        summary="Partial update user",
        description="Partially update user profile information",
        tags=['Users']
    ),
    destroy=extend_schema(
        summary="Delete user",
        description="Soft delete user account",
        tags=['Users']
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model.
    Provides CRUD operations and additional user management endpoints.
    """
    
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'list':
            return UserListSerializer
        return UserDetailSerializer
    
    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CanModifyUser()]
        elif self.action == 'list':
            return [IsAuthenticated(), CanViewAllUsers()]
        elif self.action in ['block', 'unblock', 'change_role']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        
        if not user.is_authenticated:
            return User.objects.none()
        
        # Admin and support can see all users
        if user.role in [UserRole.ADMIN, UserRole.SUPPORT]:
            return User.objects.all()
        
        # Other users can only see their own profile
        return User.objects.filter(id=user.id)
    
    def list(self, request, *args, **kwargs):
        """
        List users with filters.
        
        Query Parameters:
        - role: Filter by user role
        - is_active: Filter by active status
        - is_verified: Filter by verification status
        - search: Search by name, email, or phone
        - city: Filter by city
        - state: Filter by state
        """
        try:
            filters = {
                'role': request.query_params.get('role'),
                'is_active': request.query_params.get('is_active'),
                'is_verified': request.query_params.get('is_verified'),
                'search': request.query_params.get('search'),
                'city': request.query_params.get('city'),
                'state': request.query_params.get('state'),
            }
            
            # Remove None values
            filters = {k: v for k, v in filters.items() if v is not None}
            
            queryset = UserRepository.get_all_users(filters)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return success_response(
                data=serializer.data,
                message='Users retrieved successfully'
            )
        
        except Exception as e:
            logger.error(f'Error listing users: {str(e)}')
            return error_response(
                message='Failed to retrieve users',
                code='list_users_failed',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, *args, **kwargs):
        """Get user details"""
        try:
            user = self.get_object()
            serializer = self.get_serializer(user)
            return success_response(
                data=serializer.data,
                message='User details retrieved successfully'
            )
        
        except User.DoesNotExist:
            return error_response(
                message='User not found',
                code='user_not_found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f'Error retrieving user: {str(e)}')
            return error_response(
                message='Failed to retrieve user',
                code='retrieve_user_failed',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        """Create new user"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = UserService.create_user(
                user_data=serializer.validated_data,
                created_by=request.user if request.user.is_authenticated else None
            )
            
            response_serializer = UserDetailSerializer(user)
            return created_response(
                data=response_serializer.data,
                message='User created successfully'
            )
        
        except UserAlreadyExistsException as e:
            return error_response(
                message=str(e),
                code='user_already_exists',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f'Error creating user: {str(e)}')
            return error_response(
                message='Failed to create user',
                code='create_user_failed',
                details=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """Update user profile"""
        try:
            user = self.get_object()
            serializer = self.get_serializer(data=request.data, partial=kwargs.get('partial', False))
            serializer.is_valid(raise_exception=True)
            
            updated_user = UserService.update_user_profile(
                user=user,
                update_data=serializer.validated_data,
                updated_by=request.user
            )
            
            response_serializer = UserDetailSerializer(updated_user)
            return updated_response(
                data=response_serializer.data,
                message='User profile updated successfully'
            )
        
        except User.DoesNotExist:
            return error_response(
                message='User not found',
                code='user_not_found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f'Error updating user: {str(e)}')
            return error_response(
                message='Failed to update user',
                code='update_user_failed',
                details=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def partial_update(self, request, *args, **kwargs):
        """Partial update user profile"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete user account (soft delete)"""
        try:
            user = self.get_object()
            UserService.delete_user_account(user, deleted_by=request.user)
            
            return success_response(
                message='User account deleted successfully'
            )
        
        except User.DoesNotExist:
            return error_response(
                message='User not found',
                code='user_not_found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f'Error deleting user: {str(e)}')
            return error_response(
                message='Failed to delete user',
                code='delete_user_failed',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Get current user profile",
        description="Get the profile of the currently authenticated user",
        tags=['Users']
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile"""
        try:
            serializer = UserDetailSerializer(request.user)
            return success_response(
                data=serializer.data,
                message='Profile retrieved successfully'
            )
        except Exception as e:
            logger.error(f'Error retrieving profile: {str(e)}')
            return error_response(
                message='Failed to retrieve profile',
                code='profile_retrieval_failed',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Update profile picture",
        description="Update user's profile picture",
        request=ProfilePictureUpdateSerializer,
        tags=['Users']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwnerOrAdmin])
    def update_profile_picture(self, request, pk=None):
        """Update profile picture"""
        try:
            user = self.get_object()
            serializer = ProfilePictureUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            updated_user = UserService.update_user_profile(
                user=user,
                update_data={'profile_picture': serializer.validated_data['profile_picture']},
                updated_by=request.user
            )
            
            return updated_response(
                data={'profile_picture': updated_user.profile_picture.url if updated_user.profile_picture else None},
                message='Profile picture updated successfully'
            )
        
        except Exception as e:
            logger.error(f'Error updating profile picture: {str(e)}')
            return error_response(
                message='Failed to update profile picture',
                code='profile_picture_update_failed',
                details=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Update notification preferences",
        description="Update user's notification preferences",
        request=NotificationPreferencesSerializer,
        tags=['Users']
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsOwnerOrAdmin])
    def notification_preferences(self, request, pk=None):
        """Update notification preferences"""
        try:
            user = self.get_object()
            serializer = NotificationPreferencesSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            updated_user = UserService.update_notification_preferences(
                user=user,
                preferences=serializer.validated_data
            )
            
            response_serializer = NotificationPreferencesSerializer(updated_user)
            return updated_response(
                data=response_serializer.data,
                message='Notification preferences updated successfully'
            )
        
        except Exception as e:
            logger.error(f'Error updating notification preferences: {str(e)}')
            return error_response(
                message='Failed to update preferences',
                code='preferences_update_failed',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Update FCM token",
        description="Update Firebase Cloud Messaging token for push notifications",
        request=FCMTokenSerializer,
        tags=['Users']
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def update_fcm_token(self, request):
        """Update FCM token"""
        try:
            serializer = FCMTokenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            UserService.update_fcm_token(
                user=request.user,
                fcm_token=serializer.validated_data['fcm_token']
            )
            
            return updated_response(
                message='FCM token updated successfully'
            )
        
        except Exception as e:
            logger.error(f'Error updating FCM token: {str(e)}')
            return error_response(
                message='Failed to update FCM token',
                code='fcm_token_update_failed',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Block user",
        description="Block a user account (Admin only)",
        request=UserBlockSerializer,
        tags=['Users - Admin']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanBlockUser])
    def block(self, request, pk=None):
        """Block user account"""
        try:
            user = self.get_object()
            serializer = UserBlockSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            UserService.block_user(
                user=user,
                reason=serializer.validated_data.get('reason'),
                blocked_by=request.user
            )
            
            return success_response(
                message='User blocked successfully'
            )
        
        except Exception as e:
            logger.error(f'Error blocking user: {str(e)}')
            return error_response(
                message='Failed to block user',
                code='block_user_failed',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Unblock user",
        description="Unblock a user account (Admin only)",
        tags=['Users - Admin']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanBlockUser])
    def unblock(self, request, pk=None):
        """Unblock user account"""
        try:
            user = self.get_object()
            UserService.unblock_user(user=user, unblocked_by=request.user)
            
            return success_response(
                message='User unblocked successfully'
            )
        
        except Exception as e:
            logger.error(f'Error unblocking user: {str(e)}')
            return error_response(
                message='Failed to unblock user',
                code='unblock_user_failed',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Get user statistics",
        description="Get statistics for a specific user",
        responses={200: UserStatisticsSerializer},
        tags=['Users']
    )
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsOwnerOrAdmin])
    def statistics(self, request, pk=None):
        """Get user statistics"""
        try:
            user = self.get_object()
            stats = UserSelector.get_user_statistics(user)
            serializer = UserStatisticsSerializer(stats)
            
            return success_response(
                data=serializer.data,
                message='Statistics retrieved successfully'
            )
        
        except Exception as e:
            logger.error(f'Error retrieving statistics: {str(e)}')
            return error_response(
                message='Failed to retrieve statistics',
                code='statistics_retrieval_failed',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Get dashboard statistics",
        description="Get dashboard statistics for all users (Admin only)",
        responses={200: UserDashboardSerializer},
        tags=['Users - Admin']
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminUser])
    def dashboard(self, request):
        """Get dashboard statistics"""
        try:
            stats = UserSelector.get_dashboard_stats()
            serializer = UserDashboardSerializer(stats)
            
            return success_response(
                data=serializer.data,
                message='Dashboard statistics retrieved successfully'
            )
        
        except Exception as e:
            logger.error(f'Error retrieving dashboard stats: {str(e)}')
            return error_response(
                message='Failed to retrieve dashboard statistics',
                code='dashboard_retrieval_failed',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Search users",
        description="Search users with advanced filters",
        parameters=[OpenApiParameter('query', str, OpenApiParameter.QUERY)],
        tags=['Users']
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def search(self, request):
        """Advanced user search"""
        try:
            serializer = UserSearchSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)

            users = UserSelector.search_users_advanced(serializer.validated_data)

            page = self.paginate_queryset(users)
            if page is not None:
                result_serializer = UserListSerializer(page, many=True)
                return self.get_paginated_response(result_serializer.data)

            result_serializer = UserListSerializer(users, many=True)
            return success_response(
                data=result_serializer.data,
                message='Search completed successfully'
            )

        except Exception as e:
            logger.error(f'Error searching users: {str(e)}')
            return error_response(
                message='Search failed',
                code='search_failed',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Change user role",
        description="Change a user's role (Admin only)",
        request=UserRoleUpdateSerializer,
        tags=['Users - Admin']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanChangeRole])
    def change_role(self, request, pk=None):
        """Change user role (Admin only)"""
        try:
            user = self.get_object()
            serializer = UserRoleUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            UserService.change_user_role(
                user=user,
                new_role=serializer.validated_data['role'],
                changed_by=request.user
            )

            return success_response(
                data={'role': serializer.validated_data['role']},
                message='User role updated successfully'
            )

        except Exception as e:
            logger.error(f'Error changing user role: {str(e)}')
            return error_response(
                message='Failed to change user role',
                code='change_role_failed',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Find nearby users",
        description="Find users within a radius by geolocation",
        parameters=[
            OpenApiParameter('latitude', float, OpenApiParameter.QUERY, required=True),
            OpenApiParameter('longitude', float, OpenApiParameter.QUERY, required=True),
            OpenApiParameter('radius_km', int, OpenApiParameter.QUERY),
            OpenApiParameter('role', str, OpenApiParameter.QUERY),
        ],
        tags=['Users']
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def nearby(self, request):
        """Find nearby users by geolocation"""
        try:
            serializer = NearbyUsersSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)

            users = UserSelector.get_nearby_users(
                latitude=serializer.validated_data['latitude'],
                longitude=serializer.validated_data['longitude'],
                radius_km=serializer.validated_data.get('radius_km', 10),
                role=serializer.validated_data.get('role'),
            )

            page = self.paginate_queryset(users)
            if page is not None:
                result_serializer = UserListSerializer(page, many=True)
                return self.get_paginated_response(result_serializer.data)

            result_serializer = UserListSerializer(users, many=True)
            return success_response(
                data=result_serializer.data,
                message='Nearby users retrieved successfully'
            )

        except Exception as e:
            logger.error(f'Error finding nearby users: {str(e)}')
            return error_response(
                message='Failed to find nearby users',
                code='nearby_users_failed',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
