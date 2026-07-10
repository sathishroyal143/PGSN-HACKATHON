"""Azure OpenAI client — wraps openai SDK configured for Azure endpoint."""
import logging
from django.conf import settings
from .exceptions import OpenAIUnavailableException

logger = logging.getLogger('carebridge')


def chat_completion(system_prompt: str, user_prompt: str) -> str:
    """
    Call Azure OpenAI chat completion. Returns response text.
    Raises OpenAIUnavailableException if not configured or call fails.
    """
    endpoint = getattr(settings, 'AZURE_OPENAI_ENDPOINT', '')
    api_key  = getattr(settings, 'AZURE_OPENAI_API_KEY', '')

    if not endpoint or not api_key:
        raise OpenAIUnavailableException('Azure OpenAI not configured.')

    try:
        import openai
        client = openai.AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=getattr(settings, 'AZURE_OPENAI_API_VERSION', '2024-02-15-preview'),
        )
        response = client.chat.completions.create(
            model=getattr(settings, 'AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4'),
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
        logger.warning('Azure OpenAI call failed: %s', exc)
        raise OpenAIUnavailableException(str(exc))
