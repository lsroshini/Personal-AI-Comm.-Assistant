# Personal AI Communication Assistant

## Project Overview
The **Personal AI Communication Assistant** is designed to streamline communication management across multiple platforms, including Gmail, Slack, and WhatsApp. This AI-powered system **prioritizes messages, summarizes conversations, and suggests quick responses**, enhancing productivity and reducing information overload. 

## Features & Capabilities
### 1. Smart Email Management (Gmail)
- **Email Prioritization**: Classifies emails into **Low, Follow-up, and Urgent** using a **classification ML algorithm**.
- **Summarization**: Extracts key points from lengthy email threads using **TF-IDF**, a native machine learning algorithm.
- **Quick Replies**: AI-powered response suggestions to improve response time.
- **Unanswered Email Tracking**: Flags important unanswered emails and sends reminders.

### 2. Team Communication Optimization (Slack)
- **Slack Summarization**: Extracts key discussions and generates a **daily digest**.
- **Task Extraction**: Identifies actionable messages and logs them in the system.
- **Message Prioritization**: Highlights important Slack messages to reduce noise.

### 3. Task Management & Storage
- **Task Extraction**: Detects tasks from emails and Slack messages.
- **Priority Calculation**: Assigns priority scores based on predefined criteria using a **trained ML model**.
- **Data Storage**: Stores summarized content and task lists in an **SQLite database**.

## Project Structure
### Backend Modules:
- **config.py** – Stores configuration settings.
- **database.py** – Manages SQLite database interactions.
- **email_fetcher.py** – Fetches emails from Gmail using the Gmail API.
- **main.py** – Orchestrates the execution of all components.
- **priority_calculator.py** – Computes priority scores for emails using an ML model.
- **slack.py** – Retrieves and summarizes Slack messages.
- **setup.py** – Automates environment setup and dependency installation.
- **summarizer.py** – Summarizes email and Slack conversations using **TF-IDF**.
- **task_extractor.py** – Identifies tasks from messages and logs them.
- **utils.py** – Contains helper functions for formatting and processing.

## How It Works
1. **Emails & Slack messages** are fetched.
2. **Summarization** extracts key insights from conversations.
3. **Priority calculation** assigns urgency levels using a **classification ML algorithm**.
4. **Tasks are extracted and stored** in the database.
5. **Main script executes everything**, exporting data for tracking.

## Setup Instructions
### Prerequisites
- Python 3.8+
- Required libraries installed via `setup.py`
- Gmail API credentials for email fetching
- Slack API credentials for message retrieval


