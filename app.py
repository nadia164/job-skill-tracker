import streamlit as st
from ai import extract_skills

from database import (
    create_tables, 
    add_job_with_skills,
    get_all_jobs, 
    get_skills_for_job, 
    count_jobs
)

st.set_page_config(page_title="Job Skill Tracker", layout="wide")

create_tables()

st.sidebar.title("Job Skill Tracker")
page = st.sidebar.radio("Go to", ["Add a job", "Top skills", "Saved jobs"])

def add_job_page():
    st.title("Add a job")
    
    with st.form("add_job_form"):
        title = st.text_input("Job title", placeholder="Junior Software Engineer")
        description = st.text_area(
            "Job description",
            height=300,
            placeholder="Paste the full job posting here",
        )
        submitted = st.form_submit_button("Extract skills and save")

    if not submitted:
        return

    title = title.strip()
    description = description.strip()

    if not title or not description:
        st.error("Enter both a job title and a job description.")
        return

    with st.spinner("Extracting skills with AI..."):
        try:
            skills = extract_skills(description)

        except Exception as error:
            st.error(f"Couldn't extract skills: {error}")
            st.info("Nothing was saved. Your text is still in the form, so you can try again.")
            return

    job_id = add_job_with_skills(title, description, skills)

    st.success(f"Saved job #{job_id}: {title} ({len(skills)} skills found)")
    st.write(", ".join(skills))

def top_skills_page():
    st.title("Top skills")
    st.info("Coming soon.")

def saved_jobs_page():
    st.title("Saved jobs")

    st.metric("Jobs saved", count_jobs())

    jobs = get_all_jobs()
    if not jobs:
        st.info("No jobs saved yet. Add one on the Add a job page.")
        return
    table = [
        {"#": job_id, "Title": title, "Added": created_at}
        for job_id, title, created_at in jobs
    ]
    st.dataframe(table, hide_index=True)

    st.subheader("Skills for one job")

    job_options = {f"#{job_id} - {title}": job_id for job_id, title, _ in jobs}
    choice = st.selectbox("Pick a job", list(job_options.keys()))

    skills = get_skills_for_job(job_options[choice])
    if not skills:
        st.write("No skills saved for this job.")
        return

    for skill in skills:
        st.markdown(f"- {skill}")

if page == "Add a job":
    add_job_page()
elif page == "Top skills":
    top_skills_page()
else:
    saved_jobs_page()