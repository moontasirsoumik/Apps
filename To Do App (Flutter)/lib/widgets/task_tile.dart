import 'package:flutter/material.dart';
import 'package:flutter_slidable/flutter_slidable.dart';
import '../models/task.dart';
import 'package:intl/intl.dart';

class DiagonalHatchPainter extends CustomPainter {
  final Color hatchColor;
  final double hatchWidth; // Control the width of the hatches here
  final double hatchSpacing;

  DiagonalHatchPainter({
    required this.hatchColor,
    this.hatchWidth = 2.0, // Reduced width for narrower hatches
    this.hatchSpacing = 6.0,
  });

  @override
  void paint(Canvas canvas, Size size) {
    var paint = Paint()
      ..color = hatchColor
      ..strokeWidth = hatchWidth; // Apply the new, narrower width here

    for (double i = -size.height;
        i < size.width + size.height;
        i += hatchSpacing) {
      canvas.drawLine(
        Offset(i, 0),
        Offset(i + size.height, size.height),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return false;
  }
}

class TaskTile extends StatefulWidget {
  final Task task;
  final VoidCallback onTaskDone;
  final Function(int subtaskIndex) onSubtaskDone;
  final VoidCallback onDelete;
  final VoidCallback onEdit;
  final VoidCallback onRecurringTaskDone;
  final VoidCallback onReactivateRecurringTask;
  final List<Task> allTasks; // Add this line to accept the list of all tasks
  final bool swipeEnabled;

  TaskTile({
    required this.task,
    required this.onTaskDone,
    required this.onSubtaskDone,
    required this.onDelete,
    required this.onEdit,
    required this.onRecurringTaskDone,
    required this.onReactivateRecurringTask,
    required this.allTasks, // Make allTasks a required parameter
    this.swipeEnabled = true,
  });

  @override
  _TaskTileState createState() => _TaskTileState();
}

class _TaskTileState extends State<TaskTile> {
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    bool isDone = widget.task.isDone;

    // Color for completed progress on the separator line
    int totalSubtasks = widget.task.subtasks.length;
    int completedSubtasks =
        widget.task.subtasks.where((subtask) => subtask.isDone).length;
    double progress =
        (totalSubtasks > 0) ? completedSubtasks / totalSubtasks : 0;

    Color progressColor = isDone
        ? Colors.grey // If the task is done, use grey
        : _getPriorityColor(
            widget.task.priority); // Use priority color if not done
    Color remainingColor = Colors.grey.shade800;

    // Colors and decorations when the task is done
    Color tileColor = isDone ? Colors.grey[800]! : Colors.grey[850]!;
    Color textColor =
        isDone ? Colors.grey : Theme.of(context).textTheme.bodyText1!.color!;
    TextDecoration textDecoration =
        isDone ? TextDecoration.lineThrough : TextDecoration.none;
    Color priorityColor = _getPriorityColor(widget.task.priority);

    return widget.swipeEnabled
        ? Slidable(
            key: Key(widget.task.title),
            actionPane: SlidableDrawerActionPane(),
            actionExtentRatio: 0.25,

            // Left to right swipe for marking as done/undone
            actions: <Widget>[
              IconSlideAction(
                caption: isDone ? 'Undo' : 'Done',
                color: isDone ? Colors.orange : Colors.green,
                icon: isDone ? Icons.undo : Icons.check,
                onTap: _handleTaskCompletion,
              ),
            ],

            // Right to left swipe for Edit and Delete
            secondaryActions: <Widget>[
              IconSlideAction(
                caption: 'Edit',
                color: Colors.blueAccent,
                icon: Icons.edit,
                onTap: widget.onEdit,
              ),
              IconSlideAction(
                caption: 'Delete',
                color: Colors.redAccent,
                icon: Icons.delete,
                onTap: widget.onDelete,
              ),
            ],

            child: _buildTaskContent(progress, progressColor, remainingColor,
                textColor, textDecoration, priorityColor),
          )
        : _buildTaskContent(
            progress,
            progressColor,
            remainingColor,
            textColor,
            textDecoration,
            priorityColor); // No sliding if swipeEnabled is false
  }

  Widget _priorityIndicator() {
    return Container(
      width: 6,
      height: double.infinity, // Ensure it takes full height of the tile
      decoration: BoxDecoration(
        color: widget.task.isDone
            ? Colors.grey
            : _getPriorityColor(widget.task.priority),
      ),
      child: widget.task.dependencies.isNotEmpty
          ? ClipRect(
              child: CustomPaint(
                painter: DiagonalHatchPainter(
                    hatchColor: Colors.black.withOpacity(0.2)),
              ),
            )
          : null,
    );
  }

  Widget _buildTaskContent(
      double progress,
      Color progressColor,
      Color remainingColor,
      Color textColor,
      TextDecoration textDecoration,
      Color priorityColor) {
    return GestureDetector(
      onTap: () {
        setState(() {
          _isExpanded = !_isExpanded;
        });
      },
      child: Column(
        mainAxisSize: MainAxisSize.min, // Ensure no extra space
        children: [
          Stack(
            children: [
              // The separator line as a progress bar
              Positioned(
                left: 6, // The width of the priority indicator
                right: 0,
                bottom: 0,
                child: AnimatedContainer(
                  duration: Duration(milliseconds: 300),
                  height: 2,
                  child: Row(
                    children: [
                      Expanded(
                        flex: (progress * 100).toInt(), // Completed portion
                        child: Container(
                            color: progressColor), // Color based on priority
                      ),
                      Expanded(
                        flex:
                            100 - (progress * 100).toInt(), // Remaining portion
                        child: Container(color: remainingColor),
                      ),
                    ],
                  ),
                ),
              ),

              Container(
                decoration: BoxDecoration(
                  border: Border(
                    bottom: BorderSide(color: Colors.grey.shade800, width: 1),
                  ), // Separation line between tiles
                ),
                child: IntrinsicHeight(
                  child: Row(
                    children: [
                      _priorityIndicator(),
                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: Column(
                            mainAxisSize:
                                MainAxisSize.min, // Ensure no extra space
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  Transform.translate(
                                    offset: Offset(0,
                                        -4), // Adjust this value to shift the text up
                                    child: Text(
                                      widget.task.title,
                                      style: TextStyle(
                                        color: textColor,
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                        height: 1.0, // Control the line height
                                        decoration: widget.task.isDone
                                            ? TextDecoration
                                                .lineThrough // Apply line-through if task is done
                                            : TextDecoration
                                                .none, // No line-through if task is not done
                                      ),
                                    ),
                                  ),
                                  Icon(
                                    widget.task.isDone
                                        ? Icons.check_circle
                                        : Icons.radio_button_unchecked,
                                    color: widget.task.isDone
                                        ? Colors
                                            .grey // Grey for completed tasks
                                        : _getPriorityColor(widget.task
                                            .priority), // Use priority color
                                    size: 24,
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Row(
                                children: [
                                  const Icon(Icons.calendar_today,
                                      color: Colors.white54, size: 16),
                                  const SizedBox(width: 5),
                                  Text(
                                    widget.task.date != null
                                        ? DateFormat('d MMM')
                                            .format(widget.task.date!)
                                        : 'No date',
                                    style: TextStyle(
                                      color: Colors.white70,
                                      decoration: widget.task.isDone
                                          ? TextDecoration.lineThrough
                                          : TextDecoration.none,
                                    ),
                                  ),
                                  if (widget.task.startTime != null &&
                                      widget.task.endTime != null)
                                    Row(
                                      children: [
                                        const SizedBox(width: 10),
                                        const Icon(Icons.access_time,
                                            color: Colors.white54, size: 16),
                                        const SizedBox(width: 5),
                                        Text(
                                          '${_formatTime(widget.task.startTime!)} - ${_formatTime(widget.task.endTime!)}',
                                          style: TextStyle(
                                            color: Colors.white70,
                                            decoration: widget.task.isDone
                                                ? TextDecoration.lineThrough
                                                : TextDecoration.none,
                                          ),
                                        ),
                                      ],
                                    ),
                                ],
                              ),
                              if (_isExpanded)
                                ..._buildExpandedContent(widget.task.isDone,
                                    textColor, textDecoration),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  List<Widget> _buildExpandedContent(
      bool isDone, Color textColor, TextDecoration textDecoration) {
    List<Widget> expandedWidgets = [];

    if (widget.task.description?.isNotEmpty ?? false) {
      expandedWidgets.add(const SizedBox(height: 10));
      expandedWidgets.add(Text(
        '${widget.task.description}',
        style: TextStyle(color: textColor, decoration: textDecoration),
      ));
    }

    if (widget.task.subtasks.isNotEmpty) {
      expandedWidgets.add(const SizedBox(height: 10));
      expandedWidgets.add(Text(
        '${widget.task.subtasks.length} Subtasks',
        style: TextStyle(
            color: textColor,
            fontWeight: FontWeight.bold,
            decoration: textDecoration),
      ));
      for (int i = 0; i < widget.task.subtasks.length; i++) {
        Subtask subtask = widget.task.subtasks[i];
        expandedWidgets.add(Padding(
          padding: EdgeInsets.zero,
          child: Row(
            children: [
              Checkbox(
                value: subtask.isDone,
                onChanged: (value) {
                  setState(() {
                    widget.onSubtaskDone(i);
                  });
                },
                activeColor: _getPriorityColor(widget.task.priority),
              ),
              Text(
                subtask.title,
                style: TextStyle(
                  color: subtask.isDone ? Colors.grey : textColor,
                  decoration: subtask.isDone
                      ? TextDecoration.lineThrough
                      : textDecoration,
                ),
              ),
            ],
          ),
        ));
      }
    }

    // Dependencies display
    if (widget.task.dependencies.isNotEmpty) {
      expandedWidgets.add(SizedBox(height: 10));
      expandedWidgets.add(Text(
        'Dependencies:',
        style: TextStyle(
          color: textColor,
          fontWeight: FontWeight.bold,
          decoration: textDecoration,
        ),
      ));
      widget.task.dependencies.forEach((dependency) {
        expandedWidgets.add(Padding(
          padding: const EdgeInsets.only(
              left: 16.0), // Indentation for visual clarity

          child: Padding(
            padding:
                const EdgeInsets.only(top: 16.0), // Adjust padding as needed
            child: Row(
              children: [
                Icon(Icons.link, color: Colors.white70, size: 16),
                SizedBox(width: 10),
                Text(
                  dependency,
                  style:
                      TextStyle(color: textColor, decoration: textDecoration),
                ),
              ],
            ),
          ),
        ));
      });
    }

    if (widget.task.recurrence.isNotEmpty) {
      expandedWidgets.add(const SizedBox(height: 10));
      expandedWidgets.add(Text(
        'Repeats: ${widget.task.recurrence}',
        style: TextStyle(color: Colors.white70, decoration: textDecoration),
      ));
    }

    return expandedWidgets;
  }

  Color _getPriorityColor(String priority) {
    switch (priority) {
      case 'High':
        return Colors.redAccent;
      case 'Medium':
        return Colors.orangeAccent;
      case 'Low':
      default:
        return Colors.greenAccent;
    }
  }

  String _formatTime(DateTime time) {
    return DateFormat('hh:mm a').format(time);
  }

  void _handleTaskCompletion() {
    if (widget.task.canBeCompleted(widget.allTasks)) {
      if (widget.task.recurrence.isEmpty || widget.task.recurrence == 'None') {
        widget.onTaskDone();
      } else {
        if (widget.task.isDone) {
          widget.onReactivateRecurringTask();
        } else {
          widget.onRecurringTaskDone();
        }
        widget.onTaskDone();
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content:
            Text('Complete all dependencies before marking this task as done!'),
      ));
    }
  }
}
