"""
Signals for authentication module.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.authentication.models import LoginAttempt, RefreshToken
from apps.users.services import UserService
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=LoginAttempt)
def log_successful_login(sender, instance, created, **kwargs):
    """
    Log user login activity when login is successful.
    """
    if created and instance.status == 'SUCCESS' and instance.user:
        try:
            UserService.log_user_login(
                user=instance.user,
                ip_address=instance.ip_address,
                user_agent=instance.user_agent
            )
            logger.info(f"Login activity logged for user: {instance.user.email}")
        except Exception as e:
            logger.error(f"Failed to log login activity: {str(e)}")


@receiver(post_save, sender=RefreshToken)
def check_max_sessions(sender, instance, created, **kwargs):
    """
    Check if user has exceeded maximum active sessions.
    Revoke oldest sessions if limit exceeded.
    """
    if created:
        try:
            from apps.authentication.repositories import RefreshTokenRepository
            from apps.authentication import constants
            
            active_count = RefreshTokenRepository.get_user_token_count(instance.user)
            
            if active_count > constants.MAX_ACTIVE_SESSIONS_PER_USER:
                tokens_to_revoke = active_count - constants.MAX_ACTIVE_SESSIONS_PER_USER
                
                old_tokens = RefreshTokenRepository.get_user_active_tokens(
                    instance.user
                ).order_by('created_at')[:tokens_to_revoke]
                
                for token in old_tokens:
                    RefreshTokenRepository.revoke_token(token)
                
                logger.info(
                    f"Revoked {tokens_to_revoke} old session(s) for user: {instance.user.email}"
                )
        except Exception as e:
            logger.error(f"Failed to check max sessions: {str(e)}")
