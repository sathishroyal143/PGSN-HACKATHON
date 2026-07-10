"""Document Verification admin."""
from django.contrib import admin
from .models import Document, KYCRecord


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'doc_type', 'status', 'verified_at', 'created_at']
    list_filter = ['doc_type', 'status']
    search_fields = ['user__email', 'document_number']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(KYCRecord)
class KYCRecordAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'status', 'identity_verified',
        'address_verified', 'police_clearance_verified', 'completed_at',
    ]
    list_filter = ['status']
    search_fields = ['user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
