# Job Skill Tracker

A command-line tool that uses AI to extract skills from job postings and ranks which skills appear most often across them.

I built this during my own job search to find out which skills employers are actually asking for, so I know what to focus on learning.

## Features

- Paste in any job posting and save it to a local database
- AI automatically extracts the skills (languages, frameworks, tools, soft skills)
- See the top skills across all saved postings, with how many jobs mention each one
- View the skills for any single job
- Handles busy or unavailable AI models with automatic retries and fallbacks

## Tech Stack

- **Python 3**
- **SQLite** for storage
- **Google Gemini API** (`google-genai` SDK) for skill extraction
- **python-dotenv** for managing the API key

## How It Works

```
Job posting text
      |
      v
  main.py  ------>  ai.py  ------>  Gemini API
      |               |
      |        returns a cleaned list of skills
      v
 database.py  ---->  SQLite (jobs + skills tables)
      |
      v
 Top skills query (GROUP BY + COUNT)
```

The code is split into three files, each with one job:

- `main.py` handles the menu and user input
- `ai.py` handles everything related to the AI provider
- `database.py` handles all database queries

## Setup

1. Clone the repository:

   ```
   git clone https://github.com/nadia164/job-skill-tracker.git
   cd job-skill-tracker
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac/Linux
   ```

3. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Get a free API key from [Google AI Studio](https://aistudio.google.com/), then copy `.env.example` to a new file named `.env` and add your key.

5. Run the app:

   ```
   python main.py
   ```

## Example

```
=== Job Skill Tracker ===
1. Add a job posting
2. List saved jobs
3. Show top skills
4. Show skills for a job
5. Show number of jobs saved
6. Quit
Choose an option: 3

Top skills across 3 jobs:
   1. Python - 3 of 3 jobs (100%)
   2. Git - 2 of 3 jobs (67%)
   3. SQL - 2 of 3 jobs (67%)
```

## Design Decisions

- **Separate AI module:** All AI code lives in `ai.py` behind one function, `extract_skills()`. Switching to another provider (like Claude or OpenAI) only means replacing that file.
- **Retries and fallbacks:** If a model is busy (HTTP 503), the app waits and retries once, then falls back to another model. Requests also have a timeout, so the app never hangs.
- **Structured AI output:** The model is asked to return JSON only, and the result is cleaned to remove blanks and duplicates.
- **Atomic saves:** A job and its skills are saved in a single transaction. If anything fails, the whole save is rolled back, so there's never half-saved data.
- **Safe SQL:** All queries use parameterized placeholders (`?`) to prevent SQL injection.

## Future Improvements

- Charts of the top skills
- Filter top skills by job title or date
- Compare my own skills against the most requested ones
- Import postings from a URL