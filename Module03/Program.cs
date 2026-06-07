using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;

namespace CSharpTaskScheduler;

/// <summary>
/// Represents one task in the task scheduler.
/// This class stores the information the user enters for each task.
/// </summary>
public class TaskItem
{
    public int Id { get; set; }
    public string Title { get; set; }
    public string Description { get; set; }
    public DateTime DueDate { get; set; }
    public bool IsComplete { get; set; }

    public TaskItem(int id, string title, string description, DateTime dueDate, bool isComplete = false)
    {
        Id = id;
        Title = title;
        Description = description;
        DueDate = dueDate;
        IsComplete = isComplete;
    }

    /// <summary>
    /// Converts a task to one line of text that can be saved in a file.
    /// The pipe symbol is used to separate each field.
    /// </summary>
    public string ToFileString()
    {
        return $"{Id}|{Title}|{Description}|{DueDate:yyyy-MM-dd}|{IsComplete}";
    }

    /// <summary>
    /// Creates a TaskItem from one line of saved text.
    /// This allows the program to rebuild tasks when it loads the file.
    /// </summary>
    public static TaskItem? FromFileString(string line)
    {
        string[] parts = line.Split('|');

        if (parts.Length != 5)
        {
            return null;
        }

        bool validId = int.TryParse(parts[0], out int id);
        bool validDate = DateTime.TryParse(parts[3], out DateTime dueDate);
        bool validComplete = bool.TryParse(parts[4], out bool isComplete);

        if (!validId || !validDate || !validComplete)
        {
            return null;
        }

        return new TaskItem(id, parts[1], parts[2], dueDate, isComplete);
    }

    /// <summary>
    /// Displays a clean version of the task for the console.
    /// </summary>
    public override string ToString()
    {
        string status = IsComplete ? "Complete" : "Incomplete";
        return $"[{Id}] {Title}\n    Description: {Description}\n    Due Date: {DueDate:MMM dd, yyyy}\n    Status: {status}";
    }
}

/// <summary>
/// Handles the main task operations such as adding, viewing, searching,
/// completing, deleting, saving, and loading tasks.
/// </summary>
public class TaskManager
{
    private readonly List<TaskItem> _tasks = new();
    private readonly string _filePath;
    private int _nextId = 1;

    public TaskManager(string filePath)
    {
        _filePath = filePath;
    }

    public void AddTask()
    {
        Console.WriteLine("\n--- Add New Task ---");

        string title = ReadRequiredString("Enter task title: ");
        string description = ReadRequiredString("Enter task description: ");
        DateTime dueDate = ReadDate("Enter due date (yyyy-mm-dd): ");

        TaskItem task = new(_nextId, title, description, dueDate);
        _tasks.Add(task);
        _nextId++;

        Console.WriteLine("Task added successfully.");
    }

    public void ViewTasks()
    {
        Console.WriteLine("\n--- All Tasks ---");

        if (_tasks.Count == 0)
        {
            Console.WriteLine("No tasks have been added yet.");
            return;
        }

        foreach (TaskItem task in _tasks.OrderBy(task => task.DueDate))
        {
            Console.WriteLine(task);
            Console.WriteLine();
        }
    }

    public void MarkTaskComplete()
    {
        Console.WriteLine("\n--- Mark Task Complete ---");

        TaskItem? task = FindTaskById();

        if (task == null)
        {
            Console.WriteLine("Task not found.");
            return;
        }

        task.IsComplete = true;
        Console.WriteLine("Task marked as complete.");
    }

    public void DeleteTask()
    {
        Console.WriteLine("\n--- Delete Task ---");

        TaskItem? task = FindTaskById();

        if (task == null)
        {
            Console.WriteLine("Task not found.");
            return;
        }

        _tasks.Remove(task);
        Console.WriteLine("Task deleted successfully.");
    }

    public void SearchTasks()
    {
        Console.WriteLine("\n--- Search Tasks ---");
        string keyword = ReadRequiredString("Enter a keyword to search: ").ToLower();

        List<TaskItem> results = _tasks
            .Where(task => task.Title.ToLower().Contains(keyword) || task.Description.ToLower().Contains(keyword))
            .OrderBy(task => task.DueDate)
            .ToList();

        if (results.Count == 0)
        {
            Console.WriteLine("No matching tasks were found.");
            return;
        }

        Console.WriteLine($"Found {results.Count} matching task(s):\n");

        foreach (TaskItem task in results)
        {
            Console.WriteLine(task);
            Console.WriteLine();
        }
    }

    public void SaveTasks()
    {
        try
        {
            List<string> lines = _tasks.Select(task => task.ToFileString()).ToList();
            File.WriteAllLines(_filePath, lines);
            Console.WriteLine($"Tasks saved to {_filePath}.");
        }
        catch (IOException ex)
        {
            Console.WriteLine($"There was an error saving tasks: {ex.Message}");
        }
    }

    public void LoadTasks()
    {
        if (!File.Exists(_filePath))
        {
            Console.WriteLine("No saved task file was found. Starting with an empty task list.");
            return;
        }

        try
        {
            string[] lines = File.ReadAllLines(_filePath);
            _tasks.Clear();

            foreach (string line in lines)
            {
                TaskItem? task = TaskItem.FromFileString(line);

                if (task != null)
                {
                    _tasks.Add(task);
                }
            }

            if (_tasks.Count > 0)
            {
                _nextId = _tasks.Max(task => task.Id) + 1;
            }

            Console.WriteLine("Saved tasks loaded successfully.");
        }
        catch (IOException ex)
        {
            Console.WriteLine($"There was an error loading tasks: {ex.Message}");
        }
    }

    private TaskItem? FindTaskById()
    {
        int id = ReadInteger("Enter the task ID: ");
        return _tasks.FirstOrDefault(task => task.Id == id);
    }

    private static string ReadRequiredString(string prompt)
    {
        while (true)
        {
            Console.Write(prompt);
            string? input = Console.ReadLine();

            if (!string.IsNullOrWhiteSpace(input))
            {
                return input.Trim();
            }

            Console.WriteLine("Input cannot be blank. Please try again.");
        }
    }

    private static int ReadInteger(string prompt)
    {
        while (true)
        {
            Console.Write(prompt);
            string? input = Console.ReadLine();

            if (int.TryParse(input, out int number))
            {
                return number;
            }

            Console.WriteLine("Please enter a valid whole number.");
        }
    }

    private static DateTime ReadDate(string prompt)
    {
        while (true)
        {
            Console.Write(prompt);
            string? input = Console.ReadLine();

            if (DateTime.TryParseExact(input, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out DateTime date))
            {
                return date;
            }

            Console.WriteLine("Please enter a valid date using the format yyyy-mm-dd.");
        }
    }
}

/// <summary>
/// Program controls the menu and keeps the application running
/// until the user chooses to exit.
/// </summary>
public class Program
{
    private const string FilePath = "tasks.txt";

    public static void Main()
    {
        TaskManager manager = new(FilePath);
        manager.LoadTasks();

        bool running = true;

        while (running)
        {
            DisplayMenu();
            string? choice = Console.ReadLine();

            switch (choice)
            {
                case "1":
                    manager.AddTask();
                    break;
                case "2":
                    manager.ViewTasks();
                    break;
                case "3":
                    manager.MarkTaskComplete();
                    break;
                case "4":
                    manager.DeleteTask();
                    break;
                case "5":
                    manager.SearchTasks();
                    break;
                case "6":
                    manager.SaveTasks();
                    break;
                case "7":
                    manager.LoadTasks();
                    break;
                case "8":
                    manager.SaveTasks();
                    running = false;
                    Console.WriteLine("Goodbye. Your tasks have been saved.");
                    break;
                default:
                    Console.WriteLine("Invalid choice. Please select a number from 1 to 8.");
                    break;
            }
        }
    }

    private static void DisplayMenu()
    {
        Console.WriteLine("\n===============================");
        Console.WriteLine("         Task Scheduler");
        Console.WriteLine("===============================");
        Console.WriteLine("1. Add a task");
        Console.WriteLine("2. View all tasks");
        Console.WriteLine("3. Mark task as complete");
        Console.WriteLine("4. Delete a task");
        Console.WriteLine("5. Search tasks");
        Console.WriteLine("6. Save tasks to file");
        Console.WriteLine("7. Load tasks from file");
        Console.WriteLine("8. Save and exit");
        Console.Write("Choose an option: ");
    }
}
