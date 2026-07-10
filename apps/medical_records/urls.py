"""URL configuration for Medical Records module.

Nested routes:
  /api/v1/medical-records/patients/{patient_pk}/records/
  /api/v1/medical-records/patients/{patient_pk}/records/{record_pk}/prescriptions/
  /api/v1/medical-records/patients/{patient_pk}/records/{record_pk}/lab-reports/
  /api/v1/medical-records/patients/{patient_pk}/records/{record_pk}/documents/
"""
from django.urls import path
from .views import (
    MedicalRecordViewSet,
    PrescriptionViewSet,
    LabReportViewSet,
    RecordDocumentViewSet,
)

# Medical Records
record_list   = MedicalRecordViewSet.as_view({'get': 'list', 'post': 'create'})
record_detail = MedicalRecordViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
record_summary  = MedicalRecordViewSet.as_view({'get': 'summary'})
record_timeline = MedicalRecordViewSet.as_view({'get': 'timeline'})

# Prescriptions
rx_list   = PrescriptionViewSet.as_view({'get': 'list', 'post': 'create'})
rx_detail = PrescriptionViewSet.as_view({'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})

# Lab Reports
lab_list   = LabReportViewSet.as_view({'get': 'list', 'post': 'create'})
lab_detail = LabReportViewSet.as_view({'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})

# Documents
doc_list   = RecordDocumentViewSet.as_view({'get': 'list', 'post': 'create'})
doc_detail = RecordDocumentViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})

urlpatterns = [
    # Records under a patient
    path('patients/<uuid:patient_pk>/records/', record_list, name='medical-record-list'),
    path('patients/<uuid:patient_pk>/records/summary/', record_summary, name='medical-record-summary'),
    path('patients/<uuid:patient_pk>/records/timeline/', record_timeline, name='medical-record-timeline'),
    path('patients/<uuid:patient_pk>/records/<uuid:pk>/', record_detail, name='medical-record-detail'),

    # Prescriptions under a record
    path('records/<uuid:record_pk>/prescriptions/', rx_list, name='prescription-list'),
    path('records/<uuid:record_pk>/prescriptions/<uuid:pk>/', rx_detail, name='prescription-detail'),

    # Lab reports under a record
    path('records/<uuid:record_pk>/lab-reports/', lab_list, name='lab-report-list'),
    path('records/<uuid:record_pk>/lab-reports/<uuid:pk>/', lab_detail, name='lab-report-detail'),

    # Documents under a record
    path('records/<uuid:record_pk>/documents/', doc_list, name='record-document-list'),
    path('records/<uuid:record_pk>/documents/<uuid:pk>/', doc_detail, name='record-document-detail'),
]
