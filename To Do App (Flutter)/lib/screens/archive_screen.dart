import 'package:flutter/material.dart';
import '../models/task.dart';
import '../widgets/task_tile.dart';
import 'add_task_screen.dart'; // Ensure this import is correct for your project structure

class ArchiveScreen extends StatefulWidget {
  final List<Task> archivedTasks;
  final List<Task> activeTasks; // New field to hold active tasks

  ArchiveScreen({required this.archivedTasks, required this.activeTasks});

  @override
  _ArchiveScreenState createState() => _ArchiveScreenState();
}

class _ArchiveScreenState extends State<ArchiveScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Archived Tasks'),
      ),
      body: widget.archivedTasks.isEmpty
          ? Center(
              child: Text(
                'No archived tasks',
                style: TextStyle(fontSize: 18, color: Colors.white70),
              ),
            )
          : ListView.builder(
              padding: EdgeInsets.zero,
              itemCount: widget.archivedTasks.length,
              itemBuilder: (context, index) {
                return Padding(
                  padding: EdgeInsets.zero,
                  child: TaskTile(
                    task: widget.archivedTasks[index],
                    onTaskDone: () {
                      setState(() {
                        // Toggle the task's done state
                        widget.archivedTasks[index].isDone =
                            !widget.archivedTasks[index].isDone;
                      });
                    },

                    onSubtaskDone: (_) {}, // No action for subtasks here
                    onDelete: () {
                      setState(() {
                        widget.archivedTasks.removeAt(index); // Delete the task
                      });
                    },
                    onEdit: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => AddTaskScreen(
                            task: widget.archivedTasks[index],
                            allTasks: widget.activeTasks +
                                widget
                                    .archivedTasks, // Pass both active and archived tasks
                          ),
                        ),
                      ).then((updatedTask) {
                        if (updatedTask != null) {
                          setState(() {
                            // Check if the task date is today or in the future
                            DateTime today = DateTime(
                                DateTime.now().year,
                                DateTime.now().month,
                                DateTime.now()
                                    .day); // Strip time from the current date

                            if (updatedTask.date != null &&
                                    updatedTask.date!.isAfter(today) ||
                                updatedTask.date!.isAtSameMomentAs(today)) {
                              widget.archivedTasks
                                  .removeAt(index); // Remove from archive
                              widget.activeTasks
                                  .add(updatedTask); // Add to active tasks
                            } else {
                              // If the task remains in the past, just update it
                              widget.archivedTasks[index] = updatedTask;
                            }
                          });
                        }
                      });
                    },

                    onRecurringTaskDone: () {}, // Empty callback
                    onReactivateRecurringTask: () {}, // Empty callback
                    swipeEnabled: true, // Allow swiping in the archive screen
                    allTasks: widget.archivedTasks,
                  ),
                );
              },
            ),
    );
  }
}
