"""
Views for the Patients module.
Thin ViewSets — all business logic delegated to services.
"""
import logging
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet

from common.responses import (
    success_response, created_response, updated_response,
    deleted_response, not_found_response,
)
from apps.users.models import UserRole
from .exceptions import (
    PatientNotFoundException, PatientAccessDeniedException,
    NoFamilyProfileException, VitalNotFoundException, InsuranceNotFoundException,
)
from .permissions import IsFamilyOrAdmin, IsAdminUser, CanAccessPatient
from .repositories import PatientRepository, PatientVitalRepository, PatientInsuranceRepository
from .selectors import PatientSelector
from .serializers import (
    PatientCreateSerializer, PatientUpdateSerializer, PatientDetailSerializer,
    PatientListSerializer, PatientVitalCreateSerializer, PatientVitalDetailSerializer,
    PatientInsuranceSerializer,
)
from .services import PatientService, PatientVitalService, PatientInsuranceService
from . import constants

logger = logging.getLogger('carebridge')


def _get_family_profile(user):
    """Resolve the FamilyProfile for the requesting user or raise."""
    try:
        return user.family_profile
    except Exception:
        raise NoFamilyProfileException()


class PatientViewSet(ViewSet):
    """
    CRUD for Patient profiles.

    list        GET  /api/v1/patients/
    create      POST /api/v1/patients/
    retrieve    GET  /api/v1/patients/{id}/
    update      PUT  /api/v1/patients/{id}/
    partial_update PATCH /api/v1/patients/{id}/
    destroy     DELETE /api/v1/patients/{id}/
    summary     GET  /api/v1/patients/summary/
    set_primary POST /api/v1/patients/{id}/set-primary/
    """

    permission_classes = [IsAuthenticated, IsFamilyOrAdmin]

    def list(self, request):
        if request.user.role == UserRole.ADMIN:
            patients = Patient.objects.filter(is_deleted=False).order_by('-created_at')
        else:
            family_profile = _get_family_profile(request.user)
            patients = PatientRepository.get_by_family_profile(family_profile)
        serializer = PatientListSerializer(patients, many=True)
        return success_response(data=serializer.data, message='Patients retrieved.')

    def create(self, request):
        family_profile = _get_family_profile(request.user)
        serializer = PatientCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = PatientService.create_patient(family_profile, serializer.validated_data)
        return created_response(
            data=PatientDetailSerializer(patient).data,
            message=constants.MSG_PATIENT_CREATED,
        )

    def retrieve(self, request, pk=None):
        patient = PatientService.get_patient_or_raise(pk)
        if request.user.role != UserRole.ADMIN:
            family_profile = _get_family_profile(request.user)
            PatientService.assert_family_owns_patient(family_profile, patient)
        return success_response(
            data=PatientDetailSerializer(patient).data,
            message='Patient retrieved.',
        )

    def update(self, request, pk=None):
        patient = PatientService.get_patient_or_raise(pk)
        if request.user.role != UserRole.ADMIN:
            family_profile = _get_family_profile(request.user)
            PatientService.assert_family_owns_patient(family_profile, patient)
        serializer = PatientUpdateSerializer(patient, data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = PatientService.update_patient(patient, serializer.validated_data)
        return updated_response(
            data=PatientDetailSerializer(patient).data,
            message=constants.MSG_PATIENT_UPDATED,
        )

    def partial_update(self, request, pk=None):
        patient = PatientService.get_patient_or_raise(pk)
        if request.user.role != UserRole.ADMIN:
            family_profile = _get_family_profile(request.user)
            PatientService.assert_family_owns_patient(family_profile, patient)
        serializer = PatientUpdateSerializer(patient, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        patient = PatientService.update_patient(patient, serializer.validated_data)
        return updated_response(
            data=PatientDetailSerializer(patient).data,
            message=constants.MSG_PATIENT_UPDATED,
        )

    def destroy(self, request, pk=None):
        patient = PatientService.get_patient_or_raise(pk)
        if request.user.role != UserRole.ADMIN:
            family_profile = _get_family_profile(request.user)
            PatientService.assert_family_owns_patient(family_profile, patient)
        PatientService.delete_patient(patient)
        return deleted_response(message=constants.MSG_PATIENT_DELETED)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        family_profile = _get_family_profile(request.user)
        data = PatientSelector.get_family_patients_summary(family_profile)
        return success_response(data=data, message='Patient summary retrieved.')

    @action(detail=True, methods=['post'], url_path='set-primary')
    def set_primary(self, request, pk=None):
        patient = PatientService.get_patient_or_raise(pk)
        family_profile = _get_family_profile(request.user)
        PatientService.assert_family_owns_patient(family_profile, patient)
        PatientService.set_primary_patient(patient)
        return success_response(message='Patient set as primary.')


class PatientVitalViewSet(ViewSet):
    """
    Vital sign management per patient.

    list    GET  /api/v1/patients/{patient_pk}/vitals/
    create  POST /api/v1/patients/{patient_pk}/vitals/
    destroy DELETE /api/v1/patients/{patient_pk}/vitals/{id}/
    """

    permission_classes = [IsAuthenticated, IsFamilyOrAdmin]

    def _get_patient(self, request, patient_pk):
        patient = PatientService.get_patient_or_raise(patient_pk)
        if request.user.role != UserRole.ADMIN:
            family_profile = _get_family_profile(request.user)
            PatientService.assert_family_owns_patient(family_profile, patient)
        return patient

    def list(self, request, patient_pk=None):
        patient = self._get_patient(request, patient_pk)
        vitals = PatientVitalRepository.get_by_patient(patient)
        return success_response(
            data=PatientVitalDetailSerializer(vitals, many=True).data,
            message='Vitals retrieved.',
        )

    def retrieve(self, request, patient_pk=None, pk=None):
        patient = self._get_patient(request, patient_pk)
        vital = PatientVitalRepository.get_by_id(pk)
        if not vital or vital.patient_id != patient.id:
            raise VitalNotFoundException()
        return success_response(
            data=PatientVitalDetailSerializer(vital).data,
            message='Vital retrieved.',
        )

    def create(self, request, patient_pk=None):
        patient = self._get_patient(request, patient_pk)
        serializer = PatientVitalCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recorded_by = request.user.get_full_name()
        vital = PatientVitalService.record_vital(patient, serializer.validated_data, recorded_by)
        return created_response(
            data=PatientVitalDetailSerializer(vital).data,
            message=constants.MSG_VITAL_RECORDED,
        )

    def destroy(self, request, patient_pk=None, pk=None):
        patient = self._get_patient(request, patient_pk)
        PatientVitalService.delete_vital(pk, patient)
        return deleted_response(message=constants.MSG_VITAL_DELETED)


class PatientInsuranceViewSet(ViewSet):
    """
    Insurance management per patient.

    list    GET  /api/v1/patients/{patient_pk}/insurance/
    create  POST /api/v1/patients/{patient_pk}/insurance/
    update  PUT  /api/v1/patients/{patient_pk}/insurance/{id}/
    partial_update PATCH /api/v1/patients/{patient_pk}/insurance/{id}/
    destroy DELETE /api/v1/patients/{patient_pk}/insurance/{id}/
    """

    permission_classes = [IsAuthenticated, IsFamilyOrAdmin]

    def _get_patient(self, request, patient_pk):
        patient = PatientService.get_patient_or_raise(patient_pk)
        if request.user.role != UserRole.ADMIN:
            family_profile = _get_family_profile(request.user)
            PatientService.assert_family_owns_patient(family_profile, patient)
        return patient

    def list(self, request, patient_pk=None):
        patient = self._get_patient(request, patient_pk)
        records = PatientInsuranceRepository.get_all_by_patient(patient)
        return success_response(
            data=PatientInsuranceSerializer(records, many=True).data,
            message='Insurance records retrieved.',
        )

    def retrieve(self, request, patient_pk=None, pk=None):
        patient = self._get_patient(request, patient_pk)
        insurance = PatientInsuranceRepository.get_by_id(pk)
        if not insurance or insurance.patient_id != patient.id:
            raise InsuranceNotFoundException()
        return success_response(
            data=PatientInsuranceSerializer(insurance).data,
            message='Insurance record retrieved.',
        )

    def create(self, request, patient_pk=None):
        patient = self._get_patient(request, patient_pk)
        serializer = PatientInsuranceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        insurance = PatientInsuranceService.add_insurance(patient, serializer.validated_data)
        return created_response(
            data=PatientInsuranceSerializer(insurance).data,
            message=constants.MSG_INSURANCE_CREATED,
        )

    def update(self, request, patient_pk=None, pk=None):
        patient = self._get_patient(request, patient_pk)
        insurance = PatientInsuranceRepository.get_by_id(pk)
        if not insurance or insurance.patient_id != patient.id:
            raise InsuranceNotFoundException()
        serializer = PatientInsuranceSerializer(insurance, data=request.data)
        serializer.is_valid(raise_exception=True)
        insurance = PatientInsuranceService.update_insurance(insurance, serializer.validated_data)
        return updated_response(
            data=PatientInsuranceSerializer(insurance).data,
            message=constants.MSG_INSURANCE_UPDATED,
        )

    def partial_update(self, request, patient_pk=None, pk=None):
        patient = self._get_patient(request, patient_pk)
        insurance = PatientInsuranceRepository.get_by_id(pk)
        if not insurance or insurance.patient_id != patient.id:
            raise InsuranceNotFoundException()
        serializer = PatientInsuranceSerializer(insurance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        insurance = PatientInsuranceService.update_insurance(insurance, serializer.validated_data)
        return updated_response(
            data=PatientInsuranceSerializer(insurance).data,
            message=constants.MSG_INSURANCE_UPDATED,
        )

    def destroy(self, request, patient_pk=None, pk=None):
        patient = self._get_patient(request, patient_pk)
        PatientInsuranceService.deactivate_insurance(pk, patient)
        return deleted_response(message=constants.MSG_INSURANCE_DELETED)


# Import needed inside views to avoid circular at module level
from .models import Patient  # noqa: E402
