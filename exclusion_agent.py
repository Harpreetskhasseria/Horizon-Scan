# exclusion_agent.py

from openai import OpenAI
import json
import time
from dotenv import load_dotenv
import os

# Load variables from .env into environment
load_dotenv()


# 🔐 OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
# ✅ SET YOUR OPENAI KEY HERE
client = OpenAI(api_key=openai.api_key)

# ✅ Agent to classify entries as Applicable / Excluded
def classify_entries(entries):
    classified = []

    for entry in entries:
        try:
            prompt = f"""
You are a regulatory intelligence assistant. Determine if the following regulatory update should be classified as 'Applicable' or 'Excluded' for a large U.S. bank.

Rules to exclude:
- If it relates only to a specific company or entity (not systemic)
- If it's about internal administrative updates (e.g. record keeping, meetings)
- If it doesn't affect financial services broadly

Provide response in this JSON format:
{{
  "Title": "...",
  "Status": "Applicable" or "Excluded",
  "Reason": "..."
}}

Title: {entry['Topic']}
Summary: {entry.get('Summary', '')}
Link: {entry['Link']}
Regulator: {entry['Regulator']}
Date: {entry['Date']}
"""
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=300
            )

            content = response.choices[0].message.content.strip()
            parsed = json.loads(content)

            entry["Status"] = parsed.get("Status", "Error")
            entry["Reason"] = parsed.get("Reason", "No reason provided")
        except Exception as e:
            entry["Status"] = "Error"
            entry["Reason"] = str(e)

        classified.append(entry)
        time.sleep(1)

    return classified
