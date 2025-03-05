from flask import Flask, jsonify, request
import os
import openai  # type: ignore
import re
from flask_cors import CORS
from dateutil import parser  # type: ignore
from slack_sdk import WebClient  # type: ignore
from slack_sdk.errors import SlackApiError  # type: ignore
from datetime import datetime
import pytz  # type: ignore  # Ensure this is installed
import requests  # type: ignore
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
import csv

# Set API keys
SLACK_BOT_TOKEN = "YOUR_SLACK_BOT_TOKEN"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

client = WebClient(token=SLACK_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

def fetch_slack_messages(channel_id, limit=50):
    """Fetch recent messages from a Slack channel."""
    try:
        response = client.conversations_history(channel=channel_id, limit=limit)
        return response.get("messages", [])
    except SlackApiError as e:
        print(f"Error fetching messages: {e.response['error']}")
        return []

def generate_daily_digest(channel_id):
    """Fetch messages, summarize key points, and generate a digest."""
    messages = fetch_slack_messages(channel_id)
    tasks = detect_tasks(messages)

    digest = []
    digest.append("DAILY DIGEST")
    digest.append("=" * 50)

    # Identify tasks for today
    max_time = 12
    total_time = 0
    today_tasks = []

    sorted_tasks = sorted(tasks, key=lambda x: x["due_date"].split(" ")[0]) if tasks else []

    for task in sorted_tasks:
        time_str = task["estimated_time"].split(" ")[0]
        try:
            time_value = int(re.findall(r'\d+', time_str)[0]) if re.findall(r'\d+', time_str) else 0
        except ValueError:
            time_value = 0

        if total_time + time_value <= max_time:
            today_tasks.append(task)
            total_time += time_value

    digest.append("Tasks for Today:")
    if today_tasks:
        for i, task in enumerate(today_tasks, start=1):
            digest.append(f"{i}. {task['message'].split('\n')[0]}")
    else:
        digest.append("No tasks scheduled for today.")
    digest.append("\nTasks & Events (Sorted by Due Date):")
    digest.append("-" * 50)

    today = datetime.today().date()

    for i, task in enumerate(sorted_tasks, start=1):
        task_summary = summarize_text(task['message'])
        digest.append(f"{i}. {task_summary}")
        digest.append(f"Sender: {task.get('sender', 'Unknown')}")
        digest.append(f"Estimated Time: {task['estimated_time']}")
        
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', task["due_date"])
        if date_match:
            due_date = datetime.strptime(date_match.group(), "%Y-%m-%d").date()
            days_remaining = (due_date - today).days
            due_status = "Time Exceeded" if days_remaining < 0 else ("Today's the Last Day!" if days_remaining == 0 else f"Due Date: {due_date} ({days_remaining} days left)")
        else:
            due_status = "Invalid Due Date"
        digest.append(due_status)
        digest.append("-" * 50)

    if not tasks:
        digest.append("No tasks found.")

    return "\n".join(digest)
