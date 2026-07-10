"""Document Verification selectors."""
from .repositories import DocumentRepository, KYCRepository


class DocumentSelectors:

    @staticmethod
    def for_user(user_id):
        return DocumentRepository.get_for_user(user_id)


class KYCSelectors:

    @staticmethod
    def for_user(user_id):
        return KYCRepository.get_or_create(user_id)
