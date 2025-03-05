import os

# Gmail API Config
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
GEMINI_API_KEY = "" #enter your key

# OpenAI API Key (Set it as an environment variable for security)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY",  "")#enter your key)

# Database Config
DB_FILE = "db.sqlite"

# Priority Weights
SENDER_PRIORITY = {
    "CEO": 25, "Manager": 23, "Team Lead": 20, "Client": 22,
    "Colleague": 15, "HR": 12, "Intern": 8
}
