"""Document Verification services."""
import logging
from .repositories import DocumentRepository, KYCRepository
from .exceptions import DocumentNotFoundException
from . import constants

logger = logging.getLogger('carebridge')

# Identity doc types that satisfy identity_verified flag
_IDENTITY_DOCS = {constants.DOC_TYPE_AADHAR, constants.DOC_TYPE_PASSPORT,
                  constants.DOC_TYPE_DRIVING_LICENSE, constants.DOC_TYPE_VOTER_ID}
_ADDRESS_DOCS = {constants.DOC_TYPE_AADHAR, constants.DOC_TYPE_PASSPORT,
                 constants.DOC_TYPE_DRIVING_LICENSE}


class DocumentService:

    @staticmethod
    def upload(user_id, doc_type, file, document_number='', expiry_date=None):
        doc = DocumentRepository.create(user_id, doc_type, file, document_number, expiry_date)
        KYCRepository.get_or_create(user_id)
        logger.info('Document uploaded doc=%s user=%s type=%s', doc.id, user_id, doc_type)
        return doc

    @staticmethod
    def approve(doc_id, admin_user_id):
        doc = DocumentRepository.get_by_id(doc_id)
        if not doc:
            raise DocumentNotFoundException()
        DocumentRepository.approve(doc_id, admin_user_id)
        DocumentService._refresh_kyc_flags(doc.user_id)
        logger.info('Document approved doc=%s by=%s', doc_id, admin_user_id)

    @staticmethod
    def reject(doc_id, admin_user_id, reason):
        doc = DocumentRepository.get_by_id(doc_id)
        if not doc:
            raise DocumentNotFoundException()
        DocumentRepository.reject(doc_id, reason, admin_user_id)
        logger.info('Document rejected doc=%s by=%s', doc_id, admin_user_id)

    @staticmethod
    def _refresh_kyc_flags(user_id):
        from .models import Document
        approved = set(
            Document.objects.filter(user_id=user_id, status=constants.STATUS_APPROVED)
            .values_list('doc_type', flat=True)
        )
        identity_ok = bool(approved & _IDENTITY_DOCS)
        address_ok = bool(approved & _ADDRESS_DOCS)
        police_ok = constants.DOC_TYPE_POLICE_CLEARANCE in approved

        KYCRepository.update_flags(
            user_id,
            identity_verified=identity_ok,
            address_verified=address_ok,
            police_clearance_verified=police_ok,
            status=constants.KYC_STATUS_IN_PROGRESS,
        )
        if identity_ok and address_ok and police_ok:
            KYCRepository.mark_verified(user_id)
