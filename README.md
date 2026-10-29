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

These are the columns I plan to record:

| Column | Type | Description |
|---|---|---|
| date | Text | Date of study |
| start_time | Text | Time I started |
| module | Text | Subject I studied |
| location | Text | Where I studied |
| activity | Text | Type of study |
| duration_min | Integer | Minutes spent studying, measured with a timer |
| interruptions | Integer | Number of distractions lasting at least 10 seconds |
| energy_before | Integer | Energy level before studying (1-5) |
| noise_level | Integer | Noise level during the session (1-5) |
| focus_after | Integer | Focus rating after studying (1-5) |
| planned_goal | Text | What I wanted to finish |
| goal_met | Text | Whether I completed it (yes/no) |

For the ratings, 1 means very low and 5 means very high.

I'll try to record each session on the day it happens and update the CSV regularly on GitHub.

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
