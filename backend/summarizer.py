import time
import csv
import google.generativeai as genai
import pandas as pd
from transformers import pipeline
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from config import GEMINI_API_KEY  # Replace with your API key

# Initialize Google Gemini AI client
genai.configure(api_key=GEMINI_API_KEY)

# Load Hugging Face Summarization Model
hf_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_with_gemini(texts):
    """Uses Google Gemini AI to summarize multiple emails concisely."""
    try:
        prompt = (
            "Summarize each of the following emails in **1-2 sentences** only.\n"
            "Keep it concise and extract the most important details.\n\n"
        )
        formatted_text = "\n\n###\n\n".join(texts)

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + formatted_text)

        if hasattr(response, "text") and response.text:
            summaries = response.text.strip().split("\n\n###\n\n")
            return [summary.strip() for summary in summaries]

    except Exception as e:
        print(f"⚠️ Gemini AI failed: {e}")

    return None


    return None

def summarize_with_huggingface(text):
    """Uses Hugging Face Transformers for text summarization (fallback)."""
    try:
        summary = hf_summarizer(text, max_length=100, min_length=30, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        print(f"⚠️ Hugging Face summarization failed: {e}")
        return None

def summarize_with_sumy(text):
    """Uses Sumy for text summarization (last fallback)."""
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    return " ".join(str(sentence) for sentence in summarizer(parser.document, 2))

def summarize_emails(emails):
    """Summarizes emails using Gemini AI, Hugging Face, or Sumy as fallback."""
    summaries = []
    batch_size = 5  # Process emails in batches

    for i, email in enumerate(emails):
        email_id = email.get("id", f"unknown_{i}")  # Assign default ID if missing
        content = email.get("content", "").strip()  # Ensure content exists

        if not content:
            print(f"⚠️ Skipping email {email_id}: No content found.")
            continue
        # Try summarization in order: Gemini -> Hugging Face -> Sumy
       # Ensure the summary is stored as a string
        summary = summarize_with_gemini([content]) or \
                summarize_with_huggingface(content) or \
                summarize_with_sumy(content)

        # Convert list to string if needed
        if isinstance(summary, list):
            summary = " ".join(summary)

        summaries.append({"email_id": email_id, "summary": summary})


    return summaries

def save_to_csv(summaries, filename="data/email_summaries.csv"):
    """Saves email summaries to a CSV file with proper formatting."""
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["email_id", "summary"], quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(summaries)

    print(f"✅ Summaries saved to {filename}")


