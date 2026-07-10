"""Reviews signals — update companion average rating on review save."""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Review

logger = logging.getLogger('carebridge')


@receiver(post_save, sender=Review)
def update_companion_rating(sender, instance, **kwargs):
    try:
        from apps.companions.models import CompanionProfile
        from .repositories import ReviewRepository
        profile = CompanionProfile.objects.filter(user_id=instance.reviewee_id).first()
        if profile:
            avg = ReviewRepository.average_rating(instance.reviewee_id)
            total = ReviewRepository.get_for_reviewee(instance.reviewee_id).count()
            CompanionProfile.objects.filter(user_id=instance.reviewee_id).update(average_rating=avg, total_reviews=total)
    except Exception as exc:
        logger.warning('Could not update companion rating: %s', exc)
