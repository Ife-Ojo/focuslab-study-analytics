import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "focuslab.db"


def show_query(conn, heading, sql):
    print(f"\n--- {heading} ---")

    cursor = conn.execute(sql)

    # Show readable column headings
    headers = [column[0] for column in cursor.description]
    print(" | ".join(headers))
    print("-" * 55)

    for row in cursor.fetchall():
        print(" | ".join(str(value) for value in row))


def main():
    if not DATABASE.exists():
        print("Run load_data.py first.")
        return

    with sqlite3.connect(DATABASE) as conn:

        # 1. General study statistics
        show_query(conn, "Overall Study", """
            SELECT COUNT(*) AS Sessions,
                   COALESCE(SUM(duration_min), 0) AS Total_Minutes,
                   ROUND(COALESCE(AVG(duration_min), 0), 1) AS Average_Minutes
            FROM study_sessions
        """)

        # 2. Study time for each module
        show_query(conn, "Minutes by Module", """
            SELECT module AS Module,
                   COUNT(*) AS Sessions,
                   SUM(duration_min) AS Total_Minutes
            FROM study_sessions
            GROUP BY module
            ORDER BY Total_Minutes DESC
        """)

        # 3. Focus and interruptions by location
        show_query(conn, "Focus by Location", """
            SELECT location AS Location,
                   COUNT(*) AS Sessions,
                   ROUND(AVG(focus_after), 2) AS Average_Focus,
                   ROUND(
                       60.0 * SUM(interruptions) / SUM(duration_min), 2
                   ) AS Interruptions_Per_Hour
            FROM study_sessions
            GROUP BY location
            ORDER BY Average_Focus DESC
        """)

        # 4. Goal completion for each module
        show_query(conn, "Goal Completion by Module", """
            SELECT module AS Module,
                   COUNT(*) AS Sessions,
                   SUM(CASE WHEN goal_met = 'yes' THEN 1 ELSE 0 END)
                       AS Goals_Met,
                   ROUND(
                       100.0 * SUM(
                           CASE WHEN goal_met = 'yes' THEN 1 ELSE 0 END
                       ) / COUNT(*), 1
                   ) AS Completion_Percent
            FROM study_sessions
            GROUP BY module
            ORDER BY Module
        """)

        # 5. Goals that weren't completed
        show_query(conn, "Unfinished Goals", """
            SELECT date AS Date,
                   module AS Module,
                   planned_goal AS Planned_Goal
            FROM study_sessions
            WHERE goal_met = 'no'
            ORDER BY date, start_time
        """)

        # 6. Daily study totals including no-study days
        show_query(conn, "Daily Study Totals", """
            SELECT date AS Date,
                   COUNT(*) AS Sessions,
                   SUM(duration_min) AS Total_Minutes
            FROM study_sessions
            GROUP BY date

            UNION ALL

            SELECT date, session_count, total_minutes
            FROM daily_log

            ORDER BY Date
        """)


if __name__ == "__main__":
    main()
