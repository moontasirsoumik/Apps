import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart'; // Add this import
import 'package:path_provider/path_provider.dart'; // Add this import for Hive storage
import 'models/task.dart';
import 'screens/task_list_screen.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/data/latest.dart' as tz;

// Create a notification plugin
final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
    FlutterLocalNotificationsPlugin();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Hive.initFlutter(); // Initialize Hive for Flutter
  Hive.registerAdapter(TaskAdapter()); // Register the Task adapter
  Hive.registerAdapter(SubtaskAdapter()); // Register Subtask adapter
  await Hive.openBox('tasksBox'); // Open Hive box

  tz.initializeTimeZones(); // Initialize time zones
  _initializeNotifications();

  runApp(MyApp());
}

void _initializeNotifications() async {
  const AndroidInitializationSettings initializationSettingsAndroid =
      AndroidInitializationSettings('app_icon');
  final InitializationSettings initializationSettings = InitializationSettings(
    android: initializationSettingsAndroid,
  );
  await flutterLocalNotificationsPlugin.initialize(initializationSettings);
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Not To-Do App',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: Colors.tealAccent,
        scaffoldBackgroundColor: Colors.black,
        visualDensity: VisualDensity.adaptivePlatformDensity,
        fontFamily: 'Roboto', // Force the use of system Sans-Serif
        textTheme: TextTheme(
          headline1: TextStyle(
            fontFamily: 'Roboto', // Explicitly use system Sans-Serif
            color: Colors.white,
            fontSize: 32,
            fontWeight: FontWeight.w300,
          ),
          bodyText1: TextStyle(
            fontFamily: 'Roboto', // Explicitly use system Sans-Serif
            color: Colors.white,
            fontSize: 18,
          ),
          subtitle1: TextStyle(
            fontFamily: 'Roboto', // Explicitly use system Sans-Serif
            color: Colors.white70,
            fontSize: 16,
          ),
        ),
        cardTheme: CardTheme(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          color: Colors.white.withOpacity(0.1),
          shadowColor: Colors.tealAccent.withOpacity(0.5),
          elevation: 8,
        ),
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.black87,
          elevation: 10,
          titleTextStyle: TextStyle(
            fontFamily: 'Roboto', // Explicitly use system Sans-Serif
            color: Colors.white,
            fontSize: 22,
            fontWeight: FontWeight.w300,
          ),
        ),
        floatingActionButtonTheme: FloatingActionButtonThemeData(
          backgroundColor: Colors.purpleAccent,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          elevation: 10,
        ),
      ),
      home: TaskListScreen(), // Points to your task list screen
    );
  }
}
