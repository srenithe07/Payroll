import calendar
import sqlite3
import sys
import re

from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / "data" / "payroll.db"


# Database connection
def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)

    db = sqlite3.connect(DB)
    db.execute("PRAGMA foreign_keys = ON")

    db.executescript(
        (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8")
    )

    return db


# Validate date
def validate_date(day_text):

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day_text):
        raise ValueError("Enter date in YYYY-MM-DD format.")

    day = date.fromisoformat(day_text)

    if day.weekday() > 4:
        raise ValueError("Attendance can only be recorded on weekdays.")

    return day


# Create monthly period for employee
def create_period(db, employee_id, day):

    employee = db.execute(
        """
        SELECT name, department, designation, basic_paise
        FROM employee
        WHERE id = ?
        """,
        (employee_id,)
    ).fetchone()

    if employee is None:
        raise ValueError("Unknown employee ID.")

    month = day.strftime("%Y-%m")

    working_days = sum(
        week[i] != 0
        for week in calendar.monthcalendar(day.year, day.month)
        for i in range(5)
    )

    db.execute(
        """
        INSERT OR IGNORE INTO period
        (employee_id, month, department, basic_paise, working_days)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            employee_id,
            month,
            employee[1],
            employee[3],
            working_days
        )
    )

    return employee, month


# Record or update attendance
def record(db, employee_id, day_text, status, minutes, reason):

    employee_id = int(employee_id)
    day = validate_date(day_text)

    if status not in ("Present", "Absent", "Paid leave"):
        raise ValueError("Invalid attendance status.")

    minutes = int(minutes)
    reason = (reason or "").strip()

    if status == "Present":

        if not 1 <= minutes <= 1440:
            raise ValueError("Minutes must be between 1 and 1440.")

        reason = ""

    elif status == "Absent":

        minutes = 0

        if not reason:
            raise ValueError("Absence reason is required.")

    else:

        minutes = 0

        if not reason:
            raise ValueError("Leave reason is required.")

    employee, month = create_period(db, employee_id, day)

    db.execute(
        """
        INSERT INTO attendance
        (employee_id, day, month, status, minutes, leave_reason)
        VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(employee_id, day)
        DO UPDATE SET
            month = excluded.month,
            status = excluded.status,
            minutes = excluded.minutes,
            leave_reason = excluded.leave_reason
        """,
        (
            employee_id,
            day,
            month,
            status,
            minutes,
            reason
        )
    )

# Display database records
def show(cursor):

    if cursor.description is None:
        return

    print(" | ".join(column[0] for column in cursor.description))

    rows = cursor.fetchall()

    for row in rows:
        print(" | ".join(map(str, row)))

    if not rows:
        print("(no records)")


# Add, update and list employees
def employee_operations(db, op, args):

    if op == "add":

        if len(args) != 4:
            raise ValueError("Invalid employee details.")

        name, department, designation, salary = args

        cursor = db.execute(
            """
            INSERT INTO employee
            (name, department, designation, basic_paise)
            VALUES (?, ?, ?, ?)
            """,
            (name, department, designation, int(salary))
        )

        print("\nEmployee added successfully!")
        print("Employee ID:", cursor.lastrowid)

    elif op == "update":

        if len(args) != 5:
            raise ValueError("Invalid employee details.")

        name, department, designation, salary, employee_id = args

        cursor = db.execute(
            """
            UPDATE employee
            SET name = ?,
                department = ?,
                designation = ?,
                basic_paise = ?
            WHERE id = ?
            """,
            (
                name,
                department,
                designation,
                int(salary),
                int(employee_id)
            )
        )

        if cursor.rowcount == 0:
            raise ValueError("Unknown employee ID.")

        print("\nEmployee updated successfully!")

    elif op == "list":

        if args:
            raise ValueError("List does not require arguments.")

        print("\n===== EMPLOYEE DETAILS =====")

        show(
            db.execute(
                """
                SELECT
                    id AS employee_id,
                    name,
                    department,
                    designation,
                    basic_paise / 100.0 AS monthly_salary_INR
                FROM employee
                ORDER BY id
                """
            )
        )


# Attendance operation
def attendance_operation(db, args):

    if len(args) != 5:
        raise ValueError("Invalid attendance details.")

    employee_id, day_text, status, minutes, reason = args

    record(
        db,
        employee_id,
        day_text,
        status,
        minutes,
        reason
    )

    print("\nAttendance recorded successfully!")


# Monthly reports
def monthly_reports(db, month):

    if not re.fullmatch(r"\d{4}-\d{2}", month):
        raise ValueError("Enter month in YYYY-MM format.")

    date.fromisoformat(month + "-01")

    print("\n========== MONTHLY REPORT ==========")

    departments = db.execute(
        """
        SELECT DISTINCT department
        FROM period
        WHERE month = ?
        ORDER BY department
        """,
        (month,)
    ).fetchall()

    if not departments:
        print("No attendance records found.")
        return

    # Present and absent employee details
    for (department,) in departments:

        print("\nDEPARTMENT:", department)

        print("\n--- PRESENT EMPLOYEES ---")

        show(
            db.execute(
                """
                SELECT a.employee_id, a.status
                FROM attendance a
                JOIN period p
                ON a.employee_id = p.employee_id
                AND a.month = p.month
                WHERE a.month = ?
                AND p.department = ?
                AND a.status = 'Present'
                ORDER BY a.employee_id
                """,
                (month, department)
            )
        )

        print("\n--- ABSENT / LEAVE EMPLOYEES ---")

        show(
            db.execute(
                """
                SELECT
                    a.employee_id,
                    a.status,
                    a.leave_reason AS reason
                FROM attendance a
                JOIN period p
                ON a.employee_id = p.employee_id
                AND a.month = p.month
                WHERE a.month = ?
                AND p.department = ?
                AND a.status IN ('Absent', 'Paid leave')
                ORDER BY a.employee_id
                """,
                (month, department)
            )
        )

    # Department-wise summary
    print("\n===== DEPARTMENT-WISE SUMMARY =====")

    show(
        db.execute(
            """
            SELECT
                p.department,
                SUM(CASE WHEN a.status = 'Present'
                    THEN 1 ELSE 0 END) AS present,
                SUM(CASE WHEN a.status = 'Absent'
                    THEN 1 ELSE 0 END) AS absent,
                SUM(CASE WHEN a.status = 'Paid leave'
                    THEN 1 ELSE 0 END) AS paid_leave

            FROM period p

            LEFT JOIN attendance a
            ON p.employee_id = a.employee_id
            AND p.month = a.month

            WHERE p.month = ?

            GROUP BY p.department
            ORDER BY p.department
            """,
            (month,)
        )
    )


# Leave registration
def leave_operation(db, args):

    if len(args) != 3:
        raise ValueError("Invalid leave details.")

    employee_id, day_text, reason = args

    employee_id = int(employee_id)
    day = validate_date(day_text)

    if not reason.strip():
        raise ValueError("Leave reason is required.")

    employee, month = create_period(db, employee_id, day)

    # Register leave as Paid leave attendance
    record(
        db,
        employee_id,
        day_text,
        "Paid leave",
        0,
        reason
    )

    print("\n===== EMPLOYEE LEAVE DETAILS =====")
    print("Employee ID:", employee_id)
    print("Name:", employee[0])
    print("Department:", employee[1])
    print("Designation:", employee[2])
    print("Leave Date:", day_text)
    print("Leave Reason:", reason)

    print("\nLeave registered successfully!")


# Main operation controller
def run(db, op, args):

    if op in ("add", "update", "list"):
        employee_operations(db, op, args)

    elif op == "day":
        attendance_operation(db, args)

    elif op == "reports":

        if len(args) != 1:
            raise ValueError("Enter month YYYY-MM.")

        monthly_reports(db, args[0])

    elif op == "leave":
        leave_operation(db, args)

    else:
        raise ValueError("Unknown operation.")


# Main program
if __name__ == "__main__":

    try:

        if len(sys.argv) < 2:
            raise ValueError("Please provide an operation.")

        with connect() as db:
            run(db, sys.argv[1], sys.argv[2:])

    except (ValueError, sqlite3.Error, IndexError) as error:

        print("Rejected:", error)
        sys.exit(1)