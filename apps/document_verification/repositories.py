"""Document Verification repositories."""
from django.utils import timezone
from .models import Document, KYCRecord
from . import constants


class DocumentRepository:

    @staticmethod
    def create(user_id, doc_type, file, document_number='', expiry_date=None):
        return Document.objects.create(
            user_id=user_id, doc_type=doc_type, file=file,
            document_number=document_number, expiry_date=expiry_date,
        )

    @staticmethod
    def get_by_id(doc_id):
        return Document.objects.filter(id=doc_id).first()

    @staticmethod
    def get_for_user(user_id):
        return Document.objects.filter(user_id=user_id).order_by('-created_at')

    @staticmethod
    def approve(doc_id, verified_by_id):
        Document.objects.filter(id=doc_id).update(
            status=constants.STATUS_APPROVED,
            verified_by_id=verified_by_id,
            verified_at=timezone.now(),
        )

    @staticmethod
    def reject(doc_id, reason, verified_by_id):
        Document.objects.filter(id=doc_id).update(
            status=constants.STATUS_REJECTED,
            rejection_reason=reason,
            verified_by_id=verified_by_id,
            verified_at=timezone.now(),
        )


class KYCRepository:

    @staticmethod
    def get_or_create(user_id):
        record, _ = KYCRecord.objects.get_or_create(user_id=user_id)
        return record

    @staticmethod
    def get_for_user(user_id):
        return KYCRecord.objects.filter(user_id=user_id).first()

    @staticmethod
    def update_flags(user_id, **flags):
        KYCRecord.objects.filter(user_id=user_id).update(**flags)

    @staticmethod
    def mark_verified(user_id):
        KYCRecord.objects.filter(user_id=user_id).update(
            status=constants.KYC_STATUS_VERIFIED,
            completed_at=timezone.now(),
        )

    @staticmethod
    def mark_failed(user_id, notes=''):
        KYCRecord.objects.filter(user_id=user_id).update(
            status=constants.KYC_STATUS_FAILED,
            notes=notes,
        )
