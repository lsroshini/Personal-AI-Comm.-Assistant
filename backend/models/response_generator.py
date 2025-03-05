import openai
from email_fetcher.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def generate_response(email_body):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Suggest a response for the following email: {email_body}",
        max_tokens=50
    )
    return response.choices[0].text.strip()