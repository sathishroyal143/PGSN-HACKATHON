"""OpenAI client — wraps openai SDK with graceful fallback."""
import logging
from django.conf import settings
from .exceptions import OpenAIUnavailableException

logger = logging.getLogger('carebridge')


def _get_client():
    try:
        import openai
        openai.api_key = settings.OPENAI_API_KEY
        return openai
    except ImportError:
        raise OpenAIUnavailableException('openai package not installed.')


def chat_completion(system_prompt: str, user_prompt: str, model: str = None) -> str:
    """
    Call OpenAI chat completion. Returns response text.
    Raises OpenAIUnavailableException if API key missing or call fails.
    """
    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        raise OpenAIUnavailableException('OPENAI_API_KEY not configured.')

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=model or getattr(settings, 'OPENAI_MODEL', 'gpt-4'),
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user',   'content': user_prompt},
            ],
            max_tokens=getattr(settings, 'OPENAI_MAX_TOKENS', 500),
            temperature=getattr(settings, 'OPENAI_TEMPERATURE', 0.3),
        )
        return response.choices[0].message.content.strip()
    except OpenAIUnavailableException:
        raise
    except Exception as exc:
        logger.warning('OpenAI call failed: %s', exc)
        raise OpenAIUnavailableException(str(exc))
