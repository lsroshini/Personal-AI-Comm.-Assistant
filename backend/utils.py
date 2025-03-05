import time
import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def api_call_with_retry(api_func, *args, retries=3, delay=2, **kwargs):
    """Handles API retries in case of failure."""
    for attempt in range(retries):
        try:
            return api_func(*args, **kwargs)
        except Exception as e:
            print(f"⚠️ API Error: {e} - Retrying in {delay} sec...")
            time.sleep(delay)
    return None
