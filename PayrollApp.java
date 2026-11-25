import java.math.BigDecimal;
import java.util.*;

public class PayrollApp {

    private final Scanner scanner = new Scanner(System.in);
    private boolean done = false;

    String ask(String prompt) {
        System.out.print(prompt + ": ");
        String value = scanner.nextLine().strip();

        if (value.isEmpty()) {
            throw new IllegalArgumentException("A value is required.");
        }

        return value;
    }

    void store(String... args) throws Exception {

        List<String> cmd = new ArrayList<>();

        cmd.add(System.getenv().getOrDefault("PAYROLL_PYTHON", "python"));
        cmd.add("store.py");
        cmd.addAll(Arrays.asList(args));

        Process process = new ProcessBuilder(cmd)
                .inheritIO()
                .start();

        int result = process.waitFor();

        if (result != 0) {
            System.out.println("Operation failed.");
        }
    }

    // Add and Update Employee
    void employee(boolean update) throws Exception {

        String id = "";

        if (update) {
            id = ask("Employee ID");
        }

        String name = ask("Name");
        String department = ask("Department");
        String designation = ask("Designation");

        BigDecimal salary = new BigDecimal(
                ask("Monthly basic salary INR")
        );

        long salaryPaise = salary.movePointRight(2).longValueExact();

        if (salaryPaise <= 0 || salaryPaise > 1000000000000L) {
            throw new IllegalArgumentException("Enter a valid salary.");
        }

        if (update) {
            store("update", name, department, designation,
                    Long.toString(salaryPaise), id);
        } else {
            store("add", name, department, designation,
                    Long.toString(salaryPaise));
        }
    }

    // List Employees
    void listEmployees() throws Exception {
        store("list");
    }

    // Record Attendance
    void day() throws Exception {

        String id = ask("Employee ID");
        String date = ask("Date YYYY-MM-DD");

        String inputStatus = ask("Status (Present/Absent/Paid leave)");

        String status;

        if (inputStatus.equalsIgnoreCase("Present")) {
            status = "Present";
        } else if (inputStatus.equalsIgnoreCase("Absent")) {
            status = "Absent";
        } else if (inputStatus.equalsIgnoreCase("Paid leave")) {
            status = "Paid leave";
        } else {
            throw new IllegalArgumentException(
                    "Enter Present, Absent, or Paid leave."
            );
        }

        String minutes = "0";
        String reason = "";

        if (status.equals("Present")) {

            int worked = Integer.parseInt(ask("Minutes Worked"));

            if (worked < 1 || worked > 1440) {
                throw new IllegalArgumentException(
                        "Minutes must be between 1 and 1440."
                );
            }

            minutes = Integer.toString(worked);

        } else {

            reason = ask("Reason");
        }

        store("day", id, date, status, minutes, reason);
    }

    // Monthly Reports
    void monthlyReports() throws Exception {

        String month = ask("Month YYYY-MM");

        store("reports", month);
    }

    // Leave Register
    void leaveRegister() throws Exception {

        String id = ask("Employee ID");
        String date = ask("Leave Date YYYY-MM-DD");
        String reason = ask("Leave Reason");

        store("leave", id, date, reason);
    }

    // Main Menu
    void menu() {

        System.out.println("\n===== EMPLOYEE PAYROLL MANAGEMENT =====\n");

        System.out.println("1. Add Employee");
        System.out.println("2. Update Employee");
        System.out.println("3. List Employees");
        System.out.println("4. Record Attendance");
        System.out.println("5. Monthly Reports");
        System.out.println("6. Leave Register");
        System.out.println("0. Exit");
    }

    // Run Application
    void run() throws Exception {

        while (!done) {

            menu();

            try {

                String choice = ask("Choice");

                switch (choice) {

                    case "1":
                        employee(false);
                        break;

                    case "2":
                        employee(true);
                        break;

                    case "3":
                        listEmployees();
                        break;

                    case "4":
                        day();
                        break;

                    case "5":
                        monthlyReports();
                        break;

                    case "6":
                        leaveRegister();
                        break;

                    case "0":
                        done = true;
                        System.out.println("Thank you! Application closed.");
                        break;

                    default:
                        System.out.println("Choose 0 to 6.");
                }

            } catch (NoSuchElementException e) {

                done = true;

            } catch (Exception e) {

                System.out.println("Rejected: " + e.getMessage());
            }
        }
    }

    public static void main(String[] args) throws Exception {

        PayrollApp app = new PayrollApp();
        app.run();
    }
}