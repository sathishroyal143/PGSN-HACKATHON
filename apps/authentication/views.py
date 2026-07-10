"""
Views for authentication module.
API endpoints for authentication operations.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from apps.authentication.services import AuthenticationService, OTPService
from apps.authentication.selectors import AuthenticationSelector, OTPSelector
from apps.authentication.serializers import *
from apps.authentication.permissions import IsAuthenticatedAndActive
from apps.authentication.utils import get_device_info
from apps.authentication import constants
from common.responses import success_response, error_response, created_response
from common.exceptions import CareBridgeBaseException
import logging

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class AuthenticationViewSet(viewsets.GenericViewSet):
    """
    ViewSet for authentication operations.
    
    Provides endpoints for:
    - User registration
    - Login/Logout
    - Token refresh
    - OTP operations
    - Password reset
    - Session management
    - Security overview
    """
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        """
        if self.action in ['register', 'login', 'refresh_token', 'password_reset_request', 
                          'password_reset_verify', 'password_reset_confirm']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        serializer_map = {
            'register': RegisterSerializer,
            'login': LoginSerializer,
            'logout': LogoutSerializer,
            'logout_all': None,
            'refresh_token': RefreshTokenSerializer,
            'send_verification_otp': SendOTPSerializer,
            'verify_otp': VerifyOTPSerializer,
            'resend_verification_otp': ResendOTPSerializer,
            'password_reset_request': PasswordResetRequestSerializer,
            'password_reset_verify': PasswordResetVerifySerializer,
            'password_reset_confirm': PasswordResetConfirmSerializer,
            'change_password': ChangePasswordSerializer,
            'revoke_session': RevokeSessionSerializer,
            'revoke_device_sessions': RevokeDeviceSessionsSerializer,
        }
        return serializer_map.get(self.action)
    
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """
        Register a new user.
        
        Required fields:
        - email
        - password
        - password_confirmation
        - phone_number
        - first_name
        - last_name
        - role (FAMILY or COMPANION)
        """
        try:
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = AuthenticationService.register_user(**serializer.validated_data)
            
            from apps.users.serializers import UserDetailSerializer
            
            return created_response(
                data=UserDetailSerializer(user).data,
                message=constants.SUCCESS_REGISTRATION
            )
        
        except ValidationError as e:
            return error_response(
                message=e.detail if isinstance(e.detail, str) else str(e.detail),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except CareBridgeBaseException as e:
            logger.error(f"Registration failed: {str(e)}")
            return error_response(
                message=str(e),
                status_code=e.status_code
            )
        except Exception as e:
            logger.error(f"Unexpected error during registration: {str(e)}")
            return error_response(
                message='Registration failed. Please try again.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """
        Authenticate user and generate tokens.
        
        Required fields:
        - email
        - password
        
        Optional fields:
        - device_id
        - device_name
        """
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            device_info = get_device_info(request)
            
            result = AuthenticationService.login_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                device_info=device_info
            )
            
            response_data = {
                'access': result['tokens']['access'],
                'refresh': result['tokens']['refresh'],
                'access_expires_at': result['tokens']['access_expires_at'],
                'refresh_expires_at': result['tokens']['refresh_expires_at'],
                'session_id': result['session_id'],
                'user': result['user']
            }
            
            return success_response(
                data=LoginResponseSerializer(response_data).data,
                message=constants.SUCCESS_LOGIN
            )
        
        except ValidationError as e:
            return error_response(
                message=e.detail if isinstance(e.detail, str) else str(e.detail),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except CareBridgeBaseException as e:
            logger.error(f"Login failed: {str(e)}")
            return error_response(
                message=str(e),
                status_code=e.status_code
            )
        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}")
            return error_response(
                message='Login failed. Please try again.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        """
        Logout user by revoking refresh token.
        
        Required fields:
        - refresh (refresh token)
        """
        try:
            serializer = LogoutSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            AuthenticationService.logout_user(
                serializer.validated_data['refresh']
            )
            
            return success_response(
                message=constants.SUCCESS_LOGOUT
            )
        
        except (ValidationError, CareBridgeBaseException) as e:
            return error_response(
                message=e.detail if hasattr(e, 'detail') else str(e),
                status_code=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            )
        except Exception as e:
            logger.error(f"Unexpected error during logout: {str(e)}")
            return error_response(
                message='Logout failed. Please try again.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='logout-all')
    def logout_all(self, request):
        """
        Logout user from all devices/sessions.
        """
        try:
            AuthenticationService.logout_all_sessions(request.user)
            
            return success_response(
                message='Logged out from all devices successfully.'
            )
        
        except Exception as e:
            logger.error(f"Logout all failed: {str(e)}")
            return error_response(
                message='Failed to logout from all devices.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh_token(self, request):
        """
        Refresh access token using refresh token.
        
        Required fields:
        - refresh (refresh token)
        """
        try:
            serializer = RefreshTokenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            tokens = AuthenticationService.refresh_access_token(
                serializer.validated_data['refresh']
            )
            
            return success_response(
                data=TokenResponseSerializer(tokens).data,
                message=constants.SUCCESS_TOKEN_REFRESHED
            )
        
        except (ValidationError, CareBridgeBaseException) as e:
            return error_response(
                message=e.detail if hasattr(e, 'detail') else str(e),
                status_code=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            )
        except Exception as e:
            logger.error(f"Unexpected error during token refresh: {str(e)}")
            return error_response(
                message='Token refresh failed. Please try again.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='send-verification-otp')
    def send_verification_otp(self, request):
        """
        Send OTP for email or phone verification.
        
        Required fields:
        - otp_type (EMAIL_VERIFICATION or PHONE_VERIFICATION)
        """
        try:
            serializer = SendOTPSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            result = OTPService.generate_and_send_otp(
                user=request.user,
                otp_type=serializer.validated_data['otp_type']
            )
            
            return success_response(
                data=OTPResponseSerializer(result).data,
                message=constants.SUCCESS_OTP_SENT
            )
        
        except (ValidationError, CareBridgeBaseException) as e:
            return error_response(
                message=e.detail if hasattr(e, 'detail') else str(e),
                status_code=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            )
        except Exception as e:
            logger.error(f"Unexpected error sending OTP: {str(e)}")
            return error_response(
                message='Failed to send OTP. Please try again.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        """
        Verify OTP code.
        
        Required fields:
        - otp_code (6 digits)
        - otp_type
        """
        try:
            serializer = VerifyOTPSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            result = OTPService.verify(
                user=request.user,
                otp_code=serializer.validated_data['otp_code'],
                otp_type=serializer.validated_data['otp_type']
            )
            
            return success_response(
                data=OTPVerificationResponseSerializer(result).data,
                message=constants.SUCCESS_OTP_VERIFIED
            )
        
        except (ValidationError, CareBridgeBaseException) as e:
            return error_response(
                message=e.detail if hasattr(e, 'detail') else str(e),
                status_code=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            )
        except Exception as e:
            logger.error(f"Unexpected error verifying OTP: {str(e)}")
            return error_response(
                message='OTP verification failed. Please try again.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='resend-verification-otp')
    def resend_verification_otp(self, request):
        """
        Resend OTP for verification.
        
        Required fields:
        - otp_type (EMAIL_VERIFICATION or PHONE_VERIFICATION)
        """
        try:
            serializer = ResendOTPSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            result = OTPService.resend(
                user=request.user,
                otp_type=serializer.validated_data['otp_type']
            )
            
            return success_response(
                data=OTPResponseSerializer(result).data,
                message='OTP resent successfully.'
            )
        
        except (ValidationError, CareBridgeBaseException) as e:
            return error_response(
                message=e.detail if hasattr(e, 'detail') else str(e),
                status_code=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            )
        except Exception as e:
            logger.error(f"Unexpected error resending OTP: {str(e)}")
            return error_response(
                message='Failed to resend OTP. Please try again.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='password-reset/request')
    def password_reset_request(self, request):
        """
        Request password reset.
        
        Required fields:
        - email
        """
        try:
            serializer = PasswordResetRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            result = AuthenticationService.request_password_reset(
                email=serializer.validated_data['email'],
            )
            
            return success_response(
                data=PasswordResetResponseSerializer(result).data,
                message=constants.SUCCESS_PASSWORD_RESET_EMAIL_SENT
            )
        
        except (ValidationError, CareBridgeBaseException) as e:
            return error_response(
                message=e.detail if hasattr(e, 'detail') else str(e),
                status_code=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            )
        except Exception as e:
            logger.error(f"Unexpected error requesting password reset: {str(e)}")
            return error_response(
                message='Password reset request failed. Please try again.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='password-reset/verify')
    def password_reset_verify(self, request):
        """
        Verify password reset token.
        
        Required fields:
        - token
        """
        try:
            serializer = PasswordResetVerifySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            result = AuthenticationService.verify_password_reset_token(
                serializer.validated_data['token']
            )
            
            return success_response(
                data=PasswordResetVerifyResponseSerializer(result).data,
                message='Token is valid.'
            )
        
        except (ValidationError, CareBridgeBaseException) as e:
            return error_response(
                message=e.detail if hasattr(e, 'detail') else str(e),
                status_code=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            )
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {str(e)}")
            return error_response(
                message='Token verification failed. Please try again.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='password-reset/confirm')
    def password_reset_confirm(self, request):
        """
        Confirm password reset with new password.
        
        Required fields:
        - token
        - new_password
        - password_confirmation
        """
        try:
            serializer = PasswordResetConfirmSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            result = AuthenticationService.reset_password(
                token=serializer.validated_data['token'],
                new_password=serializer.validated_data['new_password'],
                password_confirmation=serializer.validated_data['password_confirmation']
            )
            
            return success_response(
                data=PasswordResetConfirmResponseSerializer(result).data,
                message=constants.SUCCESS_PASSWORD_RESET
            )
        
        except (ValidationError, CareBridgeBaseException) as e:
            return error_response(
                message=e.detail if hasattr(e, 'detail') else str(e),
                status_code=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            )
        except Exception as e:
            logger.error(f"Unexpected error resetting password: {str(e)}")
            return error_response(
                message='Password reset failed. Please try again.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """
        Change user password.
        
        Required fields:
        - old_password
        - new_password
        - password_confirmation
        """
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            result = AuthenticationService.change_password(
                user=request.user,
                old_password=serializer.validated_data['old_password'],
                new_password=serializer.validated_data['new_password'],
                password_confirmation=serializer.validated_data['password_confirmation']
            )
            
            return success_response(
                data=ChangePasswordResponseSerializer(result).data,
                message=constants.SUCCESS_PASSWORD_CHANGED
            )
        
        except (ValidationError, CareBridgeBaseException) as e:
            return error_response(
                message=e.detail if hasattr(e, 'detail') else str(e),
                status_code=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            )
        except Exception as e:
            logger.error(f"Unexpected error changing password: {str(e)}")
            return error_response(
                message='Password change failed. Please try again.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='sessions')
    def get_sessions(self, request):
        """
        Get all active sessions for user.
        """
        try:
            sessions = AuthenticationSelector.get_active_sessions(request.user)
            
            return success_response(
                data={'sessions': SessionSerializer(sessions, many=True).data},
                message='Sessions retrieved successfully.'
            )
        
        except Exception as e:
            logger.error(f"Failed to retrieve sessions: {str(e)}")
            return error_response(
                message='Failed to retrieve sessions.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='sessions/revoke')
    def revoke_session(self, request):
        """
        Revoke a specific session.
        
        Required fields:
        - session_id
        """
        try:
            serializer = RevokeSessionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            AuthenticationService.revoke_session(
                user=request.user,
                session_id=serializer.validated_data['session_id']
            )
            
            return success_response(
                message='Session revoked successfully.'
            )
        
        except (ValidationError, CareBridgeBaseException) as e:
            return error_response(
                message=e.detail if hasattr(e, 'detail') else str(e),
                status_code=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            )
        except Exception as e:
            logger.error(f"Unexpected error revoking session: {str(e)}")
            return error_response(
                message='Failed to revoke session.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='sessions/revoke-device')
    def revoke_device_sessions(self, request):
        """
        Revoke all sessions for a device.
        
        Required fields:
        - device_id
        """
        try:
            serializer = RevokeDeviceSessionsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            AuthenticationService.revoke_device_sessions(
                user=request.user,
                device_id=serializer.validated_data['device_id']
            )
            
            return success_response(
                message='Device sessions revoked successfully.'
            )
        
        except Exception as e:
            logger.error(f"Device sessions revoke failed: {str(e)}")
            return error_response(
                message='Failed to revoke device sessions.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='security/overview')
    def security_overview(self, request):
        """
        Get comprehensive security overview.
        """
        try:
            overview = AuthenticationSelector.get_user_security_overview(request.user)
            
            return success_response(
                data=SecurityOverviewSerializer(overview).data,
                message='Security overview retrieved successfully.'
            )
        
        except Exception as e:
            logger.error(f"Failed to retrieve security overview: {str(e)}")
            return error_response(
                message='Failed to retrieve security overview.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='security/login-history')
    def login_history(self, request):
        """
        Get login history.
        
        Query params:
        - days (default: 30)
        - limit (default: 20)
        """
        try:
            days = int(request.query_params.get('days', 30))
            limit = int(request.query_params.get('limit', 20))
            
            history = AuthenticationSelector.get_login_history(
                request.user,
                days=days,
                limit=limit
            )
            
            return success_response(
                data={'login_history': LoginHistorySerializer(history, many=True).data},
                message='Login history retrieved successfully.'
            )
        
        except Exception as e:
            logger.error(f"Failed to retrieve login history: {str(e)}")
            return error_response(
                message='Failed to retrieve login history.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='security/verification-status')
    def verification_status(self, request):
        """
        Get verification status for email and phone.
        """
        try:
            status_data = AuthenticationSelector.get_verification_status(request.user)
            
            return success_response(
                data=VerificationStatusSerializer(status_data).data,
                message='Verification status retrieved successfully.'
            )
        
        except Exception as e:
            logger.error(f"Failed to retrieve verification status: {str(e)}")
            return error_response(
                message='Failed to retrieve verification status.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='security/score')
    def security_score(self, request):
        """
        Get account security score and recommendations.
        """
        try:
            score_data = AuthenticationSelector.get_account_security_score(request.user)
            
            return success_response(
                data=SecurityScoreSerializer(score_data).data,
                message='Security score retrieved successfully.'
            )
        
        except Exception as e:
            logger.error(f"Failed to retrieve security score: {str(e)}")
            return error_response(
                message='Failed to retrieve security score.',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
