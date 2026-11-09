# FocusLab - Study Analytics

## Project Proposal

For my Data Centric Programming assignment, I've decided to collect data on my own study habits.

I want to find out if things like where I study, the time of day and how tired I am have an effect on how well I concentrate.

I'll collect the data myself by recording information after each study session. I'll then use Python to store the data in a database, analyse it using pandas and create graphs to see if there are any interesting patterns.

## Questions

The main questions I want to investigate are:

1. Do I concentrate better studying at home or in the college library?
2. Does the time of day affect how focused I am?
3. Do interruptions and energy levels affect how much work I get done?

## Data Dictionary

I'm using two CSV files to collect my data. `study_sessions.csv` contains the individual study sessions, while `daily_log.csv` records days when I didn't study.

### study_sessions.csv

| Column | Type | Description / Measurement |
|---|---|---|
| date | Text | Date of the session (YYYY-MM-DD) |
| start_time | Text | Time the session started (HH:MM, 24-hour clock) |
| module | Text | College module studied |
| location | Text | Where I studied, e.g. Home or College Library |
| activity | Text | Type of work, such as revision, coding or practice questions |
| duration_min | Integer | Session duration in minutes, measured using a timer |
| interruptions | Integer | Number of distractions lasting at least 10 seconds |
| energy_before | Integer | Energy level before studying, rated 1–5 |
| noise_level | Integer | Noise during the session, rated 1–5 |
| focus_after | Integer | How focused I felt during the session, rated afterwards from 1–5 |
| planned_goal | Text | What I wanted to complete during the session |
| goal_met | Text | Whether I completed the goal (yes/no) |

### Rating Scales

- Energy: 1 = very tired, 5 = very energetic.
- Noise: 1 = very quiet, 5 = very noisy.
- Focus: 1 = very distracted, 5 = very focused.

I record the planned goal before starting and the focus rating and goal outcome after finishing.

### daily_log.csv

| Column | Type | Description / Measurement |
|---|---|---|
| date | Text | Date when no studying took place (YYYY-MM-DD) |
| session_count | Integer | Always 0 |
| total_minutes | Integer | Always 0 minutes |
| day_type | Text | Always No Study |

This file only contains confirmed days when I didn't study. Dates that haven't been recorded aren't automatically treated as days off.

I will try to keep the measurements and rating scales consistent throughout the project. Any changes or problems with collecting the data will be explained in my collection diary.

## Project Plan

Once I have collected enough data, I plan to:

- Store the data in a CSV file.
- Use Python to load the data into SQLite.
- Check for missing or incorrect values.
- Use SQL and pandas to analyse the data.
- Create graphs using matplotlib.
- Make an interactive menu or interface for viewing the results.

## Findings

I haven't started analysing the data yet. I'll add my findings here once I've collected enough observations.

## Reflection

I'll complete this section during the project and discuss what worked, what didn't and anything I found interesting.
