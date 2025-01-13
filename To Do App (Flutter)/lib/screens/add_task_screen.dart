import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart'; // Import for notifications
import '../models/task.dart';
import '../main.dart'; // Import notification plugin
import 'package:timezone/timezone.dart' as tz;
import 'package:multi_select_flutter/multi_select_flutter.dart';

class AddTaskScreen extends StatefulWidget {
  final Task? task;
  final List<Task> allTasks;

  AddTaskScreen({this.task, required this.allTasks});

  @override
  _AddTaskScreenState createState() => _AddTaskScreenState();
}

class _AddTaskScreenState extends State<AddTaskScreen> {
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  DateTime _selectedDate = DateTime.now();
  DateTime _currentRangeStart = DateTime.now();
  String _selectedPriority = 'Low';
  TimeOfDay? _startTime;
  TimeOfDay? _endTime;
  bool _getAlert = false;
  bool _isDone = false;
  String? _selectedAlertTime = '15 mins'; // Default alert time
  List<String> _selectedDependencies = [];
  String _selectedRecurrence = 'None';
  List<Subtask> _subtasks = [];
  List<TextEditingController> _subtaskControllers = [];

  @override
  void initState() {
    super.initState();
    if (widget.task != null) {
      _titleController.text = widget.task!.title;
      _descriptionController.text = widget.task!.description ?? '';
      _selectedDate = widget.task!.date ?? DateTime.now();
      _startTime = widget.task!.startTime != null
          ? TimeOfDay.fromDateTime(widget.task!.startTime!)
          : null;
      _endTime = widget.task!.endTime != null
          ? TimeOfDay.fromDateTime(widget.task!.endTime!)
          : null;
      _selectedPriority = widget.task!.priority;
      _selectedRecurrence = widget.task!.recurrence;
      _getAlert = widget.task!.getAlert;
      _selectedAlertTime = widget.task!.alertTime ?? '15 mins';
      _subtasks = widget.task!.subtasks;
      _selectedDependencies = widget.task!.dependencies;

      // Initialize isDone field
      _isDone = widget.task!.isDone;

      // Initialize the subtask controllers with existing subtasks if editing
      if (widget.task != null) {
        for (Subtask subtask in widget.task!.subtasks) {
          _subtaskControllers.add(TextEditingController(text: subtask.title));
        }
      } else {
        _subtaskControllers
            .add(TextEditingController()); // At least one empty field
      }
    }
  }

  @override
  void dispose() {
    // Dispose of the controllers
    for (var controller in _subtaskControllers) {
      controller.dispose();
    }
    super.dispose();
  }

  Future<void> _selectTime(bool isStartTime) async {
    TimeOfDay? pickedTime = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.now(),
    );
    if (pickedTime != null) {
      setState(() {
        if (isStartTime) {
          _startTime = pickedTime;
        } else {
          _endTime = pickedTime;
        }
      });
    }
  }

  // Function to schedule a notification
  Future<void> _scheduleNotification(Task newTask) async {
    if (_getAlert && newTask.startTime != null) {
      int minutesBefore = _selectedAlertTime == '15 mins'
          ? 15
          : _selectedAlertTime == '30 mins'
              ? 30
              : 60;

      // Convert DateTime to TZDateTime for scheduling the notification
      final tz.TZDateTime reminderTime = tz.TZDateTime.from(
          newTask.startTime!.subtract(Duration(minutes: minutesBefore)),
          tz.local);

      await flutterLocalNotificationsPlugin.zonedSchedule(
        newTask
            .hashCode, // 1st positional argument: Unique ID for the notification
        'Reminder: ${newTask.title}', // 2nd positional argument: Notification title
        'Your task starts at ${DateFormat.jm().format(newTask.startTime!)}', // 3rd positional argument: Notification body
        tz.TZDateTime.from(
          newTask.startTime!.subtract(Duration(minutes: minutesBefore)),
          tz.local,
        ), // 4th positional argument: scheduledDate (TZDateTime)
        const NotificationDetails(
          android: AndroidNotificationDetails(
            'reminder_channel_id', // Channel ID
            'Task Reminders', // Channel name
            channelDescription:
                'Notification for task reminders', // Channel description
            importance: Importance.max,
            priority: Priority.high,
          ),
        ), // 5th positional argument: NotificationDetails
        androidAllowWhileIdle: true, // Named argument
        uiLocalNotificationDateInterpretation:
            UILocalNotificationDateInterpretation
                .absoluteTime, // Named argument
        matchDateTimeComponents: DateTimeComponents
            .time, // Named argument: Match only the time component
      );
    }
  }

  void _updateDateRange(bool isForward) {
    setState(() {
      _currentRangeStart = isForward
          ? _currentRangeStart.add(Duration(days: 7))
          : _currentRangeStart.subtract(Duration(days: 7));
    });
  }

  @override
  Widget build(BuildContext context) {
    DateTime startOfWeek = _currentRangeStart;
    DateTime endOfWeek = startOfWeek.add(Duration(days: 6));

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.task == null ? 'Create new task' : 'Edit Task'),
        backgroundColor: Colors.black,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Date Range Navigation
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                IconButton(
                  icon: Icon(Icons.chevron_left, color: Colors.white),
                  onPressed: () => _updateDateRange(false),
                ),
                Text(
                  "${DateFormat('dd MMM').format(startOfWeek)} - ${DateFormat('dd MMM').format(endOfWeek)}",
                  style: TextStyle(color: Colors.white, fontSize: 18),
                ),
                IconButton(
                  icon: Icon(Icons.chevron_right, color: Colors.white),
                  onPressed: () => _updateDateRange(true),
                ),
              ],
            ),
            SizedBox(height: 20),

            // Week View with uniform date buttons and border highlight
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: List.generate(7, (index) {
                DateTime day = startOfWeek.add(Duration(days: index));
                bool isSelected = day.day == _selectedDate.day &&
                    day.month == _selectedDate.month &&
                    day.year == _selectedDate.year;
                return GestureDetector(
                  onTap: () => setState(() {
                    _selectedDate = day;
                  }),
                  child: Container(
                    width: 45,
                    padding: EdgeInsets.symmetric(vertical: 8),
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: isSelected ? Colors.purpleAccent : Colors.grey,
                        width: 2,
                      ),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      children: [
                        Text(
                          DateFormat.E().format(day), // Day name
                          style: TextStyle(color: Colors.white),
                        ),
                        SizedBox(height: 5),
                        Text(
                          DateFormat.d().format(day), // Day number
                          style: TextStyle(color: Colors.white),
                        ),
                      ],
                    ),
                  ),
                );
              }),
            ),
            SizedBox(height: 20),

            // Task Name and Description
            Padding(
              padding: const EdgeInsets.only(
                  bottom: 12.0), // Adjust the value as needed
              child: Text(
                'Task Name',
                style: TextStyle(color: Colors.white),
              ),
            ),
            _buildTextField(controller: _titleController, hintText: 'Name'),
            SizedBox(height: 15),
            _buildTextField(
              controller: _descriptionController,
              hintText: 'Description',
              maxLines: 3,
            ),
            SizedBox(height: 20),

            // Start Time and End Time
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Padding(
                        padding: const EdgeInsets.only(
                            bottom: 12.0), // Adjust the value as needed
                        child: Text(
                          'Start Time',
                          style: TextStyle(color: Colors.white),
                        ),
                      ),
                      _buildTimePickerButton(
                        context,
                        time: _startTime,
                        isStartTime: true,
                      ),
                    ],
                  ),
                ),
                SizedBox(width: 20),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Padding(
                        padding: const EdgeInsets.only(
                            bottom: 12.0), // Adjust the value as needed
                        child: Text(
                          'End Time',
                          style: TextStyle(color: Colors.white),
                        ),
                      ),
                      _buildTimePickerButton(
                        context,
                        time: _endTime,
                        isStartTime: false,
                      ),
                    ],
                  ),
                ),
              ],
            ),
            SizedBox(height: 20),

            // Priority, Recurrence, and Alert Settings
            Padding(
              padding: const EdgeInsets.only(
                  bottom: 12.0), // Adjust the value as needed
              child: Text(
                'Priority',
                style: TextStyle(color: Colors.white),
              ),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildPriorityButton('Low'),
                _buildPriorityButton('Medium'),
                _buildPriorityButton('High'),
              ],
            ),
            SizedBox(height: 20),

            Padding(
              padding: const EdgeInsets.only(
                  bottom: 12.0), // Adjust the value as needed
              child: Text(
                'Recurrence',
                style: TextStyle(color: Colors.white),
              ),
            ),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildRecurrenceButton('None'),
                  SizedBox(width: 6.0), // Add space between buttons
                  _buildRecurrenceButton('Daily'),
                  SizedBox(width: 6.0), // Add space between buttons
                  _buildRecurrenceButton('Weekly'),
                  SizedBox(width: 6.0), // Add space between buttons
                  _buildRecurrenceButton('Monthly'),
                ],
              ),
            ),
            SizedBox(height: 20),

            // Alert Time
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Get alert for this task',
                    style: TextStyle(color: Colors.white)),
                Switch(
                  value: _getAlert,
                  onChanged: (value) {
                    setState(() {
                      _getAlert = value;
                    });
                  },
                  activeColor: Colors.purpleAccent,
                ),
              ],
            ),
            if (_getAlert) ...[
              SizedBox(height: 10),
              Padding(
                padding: const EdgeInsets.only(
                    bottom: 12.0), // Adjust the value as needed
                child: Text(
                  'Alert Time',
                  style: TextStyle(color: Colors.white),
                ),
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildAlertButton('15 mins'),
                  _buildAlertButton('30 mins'),
                  _buildAlertButton('1 hour'),
                ],
              ),
            ],
            // Dependency Selector
            // Padding(
            //   padding: const EdgeInsets.only(bottom: 12.0),
            //   child:
            //       Text('Dependencies', style: TextStyle(color: Colors.white)),
            // ),
            _buildDependencySelector(),
            SizedBox(height: 20),
            // Subtasks Section
            Padding(
              padding: const EdgeInsets.only(
                  bottom: 12.0), // Adjust the value as needed
              child: Text(
                'Subtasks',
                style: TextStyle(color: Colors.white),
              ),
            ),
            ListView.builder(
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              itemCount: _subtasks.length,
              itemBuilder: (context, index) {
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: _buildSubtaskItem(index),
                );
              },
            ),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  _subtasks.add(Subtask(title: '', isDone: false));
                  _subtaskControllers.add(
                      TextEditingController()); // Add a controller for the new subtask
                });
              },
              style: ElevatedButton.styleFrom(
                primary: Colors.purpleAccent,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text('Add Subtask'),
            ),

            SizedBox(height: 20),

            // Create Task Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  if (_titleController.text.isNotEmpty) {
                    Task newTask = Task(
                      title: _titleController.text,
                      description: _descriptionController.text,
                      date: _selectedDate,
                      startTime: _startTime != null
                          ? DateTime(
                              _selectedDate.year,
                              _selectedDate.month,
                              _selectedDate.day,
                              _startTime!.hour,
                              _startTime!.minute)
                          : null,
                      endTime: _endTime != null
                          ? DateTime(
                              _selectedDate.year,
                              _selectedDate.month,
                              _selectedDate.day,
                              _endTime!.hour,
                              _endTime!.minute)
                          : null,
                      priority: _selectedPriority,
                      recurrence: _selectedRecurrence,
                      subtasks: _subtasks,
                      dependencies: _selectedDependencies,
                      getAlert: _getAlert,
                      alertTime: _selectedAlertTime,
                      isDone:
                          _isDone, // Use the state variable to retain the completion status
                    );

                    // Schedule the notification if alerts are set
                    _scheduleNotification(newTask);

                    Navigator.pop(context, newTask);
                  }
                },
                style: ElevatedButton.styleFrom(
                  primary: Colors.purpleAccent,
                  padding: EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: Text(
                  widget.task == null
                      ? 'Create Task'
                      : 'Update Task', // Change the button text dynamically
                  style: TextStyle(fontSize: 18),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // Build the subtask fields dynamically
  List<Widget> _buildSubtaskFields() {
    return List.generate(_subtaskControllers.length, (index) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8.0),
        child: TextField(
          controller: _subtaskControllers[index],
          decoration: InputDecoration(
            labelText: 'Subtask ${index + 1}',
          ),
        ),
      );
    });
  }

  // Recurrence button
  Widget _buildRecurrenceButton(String recurrence) {
    return OutlinedButton(
      onPressed: () {
        setState(() {
          _selectedRecurrence = recurrence;
        });
      },
      style: OutlinedButton.styleFrom(
        side: BorderSide(
          color: _selectedRecurrence == recurrence
              ? Colors.purpleAccent
              : Colors.grey,
        ),
        padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      child: Text(
        recurrence,
        style: TextStyle(
          color: Colors.white,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

// Function to build the dependency selector dropdown
  Widget _buildDependencySelector() {
    if (widget.allTasks.isEmpty ||
        (widget.task != null && widget.allTasks.length == 1)) {
      return SizedBox.shrink(); // Hide when no other tasks are available
    }

    // Convert the list of tasks to MultiSelectItem for the dialog field
    final taskItems = _getFilteredTaskOptions()
        .map((task) => MultiSelectItem<String>(task.title, task.title))
        .toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start, // Ensure left alignment
      children: [
        SizedBox(height: 20),
        Text('Dependencies', style: TextStyle(color: Colors.white)),
        SizedBox(height: 15),
        MultiSelectDialogField(
          items: taskItems,
          title: Text(
            "Select Dependencies",
            style: TextStyle(color: Colors.white),
          ),
          selectedColor: Colors.purpleAccent,
          decoration: BoxDecoration(
            color: Colors.grey[900],
            borderRadius: BorderRadius.all(Radius.circular(8)),
            border: Border.all(
              color: Colors.purpleAccent,
              width: 1,
            ),
          ),
          buttonIcon: Icon(
            Icons.arrow_drop_down,
            color: Colors.white,
          ),
          buttonText: Text(
            "Select Dependencies",
            style: TextStyle(
              color: Colors.white60,
              fontSize: 16,
            ),
          ),
          dialogHeight: taskItems.length <= 3
              ? taskItems.length * 50.0 // Adjust based on the number of items
              : 240.0, // Maximum height if more items
          itemsTextStyle:
              TextStyle(color: Colors.white), // Set text color to white
          initialValue:
              _selectedDependencies, // Pass current dependencies as selected
          onConfirm: (results) {
            setState(() {
              _selectedDependencies = List<String>.from(results);
            });
          },
          chipDisplay: MultiSelectChipDisplay.none(),
        ),
        SizedBox(height: 10), // Add space between dropdown and chips
        if (_selectedDependencies.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(
                left: 0.0), // Add left padding for alignment
            child: Wrap(
              spacing: 8.0, // Space between chips
              runSpacing: 8.0, // Space between lines if chips wrap
              children: _selectedDependencies.map((dep) {
                return Chip(
                  label: Text(dep, style: TextStyle(color: Colors.white)),
                  backgroundColor: Colors.purpleAccent,
                  deleteIcon: Icon(Icons.close, color: Colors.white),
                  onDeleted: () {
                    setState(() {
                      // Remove from the selected dependencies
                      _selectedDependencies.remove(dep);

                      // Sync with dropdown by confirming the updated state
                      List<String> updatedDeps =
                          List<String>.from(_selectedDependencies);
                      _selectedDependencies = updatedDeps;
                    });
                  },
                );
              }).toList(),
            ),
          ),
      ],
    );
  }

// Function to filter out tasks that would create a circular dependency
  List<Task> _getFilteredTaskOptions() {
    return widget.allTasks.where((task) {
      // Exclude the task itself and circular dependencies
      return task.title != widget.task?.title &&
          (widget.task == null ||
              !widget.task!.hasCircularDependency(task.title, widget.allTasks));
    }).toList();
  }

  Widget _buildTextField(
      {required TextEditingController controller,
      required String hintText,
      int maxLines = 1}) {
    return TextField(
      controller: controller,
      style: TextStyle(color: Colors.white),
      maxLines: maxLines,
      decoration: InputDecoration(
        hintText: hintText,
        filled: true,
        fillColor: Colors.grey[900],
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        hintStyle: TextStyle(color: Colors.white60),
      ),
    );
  }

  // Alert button
  Widget _buildAlertButton(String alertTime) {
    return OutlinedButton(
      onPressed: () {
        setState(() {
          _selectedAlertTime = alertTime;
        });
      },
      style: OutlinedButton.styleFrom(
        side: BorderSide(
          color: _selectedAlertTime == alertTime
              ? Colors.purpleAccent
              : Colors.grey,
        ),
        padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      child: Text(
        alertTime,
        style: TextStyle(
          color: Colors.white,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  // Time picker button
  Widget _buildTimePickerButton(
    BuildContext context, {
    required TimeOfDay? time,
    required bool isStartTime,
  }) {
    return GestureDetector(
      onTap: () => _selectTime(isStartTime),
      child: Container(
        padding: EdgeInsets.symmetric(vertical: 12, horizontal: 16),
        decoration: BoxDecoration(
          color: Colors.grey[900],
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              time != null ? time.format(context) : '-- : --',
              style: TextStyle(color: Colors.white),
            ),
            Icon(Icons.access_time, color: Colors.white),
          ],
        ),
      ),
    );
  }

  // Priority button
  Widget _buildPriorityButton(String priority) {
    return OutlinedButton(
      onPressed: () {
        setState(() {
          _selectedPriority = priority;
        });
      },
      style: OutlinedButton.styleFrom(
        side: BorderSide(
            color: _selectedPriority == priority
                ? Colors.purpleAccent
                : Colors.grey),
        padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      child: Text(
        priority,
        style: TextStyle(
          color: Colors.white,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

// Subtask item
  Widget _buildSubtaskItem(int index) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
      ),
      padding: EdgeInsets.only(
          left: 16,
          right: 0,
          top: 8,
          bottom: 8), // 16 on the left, 0 on the right
      child: Row(
        mainAxisAlignment:
            MainAxisAlignment.spaceBetween, // Aligns elements properly
        children: [
          Expanded(
            child: TextField(
              controller: _subtaskControllers[index],
              onChanged: (value) {
                setState(() {
                  _subtasks[index].title = value;
                });
              },
              style: TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: 'Subtask Title',
                hintStyle: TextStyle(color: Colors.white60),
                border: InputBorder.none,
              ),
            ),
          ),
          IconButton(
            padding: EdgeInsets.zero, // Removes extra padding
            icon: Icon(Icons.delete, color: Colors.redAccent),
            onPressed: () {
              setState(() {
                _subtasks.removeAt(index); // Remove the subtask
                _subtaskControllers.removeAt(index); // Remove the controller
              });
            },
          ),
        ],
      ),
    );
  }
}
