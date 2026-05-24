import java.util.ArrayList;
import java.util.Scanner;

public class JavaGradebookApp {

    private static final Scanner scanner = new Scanner(System.in);
    private static final ArrayList<Student> students = new ArrayList<>();

    public static void main(String[] args) {
        boolean running = true;

        printWelcomeMessage();

        while (running) {
            printMenu();
            int choice = getIntInput("Choose an option: ");

            if (choice == 1) {
                addStudent();
            } else if (choice == 2) {
                addGradeToStudent();
            } else if (choice == 3) {
                viewStudentReport();
            } else if (choice == 4) {
                viewClassReport();
            } else if (choice == 5) {
                searchStudent();
            } else if (choice == 6) {
                removeStudent();
            } else if (choice == 7) {
                running = false;
                System.out.println("Thank you for using the Java Gradebook App.");
            } else {
                System.out.println("Invalid option. Please choose a number from 1 to 7.");
            }
        }
    }

    /**
     * Prints the title and purpose of the program.
     */
    private static void printWelcomeMessage() {
        System.out.println("==================================");
        System.out.println("       Java Gradebook App");
        System.out.println("==================================");
        System.out.println("Manage students, grades, averages, and reports.");
        System.out.println();
    }

    /**
     * Prints the main menu.
     */
    private static void printMenu() {
        System.out.println();
        System.out.println("Main Menu");
        System.out.println("1. Add student");
        System.out.println("2. Add grade to student");
        System.out.println("3. View student report");
        System.out.println("4. View class report");
        System.out.println("5. Search for student");
        System.out.println("6. Remove student");
        System.out.println("7. Exit");
    }

    /**
     * Adds a new student to the ArrayList.
     */
    private static void addStudent() {
        System.out.print("Enter student name: ");
        String name = scanner.nextLine().trim();

        if (name.isEmpty()) {
            System.out.println("Student name cannot be blank.");
            return;
        }

        if (findStudentByName(name) != null) {
            System.out.println("That student already exists.");
            return;
        }

        Student newStudent = new Student(name);
        students.add(newStudent);
        System.out.println(name + " was added to the gradebook.");
    }

    /**
     * Allows the user to add a grade to an existing student.
     */
    private static void addGradeToStudent() {
        if (students.isEmpty()) {
            System.out.println("No students have been added yet.");
            return;
        }

        System.out.print("Enter student name: ");
        String name = scanner.nextLine().trim();

        Student student = findStudentByName(name);

        if (student == null) {
            System.out.println("Student not found.");
            return;
        }

        double grade = getDoubleInput("Enter grade from 0 to 100: ");

        if (grade < 0 || grade > 100) {
            System.out.println("Grade must be between 0 and 100.");
            return;
        }

        student.addGrade(grade);
        System.out.println("Grade added for " + student.getName() + ".");
    }

    /**
     * Displays a report for one student.
     */
    private static void viewStudentReport() {
        if (students.isEmpty()) {
            System.out.println("No students have been added yet.");
            return;
        }

        System.out.print("Enter student name: ");
        String name = scanner.nextLine().trim();

        Student student = findStudentByName(name);

        if (student == null) {
            System.out.println("Student not found.");
            return;
        }

        System.out.println();
        System.out.println("Student Report");
        System.out.println("Name: " + student.getName());
        System.out.println("Grades: " + student.getGradesAsString());
        System.out.printf("Average: %.2f%n", student.calculateAverage());
        System.out.println("Letter Grade: " + student.getLetterGrade());
    }

    /**
     * Displays all students and the overall class average.
     */
    private static void viewClassReport() {
        if (students.isEmpty()) {
            System.out.println("No students have been added yet.");
            return;
        }

        double classTotal = 0;
        int studentsWithGrades = 0;

        System.out.println();
        System.out.println("Class Report");
        System.out.println("----------------------------------");

        for (Student student : students) {
            double average = student.calculateAverage();

            System.out.printf("%-20s Average: %6.2f  Letter: %s%n",
                    student.getName(),
                    average,
                    student.getLetterGrade());

            if (student.hasGrades()) {
                classTotal += average;
                studentsWithGrades++;
            }
        }

        System.out.println("----------------------------------");

        if (studentsWithGrades > 0) {
            double classAverage = classTotal / studentsWithGrades;
            System.out.printf("Class Average: %.2f%n", classAverage);
        } else {
            System.out.println("Class Average: No grades entered yet.");
        }
    }

    /**
     * Searches for a student by exact name.
     */
    private static void searchStudent() {
        if (students.isEmpty()) {
            System.out.println("No students have been added yet.");
            return;
        }

        System.out.print("Enter student name to search: ");
        String name = scanner.nextLine().trim();

        Student student = findStudentByName(name);

        if (student == null) {
            System.out.println("Student not found.");
        } else {
            System.out.println("Student found: " + student.getName());
            System.out.println("Number of grades: " + student.getGradeCount());
            System.out.printf("Current average: %.2f%n", student.calculateAverage());
        }
    }

    /**
     * Removes a student from the gradebook.
     */
    private static void removeStudent() {
        if (students.isEmpty()) {
            System.out.println("No students have been added yet.");
            return;
        }

        System.out.print("Enter student name to remove: ");
        String name = scanner.nextLine().trim();

        Student student = findStudentByName(name);

        if (student == null) {
            System.out.println("Student not found.");
            return;
        }

        students.remove(student);
        System.out.println(student.getName() + " was removed from the gradebook.");
    }

    /**
     * Finds a student by name without requiring exact capitalization.
     *
     * @param name The name being searched for.
     * @return The matching Student object, or null if not found.
     */
    private static Student findStudentByName(String name) {
        for (Student student : students) {
            if (student.getName().equalsIgnoreCase(name)) {
                return student;
            }
        }

        return null;
    }

    /**
     * Safely gets an integer from the user.
     *
     * @param prompt Text shown to the user.
     * @return A valid integer.
     */
    private static int getIntInput(String prompt) {
        while (true) {
            System.out.print(prompt);

            try {
                int number = Integer.parseInt(scanner.nextLine());
                return number;
            } catch (NumberFormatException exception) {
                System.out.println("Please enter a valid whole number.");
            }
        }
    }

    /**
     * Safely gets a decimal number from the user.
     *
     * @param prompt Text shown to the user.
     * @return A valid double.
     */
    private static double getDoubleInput(String prompt) {
        while (true) {
            System.out.print(prompt);

            try {
                double number = Double.parseDouble(scanner.nextLine());
                return number;
            } catch (NumberFormatException exception) {
                System.out.println("Please enter a valid number.");
            }
        }
    }
}

/**
 * The Student class represents one student in the gradebook.
 */
class Student {
    private final String name;
    private final ArrayList<Double> grades;

    public Student(String name) {
        this.name = name;
        this.grades = new ArrayList<>();
    }

    public String getName() {
        return name;
    }

    public void addGrade(double grade) {
        grades.add(grade);
    }

    public int getGradeCount() {
        return grades.size();
    }

    public boolean hasGrades() {
        return !grades.isEmpty();
    }

    public double calculateAverage() {
        if (grades.isEmpty()) {
            return 0;
        }

        double total = 0;

        for (double grade : grades) {
            total += grade;
        }

        return total / grades.size();
    }

    public String getLetterGrade() {
        double average = calculateAverage();

        if (!hasGrades()) {
            return "N/A";
        } else if (average >= 90) {
            return "A";
        } else if (average >= 80) {
            return "B";
        } else if (average >= 70) {
            return "C";
        } else if (average >= 60) {
            return "D";
        } else {
            return "F";
        }
    }

    public String getGradesAsString() {
        if (grades.isEmpty()) {
            return "No grades entered";
        }

        StringBuilder gradeText = new StringBuilder();

        for (int i = 0; i < grades.size(); i++) {
            gradeText.append(String.format("%.2f", grades.get(i)));

            if (i < grades.size() - 1) {
                gradeText.append(", ");
            }
        }

        return gradeText.toString();
    }
}
