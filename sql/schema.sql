PRAGMA foreign_keys = ON;

-- 1. Employee table
CREATE TABLE IF NOT EXISTS employee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    designation TEXT NOT NULL,
    basic_paise INTEGER NOT NULL CHECK(basic_paise > 0)
);


-- 2. Monthly payroll period table
CREATE TABLE IF NOT EXISTS period (
    employee_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    department TEXT NOT NULL,
    basic_paise INTEGER NOT NULL CHECK(basic_paise > 0),
    working_days INTEGER NOT NULL
        CHECK(working_days BETWEEN 20 AND 23),

    PRIMARY KEY(employee_id, month),

    FOREIGN KEY(employee_id)
        REFERENCES employee(id)
);


-- 3. Attendance table
CREATE TABLE IF NOT EXISTS attendance (
    employee_id INTEGER NOT NULL,
    day TEXT NOT NULL,
    month TEXT NOT NULL
        CHECK(month = substr(day, 1, 7)),

    status TEXT NOT NULL
        CHECK(status IN ('Present', 'Absent', 'Paid leave')),

    minutes INTEGER NOT NULL
        CHECK(
            (status = 'Present' AND minutes BETWEEN 1 AND 1440)
            OR
            (status != 'Present' AND minutes = 0)
        ),

    leave_reason TEXT NOT NULL DEFAULT '',

    PRIMARY KEY(employee_id, day),

    FOREIGN KEY(employee_id, month)
        REFERENCES period(employee_id, month),

    CHECK(
        status != 'Paid leave'
        OR length(trim(leave_reason)) > 0
    )
);


-- 4. Attendance summary view
CREATE VIEW IF NOT EXISTS summary AS

SELECT
    p.employee_id,
    p.month,
    p.department,
    p.basic_paise,
    p.working_days,

    COUNT(a.day) AS recorded,

    COUNT(
        CASE WHEN a.status = 'Present'
        THEN 1 END
    ) AS present,

    COUNT(
        CASE WHEN a.status = 'Paid leave'
        THEN 1 END
    ) AS paid_leave,

    COUNT(
        CASE WHEN a.status = 'Absent'
        THEN 1 END
    ) AS absent,

    COALESCE(SUM(a.minutes), 0) AS minutes

FROM period p

LEFT JOIN attendance a
    ON p.employee_id = a.employee_id
    AND p.month = a.month

GROUP BY
    p.employee_id,
    p.month;


-- 5. Payroll calculation view
CREATE VIEW IF NOT EXISTS payroll AS

SELECT
    *,

    CAST(
        (basic_paise * absent + working_days / 2)
        / working_days
        AS INTEGER
    ) AS deduction_paise,

    basic_paise - CAST(
        (basic_paise * absent + working_days / 2)
        / working_days
        AS INTEGER
    ) AS net_paise

FROM summary

WHERE recorded = working_days;