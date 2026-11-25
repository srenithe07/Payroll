-- ==========================================
-- EMPLOYEE PAYROLL MANAGEMENT SYSTEM
-- MONTHLY REPORT QUERIES
-- ==========================================

-- 1. Present Employees
SELECT
    employee_id,
    status
FROM attendance
WHERE month = ?
AND status = 'Present'
ORDER BY employee_id;


-- 2. Absent Employees with Reason
SELECT
    employee_id,
    status,
    leave_reason AS reason
FROM attendance
WHERE month = ?
AND status = 'Absent'
ORDER BY employee_id;


-- 3. Paid Leave Employees with Reason
SELECT
    employee_id,
    status,
    leave_reason AS reason
FROM attendance
WHERE month = ?
AND status = 'Paid leave'
ORDER BY employee_id;


-- 4. Department-wise Monthly Summary
SELECT
    p.department,

    SUM(
        CASE WHEN a.status = 'Present'
        THEN 1 ELSE 0 END
    ) AS present,

    SUM(
        CASE WHEN a.status = 'Absent'
        THEN 1 ELSE 0 END
    ) AS absent,

    SUM(
        CASE WHEN a.status = 'Paid leave'
        THEN 1 ELSE 0 END
    ) AS paid_leave

FROM period p

LEFT JOIN attendance a
    ON p.employee_id = a.employee_id
    AND p.month = a.month

WHERE p.month = ?

GROUP BY p.department
ORDER BY p.department;


-- 5. Monthly Payroll Details
SELECT
    employee_id,
    basic_paise / 100.0 AS basic_INR,
    deduction_paise / 100.0 AS deducted_INR,
    net_paise / 100.0 AS net_INR

FROM payroll

WHERE month = ?

ORDER BY employee_id;