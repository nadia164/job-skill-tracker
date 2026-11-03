from ai import extract_skills

sample = """
We are hiring a Junior Software Engineer.
Requirements:
- Bachelor's degree in Computer Science or related field
- Experience with Python and Django
- Familiarity with PostgreSQL and REST APIs
- Knowledge of Git and Docker is a plus
- Good communication and teamwork skills
"""

skills = extract_skills(sample)

print(f"Found {len(skills)} skills:")
for skill in skills:
    print(f"- {skill}")