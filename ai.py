import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.7-flash"]

TIMEOUT_MS = 30000
RETRY_WAIT_SECONDS = 5

PROMPT = """Extract the skills required or preferred in this job description.

Rules:
- Return ONLY a JSON array of strings, like ["Python", "SQL", "Git"]
- Use short, standard names (for example "JavaScript", not "knowledge of JS programming")
- Include programming languages, frameworks, tools, databases, and important soft skills
- Do not include duplicates

Job description:
{description}
"""


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=TIMEOUT_MS),
    )


def call_model(client, model, description):
    response = client.models.generate_content(
        model=model,
        contents=PROMPT.format(description=description),
        config={"response_mime_type": "application/json"},
    )
    return response.text


def ask_gemini(client, description):
    last_error = None

    for model in MODELS:
        for attempt in range(2):
            print(f"Asking {model}...")
            try:
                return call_model(client, model, description)
            except Exception as error:
                last_error = error
                code = getattr(error, "code", None)
                if code == 503 and attempt == 0:
                    print(f"{model} is busy, retrying in {RETRY_WAIT_SECONDS} seconds...")
                    time.sleep(RETRY_WAIT_SECONDS)
                else:
                    print(f"{model} failed ({code or type(error).__name__}), trying the next one...")
                    break

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


def extract_skills(description):
    client = get_client()
    text = ask_gemini(client, description)

    skills = json.loads(text)

    cleaned = []
    seen = set()
    for skill in skills:
        name = str(skill).strip()
        if name and name.lower() not in seen:
            seen.add(name.lower())
            cleaned.append(name)

    return cleaned