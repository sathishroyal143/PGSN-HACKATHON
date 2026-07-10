"""AI Engine services — orchestrates matching, trust score, priority, summary."""
import time
import logging
from .repositories import AIRequestRepository, AIResponseRepository, MatchScoreRepository
from .matching_engine import rank_companions
from .trust_score import compute_trust_score
from .priority_engine import assess_priority
from .medical_summary import generate_summary
from . import constants

logger = logging.getLogger('carebridge')


class CompanionMatchService:

    @staticmethod
    def run(user_id, patient_id, required_skills=None, top_n=10):
        from apps.companions.models import CompanionProfile

        ai_request = AIRequestRepository.create(
            user_id=user_id,
            request_type=constants.REQUEST_TYPE_COMPANION_MATCH,
            input_data={'patient_id': str(patient_id), 'required_skills': required_skills or []},
        )
        AIRequestRepository.mark_processing(ai_request.id)
        t0 = time.time()

        try:
            companions = CompanionProfile.objects.filter(
                status='ACTIVE',
                is_deleted=False,
            ).prefetch_related('skills')

            ranked = rank_companions(companions, required_skills=required_skills, top_n=top_n)
            MatchScoreRepository.bulk_create(ai_request.id, ranked)

            output = {
                'matches': [
                    {
                        'companion_id': str(c.id),
                        'companion_name': c.user.get_full_name(),
                        'experience_years': c.computed_experience_years,
                        'rank': rank + 1,
                        **scores,
                    }
                    for rank, (c, scores) in enumerate(ranked)
                ]
            }
            AIResponseRepository.create(ai_request.id, output)
            ms = int((time.time() - t0) * 1000)
            AIRequestRepository.mark_completed(ai_request.id, ms)
            logger.info('CompanionMatch completed request=%s matches=%d', ai_request.id, len(ranked))
            return ai_request, output

        except Exception as exc:
            AIRequestRepository.mark_failed(ai_request.id, str(exc))
            logger.error('CompanionMatch failed request=%s error=%s', ai_request.id, exc)
            raise


class TrustScoreService:

    @staticmethod
    def run(user_id, companion_id):
        from apps.companions.models import CompanionProfile

        ai_request = AIRequestRepository.create(
            user_id=user_id,
            request_type=constants.REQUEST_TYPE_TRUST_SCORE,
            input_data={'companion_id': str(companion_id)},
        )
        AIRequestRepository.mark_processing(ai_request.id)
        t0 = time.time()

        try:
            companion = CompanionProfile.objects.select_related('user').get(id=companion_id)
            score = compute_trust_score(companion)

            # Persist score back to companion profile
            CompanionProfile.objects.filter(id=companion_id).update(ai_trust_score=score)

            output = {'companion_id': str(companion_id), 'trust_score': score}
            AIResponseRepository.create(ai_request.id, output)
            ms = int((time.time() - t0) * 1000)
            AIRequestRepository.mark_completed(ai_request.id, ms)
            return ai_request, output

        except Exception as exc:
            AIRequestRepository.mark_failed(ai_request.id, str(exc))
            raise


class PriorityService:

    @staticmethod
    def run(user_id, patient_id, is_emergency=False):
        from apps.patients.models import Patient

        ai_request = AIRequestRepository.create(
            user_id=user_id,
            request_type=constants.REQUEST_TYPE_PRIORITY,
            input_data={'patient_id': str(patient_id), 'is_emergency': is_emergency},
        )
        AIRequestRepository.mark_processing(ai_request.id)
        t0 = time.time()

        try:
            patient = Patient.objects.prefetch_related('medical_records').get(id=patient_id)
            conditions = list(
                patient.medical_records.values_list('diagnosis', flat=True)
            ) if hasattr(patient, 'medical_records') else []

            patient_data = {
                'mobility_level': patient.mobility_level,
                'requires_wheelchair': patient.requires_wheelchair,
                'requires_oxygen': patient.requires_oxygen,
                'requires_stretcher': patient.requires_stretcher,
                'chronic_conditions': patient.chronic_conditions,
                'emergency_notes': patient.emergency_notes,
            }

            level, score = assess_priority(
                patient_age=patient.age if hasattr(patient, 'age') else None,
                conditions=conditions,
                is_emergency=is_emergency,
                patient_data=patient_data,
            )
            output = {'patient_id': str(patient_id), 'priority_level': level, 'priority_score': score}
            AIResponseRepository.create(ai_request.id, output)
            ms = int((time.time() - t0) * 1000)
            AIRequestRepository.mark_completed(ai_request.id, ms)
            return ai_request, output

        except Exception as exc:
            AIRequestRepository.mark_failed(ai_request.id, str(exc))
            raise


class MedicalSummaryService:

    @staticmethod
    def run(user_id, patient_id):
        from apps.patients.models import Patient
        
        ai_request = AIRequestRepository.create(
            user_id=user_id,
            request_type=constants.REQUEST_TYPE_MEDICAL_SUMMARY,
            input_data={'patient_id': str(patient_id)},
        )
        AIRequestRepository.mark_processing(ai_request.id)
        t0 = time.time()

        try:
            patient = Patient.objects.prefetch_related(
                'medical_records__prescriptions'
            ).get(id=patient_id)

            conditions = list(patient.medical_records.values_list('diagnosis', flat=True))
            medications = []
            for mr in patient.medical_records.all():
                for p in mr.prescriptions.all():
                    medications.append(p.medicine_name)
            
            allergies = [a.strip() for a in patient.known_allergies.split(',')] if patient.known_allergies else []

            patient_data = {
                'name': patient.get_full_name(),
                'age': patient.age,
                'gender': patient.gender,
                'blood_group': patient.blood_group,
                'mobility_level': patient.mobility_level,
                'requires_wheelchair': patient.requires_wheelchair,
                'requires_oxygen': patient.requires_oxygen,
                'requires_stretcher': patient.requires_stretcher,
                'known_allergies': patient.known_allergies,
                'chronic_conditions': patient.chronic_conditions,
                'current_medications': patient.current_medications,
                'special_needs': patient.special_needs,
                'dietary_restrictions': patient.dietary_restrictions,
                'emergency_notes': patient.emergency_notes,
                'recent_diagnoses': [c for c in conditions if c],
                'recent_prescriptions': medications,
            }

            summary = generate_summary(patient_data)
            output = {'summary': summary}
            AIResponseRepository.create(ai_request.id, output)
            ms = int((time.time() - t0) * 1000)
            AIRequestRepository.mark_completed(ai_request.id, ms)
            return ai_request, output

        except Exception as exc:
            AIRequestRepository.mark_failed(ai_request.id, str(exc))
            raise
