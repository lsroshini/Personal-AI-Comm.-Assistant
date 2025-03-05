import re
from dateutil import parser
from datetime import datetime, timezone
import pytz

def extract_due_date(email_content):
    date_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', email_content)
    if date_match:
        due_date = parser.parse(date_match.group()).replace(tzinfo=pytz.UTC)
        days_left = (due_date - datetime.now(timezone.utc)).days
        return due_date.strftime('%Y-%m-%d'), days_left
    return "Not specified", None

def extract_tasks(emails):
    task_list = []
    sender_priority = {
        "CEO": 25, "Manager": 23, "Team Lead": 20, "Client": 22, "Colleague": 15, "HR": 12, "Intern": 8
    }

    for email in emails:
        due_date, days_left = extract_due_date(email["content"])
        sender_priority_score = sender_priority.get(email["sender"], 10)

        task_list.append({
            "email_id": email["id"],
            "sender": email["sender"],
            "due_date": due_date,
            "days_left": days_left or 30,  # Default 30 days if not mentioned
            "assigned_by": sender_priority_score
        })

    return task_list
