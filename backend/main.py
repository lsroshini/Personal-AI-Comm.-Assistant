from flask import Flask, request, jsonify
from flask_cors import CORS  # Import Flask-CORS
from email_fetcher import fetch_gmail_messages
from task_extractor import extract_tasks
from priority_calculator import calculate_priority
from summarizer import summarize_emails
from database import save_tasks_to_db, save_summaries_to_db
from setup import generate_smart_reply
import pandas as pd
import openai  # type: ignore
import re
from dateutil import parser  # type: ignore
from slack_sdk import WebClient  # type: ignore
from slack_sdk.errors import SlackApiError  # type: ignore
from datetime import datetime
import pytz  # type: ignore  # Ensure this is installed
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
import csv

SLACK_BOT_TOKEN = "" #enter your key
OPENAI_API_KEY = ""#enter your key
DEFAULT_TIME_ESTIMATE = "No info"

client = WebClient(token=SLACK_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}) # Enable CORS for all routes

@app.route("/fetch-emails", methods=["GET"])
def fetch_emails():
    emails = fetch_gmail_messages()
    return jsonify({"emails": emails})

@app.route("/process-emails", methods=["POST"])
def process_emails():
    emails = fetch_gmail_messages()
    tasks = extract_tasks(emails)
    email_summaries = summarize_emails(emails)

    task_data = []
    for task in tasks:
        priority = calculate_priority(task["days_left"], task["assigned_by"])
        task["priority_score"] = priority
        task_data.append(task)

    save_tasks_to_db(task_data)
    save_summaries_to_db(email_summaries)

    pd.DataFrame(task_data).to_csv("data/task_priority.csv", index=False)
    pd.DataFrame(email_summaries).to_csv("data/email_summaries.csv", index=False)

    return jsonify({"tasks": task_data, "summaries": email_summaries})

@app.route("/smart-reply", methods=["POST"])
def smart_reply():
    data = request.json
    email_text = data.get("email_text")
    if not email_text:
        return jsonify({"error": "Email text is required"}), 400

    replies = generate_smart_reply(email_text)
    return jsonify({"smart_replies": [replies]})

def fetch_avg_time_online(task_type):
    """Fetch estimated average time for different task types."""
    avg_times = {
    "technical documentation": 6,
    "client presentation": 5,
    "software development": 15,
    "code review": 6,
    "research & development": 12,
    "bug fixing": 5,
    "system design": 10,
    "database optimization": 8,
    "whitepaper writing": 10,
    "task planning": 4,
    "testing & debugging": 8,
    "deployment": 7,
    "data analysis": 10,
    "meeting": 3,
    "feature implementation": 12,
    "API integration": 8,
    "UX/UI design": 10,
    "documentation review": 5,
    "workshop/conference": 20,  # Retaining long-duration learning sessions
}

    return avg_times.get(task_type, DEFAULT_TIME_ESTIMATE)

def fetch_slack_messages(channel_id, limit=50):
    """Fetch recent messages from a Slack channel."""
    try:
        response = client.conversations_history(channel=channel_id, limit=limit)
        print(response["messages"])
        return response["messages"]
    except SlackApiError as e:
        print(f"⚠️ Error fetching messages: {e.response['error']}")
        return []

date_pattern = [
    r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:\w+\s+){0,2}[A-Z][a-z]+[a-z]*\s+\d{4})',
    r'(\d{1,2}[a-z]{2}\s+(?:of\s+)?(?:\w+\s+){0,2}[A-Z][a-z]+(?:\s+.+)?\s+\d{4})',
    r'([A-Z][a-z]+[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:\w+\s+){0,2}\d{4})',
    r'([A-Z][a-z]+[a-z]*\s+\d{1,2},\s+\d{4})',
    r'(\d{4}-\d{1,2}-\d{1,2})',
    r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
    r'(\d{1,2}\s+(?:of\s+)?(?:\w+\s+){0,2}[A-Z][a-z]+(?:\s+.+)?\s+\d{4})',
    r'([A-Z][a-z]+(?:\s+.+)?\s+\d{1,2}(?:st|nd|rd|th)?)',
    r'(\d{1,2}(?:st|nd|rd|th)?\s+[A-Z][a-z]+)\s+to\s+(\d{1,2}(?:st|nd|rd|th)?\s+[A-Z][a-z]+)',
]

def extract_due_date(message):
    """Extracts single or multiple dates, correctly handling date ranges."""
    dates = []
    current_year = datetime.now().year
    current_month = datetime.now().month

    for pattern in date_pattern:
        matches = re.findall(pattern, message)
        for match in matches:
            try:
                if isinstance(match, tuple):
                    start_date = parser.parse(match[0] + f" {current_year}", fuzzy=True)
                    end_date = parser.parse(match[1] + f" {current_year}", fuzzy=True)

                    if end_date < start_date:
                        end_date = end_date.replace(year=current_year + 1)

                    dates.append(start_date)
                    dates.append(end_date)
                else:
                    parsed_date = parser.parse(match, fuzzy=True)

                    if parsed_date.year == 1900:
                        parsed_date = parsed_date.replace(year=current_year)

                    if parsed_date.month == 1 and parsed_date.day == 1:
                        parsed_date = parsed_date.replace(month=current_month)

                    dates.append(parsed_date)

            except (ValueError, TypeError):
                continue

    if not dates:
        return "Not specified"

    dates.sort()

    if len(dates) == 1:
        due_date = dates[0].replace(tzinfo=pytz.UTC)
        now = datetime.now(pytz.UTC)
        days_left = (due_date - now).days

        days_left_message = "Time limit exceeded" if days_left < 0 else (f"{days_left} days left" if days_left > 0 else "Today's the last day")

        return f"{due_date.strftime('%Y-%m-%d')} ({days_left} days until this date)"

    else:
        start_date = dates[0].strftime('%Y-%m-%d')
        end_date = dates[-1].strftime('%Y-%m-%d')
        duration_days = (dates[-1] - dates[0]).days + 1

        start_date = dates[0].replace(tzinfo=pytz.UTC)
        now = datetime.now(pytz.UTC)
        days_left = (start_date - now).days

        days_left_message = "Time limit exceeded" if days_left < 0 else (f"{days_left} days left" if days_left > 0 else "Today's the last day")

        return f"{start_date.strftime('%Y-%m-%d')} ({days_left} days until this date)"

def extract_task_details(message):
    """Extracts task details like type, estimated time, and due date."""
    type_match = re.search(
        r"(essay|presentation|project|coding|research|homework|lab report|case study|thesis|assignment|exam preparation|data analysis|article review|documentation|design work|report writing|reading assignment|conference)",
        message,
        re.IGNORECASE,
    )
    time_match = re.search(r"(\d+[-\s]?\d*)\s*hours", message, re.IGNORECASE)

    task_type = type_match.group(1).lower() if type_match else "general"
    estimated_time = (
        fetch_avg_time_online(task_type) if time_match is None else time_match.group(1)
    )
    due_date = extract_due_date(message)

    return {
        "message": message,
        "estimated_time": f"{estimated_time} hrs" if estimated_time != "No info" else "No info",
        "due_date": due_date,
        "task_type": task_type,
    }

TASK_KEYWORDS = [
    "task", "project", "deadline", "milestone", "sprint", "standup", "meeting",
    "presentation", "workshop", "hackathon", "event", "submission", "review",
    "survey", "research", "training", "seminar", "interview", "proposal", 
    "whitepaper", "documentation", "report", "analysis", "write-up", "plan",
    "strategy", "brainstorm", "outline", "agenda", "goal", "feature request",
    "bug report", "code review", "deployment", "API integration", "testing",
    "debugging", "system design", "architecture review", "workflow", "optimization",
    "audit", "conference", "webinar", "client demo", "product launch", "feedback session",
    "proof of concept", "beta testing", "MVP", "scalability discussion", 
    "security assessment", "usability testing", "mock interview", "presentation rehearsal"
]


def detect_tasks(messages):
    """Finds all academic tasks in Slack messages."""
    tasks = []
    for msg in messages:
        if "text" in msg and any(keyword in msg["text"].lower() for keyword in TASK_KEYWORDS):
            user_id = msg.get("user")  # Ensure 'user' field exists
            sender_name = get_user_name(user_id) if user_id else None  # Fetch name
            
            task_details = extract_task_details(msg["text"])
            if sender_name:
                task_details["sender"] = sender_name  # Add sender name if available
            tasks.append(task_details)
    return tasks

def get_user_name(user_id):
    """Fetch the real name of a user from Slack."""
    if not user_id:
        return None  # Return None if user_id is missing
    
    try:
        response = client.users_info(user=user_id)
        return response["user"].get("real_name", "Unknown User")  # Get real name or fallback
    except SlackApiError as e:
        print(f"⚠️ Error fetching user info: {e.response['error']}")
        return None  # Return None instead of "Unknown User"

def summarize_text(text, num_sentences=2):
    """Summarize the given text by extracting the most important sentences."""
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)
    
    # Tokenize the remaining sentences into words and compute word frequencies
    words = word_tokenize(text.lower())
    word_freq = Counter(words)
    
    # Score sentences based on word frequencies
    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_freq:
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = word_freq[word]
                else:
                    sentence_scores[sentence] += word_freq[word]

    # Select the top N sentences as the summary
    summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    
    return ' '.join(summary_sentences)

def generate_daily_digest(channel_id):
    """Fetch messages, summarize key points, and generate a digest."""
    messages = fetch_slack_messages(channel_id)
    tasks = detect_tasks(messages)

    digest = "Daily Digest\n\n"

    # Identify tasks that should be performed today (12-hour work limit)
    max_time = 12
    total_time = 0
    today_tasks = []

    if tasks:
        sorted_tasks = sorted(tasks, key=lambda x: x["due_date"].split(" ")[0])

        for task in sorted_tasks:
            time_str = task["estimated_time"].split(" ")[0]

            # Handle estimated time format correctly
            if "-" in time_str:
                time_values = list(map(int, re.findall(r'\d+', time_str)))  # Extract numbers
                time_value = sum(time_values) // len(time_values) if time_values else 0
            else:
                try:
                    time_value = int(time_str)
                except ValueError:
                    time_value = 0  # Default to 0 if parsing fails

            if total_time + time_value <= max_time:
                today_tasks.append(task)
                total_time += time_value

    # Add tasks for today section
    digest += "Tasks for Today:\n"
    if today_tasks:
        for i, task in enumerate(today_tasks, start=1):
            first_line = task["message"].split("\n")[0]  # Get first line of task description
            digest += f"{i}. {first_line}\n"
    else:
        digest += "No tasks scheduled for today.\n"

    # Add the main task/event list
    digest += "\nTasks & Events (Sorted by Due Date):\n\n"

    if tasks:
        today = datetime.today().date()

        for i, task in enumerate(sorted_tasks, start=1):
            task_summary = summarize_text(task['message'])
            digest += f"{i}. {task_summary}\n"

            if "sender" in task:
                digest += f"Sender: {task['sender']}\n"

            digest += f"Estimated Time: {task['estimated_time']}\n"

            # Extract valid date from due_date
            date_match = re.search(r'\d{4}-\d{2}-\d{2}', task["due_date"])
            if date_match:
                due_date = datetime.strptime(date_match.group(), "%Y-%m-%d").date()
                days_remaining = (due_date - today).days

                if days_remaining < 0:
                    due_status = "Time Exceeded"
                elif days_remaining == 0:
                    due_status = "Today's the Last Day!"
                else:
                    due_status = f"Due Date: {due_date} ({days_remaining} days left)"
            else:
                due_status = "Invalid Due Date"

            digest += f"{due_status}\n\n"
    else:
        digest += "No tasks found."

    # Remove emojis and Markdown formatting manually
    digest = re.sub(r'[^\x00-\x7F]+', '', digest)  # Remove non-ASCII characters (including emojis)
    digest = re.sub(r'\*\*([^*]+)\*\*', r'\1', digest)  # Remove bold
    digest = re.sub(r'\*([^*]+)\*', r'\1', digest)  # Remove italics

    return digest.strip()

def save_to_file(content, filename="summary.txt"):
    """Saves the given content to a text file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"✅ Data saved to {filename}")

def save_to_csv(content, filename="summary.csv"):
    """Saves the given content to a CSV file."""
    with open(filename, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for line in content.splitlines():
            writer.writerow([line])  # Write each line as a new row
    print(f"✅ Data saved to {filename}")

@app.route('/daily_digest', methods=['GET'])
def api_daily_digest():
    channel_id = request.args.get('channel_id')
    digest = generate_daily_digest(channel_id)
    return jsonify({"digest": digest})


if __name__ == "__main__":
    app.run(debug=True)
