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
    add_my_skills,
    remove_my_skills,
    get_my_skills,
)
from scraper import FetchError, fetch_posting_text

st.set_page_config(page_title="Job Skill Tracker", layout="wide")

create_tables()

st.sidebar.title("Job Skill Tracker")
page = st.sidebar.radio("Go to", ["Add a job", "Top skills", "My skills", "Saved jobs"])


def add_job_page():
    st.title("Add a job")

    source = st.radio("How do you want to add it?", ["Paste text", "From a link"], horizontal=True)

    with st.form("add_job_form"):
        if source == "Paste text":
            title = st.text_input("Job title", placeholder="Junior Software Engineer")
            description = st.text_area(
                "Job description",
                height=300,
                placeholder="Paste the full job posting here",
            )
            url = ""
        else:
            title = st.text_input(
                "Job title (optional)",
                placeholder="Leave empty to use the page's title",
            )
            url = st.text_input("Link to the job posting", placeholder="https://company.com/careers/junior-engineer")
            st.caption("Works best with company career pages. Sites like LinkedIn and Indeed usually block this.")
            description = ""

        submitted = st.form_submit_button("Extract skills and save")

    if not submitted:
        return

    title = title.strip()
    description = description.strip()
    url = url.strip()

    if source == "Paste text":
        if not title:
            st.error("Enter a job title.")
            return
        if not description:
            st.error("Paste the job description.")
            return

    if source == "From a link":
        if not url:
            st.error("Enter a link to the job posting.")
            return

        with st.spinner("Reading the page..."):
            try:
                page_title, description = fetch_posting_text(url)
            except FetchError as error:
                st.error(str(error))
                return

        if not title:
            title = page_title

        if not title:
            st.error("Couldn't find a title on this page. Enter a job title and try again.")
            return

    with st.spinner("Extracting skills with AI..."):
        try:
            skills = extract_skills(description)
        except Exception as error:
            st.error(f"Couldn't extract skills: {error}")
            st.info("Nothing was saved. Your input is still in the form, so you can try again.")
            return

    if not skills:
        st.warning("No skills were found, so nothing was saved. Make sure the text or link is a job posting.")
        return

    job_id = add_job_with_skills(title, description, skills)

    st.success(f"Saved job #{job_id}: {title} ({len(skills)} skills found)")
    st.write(", ".join(skills))

    if source == "From a link":
        with st.expander("Text read from the page"):
            st.text(description)


def top_skills_page():
    st.title("Top skills")

    all_jobs = count_jobs()
    if not all_jobs:
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


def my_skills_page():
    st.title("My skills")

    with st.form("add_my_skills_form", clear_on_submit=True):
        new_skills = st.text_input(
            "Add your skills, separated by commas",
            placeholder="Python, SQL, Git, Kotlin",
        )
        add_clicked = st.form_submit_button("Add skills")

    if add_clicked:
        skills = [skill.strip() for skill in new_skills.split(",") if skill.strip()]
        if not skills:
            st.error("Enter at least one skill.")
        else:
            added = add_my_skills(skills)
            st.success(f"Added {added} new skill(s).")

    my_skills = get_my_skills()
    if not my_skills:
        st.info("Add your skills above to compare them with your saved job postings.")
        return

    st.write("Your skills: " + ", ".join(my_skills))

    to_remove = st.multiselect("Select skills to remove", my_skills)
    if to_remove and st.button("Remove selected"):
        remove_my_skills(to_remove)
        st.rerun()

    st.subheader("Compare with job postings")

    total = count_jobs()
    if not total:
        st.info("Add some job postings to compare your skills against.")
        return

    limit = st.slider("Compare against the top", min_value=5, max_value=30, value=10)

    top = get_top_skills(limit)
    if not top:
        st.info("No skills saved from job postings yet.")
        return

    my_lower = {skill.lower() for skill in my_skills}

    df = pd.DataFrame(top, columns=["Skill", "Jobs"])
    df["Percent of jobs"] = (df["Jobs"] / total * 100).round().astype(int)
    df["Status"] = [
        "You have it" if skill.lower() in my_lower else "To learn"
        for skill in df["Skill"]
    ]

    have = int((df["Status"] == "You have it").sum())
    shown = len(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Match", f"{have / shown * 100:.0f}%")
    col2.metric("Skills you have", f"{have} of {shown}")
    col3.metric("Skills to learn", shown - have)

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Jobs:Q", title="Number of jobs", axis=alt.Axis(tickMinStep=1)),
            y=alt.Y("Skill:N", sort="-x", title=None),
            color=alt.Color(
                "Status:N",
                scale=alt.Scale(
                    domain=["You have it", "To learn"],
                    range=["#1D9E75", "#D85A30"],
                ),
                legend=alt.Legend(title=None, orient="top"),
            ),
            tooltip=["Skill", "Jobs", "Percent of jobs", "Status"],
        )
    )
    st.altair_chart(chart)

    to_learn = df[df["Status"] == "To learn"]
    if to_learn.empty:
        st.success("You have every skill in this list.")
    else:
        st.subheader("What to learn next")
        for skill, jobs, percent in zip(
            to_learn["Skill"], to_learn["Jobs"], to_learn["Percent of jobs"]
        ):
            st.markdown(f"- **{skill}**: in {jobs} of {total} jobs ({percent}%)")

    top_lower = {skill.lower() for skill in df["Skill"]}
    other_skills = [skill for skill in my_skills if skill.lower() not in top_lower]

    if other_skills:
        st.subheader("Your other skills")
        st.caption("Skills you have that aren't in this top list.")
        st.write(", ".join(other_skills))


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
elif page == "My skills":
    my_skills_page()
else:
    saved_jobs_page()