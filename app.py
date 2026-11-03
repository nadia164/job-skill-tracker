import streamlit as st

from database import create_tables, get_all_jobs, get_skills_for_job, count_jobs

st.set_page_config(page_title="Job Skill Tracker", layout="wide")

create_tables()

st.sidebar.title("Job Skill Tracker")
page = st.sidebar.radio("Go to", ["Add a job", "Top skills", "Saved jobs"])

def add_job_page():
    st.title("Add a job")
    st.info("Coming in the next step.")

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