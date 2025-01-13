import 'package:flutter/material.dart';
import 'package:hive/hive.dart'; // Import Hive
import '../models/task.dart';
import '../widgets/task_tile.dart';
import 'add_task_screen.dart';
import 'calendar_screen.dart';
import 'archive_screen.dart'; // Import archive screen
import 'package:intl/intl.dart'; // For date formatting
import 'dart:math'; // For random effects and 3D flip
import 'dart:async'; // For particle animation
import 'package:flutter_local_notifications/flutter_local_notifications.dart'; // For notifications
import 'package:permission_handler/permission_handler.dart';

class NotificationManager {
  FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
      FlutterLocalNotificationsPlugin();

  void initializeNotifications() async {
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    final IOSInitializationSettings initializationSettingsIOS =
        IOSInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
      onDidReceiveLocalNotification:
          (int id, String? title, String? body, String? payload) async {
        // Handle the notification received
      },
    );

    final InitializationSettings initializationSettings =
        InitializationSettings(
      android: initializationSettingsAndroid,
      iOS: initializationSettingsIOS, // Use IOSInitializationSettings here
    );

    await flutterLocalNotificationsPlugin.initialize(initializationSettings,
        onSelectNotification: (String? payload) async {
      if (payload != null) {
        // Handle notification tapped logic here
      }
    });
  }
}

class TaskListScreen extends StatefulWidget {
  @override
  _TaskListScreenState createState() => _TaskListScreenState();
}

class _TaskListScreenState extends State<TaskListScreen> {
  Timer? _archiveTimer; // Add a Timer to check for overdue tasks
  List<Task> tasks = []; // List of all active tasks
  List<Task> archivedTasks = []; // List of archived tasks
  String searchQuery = ""; // Search query
  DateTime today = DateTime.now();
  Map<DateTime, bool> expandedSections = {}; // To track expanded sections
  int _tapCount = 0; // Count taps for the Easter egg
  bool _showEasterEgg = false; // To toggle Easter egg view
  bool _glitchEffect = false; // To trigger the glitch effect
  Color _backgroundColor = Colors.black; // Start with a pitch-black background
  List<Particle> _particles = []; // List to store particles for Easter Egg
  bool _showMenu = false; // State for showing the vertical slide menu

  // For notifications
  FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
      FlutterLocalNotificationsPlugin();

  @override
  void initState() {
    super.initState();
    _loadTasks(); // Load tasks from Hive
    _checkForOldTasks(); // Check and move old tasks to archive
    _initParticles(); // Initialize particles for the Easter Egg
    _startArchiveTimer(); // Start the real-time archiving process
    _requestNotificationPermission();
  }

  @override
  void dispose() {
    _archiveTimer?.cancel(); // Cancel the timer when the widget is disposed
    super.dispose();
  }

  // Request notification permission using the permission_handler package
  Future<void> _requestNotificationPermission() async {
    PermissionStatus status = await Permission.notification.request();
    if (status.isGranted) {
      print("Notification permission granted");
    } else {
      print("Notification permission denied");
    }
  }

  // Initialize notifications
  void initializeNotifications() async {
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    final IOSInitializationSettings initializationSettingsIOS =
        IOSInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
      onDidReceiveLocalNotification:
          (int id, String? title, String? body, String? payload) async {
        // Handle the notification received
      },
    );

    final InitializationSettings initializationSettings =
        InitializationSettings(
      android: initializationSettingsAndroid,
      iOS: initializationSettingsIOS,
    );

    await flutterLocalNotificationsPlugin.initialize(initializationSettings,
        onSelectNotification: (String? payload) async {
      if (payload != null) {
        // Handle notification tapped logic here
      }
    });
  }

  // Load tasks from Hive
  void _loadTasks() async {
    var box = await Hive.openBox('tasksBox');
    setState(() {
      tasks = box.get('tasks', defaultValue: <Task>[])?.cast<Task>() ?? [];
      archivedTasks =
          box.get('archivedTasks', defaultValue: <Task>[])?.cast<Task>() ?? [];
    });
  }

  // Save tasks to Hive
  void _saveTasks() async {
    var box = await Hive.openBox('tasksBox');
    await box.put('tasks', tasks);
    await box.put('archivedTasks', archivedTasks);
  }

  // Function to start the timer that periodically checks for overdue tasks
  void _startArchiveTimer() {
    _archiveTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      _checkForOldTasks(); // Check for overdue tasks every 1 minute
    });
  }

  // Get tasks for specific date
  List<Task> getTasksForDate(DateTime date) {
    return tasks.where((task) {
      if (task.date != null) {
        return task.date!.year == date.year &&
            task.date!.month == date.month &&
            task.date!.day == date.day;
      }
      return false;
    }).toList();
  }

  // Check if any tasks are older than today and move them to archive
  void _checkForOldTasks() {
    DateTime today =
        DateTime(DateTime.now().year, DateTime.now().month, DateTime.now().day);

    List<Task> tasksToArchive = tasks.where((task) {
      if (task.date != null && task.date!.isBefore(today)) {
        return true; // Archive tasks that are older than today
      }
      return false;
    }).toList();

    setState(() {
      for (Task task in tasksToArchive) {
        if (task.recurrence != 'None' && !task.isDone) {
          // Calculate the next recurrence date
          DateTime? nextDate;
          if (task.recurrence == 'Daily') {
            nextDate = task.date?.add(Duration(days: 1));
          } else if (task.recurrence == 'Weekly') {
            nextDate = task.date?.add(Duration(days: 7));
          } else if (task.recurrence == 'Monthly') {
            nextDate =
                DateTime(task.date!.year, task.date!.month + 1, task.date!.day);
          }

          // Create a new recurring task if nextDate is valid
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
              isDone: false, // New task instance should be active (not done)
            );

            tasks.add(newRecurringTask); // Add the new task for next recurrence
          }
        }
        // Preserve the `isDone` state when moving the task to the archive
        archivedTasks.add(task); // Archive the task without modifying isDone
        tasks.remove(task); // Remove the original task from active tasks
      }
      _saveTasks(); // Save the updated tasks and archive list to Hive
    });
  }

  // Archive a task (move it to the archivedTasks list)
  void archiveTask(Task task) {
    setState(() {
      tasks.remove(task);
      archivedTasks.add(task);
    });
    _saveTasks(); // Save the updated tasks to Hive
  }

  // Function to add or update tasks
  Future<void> _addOrUpdateTask(Task? task) async {
    Task? newTask = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AddTaskScreen(
          task: task,
          allTasks: tasks,
        ),
      ),
    );
    if (newTask != null) {
      setState(() {
        if (task != null) {
          // If updating a task
          int index = tasks.indexOf(task);
          tasks[index] = newTask;
        } else {
          // If adding a new task
          tasks.add(newTask);
        }
      });
      _saveTasks(); // Save the tasks to Hive after adding or updating
    }
  }

  // Function to delete a task
  void _deleteTask(Task task) {
    setState(() {
      tasks.remove(task);
    });
    _saveTasks(); // Save after deleting the task
  }

  // Easter egg logic - 3D flip animation triggered after tapping bottom-left corner multiple times
  void _triggerEasterEgg() {
    setState(() {
      _tapCount++;
      if (_tapCount >= 5) {
        _showEasterEgg = true;
        _tapCount = 0;
      }
    });
  }

  // Method to handle subtle interaction on no task screen
  void _onNoTaskInteraction(TapDownDetails details) {
    setState(() {
      _backgroundColor =
          Colors.purpleAccent.withOpacity(0.1); // Light pulse effect
      _glitchEffect = true;
      Future.delayed(Duration(milliseconds: 500), () {
        setState(() {
          _backgroundColor = Colors.black; // Reset to black after interaction
          _glitchEffect = false;
        });
      });
    });
  }

  // Initialize particles for Easter egg
  void _initParticles() {
    for (int i = 0; i < 50; i++) {
      _particles.add(Particle());
    }
    Timer.periodic(Duration(milliseconds: 50), (timer) {
      setState(() {
        for (Particle particle in _particles) {
          particle.move();
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    DateTime tomorrow = today.add(Duration(days: 1));
    List<DateTime> upcomingDates = tasks
        .where((task) => task.date != null)
        .map((task) =>
            DateTime(task.date!.year, task.date!.month, task.date!.day))
        .toSet()
        .toList()
      ..sort();

    return Scaffold(
      appBar: AppBar(
        title: Text('My Tasks'),
        centerTitle: true,
        leading: IconButton(
          icon: Icon(Icons.menu), // Use the three-bar menu icon
          onPressed: () {
            setState(() {
              _showMenu = !_showMenu; // Toggle menu visibility
            });
          },
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.add), // Add button on top-right
            onPressed: () async {
              Task? newTask = await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => AddTaskScreen(
                    allTasks: tasks,
                  ),
                ),
              );
              if (newTask != null) {
                setState(() {
                  tasks.add(newTask);
                });
                _checkForOldTasks();
                _saveTasks();
              }
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          // Main task list content
          Column(
            children: [
              if (tasks.length >= 1)
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: TextField(
                    onChanged: (query) {
                      setState(() {
                        searchQuery = query;
                      });
                    },
                    decoration: InputDecoration(
                      labelText: 'Search tasks',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.search),
                    ),
                  ),
                ),
              if (tasks.isEmpty)
                _showEasterEgg
                    ? _buildEasterEggContent()
                    : _buildNoTasksContent(),
              if (tasks.isNotEmpty)
                Expanded(
                  child: ListView.builder(
                    itemCount: upcomingDates.length,
                    itemBuilder: (context, index) {
                      DateTime sectionDate = upcomingDates[index];
                      List<Task> tasksForDate = getTasksForDate(sectionDate);

                      if (searchQuery.isNotEmpty) {
                        tasksForDate = tasksForDate.where((task) {
                          return task.title
                              .toLowerCase()
                              .contains(searchQuery.toLowerCase());
                        }).toList();
                      }

                      if (tasksForDate.isEmpty) {
                        return SizedBox();
                      }

                      bool isExpanded = expandedSections[sectionDate] ?? false;
                      int tasksToShow = isExpanded ? tasksForDate.length : 3;

                      return Padding(
                        padding: EdgeInsets.zero,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Text(
                                getSectionTitle(sectionDate),
                                style: TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            // Build the task list for each date section
                            ListView.builder(
                              shrinkWrap: true,
                              physics: NeverScrollableScrollPhysics(),
                              itemCount: isExpanded
                                  ? tasksForDate.length
                                  : 3, // Show only 3 tasks if not expanded
                              itemBuilder: (context, taskIndex) {
                                if (taskIndex >= tasksForDate.length)
                                  return SizedBox(); // Prevent overflow
                                return Padding(
                                  padding: EdgeInsets.zero,
                                  child: TaskTile(
                                    task: tasksForDate[taskIndex],
                                    onTaskDone: () {
                                      setState(() {
                                        tasksForDate[taskIndex].isDone =
                                            !tasksForDate[taskIndex].isDone;
                                      });
                                      _checkForOldTasks();
                                      _saveTasks();
                                    },
                                    onSubtaskDone: (subtaskIndex) {
                                      setState(() {
                                        tasksForDate[taskIndex]
                                                .subtasks[subtaskIndex]
                                                .isDone =
                                            !tasksForDate[taskIndex]
                                                .subtasks[subtaskIndex]
                                                .isDone;
                                      });
                                      _saveTasks();
                                    },
                                    onDelete: () {
                                      setState(() {
                                        tasks.remove(tasksForDate[taskIndex]);
                                      });
                                      _saveTasks();
                                    },
                                    onEdit: () async {
                                      Task? updatedTask = await Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder: (context) => AddTaskScreen(
                                            task: tasksForDate[taskIndex],
                                            allTasks: tasks,
                                          ),
                                        ),
                                      );

                                      if (updatedTask != null) {
                                        setState(() {
                                          int idx = tasks
                                              .indexOf(tasksForDate[taskIndex]);
                                          tasks[idx] = updatedTask;
                                        });
                                        _checkForOldTasks();
                                        _saveTasks();
                                      }
                                    },
                                    onRecurringTaskDone: () {
                                      setState(() {
                                        Task currentTask =
                                            tasksForDate[taskIndex];
                                        DateTime? nextDate;

                                        if (currentTask.recurrence == 'Daily') {
                                          nextDate = currentTask.date
                                              ?.add(Duration(days: 1));
                                        } else if (currentTask.recurrence ==
                                            'Weekly') {
                                          nextDate = currentTask.date
                                              ?.add(Duration(days: 7));
                                        } else if (currentTask.recurrence ==
                                            'Monthly') {
                                          nextDate = DateTime(
                                            currentTask.date!.year,
                                            currentTask.date!.month + 1,
                                            currentTask.date!.day,
                                          );
                                        }

                                        if (nextDate != null) {
                                          Task newRecurringTask = Task(
                                            title: currentTask.title,
                                            description:
                                                currentTask.description,
                                            date: nextDate,
                                            startTime: currentTask.startTime,
                                            endTime: currentTask.endTime,
                                            priority: currentTask.priority,
                                            category: currentTask.category,
                                            recurrence: currentTask.recurrence,
                                            subtasks: currentTask.subtasks
                                                .map((subtask) {
                                              return Subtask(
                                                title: subtask.title,
                                                isDone: false,
                                              );
                                            }).toList(),
                                            dependencies:
                                                currentTask.dependencies,
                                          );

                                          tasks.removeWhere((task) =>
                                              task.date?.isAtSameMomentAs(
                                                  nextDate!) ??
                                              false &&
                                                  task.title ==
                                                      currentTask.title);

                                          tasks.add(newRecurringTask);
                                        }
                                      });
                                      _saveTasks();
                                    },
                                    onReactivateRecurringTask: () {
                                      setState(() {
                                        Task currentTask =
                                            tasksForDate[taskIndex];
                                        DateTime? nextDate;

                                        if (currentTask.recurrence == 'Daily') {
                                          nextDate = currentTask.date
                                              ?.add(Duration(days: 1));
                                        } else if (currentTask.recurrence ==
                                            'Weekly') {
                                          nextDate = currentTask.date
                                              ?.add(Duration(days: 7));
                                        } else if (currentTask.recurrence ==
                                            'Monthly') {
                                          nextDate = DateTime(
                                            currentTask.date!.year,
                                            currentTask.date!.month + 1,
                                            currentTask.date!.day,
                                          );
                                        }

                                        tasks.removeWhere((task) =>
                                            task.date
                                                ?.isAtSameMomentAs(nextDate!) ??
                                            false &&
                                                task.title ==
                                                    currentTask.title);
                                      });
                                      _saveTasks();
                                    },
                                    allTasks: tasks,
                                  ),
                                );
                              },
                            ),

                            if (tasksForDate.length > 3)
                              TextButton(
                                onPressed: () {
                                  toggleSection(sectionDate);
                                },
                                style: TextButton.styleFrom(
                                  padding: const EdgeInsets.fromLTRB(
                                      16.0, 16.0, 16.0, 0.0),
                                  minimumSize: Size(0, 0),
                                  tapTargetSize:
                                      MaterialTapTargetSize.shrinkWrap,
                                ),
                                child:
                                    Text(isExpanded ? 'See Less' : 'See All'),
                              ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
            ],
          ),
          // Vertical Slide Menu with dynamic height and improved layout
          AnimatedContainer(
            duration: Duration(milliseconds: 200),
            height:
                _showMenu ? null : 0.0, // Dynamically fit the content's height
            constraints: BoxConstraints(
              maxHeight:
                  MediaQuery.of(context).size.height * 0.2, // Limit max height
            ),
            width: double.infinity,
            color: Colors.grey[850], // Background color
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.symmetric(
                    vertical: 4.0), // Reduced vertical padding around the menu
                child: Column(
                  mainAxisSize:
                      MainAxisSize.min, // Fit only the necessary height
                  children: [
                    // Archive Option
                    Padding(
                      padding: const EdgeInsets.symmetric(
                          vertical: 4.0), // Reduced padding
                      child: ListTile(
                        leading: Icon(Icons.archive,
                            color: Colors.white, size: 18), // Smaller icon
                        title: Text(
                          'Archive',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 14, // Reduced font size for compact look
                          ),
                        ),
                        onTap: () {
                          setState(() {
                            _showMenu = false; // Hide the menu when tapped
                          });
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => ArchiveScreen(
                                archivedTasks: archivedTasks,
                                activeTasks:
                                    tasks, // Pass the actual active tasks list
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                    Divider(
                        color: Colors.grey[700],
                        thickness: 0.8), // Thinner divider

                    // Calendar Option
                    Padding(
                      padding: const EdgeInsets.symmetric(
                          vertical: 4.0), // Reduced padding
                      child: ListTile(
                        leading: Icon(Icons.calendar_today,
                            color: Colors.white, size: 18), // Smaller icon
                        title: Text(
                          'Calendar',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 14, // Reduced font size for compact look
                          ),
                        ),
                        onTap: () {
                          setState(() {
                            _showMenu = false; // Hide the menu when tapped
                          });
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) =>
                                  CalendarScreen(tasks: tasks),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // Subtle glitch effect for "No Task Yet" screen interaction
  Widget _buildNoTasksContent() {
    return Expanded(
      child: GestureDetector(
        onTapDown: _onNoTaskInteraction,
        child: AnimatedContainer(
          duration: Duration(milliseconds: 300),
          curve: Curves.easeInOut,
          color: _backgroundColor,
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Transform.translate(
                  offset: _glitchEffect
                      ? Offset(Random().nextDouble() * 20 - 10, 0)
                      : Offset.zero,
                  child: Icon(
                    Icons.task_alt_rounded,
                    size: 100,
                    color: Colors.purpleAccent,
                  ),
                ),
                const SizedBox(height: 20),
                Transform.translate(
                  offset: _glitchEffect
                      ? Offset(Random().nextDouble() * 20 - 10, 0)
                      : Offset.zero,
                  child: Text(
                    'No tasks yet!',
                    style: TextStyle(
                      fontSize: 24,
                      color: Colors.white70,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                Text(
                  'Tap on the + icon to start adding tasks!',
                  style: TextStyle(
                    fontSize: 18,
                    color: Colors.white60,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // Easter egg content: Particles that move and respond to taps
  Widget _buildEasterEggContent() {
    return Expanded(
      child: GestureDetector(
        onTapDown: (details) {
          for (Particle particle in _particles) {
            particle.changeDirection();
          }
        },
        child: Stack(
          children: _particles.map((particle) {
            return Positioned(
              left: particle.x,
              top: particle.y,
              child: Transform.rotate(
                angle: particle.angle,
                child: Icon(
                  Icons.blur_circular,
                  size: particle.size,
                  color: Colors
                      .primaries[Random().nextInt(Colors.primaries.length)],
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  String getSectionTitle(DateTime date) {
    if (isSameDay(date, today)) {
      return "Today";
    } else if (isSameDay(date, today.add(Duration(days: 1)))) {
      return "Tomorrow";
    } else {
      return DateFormat('EEEE, MMM d').format(date);
    }
  }

  bool isSameDay(DateTime date1, DateTime date2) {
    return date1.year == date2.year &&
        date1.month == date2.month &&
        date1.day == date2.day;
  }

  void toggleSection(DateTime date) {
    setState(() {
      expandedSections[date] = !(expandedSections[date] ?? false);
    });
  }
}

// Particle class for Easter egg animation
class Particle {
  double x, y;
  double speedX, speedY;
  double size;
  double angle;

  Particle()
      : x = Random().nextDouble() * 300,
        y = Random().nextDouble() * 600,
        speedX = Random().nextDouble() * 2 - 1,
        speedY = Random().nextDouble() * 2 - 1,
        size = 10 + Random().nextDouble() * 30,
        angle = Random().nextDouble() * 2 * pi;

  void move() {
    x += speedX;
    y += speedY;
    angle += 0.01;
  }

  void changeDirection() {
    speedX = Random().nextDouble() * 2 - 1;
    speedY = Random().nextDouble() * 2 - 1;
  }
}
