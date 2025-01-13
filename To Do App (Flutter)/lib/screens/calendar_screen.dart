import 'package:flutter/material.dart';
import 'package:table_calendar/table_calendar.dart';
import '../models/task.dart';
import 'package:intl/intl.dart';
import '../widgets/task_tile.dart'; // Import TaskTile
import 'add_task_screen.dart'; // Import AddTaskScreen

class CalendarScreen extends StatefulWidget {
  final List<Task> tasks; // All tasks passed from My Tasks screen

  const CalendarScreen({required this.tasks});

  @override
  _CalendarScreenState createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  DateTime _selectedDay = DateTime.now();
  DateTime _focusedDay = DateTime.now();

  @override
  Widget build(BuildContext context) {
    // Filter tasks for the selected day from the My Tasks list
    List<Task> tasksForSelectedDay = _getTasksForDay(_selectedDay);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Calendar View'),
        backgroundColor: Colors.black,
        actions: [
          IconButton(
            icon: Icon(Icons.add), // Use "+" icon for adding tasks
            onPressed: () async {
              // Navigate to the AddTaskScreen to create a new task.
              Task? newTask = await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => AddTaskScreen(allTasks: widget.tasks),
                ),
              );
              if (newTask != null) {
                setState(() {
                  widget.tasks.add(newTask); // Add the new task to the list
                });
              }
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 16.0), // Add bottom padding
            child: TableCalendar(
              firstDay: DateTime.utc(2020, 1, 1),
              lastDay: DateTime.utc(2030, 12, 31),
              focusedDay: _focusedDay,
              selectedDayPredicate: (day) {
                return isSameDay(_selectedDay, day);
              },
              onDaySelected: (selectedDay, focusedDay) {
                setState(() {
                  _selectedDay = selectedDay;
                  _focusedDay = focusedDay;
                });
              },
              calendarStyle: CalendarStyle(
                selectedDecoration: const BoxDecoration(
                  color: Colors.purpleAccent,
                  shape: BoxShape.circle,
                ),
                todayDecoration: const BoxDecoration(
                  color: Colors.blueAccent,
                  shape: BoxShape.circle,
                ),
                markerDecoration: const BoxDecoration(
                  color: Colors.redAccent,
                  shape: BoxShape.circle,
                ),
                markersAlignment: Alignment.bottomCenter,
                markersOffset: const PositionedOffset(bottom: 0.0, start: 0.0),
                markersMaxCount: 1, // Only one marker per day
              ),
              headerStyle: const HeaderStyle(
                formatButtonVisible: false,
                titleCentered: true,
              ),
              eventLoader: (day) {
                return _getTasksForDay(day); // Load tasks for the day
              },
            ),
          ),
          Expanded(
            // Show task list for the selected day
            child: _buildTaskListForSelectedDay(tasksForSelectedDay),
          ),
        ],
      ),
    );
  }

  // Function to get tasks for the selected day
  List<Task> _getTasksForDay(DateTime day) {
    return widget.tasks.where((task) {
      if (task.date != null) {
        // Match tasks for the exact date
        return isSameDay(task.date!, day);
      }
      return false;
    }).toList();
  }

  // Function to build the task list for the selected day
  Widget _buildTaskListForSelectedDay(List<Task> tasksForSelectedDay) {
    if (tasksForSelectedDay.isEmpty) {
      return const Center(
        child: Text(
          'No tasks for this day!',
          style: TextStyle(fontSize: 18, color: Colors.white70),
        ),
      );
    }

    return ListView.builder(
      itemCount: tasksForSelectedDay.length,
      itemBuilder: (context, index) {
        return Padding(
          padding: EdgeInsets.zero,
          child: TaskTile(
            task: tasksForSelectedDay[index],
            onTaskDone: () {
              setState(() {
                _handleTaskCompletion(tasksForSelectedDay[index]);
              });
            },
            onSubtaskDone: (subtaskIndex) {
              setState(() {
                tasksForSelectedDay[index].subtasks[subtaskIndex].isDone =
                    !tasksForSelectedDay[index].subtasks[subtaskIndex].isDone;
              });
            },
            onDelete: () {
              setState(() {
                widget.tasks.remove(tasksForSelectedDay[index]);
              });
            },
            onEdit: () async {
              Task? updatedTask = await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => AddTaskScreen(
                    task: tasksForSelectedDay[index],
                    allTasks: widget.tasks,
                  ),
                ),
              );
              if (updatedTask != null) {
                setState(() {
                  int idx = widget.tasks.indexOf(tasksForSelectedDay[index]);
                  widget.tasks[idx] = updatedTask;
                });
              }
            },
            onRecurringTaskDone: () {
              // Recurring task logic can be handled here if needed.
            },
            onReactivateRecurringTask: () {
              // Recurring task reactivation logic can be handled here if needed.
            },
            allTasks: [],
          ),
        );
      },
    );
  }

  // Helper function to handle task completion for both recurring and non-recurring tasks
  void _handleTaskCompletion(Task task) {
    if (task.recurrence == 'None' || task.recurrence.isEmpty) {
      // Non-recurring task, just toggle done/undone
      task.isDone = !task.isDone;
    } else {
      if (task.isDone) {
        _reactivateRecurringTask(task);
      } else {
        _completeRecurringTask(task);
      }
    }
  }

  // Complete a recurring task and create the next instance
  void _completeRecurringTask(Task task) {
    setState(() {
      task.isDone = true;

      // Calculate the next recurring date based on the recurrence type
      DateTime? nextDate;
      if (task.recurrence == 'Daily') {
        nextDate = task.date?.add(Duration(days: 1));
      } else if (task.recurrence == 'Weekly') {
        nextDate = task.date?.add(Duration(days: 7));
      } else if (task.recurrence == 'Monthly') {
        nextDate =
            DateTime(task.date!.year, task.date!.month + 1, task.date!.day);
      }

      // Create a new task for the next recurring instance
      if (nextDate != null) {
        Task newRecurringTask = Task(
          title: task.title,
          description: task.description,
          date: nextDate,
          startTime: task.startTime,
          endTime: task.endTime,
          priority: task.priority,
          category: task.category,
          recurrence: task.recurrence,
          subtasks: task.subtasks.map((subtask) {
            return Subtask(title: subtask.title, isDone: false);
          }).toList(),
          dependencies: task.dependencies,
        );
        widget.tasks.add(newRecurringTask); // Add the new recurring task
      }
    });
  }

  // Reactivate a recurring task and delete the next instance if it exists
  void _reactivateRecurringTask(Task task) {
    setState(() {
      task.isDone = false;

      // Calculate the next recurring date based on the recurrence type
      DateTime? nextDate;
      if (task.recurrence == 'Daily') {
        nextDate = task.date?.add(Duration(days: 1));
      } else if (task.recurrence == 'Weekly') {
        nextDate = task.date?.add(Duration(days: 7));
      } else if (task.recurrence == 'Monthly') {
        nextDate =
            DateTime(task.date!.year, task.date!.month + 1, task.date!.day);
      }

      // Remove the next recurrence if it exists
      if (nextDate != null) {
        widget.tasks.removeWhere((t) =>
            t.date?.isAtSameMomentAs(nextDate!) ??
            false && t.title == task.title);
      }
    });
  }

  // Helper function to check if two dates are the same
  bool isSameDay(DateTime date1, DateTime date2) {
    return date1.year == date2.year &&
        date1.month == date2.month &&
        date1.day == date2.day;
  }
}
