from django.contrib.auth import get_user_model
from apps.companions.models import CompanionProfile
from apps.document_verification.models import Document, KYCRecord
from apps.document_verification.constants import DOC_TYPE_AADHAR, DOC_TYPE_POLICE_CLEARANCE, STATUS_APPROVED, KYC_STATUS_VERIFIED
from django.utils import timezone

User = get_user_model()
companions = User.objects.filter(role='COMPANION')
admin = User.objects.filter(is_superuser=True).first()

for user in companions:
    Document.objects.get_or_create(
        user=user, doc_type=DOC_TYPE_AADHAR, 
        defaults={'status': STATUS_APPROVED, 'verified_by': admin, 'verified_at': timezone.now(), 'file': 'dummy.pdf'}
    )
    Document.objects.get_or_create(
        user=user, doc_type=DOC_TYPE_POLICE_CLEARANCE, 
        defaults={'status': STATUS_APPROVED, 'verified_by': admin, 'verified_at': timezone.now(), 'file': 'dummy.pdf'}
    )
    KYCRecord.objects.update_or_create(
        user=user, 
        defaults={
            'identity_verified': True, 
            'address_verified': True, 
            'police_clearance_verified': True, 
            'status': KYC_STATUS_VERIFIED, 
            'completed_at': timezone.now()
        }
    )
    CompanionProfile.objects.filter(user=user).update(status='ACTIVE')

print("Completely verified all companions and made them ACTIVE!")
