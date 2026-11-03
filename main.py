from database import create_tables, add_job, get_all_jobs, count_jobs

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
    job_id = add_job(title, description)
    print(f"Saved job #{job_id}: {title}")

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
            print("Top skills coming soon!")
        elif choice == "4":
            count_jobs_flow()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please choose 1-5.")

if __name__ == "__main__":
    main()