"""Document Verification serializers."""
from rest_framework import serializers
from .models import Document, KYCRecord
from . import constants


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'id', 'user', 'doc_type', 'document_number', 'file',
            'status', 'rejection_reason', 'expiry_date',
            'verified_at', 'created_at',
        ]
        read_only_fields = fields


class UploadDocumentSerializer(serializers.Serializer):
    doc_type = serializers.ChoiceField(choices=[c[0] for c in constants.DOCUMENT_TYPE_CHOICES])
    document_number = serializers.CharField(max_length=100, required=False, default='')
    expiry_date = serializers.DateField(required=False, allow_null=True)
    file = serializers.FileField()


class ReviewDocumentSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    reason = serializers.CharField(required=False, default='')


class KYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCRecord
        fields = [
            'id', 'user', 'status',
            'identity_verified', 'address_verified', 'police_clearance_verified',
            'notes', 'completed_at', 'created_at',
        ]
        read_only_fields = fields
