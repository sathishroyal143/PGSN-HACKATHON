"""
Celery tasks for authentication module.
Handles async email and SMS delivery for OTP, welcome, password reset notifications.
"""
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from apps.authentication import constants
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name='authentication.send_otp_email'
)
def send_otp_email_task(self, email, otp_code, otp_type, full_name):
    """
    Send OTP via email asynchronously.

    Args:
        email: Recipient email address
        otp_code: OTP code to send
        otp_type: Type of OTP (EMAIL_VERIFICATION, PASSWORD_RESET, etc.)
        full_name: Recipient full name
    """
    try:
        subject_map = {
            constants.OTP_TYPE_EMAIL_VERIFICATION: constants.EMAIL_SUBJECT_EMAIL_VERIFICATION,
            constants.OTP_TYPE_PASSWORD_RESET: constants.EMAIL_SUBJECT_PASSWORD_RESET,
            constants.OTP_TYPE_LOGIN: 'Your CareBridge Login Code',
        }
        template_map = {
            constants.OTP_TYPE_EMAIL_VERIFICATION: constants.EMAIL_TEMPLATE_EMAIL_VERIFICATION,
            constants.OTP_TYPE_PASSWORD_RESET: constants.EMAIL_TEMPLATE_PASSWORD_RESET,
            constants.OTP_TYPE_LOGIN: constants.EMAIL_TEMPLATE_EMAIL_VERIFICATION,
        }

        subject = subject_map.get(otp_type, 'Your CareBridge Verification Code')
        template = template_map.get(otp_type, constants.EMAIL_TEMPLATE_EMAIL_VERIFICATION)

        context = {
            'full_name': full_name,
            'otp_code': otp_code,
            'otp_type': otp_type,
            'expiry_minutes': constants.OTP_EXPIRY_MINUTES,
            'support_email': settings.SUPPORT_EMAIL,
            'frontend_url': settings.FRONTEND_URL,
        }

        html_content = render_to_string(template, context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send(fail_silently=False)

        logger.info(f"OTP email sent to {email} for type {otp_type}")
        return {'sent': True, 'email': email}

    except Exception as exc:
        logger.error(f"Failed to send OTP email to {email}: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name='authentication.send_otp_sms'
)
def send_otp_sms_task(self, phone_number, otp_code, otp_type):
    try:
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            template_map = {
                constants.OTP_TYPE_PHONE_VERIFICATION: constants.SMS_TEMPLATE_PHONE_VERIFICATION,
                constants.OTP_TYPE_PASSWORD_RESET: constants.SMS_TEMPLATE_PASSWORD_RESET,
                constants.OTP_TYPE_LOGIN: constants.SMS_TEMPLATE_LOGIN_OTP,
            }
            template = template_map.get(otp_type, constants.SMS_TEMPLATE_PHONE_VERIFICATION)
            message_body = template.format(otp_code=otp_code, minutes=constants.OTP_EXPIRY_MINUTES)
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            msg = client.messages.create(
                body=message_body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=str(phone_number),
            )
            logger.info(f"OTP SMS sent via Twilio to {phone_number}, SID: {msg.sid}")
            return {'sent': True}
        logger.info(f"SMS provider not configured — OTP for {phone_number} handled by frontend display")
        return {'sent': False, 'reason': 'no_provider'}
    except Exception as exc:
        logger.error(f"Failed to send OTP SMS to {phone_number}: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=120,
    name='authentication.send_welcome_email'
)
def send_welcome_email_task(self, email, full_name):
    """
    Send welcome email to newly registered user.

    Args:
        email: Recipient email address
        full_name: User's full name
    """
    try:
        context = {
            'full_name': full_name,
            'support_email': settings.SUPPORT_EMAIL,
            'frontend_url': settings.FRONTEND_URL,
        }

        html_content = render_to_string(constants.EMAIL_TEMPLATE_WELCOME, context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=constants.EMAIL_SUBJECT_WELCOME,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send(fail_silently=False)

        logger.info(f"Welcome email sent to {email}")
        return {'sent': True, 'email': email}

    except Exception as exc:
        logger.error(f"Failed to send welcome email to {email}: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name='authentication.send_password_reset_email'
)
def send_password_reset_email_task(self, email, reset_token, full_name):
    """
    Send password reset email with token link.

    Args:
        email: Recipient email address
        reset_token: Password reset token
        full_name: User's full name
    """
    try:
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        context = {
            'full_name': full_name,
            'reset_url': reset_url,
            'reset_token': reset_token,
            'expiry_hours': constants.PASSWORD_RESET_TOKEN_EXPIRY_HOURS,
            'support_email': settings.SUPPORT_EMAIL,
            'frontend_url': settings.FRONTEND_URL,
        }

        html_content = render_to_string(constants.EMAIL_TEMPLATE_PASSWORD_RESET, context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=constants.EMAIL_SUBJECT_PASSWORD_RESET,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send(fail_silently=False)

        logger.info(f"Password reset email sent to {email}")
        return {'sent': True, 'email': email}

    except Exception as exc:
        logger.error(f"Failed to send password reset email to {email}: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name='authentication.send_password_changed_email'
)
def send_password_changed_email_task(self, email, full_name):
    """
    Send password changed confirmation email.

    Args:
        email: Recipient email address
        full_name: User's full name
    """
    try:
        context = {
            'full_name': full_name,
            'support_email': settings.SUPPORT_EMAIL,
            'frontend_url': settings.FRONTEND_URL,
        }

        html_content = render_to_string(constants.EMAIL_TEMPLATE_PASSWORD_CHANGED, context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=constants.EMAIL_SUBJECT_PASSWORD_CHANGED,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send(fail_silently=False)

        logger.info(f"Password changed email sent to {email}")
        return {'sent': True, 'email': email}

    except Exception as exc:
        logger.error(f"Failed to send password changed email to {email}: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    name='authentication.send_login_alert_email'
)
def send_login_alert_email_task(self, email, full_name, ip_address, device_name, login_time):
    """
    Send login alert email for new device/location login.

    Args:
        email: Recipient email address
        full_name: User's full name
        ip_address: Login IP address
        device_name: Device name
        login_time: Login timestamp string
    """
    try:
        context = {
            'full_name': full_name,
            'ip_address': ip_address,
            'device_name': device_name or 'Unknown Device',
            'login_time': login_time,
            'support_email': settings.SUPPORT_EMAIL,
            'frontend_url': settings.FRONTEND_URL,
        }

        html_content = render_to_string(constants.EMAIL_TEMPLATE_LOGIN_ALERT, context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=constants.EMAIL_SUBJECT_LOGIN_ALERT,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send(fail_silently=False)

        logger.info(f"Login alert email sent to {email}")
        return {'sent': True, 'email': email}

    except Exception as exc:
        logger.error(f"Failed to send login alert email to {email}: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(name='authentication.cleanup_expired_tokens')
def cleanup_expired_tokens_task():
    """
    Periodic task to clean up expired OTPs, tokens, and old login attempts.
    Should be scheduled via Celery Beat.
    """
    from apps.authentication.repositories import (
        OTPRepository,
        PasswordResetTokenRepository,
        RefreshTokenRepository,
        LoginAttemptRepository,
    )

    otp_count = OTPRepository.delete_expired_otps()
    reset_count = PasswordResetTokenRepository.delete_expired_tokens()
    refresh_count = RefreshTokenRepository.delete_expired_tokens()
    attempt_count = LoginAttemptRepository.delete_old_attempts(days=90)

    logger.info(
        f"Cleanup completed: {otp_count} OTPs, {reset_count} reset tokens, "
        f"{refresh_count} refresh tokens, {attempt_count} login attempts deleted."
    )

    return {
        'otps_deleted': otp_count,
        'reset_tokens_deleted': reset_count,
        'refresh_tokens_deleted': refresh_count,
        'login_attempts_deleted': attempt_count,
    }
