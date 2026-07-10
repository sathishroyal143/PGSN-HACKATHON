"""Reviews views."""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .selectors import ComplaintSelectors, ReviewSelectors
from .services import ComplaintService, ReviewService
from .repositories import ComplaintRepository, ReviewRepository
from .serializers import (
    ComplaintSerializer, FileComplaintSerializer,
    ReplySerializer, ReviewSerializer, SubmitReviewSerializer,
)


class ReviewListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.users.models import UserRole
        if request.user.role == UserRole.COMPANION:
            qs = ReviewSelectors.for_reviewee(request.user.id)
        else:
            qs = ReviewSelectors.by_reviewer(request.user.id)
        return Response({'data': ReviewSerializer(qs, many=True).data})

    def post(self, request):
        ser = SubmitReviewSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        review = ReviewService.submit(
            booking_id=d['booking_id'],
            reviewer_id=request.user.id,
            reviewee_id=d['reviewee_id'],
            rating=d['rating'],
            title=d.get('title', ''),
            comment=d.get('comment', ''),
            is_anonymous=d.get('is_anonymous', False),
        )
        return Response({'data': ReviewSerializer(review).data}, status=status.HTTP_201_CREATED)


class RevieweeReviewsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        qs = ReviewSelectors.for_reviewee(user_id)
        avg = ReviewSelectors.average_rating(user_id)
        return Response({'data': ReviewSerializer(qs, many=True).data, 'average_rating': avg})


class ReviewReplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        from apps.users.models import UserRole
        if request.user.role != UserRole.COMPANION:
            return Response({'error': 'Only companions can reply to reviews.'}, status=status.HTTP_403_FORBIDDEN)
        ser = ReplySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        reply = ReviewService.reply(review_id, request.user.id, ser.validated_data['comment'])
        from .serializers import ReviewReplySerializer
        return Response({'data': ReviewReplySerializer(reply).data}, status=status.HTTP_201_CREATED)


class ComplaintListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = ComplaintSelectors.for_user(request.user.id)
        return Response({'data': ComplaintSerializer(qs, many=True).data})

    def post(self, request):
        ser = FileComplaintSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        complaint = ComplaintService.file(
            booking_id=d['booking_id'],
            filed_by_id=request.user.id,
            against_id=d.get('against_id'),
            subject=d['subject'],
            description=d['description'],
            priority=d.get('priority', 'medium'),
        )
        return Response({'data': ComplaintSerializer(complaint).data}, status=status.HTTP_201_CREATED)


class ComplaintDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, complaint_id):
        complaint = ComplaintRepository.get_by_id(complaint_id)
        if not complaint:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'data': ComplaintSerializer(complaint).data})

    def patch(self, request, complaint_id):
        """Admin/Support: update complaint status and resolution notes."""
        from apps.users.models import UserRole
        if request.user.role not in (UserRole.ADMIN, UserRole.SUPPORT):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        complaint = ComplaintRepository.get_by_id(complaint_id)
        if not complaint:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        from rest_framework import serializers as drf_serializers
        from . import constants as review_constants

        class _Ser(drf_serializers.Serializer):
            status = drf_serializers.ChoiceField(
                choices=[c[0] for c in review_constants.COMPLAINT_STATUS_CHOICES], required=False
            )
            resolution_notes = drf_serializers.CharField(required=False, allow_blank=True)

        ser = _Ser(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        if 'status' in d:
            complaint.status = d['status']
        if 'resolution_notes' in d:
            complaint.resolution_notes = d['resolution_notes']
        if complaint.status == review_constants.COMPLAINT_STATUS_RESOLVED and not complaint.resolved_at:
            from django.utils import timezone
            complaint.resolved_at = timezone.now()
        complaint.save()
        return Response({'data': ComplaintSerializer(complaint).data})
