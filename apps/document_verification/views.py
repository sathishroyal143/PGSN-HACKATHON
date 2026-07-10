"""Document Verification views."""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .selectors import DocumentSelectors, KYCSelectors
from .services import DocumentService
from .repositories import DocumentRepository, KYCRepository
from .serializers import (
    DocumentSerializer, KYCSerializer,
    ReviewDocumentSerializer, UploadDocumentSerializer,
)
from . import constants


class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = DocumentSelectors.for_user(request.user.id)
        return Response({'data': DocumentSerializer(qs, many=True).data})

    def post(self, request):
        ser = UploadDocumentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        doc = DocumentService.upload(
            user_id=request.user.id,
            doc_type=d['doc_type'],
            file=d['file'],
            document_number=d.get('document_number', ''),
            expiry_date=d.get('expiry_date'),
        )
        return Response({'data': DocumentSerializer(doc).data}, status=status.HTTP_201_CREATED)


class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, doc_id):
        doc = DocumentRepository.get_by_id(doc_id)
        if not doc:
            return Response({'error': 'Document not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'data': DocumentSerializer(doc).data})

    def put(self, request, doc_id):
        """Re-upload a document (replace file for rejected/pending docs)."""
        doc = DocumentRepository.get_by_id(doc_id)
        if not doc:
            return Response({'error': 'Document not found.'}, status=status.HTTP_404_NOT_FOUND)
        if doc.user_id != request.user.id:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        if doc.status not in (constants.STATUS_PENDING, constants.STATUS_REJECTED):
            return Response(
                {'error': 'Only pending or rejected documents can be re-uploaded.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ser = UploadDocumentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        doc.file = d['file']
        doc.document_number = d.get('document_number', doc.document_number)
        doc.expiry_date = d.get('expiry_date', doc.expiry_date)
        doc.status = constants.STATUS_PENDING
        doc.rejection_reason = ''
        doc.save(update_fields=['file', 'document_number', 'expiry_date', 'status', 'rejection_reason', 'updated_at'])
        return Response({'data': DocumentSerializer(doc).data})


class DocumentReviewView(APIView):
    """Admin-only: approve or reject a document."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, doc_id):
        ser = ReviewDocumentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        action = ser.validated_data['action']
        reason = ser.validated_data.get('reason', '')
        if action == 'approve':
            DocumentService.approve(doc_id, request.user.id)
        else:
            DocumentService.reject(doc_id, request.user.id, reason)
        return Response({'message': f'Document {action}d successfully.'})


class KYCView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        kyc = KYCSelectors.for_user(request.user.id)
        return Response({'data': KYCSerializer(kyc).data})


class KYCAdminUpdateView(APIView):
    """Admin-only: manually update KYC status or notes."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, user_id):
        from rest_framework import serializers as drf_serializers

        class _KYCUpdateSerializer(drf_serializers.Serializer):
            status = drf_serializers.ChoiceField(
                choices=[c[0] for c in constants.KYC_STATUS_CHOICES], required=False
            )
            notes = drf_serializers.CharField(required=False, allow_blank=True)

        ser = _KYCUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        record = KYCRepository.get_or_create(user_id)
        update_fields = {}
        if 'status' in ser.validated_data:
            update_fields['status'] = ser.validated_data['status']
        if 'notes' in ser.validated_data:
            update_fields['notes'] = ser.validated_data['notes']
        if update_fields:
            KYCRepository.update_flags(user_id, **update_fields)
            record.refresh_from_db()
        return Response({'data': KYCSerializer(record).data})
