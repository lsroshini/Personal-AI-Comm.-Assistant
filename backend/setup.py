import google.generativeai as genai

# Set up Gemini API key
genai.configure(api_key="")  # Replace with your actual API key

def generate_smart_reply(email_text):
    """
    Generates AI-powered smart replies using Google Gemini AI.
    """
    model = genai.GenerativeModel("gemini-pro")

    # Define a structured prompt
    prompt = f"Generate a single short, professional email reply bodies for this email:\n\n'{email_text}'\n\nResponse should be polite and concise.Dont include salutations"

    response = model.generate_content(prompt)

    # Extract the reply text
    return response.text