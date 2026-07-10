"""AI Engine custom exceptions."""


class AIEngineException(Exception):
    """Base exception for AI Engine."""
    default_message = 'An AI engine error occurred.'

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class CompanionMatchException(AIEngineException):
    default_message = 'Companion matching failed.'


class TrustScoreException(AIEngineException):
    default_message = 'Trust score computation failed.'


class PriorityAssessmentException(AIEngineException):
    default_message = 'Priority assessment failed.'


class MedicalSummaryException(AIEngineException):
    default_message = 'Medical summary generation failed.'


class AIRequestNotFoundException(AIEngineException):
    default_message = 'AI request not found.'


class OpenAIUnavailableException(AIEngineException):
    default_message = 'OpenAI service is unavailable. Falling back to rule-based engine.'
