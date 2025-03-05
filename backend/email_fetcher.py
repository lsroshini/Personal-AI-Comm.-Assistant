import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    token_path = 'token.json'

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8081, prompt='consent')  # Forces consent screen to get refresh_token

        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds

def fetch_gmail_messages():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    
    results = service.users().messages().list(userId='me', maxResults=50).execute()
    messages = results.get('messages', [])

    email_contents = []
    if messages:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            payload = msg.get('payload', {})
            headers = payload.get('headers', [])
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')

            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body']['data']
                        decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
                        email_contents.append({"id": message['id'], "sender": sender, "content": decoded_data})
    return email_contents
