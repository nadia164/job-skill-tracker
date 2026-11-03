from ai import extract_skills
from database import (
    create_tables,
    add_job_with_skills,
    get_all_jobs,
    count_jobs,
    get_top_skills,
)


def read_multiline(prompt):
    print(prompt)
    print("(Type END on its own line when you're done.)")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def add_job_flow():
    title = input("Job title: ").strip()
    if not title:
        print("Title can't be empty.")
        return

    description = read_multiline("Paste the job description:")
    if not description:
        print("Description can't be empty.")
        return

    print("\nExtracting skills with AI...")
    try:
        skills = extract_skills(description)
    except Exception as error:
        print(f"Couldn't extract skills: {error}")
        print("Nothing was saved. Please try again.")
        return

    job_id = add_job_with_skills(title, description, skills)
    print(f"Saved job #{job_id}: {title} ({len(skills)} skills found)")
    print("Skills: " + ", ".join(skills))


def list_jobs_flow():
    jobs = get_all_jobs()
    if not jobs:
        print("No jobs saved yet.")
        return

    print("\nSaved jobs:")
    for job_id, title, created_at in jobs:
        print(f"   #{job_id}  {title}  (added {created_at})")


def count_jobs_flow():
    count = count_jobs()
    if not count:
        print("No jobs are saved.")
        return

    print(f"\nNumber of jobs saved: {count}")


def top_skills_flow():
    total = count_jobs()
    if not total:
        print("No jobs saved yet.")
        return

    top = get_top_skills(10)
    if not top:
        print("No skills saved yet.")
        return

    print(f"\nTop skills across {total} jobs:")
    for rank, (skill, job_count) in enumerate(top, start=1):
        percent = job_count / total * 100
        print(f"   {rank}. {skill} - {job_count} of {total} jobs ({percent:.0f}%)")


def show_menu():
    print("\n=== Job Skill Tracker ===")
    print("1. Add a job posting")
    print("2. List saved jobs")
    print("3. Show top skills")
    print("4. Show number of jobs saved")
    print("5. Quit")


def main():
    create_tables()

    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_job_flow()
        elif choice == "2":
            list_jobs_flow()
        elif choice == "3":
            top_skills_flow()
        elif choice == "4":
            count_jobs_flow()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please choose 1-5.")


if __name__ == "__main__":
    main()