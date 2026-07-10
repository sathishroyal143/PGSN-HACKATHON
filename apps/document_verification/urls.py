"""URL configuration for Document Verification module."""
from django.urls import path
from .views import DocumentDetailView, DocumentListView, DocumentReviewView, KYCView, KYCAdminUpdateView

app_name = 'document_verification'

urlpatterns = [
    path('documents/', DocumentListView.as_view(), name='document-list'),
    path('documents/<uuid:doc_id>/', DocumentDetailView.as_view(), name='document-detail'),
    path('documents/<uuid:doc_id>/review/', DocumentReviewView.as_view(), name='document-review'),
    path('kyc/', KYCView.as_view(), name='kyc'),
    path('kyc/<uuid:user_id>/', KYCAdminUpdateView.as_view(), name='kyc-admin-update'),
]
