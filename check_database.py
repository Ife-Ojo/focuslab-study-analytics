import sqlite3
from pathlib import Path

folder = Path(__file__).resolve().parent
db_path = folder / "focuslab.db"

if not db_path.exists():
    raise SystemExit("Database missing. Run load_data.py first.")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check how many records are stored
cursor.execute("SELECT COUNT(*) FROM study_sessions")
sessions = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM daily_log")
no_study_days = cursor.fetchone()[0]

print(f"Study sessions: {sessions}")
print(f"No-study days: {no_study_days}")

# Check whether a date appears in both tables
cursor.execute("""
    SELECT DISTINCT s.date
    FROM study_sessions s
    INNER JOIN daily_log d ON s.date = d.date
""")

conflicts = cursor.fetchall()

if conflicts:
    print("Conflicting dates found:")
    for date in conflicts:
        print(date[0])
else:
    print("No conflicting dates found.")

conn.close()
