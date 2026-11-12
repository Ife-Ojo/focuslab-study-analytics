import csv
import shutil
import sqlite3
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path

from analysis import main as run_analysis
from load_data import (
    STUDY_COLUMNS, check_row, load_sessions,
    load_no_study, main as update_database
)

from queries import main as show_queries

FOLDER = Path(__file__).resolve().parent
STUDY_CSV = FOLDER / "data" / "study_sessions.csv"
NO_STUDY_CSV = FOLDER / "data" / "daily_log.csv"
DATABASE = FOLDER / "focuslab.db"
CHARTS = FOLDER / "charts"

CHART_FILES = [
    ("Daily study time", "daily_study_time.png"),
    ("Time by module", "study_time_by_module.png"),
    ("Focus and interruptions", "focus_and_interruptions.png"),
    ("Session length distribution", "session_length_distribution.png"),
    ("Interruptions vs focus", "interruptions_vs_focus.png")
]


def filter_sessions():
    """Search study sessions by module and location."""

    module = input("Module (Enter for all): ").strip()
    location = input("Location (Enter for all): ").strip()

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("""
            SELECT date, start_time, module, location,
                   duration_min, focus_after, goal_met
            FROM study_sessions
            WHERE module LIKE ? AND location LIKE ?
            ORDER BY date DESC, start_time DESC
        """, (f"%{module}%", f"%{location}%"))

        rows = cursor.fetchall()

    print(f"\nFound {len(rows)} session(s)")
    print("Date | Start | Module | Location | Minutes | Focus | Goal met")

    for row in rows:
        print(" | ".join(str(value) for value in row))


def view_chart():
    """Open a saved chart."""

    for number, (title, _) in enumerate(CHART_FILES, start=1):
        print(f"{number}. {title}")

    choice = input("Choose a chart: ").strip()

    if not choice.isdigit() or not 1 <= int(choice) <= len(CHART_FILES):
        print("Invalid chart number.")
        return

    filename = CHART_FILES[int(choice) - 1][1]
    path = CHARTS / filename

    if not path.exists():
        print("Chart not found. Choose option 3 to generate charts first.")
        return

    webbrowser.open(path.resolve().as_uri())
    print(f"Requested to open {filename}")


def add_session():
    """Add a completed session and update the database."""

    today = date.today().isoformat()

    sessions = load_sessions(STUDY_CSV)
    no_study_days = load_no_study(NO_STUDY_CSV)

    if today in {day[0] for day in no_study_days}:
        print("Today is marked No Study in daily_log.csv.")
        print("Correct that CSV entry first if you did study today.")
        return

    print(f"\nAdding a completed study session for {today}")
    print("Type 'cancel' at any prompt to go back.")

    prompts = {
        "start_time": "Start time (HH:MM): ",
        "module": "Module: ",
        "location": "Location: ",
        "activity": "Activity: ",
        "duration_min": "Duration in minutes: ",
        "interruptions": "Number of interruptions: ",
        "energy_before": "Energy before (1-5): ",
        "noise_level": "Noise level (1-5): ",
        "focus_after": "Focus after (1-5): ",
        "planned_goal": "Planned goal: ",
        "goal_met": "Was the goal met? (yes/no): "
    }

    row = {"date": today}

    for column, question in prompts.items():
        answer = input(question).strip()

        if answer.lower() == "cancel":
            print("Nothing saved.")
            return

        row[column] = answer

    # Check the values using our existing validation function
    session = check_row(row, 2)

    start = datetime.strptime(
        f"{today} {session[1]}", "%Y-%m-%d %H:%M"
    )
    end = start + timedelta(minutes=session[5])

    if end.date() != start.date():
        print("Please record sessions within one calendar day.")
        return

    # Check for clashes with sessions already recorded today
    for old in sessions:
        if old[0] != today:
            continue

        old_start = datetime.strptime(
            f"{old[0]} {old[1]}", "%Y-%m-%d %H:%M"
        )
        old_end = old_start + timedelta(minutes=old[5])

        if start < old_end and old_start < end:
            print("This session overlaps another session. Nothing saved.")
            return

    print(
        f"\n{today} | {session[1]} | "
        f"{session[2]} | {session[5]} min"
    )

    confirm = input("Save this session? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("Nothing saved.")
        return

    # Save the new session with the existing records
    save_sessions(sessions + [session])



def save_sessions(records):
    """Validate changes, back up the CSV, then update SQLite."""

    temporary = STUDY_CSV.with_suffix(".tmp")

    try:
        with open(temporary, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(STUDY_COLUMNS)
            writer.writerows(records)

        # Check the edited CSV before replacing the original
        checked = load_sessions(temporary)

        no_study_dates = {
            day[0] for day in load_no_study(NO_STUDY_CSV)
        }

        for session in checked:
            if session[0] in no_study_dates:
                raise ValueError("Session conflicts with a no-study date.")

            start = datetime.strptime(
                f"{session[0]} {session[1]}", "%Y-%m-%d %H:%M"
            )

            if (start + timedelta(minutes=session[5])).date() != start.date():
                raise ValueError("A session cannot cross midnight.")

        # Keep a backup in case a correction needs reversing
        backup_folder = FOLDER / "data" / "backups"
        backup_folder.mkdir(exist_ok=True)

        backup_name = (
            f"study_sessions_{datetime.now():%Y%m%d_%H%M%S_%f}.csv"
        )
        shutil.copy2(STUDY_CSV, backup_folder / backup_name)

        temporary.replace(STUDY_CSV)

    finally:
        temporary.unlink(missing_ok=True)

    update_database()
    print("Changes saved to CSV and SQLite.")

def manage_sessions():
    """Correct or delete an existing study session."""

    sessions = load_sessions(STUDY_CSV)

    if not sessions:
        print("There are no sessions to manage.")
        return

    print("\n--- Recorded Sessions ---")

    for number, session in enumerate(sessions, start=1):
        print(
            f"{number}. {session[0]} {session[1]} | "
            f"{session[2]} | {session[5]} minutes"
        )

    choice = input("\nSession number (0 to cancel): ").strip()

    if not choice.isdigit() or not 0 <= int(choice) <= len(sessions):
        print("Invalid session number.")
        return

    number = int(choice)

    if number == 0:
        print("Cancelled.")
        return

    index = number - 1
    updated = sessions.copy()

    print("\n1. Edit session")
    print("2. Delete session")
    print("0. Cancel")

    action = input("Choose an action: ").strip()

    if action == "1":
        # Convert the saved values back to editable text
        row = {
            column: str(value)
            for column, value in zip(STUDY_COLUMNS, sessions[index])
        }

        print("\nPress Enter to keep a value unchanged.")
        print("Type 'cancel' to stop editing.")

        for column in STUDY_COLUMNS:
            answer = input(f"{column} [{row[column]}]: ").strip()

            if answer.lower() == "cancel":
                print("Nothing changed.")
                return

            if answer:
                row[column] = answer

        updated[index] = check_row(row, index + 2)

        if updated[index] == sessions[index]:
            print("No changes made.")
            return

        confirm = input("Save these corrections? (yes/no): ").strip().lower()

        if confirm != "yes":
            print("Nothing changed.")
            return

    elif action == "2":
        confirm = input(
            "Type DELETE to permanently remove this entry: "
        ).strip()

        if confirm != "DELETE":
            print("Deletion cancelled.")
            return

        updated.pop(index)

    else:
        print("Cancelled.")
        return

    save_sessions(updated)

def main():
    while True:

        print("\n===== FocusLab =====")
        print("1. Run SQL reports")
        print("2. Filter study sessions")
        print("3. Run pandas analysis and update charts")
        print("4. View a chart")
        print("5. Add today's completed session")
        print("6. Edit or delete a session")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                show_queries()

            elif choice == "2":
                filter_sessions()

            elif choice == "3":
                run_analysis()

            elif choice == "4":
                view_chart()

            elif choice == "5":
                add_session()

            elif choice == "6":
                manage_sessions()

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Please choose a number from 0 to 6.")

        except (ValueError, OSError, sqlite3.Error) as error:
            print(f"Could not complete that action: {error}")


if __name__ == "__main__":
    main()
