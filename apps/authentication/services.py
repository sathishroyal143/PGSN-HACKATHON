"""
Service layer for authentication module.
Contains all business logic for authentication operations.
"""
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken as JWTRefreshToken
from apps.users.repositories import UserRepository
from apps.authentication.repositories import (
    OTPRepository,
    PasswordResetTokenRepository,
    RefreshTokenRepository,
    LoginAttemptRepository
)
from apps.authentication.exceptions import *
from apps.authentication.utils import (
    generate_otp,
    generate_token,
    get_otp_expiry_time,
    get_token_expiry_time,
    get_refresh_token_expiry_time,
    generate_jwt_tokens,
    validate_password_strength,
    normalize_phone_number
)
from apps.authentication import constants
from apps.authentication.tasks import (
    send_otp_email_task,
    send_otp_sms_task,
    send_welcome_email_task,
    send_password_reset_email_task,
    send_password_changed_email_task,
    send_login_alert_email_task
)
from common.tasks import dispatch
import logging

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Service for authentication operations."""
    
    @staticmethod
    @transaction.atomic
    def register_user(email, password, password_confirmation, phone_number, 
                     first_name, last_name, role, **extra_data):
        """
        Register a new user.
        """
        if password != password_confirmation:
            raise PasswordMismatchException()
        
        is_valid, error_message = validate_password_strength(password)
        if not is_valid:
            raise WeakPasswordException(error_message)
        
        if UserRepository.get_by_email(email):
            raise EmailAlreadyExistsException()
        
        normalized_phone = normalize_phone_number(phone_number)
        if UserRepository.get_by_phone(normalized_phone):
            raise PhoneAlreadyExistsException()
        
        user_data = {
            'email': email,
            'password': password,
            'phone_number': normalized_phone,
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'is_active': True,
            'is_email_verified': False,
            'is_phone_verified': False,
            **extra_data
        }
        
        user = UserRepository.create_user(user_data)
        
        try:
            dispatch(send_welcome_email_task, user.email, user.get_full_name())
        except Exception as e:
            logger.warning(f"Welcome email failed: {e}")
        
        try:
            AuthenticationService.send_verification_otp(
                user,
                constants.OTP_TYPE_EMAIL_VERIFICATION
            )
        except Exception as e:
            logger.warning(f"OTP send failed: {e}")
        
        logger.info(f"User registered successfully: {user.email}")
        
        return user
    
    @staticmethod
    @transaction.atomic
    def login_user(email, password, device_info=None):
        """
        Authenticate user and create session.
        """
        if LoginAttemptRepository.is_blocked(
            email,
            'email',
            constants.MAX_LOGIN_ATTEMPTS,
            constants.LOGIN_ATTEMPT_WINDOW_HOURS
        ):
            LoginAttemptRepository.create(
                status=constants.LOGIN_STATUS_BLOCKED,
                email=email,
                failure_reason=constants.FAILURE_TOO_MANY_ATTEMPTS,
                **(device_info or {})
            )
            raise TooManyAttemptsException()
        
        user = UserRepository.get_by_email(email)
        if not user:
            LoginAttemptRepository.create(
                status=constants.LOGIN_STATUS_FAILED,
                email=email,
                failure_reason=constants.FAILURE_USER_NOT_FOUND,
                **(device_info or {})
            )
            raise UserNotFoundException()
        
        if not user.check_password(password):
            LoginAttemptRepository.create(
                status=constants.LOGIN_STATUS_FAILED,
                user=user,
                email=email,
                failure_reason=constants.FAILURE_INVALID_CREDENTIALS,
                **(device_info or {})
            )
            raise InvalidCredentialsException()
        
        if user.is_blocked:
            LoginAttemptRepository.create(
                status=constants.LOGIN_STATUS_FAILED,
                user=user,
                email=email,
                failure_reason=constants.FAILURE_USER_BLOCKED,
                **(device_info or {})
            )
            raise UserBlockedException()
        
        if not user.is_active:
            LoginAttemptRepository.create(
                status=constants.LOGIN_STATUS_FAILED,
                user=user,
                email=email,
                failure_reason=constants.FAILURE_USER_INACTIVE,
                **(device_info or {})
            )
            raise UserInactiveException()
        
        tokens = generate_jwt_tokens(user)
        
        refresh_token_obj = RefreshTokenRepository.create(
            user=user,
            token=tokens['refresh'],
            jti=JWTRefreshToken(tokens['refresh']).get('jti'),
            expires_at=tokens['refresh_expires_at'],
            **(device_info or {})
        )
        
        LoginAttemptRepository.create(
            status=constants.LOGIN_STATUS_SUCCESS,
            user=user,
            email=email,
            **(device_info or {})
        )
        
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return {
            'user': user,
            'tokens': tokens,
            'session_id': str(refresh_token_obj.id)
        }
    
    @staticmethod
    @transaction.atomic
    def logout_user(refresh_token_string):
        """
        Logout user by revoking refresh token.
        """
        token = RefreshTokenRepository.get_by_token(refresh_token_string)
        
        if not token:
            raise TokenInvalidException()
        
        if token.is_revoked:
            raise TokenRevokedException()
        
        RefreshTokenRepository.revoke_token(token)
        
        logger.info(f"User logged out successfully: {token.user.email}")
        
        return True
    
    @staticmethod
    @transaction.atomic
    def logout_all_sessions(user):
        """
        Logout user from all devices.
        """
        RefreshTokenRepository.revoke_all_user_tokens(user)
        
        logger.info(f"User logged out from all sessions: {user.email}")
        
        return True
    
    @staticmethod
    @transaction.atomic
    def refresh_access_token(refresh_token_string):
        """
        Refresh access token using refresh token.
        """
        token = RefreshTokenRepository.get_valid_token(refresh_token_string)
        
        if not token:
            raise TokenInvalidException()
        
        new_tokens = generate_jwt_tokens(token.user)
        
        if constants.TOKEN_ROTATION_ENABLED:
            RefreshTokenRepository.revoke_token(token)
            
            new_refresh_token = RefreshTokenRepository.create(
                user=token.user,
                token=new_tokens['refresh'],
                jti=JWTRefreshToken(new_tokens['refresh']).get('jti'),
                expires_at=new_tokens['refresh_expires_at'],
                device_id=token.device_id,
                device_name=token.device_name,
                ip_address=token.ip_address,
                user_agent=token.user_agent
            )
        
        logger.info(f"Access token refreshed for user: {token.user.email}")
        
        return new_tokens
    
    @staticmethod
    @transaction.atomic
    def send_verification_otp(user, otp_type, contact_info=None):
        """
        Send OTP for verification (email or phone).
        """
        rate_limit = OTPRepository.get_recent_otp_count(
            user,
            otp_type,
            hours=1
        )
        
        if rate_limit >= constants.RATE_LIMIT_OTP_PER_HOUR:
            raise OTPMaxAttemptsException(
                f"Maximum {constants.RATE_LIMIT_OTP_PER_HOUR} OTPs per hour exceeded"
            )
        
        OTPRepository.invalidate_previous_otps(user, otp_type)
        
        otp_code = generate_otp(constants.OTP_LENGTH)
        expires_at = get_otp_expiry_time(constants.OTP_EXPIRY_MINUTES)
        
        otp_data = {
            'user': user,
            'otp_code': otp_code,
            'otp_type': otp_type,
            'expires_at': expires_at,
        }
        
        if otp_type == constants.OTP_TYPE_EMAIL_VERIFICATION:
            otp_data['email'] = user.email
            OTPRepository.create(**otp_data)
            try:
                dispatch(send_otp_email_task,
                    user.email, otp_code, otp_type, user.get_full_name())
            except Exception as e:
                logger.warning(f"OTP email failed: {e}")

        elif otp_type == constants.OTP_TYPE_PHONE_VERIFICATION:
            otp_data['phone_number'] = user.phone_number
            OTPRepository.create(**otp_data)
            try:
                dispatch(send_otp_sms_task, user.phone_number, otp_code, otp_type)
            except Exception as e:
                logger.warning(f"OTP SMS failed: {e}")

        logger.info(f"OTP sent to user: {user.email}, type: {otp_type}")

        from django.conf import settings as django_settings
        result = {'otp_sent': True, 'expires_at': expires_at, 'otp_type': otp_type}
        if otp_type == constants.OTP_TYPE_PHONE_VERIFICATION and not getattr(django_settings, 'TWILIO_ACCOUNT_SID', ''):
            result['dev_otp'] = otp_code
        return result

    @staticmethod
    @transaction.atomic
    def verify_otp(user, otp_code, otp_type):
        """
        Verify OTP code.
        """
        otp = OTPRepository.get_valid_otp(user, otp_code, otp_type)
        
        if not otp:
            raise OTPInvalidException()
        
        if otp.is_expired():
            raise OTPExpiredException()
        
        if otp.is_used:
            raise OTPAlreadyUsedException()
        
        if otp.attempts >= otp.max_attempts:
            raise OTPMaxAttemptsException()
        
        if otp.otp_code != otp_code:
            OTPRepository.increment_attempts(otp)
            raise OTPInvalidException()
        
        OTPRepository.mark_as_verified(otp)
        
        if otp_type == constants.OTP_TYPE_EMAIL_VERIFICATION:
            user.is_email_verified = True
            user.email_verified_at = timezone.now()
            user.save(update_fields=['is_email_verified', 'email_verified_at'])
        
        elif otp_type == constants.OTP_TYPE_PHONE_VERIFICATION:
            user.is_phone_verified = True
            user.phone_verified_at = timezone.now()
            user.save(update_fields=['is_phone_verified', 'phone_verified_at'])
        
        logger.info(f"OTP verified for user: {user.email}, type: {otp_type}")
        
        return {
            'verified': True,
            'otp_type': otp_type
        }
    
    @staticmethod
    @transaction.atomic
    def resend_verification_otp(user, otp_type):
        """
        Resend OTP for verification.
        """
        latest_otp = OTPRepository.get_latest_otp(user, otp_type)
        
        if latest_otp:
            time_since_last = (timezone.now() - latest_otp.created_at).total_seconds()
            if time_since_last < constants.OTP_RESEND_COOLDOWN_SECONDS:
                raise OTPResendCooldownException(
                    f"Please wait {int(constants.OTP_RESEND_COOLDOWN_SECONDS - time_since_last)} seconds before requesting a new OTP"
                )
        
        return AuthenticationService.send_verification_otp(user, otp_type)
    
    @staticmethod
    @transaction.atomic
    def request_password_reset(email):
        """
        Initiate password reset process.
        """
        user = UserRepository.get_by_email(email)
        
        if not user:
            raise UserNotFoundException()
        
        rate_limit_count = PasswordResetTokenRepository.get_recent_token_count(
            user,
            hours=24
        )
        
        if rate_limit_count >= constants.RATE_LIMIT_PASSWORD_RESET_PER_DAY:
            raise PasswordResetMaxAttemptsException(
                f"Maximum {constants.RATE_LIMIT_PASSWORD_RESET_PER_DAY} password reset requests per day exceeded"
            )
        
        PasswordResetTokenRepository.invalidate_user_tokens(user)
        
        reset_token = generate_token()
        expires_at = get_token_expiry_time(constants.PASSWORD_RESET_TOKEN_EXPIRY_HOURS)
        
        PasswordResetTokenRepository.create(
            user=user,
            token=reset_token,
            expires_at=expires_at,
        )
        
        try:
            dispatch(send_password_reset_email_task,
                user.email, reset_token, user.get_full_name())
        except Exception as e:
            logger.warning(f"Password reset email failed: {e}")
        
        logger.info(f"Password reset requested for user: {user.email}")
        
        return {
            'reset_requested': True,
            'expires_at': expires_at
        }
    
    @staticmethod
    @transaction.atomic
    def verify_password_reset_token(token):
        """
        Verify password reset token validity.
        """
        token_obj = PasswordResetTokenRepository.get_valid_token(token)
        
        if not token_obj:
            raise PasswordResetTokenInvalidException()
        
        return {
            'valid': True,
            'user_email': token_obj.user.email,
            'expires_at': token_obj.expires_at
        }
    
    @staticmethod
    @transaction.atomic
    def reset_password(token, new_password, password_confirmation):
        """
        Reset user password using token.
        """
        if new_password != password_confirmation:
            raise PasswordMismatchException()
        
        is_valid, error_message = validate_password_strength(new_password)
        if not is_valid:
            raise WeakPasswordException(error_message)
        
        token_obj = PasswordResetTokenRepository.get_valid_token(token)
        
        if not token_obj:
            raise PasswordResetTokenInvalidException()
        
        user = token_obj.user
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        PasswordResetTokenRepository.mark_as_used(token_obj)
        
        RefreshTokenRepository.revoke_all_user_tokens(user)
        
        try:
            dispatch(send_password_changed_email_task, user.email, user.get_full_name())
        except Exception as e:
            logger.warning(f"Password changed email failed: {e}")
        
        logger.info(f"Password reset successful for user: {user.email}")
        
        return {
            'password_reset': True,
            'message': 'Password has been reset successfully'
        }
    
    @staticmethod
    @transaction.atomic
    def change_password(user, old_password, new_password, password_confirmation):
        """
        Change user password (requires old password).
        """
        if not user.check_password(old_password):
            raise InvalidCredentialsException('Current password is incorrect')
        
        if new_password != password_confirmation:
            raise PasswordMismatchException()
        
        is_valid, error_message = validate_password_strength(new_password)
        if not is_valid:
            raise WeakPasswordException(error_message)
        
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        RefreshTokenRepository.revoke_all_user_tokens(user)
        
        try:
            dispatch(send_password_changed_email_task, user.email, user.get_full_name())
        except Exception as e:
            logger.warning(f"Password changed email failed: {e}")
        
        logger.info(f"Password changed for user: {user.email}")
        
        return {
            'password_changed': True,
            'message': 'Password has been changed successfully'
        }
    
    @staticmethod
    def revoke_session(user, session_id):
        """
        Revoke a specific session by session ID.
        """
        token = RefreshTokenRepository.get_by_id(session_id)
        
        if not token or token.user != user:
            raise TokenInvalidException()
        
        if token.is_revoked:
            raise TokenRevokedException()
        
        RefreshTokenRepository.revoke_token(token)
        
        logger.info(f"Session revoked for user: {user.email}, session: {session_id}")
        
        return True
    
    @staticmethod
    def revoke_device_sessions(user, device_id):
        """
        Revoke all sessions for a specific device.
        """
        RefreshTokenRepository.revoke_device_tokens(user, device_id)
        
        logger.info(f"All sessions revoked for device: {device_id}, user: {user.email}")
        
        return True


class OTPService:
    """Service for OTP-specific operations."""
    
    @staticmethod
    def generate_and_send_otp(user, otp_type, contact_info=None):
        """
        Generate and send OTP.
        """
        return AuthenticationService.send_verification_otp(user, otp_type, contact_info)
    
    @staticmethod
    def verify(user, otp_code, otp_type):
        """
        Verify OTP.
        """
        return AuthenticationService.verify_otp(user, otp_code, otp_type)
    
    @staticmethod
    def resend(user, otp_type):
        """
        Resend OTP.
        """
        return AuthenticationService.resend_verification_otp(user, otp_type)
