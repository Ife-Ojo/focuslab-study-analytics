# Data Centric Programming Assignment 2026

**FocusLab - Study Analytics**

[Assignment Brief](https://github.com/skooter500/dcp26-assignment/blob/main/dataset_assignment.md)

# Questions

For this assignment, I decided to collect data about my own study habits.

The three main questions I wanted to investigate were:

1. Do I concentrate better studying at home or in the college library?
2. Does the time of day affect how focused I am?
3. Do interruptions and energy levels affect how much work I get done?

I chose these questions because I wanted to see whether my study habits matched how productive I actually felt during different sessions.

# Data Dictionary

I'm using two CSV files to record my data. `study_sessions.csv` contains information about individual study sessions, while `daily_log.csv` records days when I didn't study.

## study_sessions.csv

| Column | Type | Description / Measurement |
|---|---|---|
| date | Text | Date of the session (YYYY-MM-DD) |
| start_time | Text | Time the session started (HH:MM, 24-hour clock) |
| module | Text | College module studied |
| location | Text | Where I studied, such as Home or College Library |
| activity | Text | Type of work, such as revision, coding or practice questions |
| duration_min | Integer | Length of the session in minutes, measured using a timer |
| interruptions | Integer | Number of interruptions lasting at least 10 seconds |
| energy_before | Integer | Energy level before starting, rated from 1 to 5 |
| noise_level | Integer | Noise during the session, rated from 1 to 5 |
| focus_after | Integer | How focused I felt during the session, rated afterwards from 1 to 5 |
| planned_goal | Text | What I planned to complete during the session |
| goal_met | Text | Whether I completed the goal (yes/no) |

## Rating Scales

- **Energy:** 1 = very tired, 5 = very energetic.
- **Noise:** 1 = very quiet, 5 = very noisy.
- **Focus:** 1 = very distracted, 5 = very focused.

I record my planned goal before studying and my focus rating and goal outcome after finishing. I use the same rating scales throughout the project so the results can be compared.

## daily_log.csv

| Column | Type | Description / Measurement |
|---|---|---|
| date | Text | Date when no studying took place (YYYY-MM-DD) |
| session_count | Integer | Always 0 |
| total_minutes | Integer | Always 0 minutes |
| day_type | Text | Always No Study |

I added this file because I realised that recording only completed sessions wouldn't show the days when I didn't study.

A date is only recorded as No Study when I can confirm that I didn't study that day. Unrecorded dates aren't automatically counted as days off.

# Description of the project

FocusLab is a Python application that I built for analysing my own study habits.

The idea came from wanting to understand how I actually spend my study time. I study different modules throughout the week, and some sessions feel much more productive than others. I wanted to see if there were any patterns in my concentration, interruptions, energy levels and study environment.

I collect information about my study sessions and save it in CSV files. The program then loads the data into an SQLite database, runs SQL queries and uses pandas to analyse it.

I also use matplotlib to create graphs showing things such as total study time, differences between modules, session lengths and the relationship between interruptions and focus.

The application has a menu that allows a user to explore the data without having to write SQL queries themselves.

# Instructions for use

The project requires Python 3, pandas and matplotlib.

Download or clone the repository and open a terminal in the project folder.

**1. Install the required libraries:**

```
pip install -r requirements.txt
```

**2. Load the CSV data into SQLite:**

```
python load_data.py
```

This creates `focuslab.db` using the data stored in the CSV files.

**3. Start the application:**

```
python app.py
```

The main menu has the following options:

| Option | Function |
|---|---|
| 1 | Run SQL reports |
| 2 | Filter study sessions by module and location |
| 3 | Run pandas analysis and update charts |
| 4 | View a saved chart |
| 5 | Add today's completed study session |
| 6 | Edit or delete a recorded session |
| 0 | Exit |

Option 3 generates the charts and saves them in the `charts` folder. Option 4 opens a selected chart.

The user can also add completed sessions or correct existing records through the menu.

If either CSV file is changed manually, run `python load_data.py` again to update the database.

**Running the tests:**

```
python test_validation.py
```

**Checking the database:**

```
python check_database.py
```

The database checker displays the number of study sessions, the number of no-study days and whether any dates appear in both tables.

# How it works:

## Collecting and validating the data

The main dataset is stored in `data/study_sessions.csv`, with no-study days stored separately in `data/daily_log.csv`.

`load_data.py` reads both files and checks the records before loading them into SQLite.

The validation includes:

- Checking that dates and times are in the correct format.
- Checking for missing values.
- Making sure durations and interruptions are valid numbers.
- Making sure ratings are between 1 and 5.
- Checking that goal completion is either yes or no.
- Preventing duplicate or overlapping sessions.
- Preventing sessions from crossing midnight.
- Checking that study days don't conflict with no-study days.

If the data passes validation, the database tables are updated.

## SQL queries

`queries.py` contains six SQL reports that examine different parts of the dataset.

They include overall study statistics, total time by module, focus by location, goal completion, unfinished goals and daily study totals.

I used SQL operations including `WHERE`, `GROUP BY`, `ORDER BY`, `COUNT`, `SUM` and `AVG`.

The daily totals query also combines information from the study sessions and no-study days.

## Pandas analysis

`analysis.py` loads the SQLite data into pandas DataFrames.

It calculates total and average study time, compares modules and locations, and looks at focus ratings for different times of day.

I also compare interruptions with focus and starting energy with goal completion.

The program calculates a correlation between interruptions and focus when there is enough variation in the data.

## Charts

The program creates five charts using matplotlib:

1. **Daily Study Time:** Minutes studied each day, including no-study days.
2. **Study Time by Module:** Total minutes spent studying each module.
3. **Focus and Interruptions:** Average focus rating for different numbers of interruptions.
4. **Session Length Distribution:** How session durations are spread out.
5. **Interruptions vs Focus:** A scatter plot comparing interruptions with focus ratings.

These charts are saved as PNG files in the `charts` folder.

## Interactive menu

`app.py` brings the different parts of the program together.

Instead of running separate scripts for every task, the user can choose what they want to do from the menu.

The program also allows users to add, edit and delete study sessions. Changes are checked before being saved, and backups are created when the session CSV is updated through the application.

## Testing

I used Python's `unittest` module to test the data validation and database loading.

There are 15 automated tests covering valid and invalid records, duplicate sessions, overlaps, incorrect ratings, dates and times, database constraints and failed database updates.

The tests use temporary files and databases so they don't change the main study records.

# Data Collection and Reflection

I began the dataset during reading week in October.

One decision I made early on was not to use fixed study blocks. Some subjects take longer than others, especially when I'm working through Maths problems or completing programming labs. I wanted to record the actual time spent rather than assume every session would last an hour.

I also added the separate daily log after realising that days without studying would otherwise be missing from the analysis.

My study routine changed unexpectedly in early November because of a knee injury and time spent in hospital. This affected how much studying I could do and made the collection period less consistent than I originally expected.

I kept track of these changes in `collection_diary.md`, as they are important when interpreting the results. A normal college week and a week spent recovering at home aren't necessarily comparable.

One thing I've learned from collecting this data is that keeping consistent records is just as important as analysing them. It's easier to record a session when it finishes than to try to remember the details later.

The collection process has also made me pay more attention to interruptions, how I feel before studying and whether I'm actually completing what I planned.

# Photos

# Findings

# List of files in the project

| Files | Source |
|---|---|
| `README.md` | Project documentation |
| `collection_diary.md` | My data collection diary |
| `data/study_sessions.csv` | Study session observations |
| `data/daily_log.csv` | Recorded no-study days |
| `load_data.py` | Project code |
| `queries.py` | Project code |
| `analysis.py` | Project code |
| `app.py` | Project code |
| `test_validation.py` | Project testing code |
| `check_database.py` | Project database checker |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Git configuration |
| `charts/` | Charts generated by `analysis.py` |

# References

- [Data Centric Programming Assignment Brief](https://github.com/skooter500/dcp26-assignment/blob/main/dataset_assignment.md)
- [Python Documentation](https://docs.python.org/3/)
- [SQLite documentation for Python](https://docs.python.org/3/library/sqlite3.html)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Documentation](https://matplotlib.org/stable/)

# What I am most proud of in the assignment

The part I'm most proud of is getting the different parts of the project working together.

At first, the idea was just to collect my study data and analyse it. I ended up building an application where I can load the data, run SQL queries, generate charts and manage study sessions from one menu.

I'm also happy with the validation and testing. I wanted to make sure mistakes in the CSV wouldn't quietly affect the results or cause problems with the database.

# What I learned

This project gave me a better understanding of how CSV files, SQLite and pandas can work together.

I learned more about validating data before inserting it into a database, writing SQL queries to summarise records and using pandas to compare different parts of a dataset.

I also got more practice with matplotlib, especially choosing graphs that make sense for the data rather than just creating charts for the sake of it.

Another useful part was testing. Writing tests helped me check whether the program would handle incorrect values, duplicate records and database errors properly.

I also learned that collecting your own data isn't always straightforward. Your routine can change, you can miss days, and you have to think carefully about what the measurements actually mean.

Overall, the project helped me connect what we've covered in Data Centric Programming with something from my own daily life.
