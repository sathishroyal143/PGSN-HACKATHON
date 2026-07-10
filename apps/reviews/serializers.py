"""Reviews serializers."""
from rest_framework import serializers
from .models import Complaint, Review, ReviewReply
from . import constants


class ReviewReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = ['id', 'author', 'comment', 'created_at']
        read_only_fields = fields


class ReviewSerializer(serializers.ModelSerializer):
    reply = ReviewReplySerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'booking', 'reviewer', 'reviewee', 'rating',
            'title', 'comment', 'status', 'is_anonymous', 'reply', 'created_at',
        ]
        read_only_fields = fields


class SubmitReviewSerializer(serializers.Serializer):
    booking_id = serializers.UUIDField()
    reviewee_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=constants.MIN_RATING, max_value=constants.MAX_RATING)
    title = serializers.CharField(max_length=200, required=False, allow_blank=True, default='')
    comment = serializers.CharField(required=False, allow_blank=True, default='')
    is_anonymous = serializers.BooleanField(default=False)


class ReplySerializer(serializers.Serializer):
    comment = serializers.CharField()


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            'id', 'booking', 'filed_by', 'against', 'subject', 'description',
            'status', 'priority', 'resolution_notes', 'resolved_at', 'created_at',
        ]
        read_only_fields = fields


class FileComplaintSerializer(serializers.Serializer):
    booking_id = serializers.UUIDField()
    against_id = serializers.IntegerField(required=False, allow_null=True)
    subject = serializers.CharField(max_length=255)
    description = serializers.CharField()
    priority = serializers.ChoiceField(
        choices=[c[0] for c in constants.COMPLAINT_PRIORITY_CHOICES],
        default=constants.COMPLAINT_PRIORITY_MEDIUM,
    )
