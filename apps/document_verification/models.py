"""Document Verification models — Document, KYCRecord."""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from . import constants

User = get_user_model()


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='documents', db_index=True,
    )
    doc_type = models.CharField(
        max_length=25, choices=constants.DOCUMENT_TYPE_CHOICES,
        db_index=True,
    )
    document_number = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to='documents/%Y/%m/')
    status = models.CharField(
        max_length=15, choices=constants.VERIFICATION_STATUS_CHOICES,
        default=constants.STATUS_PENDING, db_index=True,
    )
    rejection_reason = models.TextField(blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='verified_documents',
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'doc_type', 'status']),
        ]

    def __str__(self):
        return f"Document {self.doc_type} — {self.user_id} [{self.status}]"


class KYCRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='kyc_record',
    )
    status = models.CharField(
        max_length=15, choices=constants.KYC_STATUS_CHOICES,
        default=constants.KYC_STATUS_NOT_STARTED, db_index=True,
    )
    # Required document flags
    identity_verified = models.BooleanField(default=False)
    address_verified = models.BooleanField(default=False)
    police_clearance_verified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kyc_records'

    def __str__(self):
        return f"KYC {self.user_id} [{self.status}]"
