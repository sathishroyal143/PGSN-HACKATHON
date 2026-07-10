"""Reviews models — Review, ReviewReply, Complaint."""
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from apps.bookings.models import Booking
from . import constants

User = get_user_model()


class Review(models.Model):
    """Family reviews a companion after a completed booking."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(
        Booking, on_delete=models.PROTECT,
        related_name='review',
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='reviews_given', db_index=True,
    )
    reviewee = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='reviews_received', db_index=True,
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(constants.MIN_RATING), MaxValueValidator(constants.MAX_RATING)],
        db_index=True,
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=constants.REVIEW_STATUS_CHOICES,
        default=constants.REVIEW_STATUS_APPROVED, db_index=True,
    )
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reviewee', 'status', 'rating']),
            models.Index(fields=['reviewer', 'created_at']),
        ]

    def __str__(self):
        return f"Review {self.id} — {self.rating}★ by {self.reviewer_id}"


class ReviewReply(models.Model):
    """Companion can reply to a review once."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.OneToOneField(
        Review, on_delete=models.CASCADE,
        related_name='reply',
    )
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='review_replies')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'review_replies'

    def __str__(self):
        return f"Reply to Review {self.review_id}"


class Complaint(models.Model):
    """User files a complaint about a booking or companion."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking, on_delete=models.PROTECT,
        related_name='complaints', db_index=True,
    )
    filed_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='complaints_filed', db_index=True,
    )
    against = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='complaints_against', null=True, blank=True,
    )
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=15, choices=constants.COMPLAINT_STATUS_CHOICES,
        default=constants.COMPLAINT_STATUS_OPEN, db_index=True,
    )
    priority = models.CharField(
        max_length=10, choices=constants.COMPLAINT_PRIORITY_CHOICES,
        default=constants.COMPLAINT_PRIORITY_MEDIUM,
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'complaints'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['filed_by', 'status']),
            models.Index(fields=['status', 'priority']),
        ]

    def __str__(self):
        return f"Complaint {self.id} — {self.subject} [{self.status}]"
