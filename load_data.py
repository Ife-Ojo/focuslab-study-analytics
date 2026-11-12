import csv
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
DATA = FOLDER / "data"
DATABASE = FOLDER / "focuslab.db"

STUDY_COLUMNS = [
    "date", "start_time", "module", "location", "activity",
    "duration_min", "interruptions", "energy_before", "noise_level",
    "focus_after", "planned_goal", "goal_met"
]

DAILY_COLUMNS = ["date", "session_count", "total_minutes", "day_type"]


def read_rows(path, columns):
    """Read a CSV and check for missing or extra values."""
    rows = []

    with open(path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != columns:
            raise ValueError(f"{path.name}: incorrect column headings")

        for line, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"{path.name}, line {line}: too many values")

            for column in columns:
                if row.get(column) is None or not row[column].strip():
                    raise ValueError(
                        f"{path.name}, line {line}: missing {column}"
                    )

            rows.append((
                line,
                {column: row[column].strip() for column in columns}
            ))

    return rows


def check_date(value, line):
    try:
        date = datetime.strptime(value, "%Y-%m-%d")

        if date.strftime("%Y-%m-%d") != value:
            raise ValueError

    except ValueError:
        raise ValueError(f"Line {line}: invalid date") from None


def check_row(row, line):
    """Check one study session before storing it."""

    for column in STUDY_COLUMNS:
        if row.get(column) is None or not str(row[column]).strip():
            raise ValueError(f"Line {line}: missing {column}")

    row = {column: row[column].strip() for column in STUDY_COLUMNS}

    check_date(row["date"], line)

    try:
        start = datetime.strptime(row["start_time"], "%H:%M")

        if start.strftime("%H:%M") != row["start_time"]:
            raise ValueError

    except ValueError:
        raise ValueError(f"Line {line}: invalid start time") from None

    # Convert the numeric values
    try:
        duration = int(row["duration_min"])
        interruptions = int(row["interruptions"])
        energy = int(row["energy_before"])
        noise = int(row["noise_level"])
        focus = int(row["focus_after"])

    except ValueError:
        raise ValueError(
            f"Line {line}: a numeric value is invalid"
        ) from None

    # Check whether the numbers make sense
    if duration <= 0 or interruptions < 0:
        raise ValueError(
            f"Line {line}: duration or interruptions out of range"
        )

    if not all(1 <= value <= 5 for value in (energy, noise, focus)):
        raise ValueError(
            f"Line {line}: ratings must be between 1 and 5"
        )

    goal = row["goal_met"].lower()

    if goal not in ("yes", "no"):
        raise ValueError(
            f"Line {line}: goal_met must be yes or no"
        )

    return (
        row["date"],
        row["start_time"],
        row["module"],
        row["location"],
        row["activity"],
        duration,
        interruptions,
        energy,
        noise,
        focus,
        row["planned_goal"],
        goal
    )


def load_sessions(path):
    sessions = []
    seen = set()

    for line, row in read_rows(path, STUDY_COLUMNS):
        session = check_row(row, line)

        key = (session[0], session[1])

        if key in seen:
            raise ValueError(f"Line {line}: duplicate study session")

        seen.add(key)
        sessions.append(session)

    # Make sure study sessions don't overlap
    previous_end = None

    for session in sorted(sessions, key=lambda s: (s[0], s[1])):
        start = datetime.strptime(
            session[0] + " " + session[1],
            "%Y-%m-%d %H:%M"
        )

        if previous_end is not None and start < previous_end:
            raise ValueError(
                f"Overlapping study sessions near {session[0]} {session[1]}"
            )


        end = start + timedelta(minutes=session[5])

        if end.date() != start.date():
            raise ValueError(
                f"Session crosses midnight: {session[0]} {session[1]}"
            )

        previous_end = end


    return sessions


def load_no_study(path):
    days = []
    seen = set()

    for line, row in read_rows(path, DAILY_COLUMNS):
        check_date(row["date"], line)

        try:
            count = int(row["session_count"])
            minutes = int(row["total_minutes"])

        except ValueError:
            raise ValueError(
                f"Line {line}: invalid daily totals"
            ) from None

        if (
            count != 0
            or minutes != 0
            or row["day_type"].lower() != "no study"
        ):
            raise ValueError(
                f"Line {line}: expected 0,0,No Study"
            )

        if row["date"] in seen:
            raise ValueError(
                f"Line {line}: duplicate no-study date"
            )

        seen.add(row["date"])
        days.append((row["date"], 0, 0, "No Study"))

    return days


def save_database(sessions, days, db_path):
    """Update both database tables using the CSV data."""

    conn = sqlite3.connect(db_path)

    try:
        with conn:
            conn.execute("BEGIN")

            # Recreate the tables using the latest CSV records
            conn.execute("DROP TABLE IF EXISTS daily_log")
            conn.execute("DROP TABLE IF EXISTS study_sessions")

            conn.execute("""
                CREATE TABLE study_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    module TEXT NOT NULL,
                    location TEXT NOT NULL,
                    activity TEXT NOT NULL,
                    duration_min INTEGER NOT NULL CHECK(duration_min > 0),
                    interruptions INTEGER NOT NULL CHECK(interruptions >= 0),
                    energy_before INTEGER NOT NULL CHECK(energy_before BETWEEN 1 AND 5),
                    noise_level INTEGER NOT NULL CHECK(noise_level BETWEEN 1 AND 5),
                    focus_after INTEGER NOT NULL CHECK(focus_after BETWEEN 1 AND 5),
                    planned_goal TEXT NOT NULL,
                    goal_met TEXT NOT NULL CHECK(goal_met IN ('yes', 'no')),
                    UNIQUE(date, start_time)
                )
            """)

            conn.execute("""
                CREATE TABLE daily_log (
                    date TEXT PRIMARY KEY,
                    session_count INTEGER NOT NULL CHECK(session_count = 0),
                    total_minutes INTEGER NOT NULL CHECK(total_minutes = 0),
                    day_type TEXT NOT NULL CHECK(day_type = 'No Study')
                )
            """)

            conn.executemany("""
                INSERT INTO study_sessions (
                    date, start_time, module, location, activity,
                    duration_min, interruptions, energy_before,
                    noise_level, focus_after, planned_goal, goal_met
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sessions)

            conn.executemany("""
                INSERT INTO daily_log (
                    date, session_count, total_minutes, day_type
                )
                VALUES (?, ?, ?, ?)
            """, days)

    finally:
        conn.close()


def main():
    sessions = load_sessions(DATA / "study_sessions.csv")
    days = load_no_study(DATA / "daily_log.csv")

    # A date cannot be a study day and a no-study day
    conflicts = {session[0] for session in sessions} & {
        day[0] for day in days
    }

    if conflicts:
        raise ValueError(
            f"Study and no-study dates conflict: {', '.join(sorted(conflicts))}"
        )

    save_database(sessions, days, DATABASE)

    print(
        f"Loaded {len(sessions)} study sessions "
        f"and {len(days)} no-study days."
    )


if __name__ == "__main__":
    try:
        main()

    except (ValueError, OSError, sqlite3.Error) as error:
        print(f"Load failed: {error}")
        raise SystemExit(1)
