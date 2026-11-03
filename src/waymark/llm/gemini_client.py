
from google import genai
from google.genai import types

from waymark.config import settings

client = genai.Client(
    api_key=settings.gemini_api_key,
    http_options=types.HttpOptions(
        timeout=60_000,
        retry_options=types.HttpRetryOptions(
            attempts=1,
            initial_delay=1.0,
            max_delay=3.0,
            exp_base=2.0,
            jitter=0.2,
        ),
    ),
)
