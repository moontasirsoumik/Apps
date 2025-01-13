import 'package:hive/hive.dart';

part 'task.g.dart'; // Hive will generate this part

@HiveType(typeId: 0)
class Task extends HiveObject {
  @HiveField(0)
  String title;

  @HiveField(1)
  String? description;

  @HiveField(2)
  DateTime? date;

  @HiveField(3)
  DateTime? startTime;

  @HiveField(4)
  DateTime? endTime;

  @HiveField(5)
  bool isDone;

  @HiveField(6)
  String priority;

  @HiveField(7)
  String category;

  @HiveField(8)
  String recurrence;

  @HiveField(9)
  List<Subtask> subtasks;

  @HiveField(10)
  List<String> dependencies;

  @HiveField(11)
  bool getAlert;

  @HiveField(12)
  String? alertTime;

  Task({
    required this.title,
    this.description,
    this.date,
    this.startTime,
    this.endTime,
    this.isDone = false,
    this.priority = 'Low',
    this.category = 'None',
    this.recurrence = 'None',
    this.subtasks = const [],
    this.dependencies = const [],
    this.getAlert = false,
    this.alertTime,
  });

  bool canBeCompleted(List<Task> allTasks) {
    for (String dependencyId in dependencies) {
      Task? dependency =
          allTasks.firstWhereOrNull((task) => task.title == dependencyId);
      if (dependency != null && !dependency.isDone) {
        return false; // Return false if a dependency is incomplete
      }
    }
    return true;
  }

  // Check if the dependency is circular
  bool hasCircularDependency(String newDependencyId, List<Task> allTasks) {
    if (newDependencyId == title) return true; // Self-dependency check

    Task? dependency =
        allTasks.firstWhereOrNull((task) => task.title == newDependencyId);
    if (dependency != null) {
      return dependency.dependencies
          .contains(title); // Circular dependency check
    }
    return false;
  }
}

@HiveType(typeId: 1)
class Subtask {
  @HiveField(0)
  String title;

  @HiveField(1)
  bool isDone;

  Subtask({required this.title, this.isDone = false});
}

extension FirstWhereOrNullExtension<E> on Iterable<E> {
  E? firstWhereOrNull(bool Function(E) test) {
    for (E element in this) {
      if (test(element)) {
        return element;
      }
    }
    return null;
  }
}
