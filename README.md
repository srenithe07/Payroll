# Employee Attendance and Payroll Management Analysis System
Scenario 13 • register numbers 13, 43, 73, 103

## First run on Windows
1. Extract the ZIP. Open the payroll folder in VS Code. Open Terminal → New Terminal.
2. Check `java --version` and `python --version`. Use JDK 17+ and Python 3.10+. If your Python launcher is py, enter `$env:PAYROLL_PYTHON='py'` in PowerShell and substitute py in Python commands.
3. Run `java PayrollApp.java`. Choose **5** and enter **2026-09**. Scroll up to see the employee attendance, payroll and department tables. Choose **6** for leave records. Choose **0** to exit.
4. To rebuild the charts run `python -m pip install -r analysis/requirements.txt` then `python analysis/charts.py`. Open analysis/output.

## Sample and policy
The included SQLite database contains three fictional employees with complete weekday attendance for September and October 2026. Sample payroll uses a Monday–Friday calendar, full-month employment, fully paid leave and proportional absence deductions. Hours are reported separately. Each employee first appears in a month's reports after an attendance entry opens their period. Only complete employee periods produce payroll. These rules are academic project assumptions.

## Project files
docs contains the structured SRS, diagrams, database design, four subject write-ups and acceptance results. samples contains actual Java inputs and outputs and chart totals. sql contains the schema, synthetic data and three report queries; question marks are month parameters bound by store.py. Python uses the built-in sqlite3 library. The Java console invokes store.py from the project folder.

The included database is ready to use. To rebuild a separate practice copy from SQL, run the line below from this folder using a fresh filename:
```
python -c "import sqlite3,pathlib; d=sqlite3.connect('practice.db'); d.executescript(pathlib.Path('sql/schema.sql').read_text()); d.executescript(pathlib.Path('sql/sample_data.sql').read_text()); d.close()"
```
For GitHub upload the extracted folder contents, including source, SQL, documents, charts and samples.
