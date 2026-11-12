import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

FOLDER = Path(__file__).resolve().parent
DATABASE = FOLDER / "focuslab.db"
CHARTS = FOLDER / "charts"

WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]

def load_data():
    """Read the SQLite tables into pandas DataFrames."""

    if not DATABASE.exists():
        raise FileNotFoundError(
            "Database missing. Run load_data.py first."
        )

    with sqlite3.connect(DATABASE) as conn:
        study = pd.read_sql_query(
            "SELECT * FROM study_sessions", conn
        )
        no_study = pd.read_sql_query(
            "SELECT date, total_minutes FROM daily_log", conn
        )

    if study.empty:
        raise ValueError("No study sessions available to analyse.")

    # Converts dates so pandas can work with them
    study["date"] = pd.to_datetime(study["date"])
    study["weekday"] = study["date"].dt.day_name()

    no_study["date"] = pd.to_datetime(no_study["date"])

    return study, no_study


def calculate_daily_totals(study, no_study):
    """Include days when no study took place."""

    totals = study.groupby("date", as_index=False)["duration_min"].sum()

    totals = totals.rename(
        columns={"duration_min": "total_minutes"}
    )

    daily = pd.concat([totals, no_study], ignore_index=True)
    daily = daily.sort_values("date")

    daily["weekday"] = daily["date"].dt.day_name()

    return daily


def show_analysis(study, daily):
    """Display study statistics and comparisons."""

    print("\n--- Study Overview ---")
    print(f"Sessions: {len(study)}")
    print(f"Total minutes: {study['duration_min'].sum()}")
    print(f"Average session: {study['duration_min'].mean():.1f} minutes")
    print(f"Goals completed: {study['goal_met'].eq('yes').mean() * 100:.1f}%")

    # Compare modules
    print("\n--- Module Comparison ---")

    modules = study.groupby("module").agg(
        sessions=("duration_min", "count"),
        total_minutes=("duration_min", "sum"),
        average_focus=("focus_after", "mean")
    ).round(2).sort_values("total_minutes", ascending=False)

    print(modules.to_string())

    # Average study time for each weekday, including zero days
    print("\n--- Average Study Minutes by Weekday ---")

    weekdays = daily.groupby("weekday")["total_minutes"].agg(
        days_recorded="count",
        average_minutes="mean"
    ).reindex(WEEKDAYS).dropna().round(1)

    print(weekdays.to_string())

    # Compare study locations
    print("\n--- Focus by Location ---")

    locations = study.groupby("location").agg(
        sessions=("focus_after", "count"),
        average_focus=("focus_after", "mean"),
        average_interruptions=("interruptions", "mean")
    ).round(2)

    print(locations.to_string())

    # Look at the relationship between interruptions and focus
    print("\n--- Interruptions and Focus ---")

    comparison = study.groupby("interruptions")["focus_after"].agg(
        sessions="count",
        average_focus="mean"
    ).round(2)

    print(comparison.to_string())

    if (
        study["interruptions"].nunique() > 1
        and study["focus_after"].nunique() > 1
    ):
        correlation = study["interruptions"].corr(
            study["focus_after"]
        )

        print(f"Correlation: {correlation:.2f}")


    # Compare focus at different times of day
    study["hour"] = study["start_time"].str[:2].astype(int)

    study["time_of_day"] = pd.cut(
        study["hour"],
        bins=[-1, 11, 16, 23],
        labels=["Morning", "Afternoon", "Evening"]
    )

    print("\n--- Focus by Time of Day ---")

    periods = study.groupby("time_of_day", observed=True).agg(
        sessions=("focus_after", "count"),
        average_focus=("focus_after", "mean"),
        average_interruptions=("interruptions", "mean")
    ).round(2)

    print(periods.to_string())

    # Compare starting energy with goal completion
    print("\n--- Energy and Goal Completion ---")

    study["goal_completed"] = study["goal_met"].eq("yes")

    energy = study.groupby("energy_before").agg(
        sessions=("goal_completed", "count"),
        completion_percent=("goal_completed", "mean")
    )

    energy["completion_percent"] = (
        energy["completion_percent"] * 100
    ).round(1)

    print(energy.to_string())

    print(
        "\nThese results show patterns in the recorded data"
    )

def save_charts(study, daily):
    """Create and save five matplotlib charts."""

    CHARTS.mkdir(exist_ok=True)

    # Chart 1: Study time per day
    plt.figure(figsize=(10, 4))

    plt.bar(daily["date"], daily["total_minutes"])


    plt.title("Daily Study Time (Including No-Study Days)")
    plt.xlabel("Date")
    plt.ylabel("Minutes")
    plt.gcf().autofmt_xdate()


    plt.tight_layout()
    plt.savefig(CHARTS / "daily_study_time.png")
    plt.close()

    # Chart 2: Total minutes by module
    by_module = study.groupby("module")["duration_min"].sum()
    by_module = by_module.sort_values()

    plt.figure(figsize=(9, 4))

    plt.barh(by_module.index, by_module.values)

    plt.title("Total Study Time by Module")
    plt.xlabel("Minutes")

    plt.tight_layout()
    plt.savefig(CHARTS / "study_time_by_module.png")
    plt.close()

    # Chart 3: Interruptions and average focus
    focus = study.groupby("interruptions")["focus_after"].agg(
        ["mean", "count"]
    )

    labels = [
        f"{number} (n={count})"
        for number, count in zip(focus.index, focus["count"])
    ]

    plt.figure(figsize=(7, 4))

    plt.bar(labels, focus["mean"])

    plt.title("Average Focus by Number of Interruptions")
    plt.xlabel("Interruptions per Session (Sample Size)")
    plt.ylabel("Average Focus (1-5)")
    plt.ylim(0, 5)

    plt.tight_layout()
    plt.savefig(CHARTS / "focus_and_interruptions.png")
    plt.close()


    # Chart 4: Distribution of session lengths
    plt.figure(figsize=(8, 4))

    plt.hist(study["duration_min"], bins=8, edgecolor="black")

    plt.title("Distribution of Study Session Lengths")
    plt.xlabel("Session Duration (Minutes)")
    plt.ylabel("Number of Sessions")

    plt.tight_layout()
    plt.savefig(CHARTS / "session_length_distribution.png")
    plt.close()

    # Chart 5: Relationship between interruptions and focus
    plt.figure(figsize=(7, 4))

    plt.scatter(
        study["interruptions"],
        study["focus_after"],
        alpha=0.7
    )

    plt.title("Interruptions vs Focus")
    plt.xlabel("Number of Interruptions")
    plt.ylabel("Focus Rating (1-5)")
    plt.yticks(range(1, 6))

    plt.tight_layout()
    plt.savefig(CHARTS / "interruptions_vs_focus.png")
    plt.close()

    print("\nSaved 5 charts in the charts folder.")


def main():
    study, no_study = load_data()

    daily = calculate_daily_totals(study, no_study)

    show_analysis(study, daily)
    save_charts(study, daily)


if __name__ == "__main__":
    try:
        main()

    except (FileNotFoundError, ValueError, sqlite3.Error) as error:
        print(f"Analysis failed: {error}")
