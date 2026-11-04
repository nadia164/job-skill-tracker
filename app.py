from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

from ai import extract_skills
from database import (
    create_tables,
    add_job_with_skills,
    get_all_jobs,
    get_skills_for_job,
    count_jobs,
    get_top_skills,
    count_unique_skills,
    get_job_date_range,
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

    if not skills:
        st.warning("No skills were found, so nothing was saved. Make sure you pasted a job posting.")
        return

    job_id = add_job_with_skills(title, description, skills)

    st.success(f"Saved job #{job_id}: {title} ({len(skills)} skills found)")
    st.write(", ".join(skills))


def top_skills_page():
    st.title("Top skills")

    all_jobs = count_jobs()
    if not count_jobs():
        st.info("No jobs saved yet. Add one on the Add a job page.")
        return

    first_date, last_date = get_job_date_range()
    first_date = date.fromisoformat(first_date)
    last_date = date.fromisoformat(last_date)

    filter_col1, filter_col2 = st.columns(2)
    title_filter = filter_col1.text_input(
        "Job title contains",
        placeholder="engineer",
    ).strip()
    date_range = filter_col2.date_input(
        "Date added",
        value=(first_date, last_date),
        min_value=first_date,
        max_value=last_date,
    )

    if len(date_range) != 2:
        st.info("Pick an end date to apply the date filter.")
        return

    start_date, end_date = date_range

    filters = {
        "title_filter": title_filter or None,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }

    total = count_jobs(**filters)
    if not total:
        st.info("No jobs match these filters.")
        return

    if total != all_jobs:
        st.caption(f"Showing {total} of {all_jobs} jobs")

    limit = st.slider("How many skills to show", min_value=5, max_value=30, value=10)

    top = get_top_skills(limit, **filters)
    if not top:
        st.info("No skills found for these jobs.")
        return

    unique_count = count_unique_skills(**filters)

    col1, col2, col3 = st.columns(3)
    col1.metric("Matching jobs", total)
    col2.metric("Top skill", top[0][0])
    col3.metric("Unique skills", unique_count)

    df = pd.DataFrame(top, columns=["Skill", "Jobs"])
    df["Percent of jobs"] = (df["Jobs"] / total * 100).round().astype(int)

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Jobs:Q", title="Number of jobs", axis=alt.Axis(tickMinStep=1)),
            y=alt.Y("Skill:N", sort="-x", title=None),
            tooltip=["Skill", "Jobs", "Percent of jobs"],
        )
    )
    st.altair_chart(chart)

    st.dataframe(df, hide_index=True)


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