import csv
import sqlite3
import tempfile
import unittest
from pathlib import Path

from load_data import (
    DAILY_COLUMNS, STUDY_COLUMNS, check_row,
    load_sessions, load_no_study, save_database
)


class TestValidation(unittest.TestCase):

    def setUp(self):
        # Example study session used for testing
        self.row = {
            "date": "2026-11-08",
            "start_time": "14:30",
            "module": "Databases",
            "location": "Home",
            "activity": "SQL revision",
            "duration_min": "60",
            "interruptions": "2",
            "energy_before": "4",
            "noise_level": "2",
            "focus_after": "4",
            "planned_goal": "Revise joins",
            "goal_met": "yes"
        }

        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name)

    def write_csv(self, filename, columns, rows):
        path = self.path / filename

        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

        return path

    def test_valid_row(self):
        self.assertEqual(check_row(self.row, 2)[5], 60)

    def test_missing_module(self):
        self.row["module"] = ""

        with self.assertRaises(ValueError):
            check_row(self.row, 2)

    def test_negative_duration(self):
        self.row["duration_min"] = "-10"

        with self.assertRaises(ValueError):
            check_row(self.row, 2)

    def test_invalid_number(self):
        self.row["interruptions"] = "abc"

        with self.assertRaises(ValueError):
            check_row(self.row, 2)

    def test_invalid_rating(self):
        self.row["focus_after"] = "8"

        with self.assertRaises(ValueError):
            check_row(self.row, 2)

    def test_invalid_date(self):
        self.row["date"] = "2026-15-40"

        with self.assertRaises(ValueError):
            check_row(self.row, 2)

    def test_invalid_time(self):
        self.row["start_time"] = "25:00"

        with self.assertRaises(ValueError):
            check_row(self.row, 2)

    def test_invalid_goal(self):
        self.row["goal_met"] = "maybe"

        with self.assertRaises(ValueError):
            check_row(self.row, 2)

    def test_duplicate_session(self):
        path = self.write_csv(
            "sessions.csv",
            STUDY_COLUMNS,
            [self.row, self.row]
        )

        with self.assertRaisesRegex(ValueError, "duplicate"):
            load_sessions(path)

    def test_overlapping_sessions(self):
        second = dict(self.row, start_time="15:00")

        path = self.write_csv(
            "sessions.csv",
            STUDY_COLUMNS,
            [self.row, second]
        )

        with self.assertRaisesRegex(ValueError, "Overlapping"):
            load_sessions(path)


    def test_session_crosses_midnight(self):
        self.row["start_time"] = "23:30"
        self.row["duration_min"] = "60"

        path = self.write_csv(
            "sessions.csv",
            STUDY_COLUMNS,
            [self.row]
        )

        with self.assertRaisesRegex(ValueError, "midnight"):
            load_sessions(path)

    def test_no_study_must_be_zero(self):
        path = self.write_csv(
            "daily.csv",
            DAILY_COLUMNS,
            [{
                "date": "2026-11-07",
                "session_count": "1",
                "total_minutes": "0",
                "day_type": "No Study"
            }]
        )

        with self.assertRaises(ValueError):
            load_no_study(path)

    def test_reloading_does_not_duplicate(self):
        database = self.path / "test.db"
        sessions = [check_row(self.row, 2)]
        days = [("2026-11-07", 0, 0, "No Study")]

        save_database(sessions, days, database)
        save_database(sessions, days, database)

        conn = sqlite3.connect(database)
        count = conn.execute(
            "SELECT COUNT(*) FROM study_sessions"
        ).fetchone()[0]
        conn.close()

        self.assertEqual(count, 1)

    def test_database_rejects_bad_rating(self):
        database = self.path / "test.db"

        save_database([check_row(self.row, 2)], [], database)

        conn = sqlite3.connect(database)

        try:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    "UPDATE study_sessions SET focus_after = 9"
                )
        finally:
            conn.close()

    def test_failed_load_preserves_previous_data(self):
        database = self.path / "test.db"
        sessions = [check_row(self.row, 2)]

        save_database(sessions, [], database)

        with self.assertRaises(sqlite3.IntegrityError):
            save_database(
                [sessions[0], sessions[0]],
                [],
                database
            )

        conn = sqlite3.connect(database)
        count = conn.execute(
            "SELECT COUNT(*) FROM study_sessions"
        ).fetchone()[0]
        conn.close()

        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
