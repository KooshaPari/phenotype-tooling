import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart'; // Import fl_chart
import 'dart:math'; // Import for max function
import 'package:intl/intl.dart'; // Import intl package
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'auth_service.dart';
import 'auth_wrapper.dart';
import 'app_routes.dart';

// --- Dummy Data (Converted from JS) ---

const List<Map<String, dynamic>> dummyLogs = [
  {
    "date": "Monday, March 24, 2025",
    "mood": "3/5 (Average)",
    "energy": "2/5 (Low)",
    "symptoms": "Headache (6/10 severity)",
    "notes":
        "Slept poorly last night. Busy day at work with back-to-back meetings.",
    "tags": ["#stress", "#poor_sleep"],
    "healthData": {
      "sleep": "5.5 hours",
      "steps": "4200", // Removed comma for easier parsing
      "activeCalories": "180",
      "restingHR": "72 bpm",
    },
  },
  {
    "date": "Wednesday, March 26, 2025",
    "mood": "4/5 (Good)",
    "energy": "4/5 (Good)",
    "symptoms": "None",
    "notes": "Productive day. Took a walk during lunch break.",
    "tags": ["#good_day"],
    "healthData": {
      "sleep": "7.2 hours",
      "steps": "9100", // Removed comma
      "activeCalories": "320",
      "restingHR": "68 bpm",
    },
  },
  {
    "date": "Friday, March 28, 2025",
    "mood": "2/5 (Poor)",
    "energy": "2/5 (Low)",
    "symptoms": "Headache (7/10 severity), Fatigue (6/10)",
    "notes":
        "Skipped breakfast, worked through lunch. Headache started around 2pm.",
    "tags": ["#skipped_meals", "#headache"],
    "healthData": {
      "sleep": "6.1 hours",
      "steps": "3800", // Removed comma
      "activeCalories": "150",
      "restingHR": "74 bpm",
    },
  },
  {
    "date": "Sunday, March 30, 2025",
    "mood": "5/5 (Excellent)",
    "energy": "5/5 (High)",
    "symptoms": "None",
    "notes": "Relaxing day off. Went for a long hike.",
    "tags": ["#relax", "#exercise"],
    "healthData": {
      "sleep": "8.0 hours",
      "steps": "15300",
      "activeCalories": "550",
      "restingHR": "65 bpm",
    },
  },
  {
    "date": "Tuesday, April 1, 2025",
    "mood": "3/5 (Average)",
    "energy": "3/5 (Average)",
    "symptoms": "Slight allergy symptoms",
    "notes": "Spring allergies starting up. Otherwise okay.",
    "tags": ["#allergies"],
    "healthData": {
      "sleep": "7.5 hours",
      "steps": "6800",
      "activeCalories": "250",
      "restingHR": "70 bpm",
    },
  },
  {
    "date": "Thursday, April 3, 2025",
    "mood": "4/5 (Good)",
    "energy": "3/5 (Average)",
    "symptoms": "None",
    "notes": "Felt a bit tired but got work done. Evening walk helped.",
    "tags": ["#productive"],
    "healthData": {
      "sleep": "6.8 hours",
      "steps": "7200",
      "activeCalories": "280",
      "restingHR": "69 bpm",
    },
  },
];

// Basic HTML stripping for narrative/summary for simplicity
String _stripHtmlTags(String htmlString) {
  return htmlString
      .replaceAll(RegExp(r'<[^>]*>'), '\n') // Replace tags with newlines
      .replaceAll(
        RegExp(r'\n\s*\n'),
        '\n',
      ) // Remove multiple consecutive newlines
      .trim();
}

const String dummyNarrativeRaw = """
    <p><strong>Your Week in Review (March 24-28)</strong></p>
    <p>This week, you logged headaches on 2 days, typically rating them as moderate to severe (6-7/10). Your energy levels tended to be higher on days when you slept more than 7 hours and took more than 8,000 steps. Notably, both headache days occurred when you had fewer than 6 hours of sleep and lower physical activity. Your heart rate was also slightly elevated on these days compared to your headache-free days.</p>
    <p><strong>Pattern Spotlight: Headaches</strong></p>
    <p>Based on your recent entries, three factors appear to correlate with your headache days:</p>
    <ul>
        <li><strong>Sleep Duration:</strong> You averaged 5.8 hours of sleep on headache days vs. 7.3 hours on headache-free days.</li>
        <li><strong>Meal Patterns:</strong> You tagged "skipped meals" on 100% of headache days vs. 0% of headache-free days.</li>
        <li><strong>Physical Activity:</strong> Your step count averaged 4,000 on headache days vs. 8,500 on headache-free days.</li>
    </ul>
""";
// Extract only the "Week in Review" part for the card
final String weekInReviewText = _stripHtmlTags(
  dummyNarrativeRaw.substring(
    dummyNarrativeRaw.indexOf("<p><strong>Your Week in Review"),
    dummyNarrativeRaw.indexOf("<p><strong>Pattern Spotlight:"),
  ),
);
// Keep the full narrative for potential future use or if needed elsewhere
final String fullDummyNarrative = _stripHtmlTags(dummyNarrativeRaw);

const String dummyDoctorSummaryRaw = """
    <p><strong>Health Summary: Feb 28 - March 28</strong></p>
    <p><strong>Key Symptoms Reported:</strong></p>
    <ul>
        <li>Headaches: 8 occurrences (avg. severity 6.5/10)</li>
        <li>Fatigue: 5 occurrences (avg. severity 5/10)</li>
        <li>Digestive Issues: 3 occurrences (avg. severity 4/10)</li>
    </ul>
    <p><strong>Overall Patterns:</strong></p>
    <ul>
        <li>Headaches occurred most frequently on days following less than 6 hours of sleep (75% of instances).</li>
        <li>Headaches were reported on 80% of days with "skipped meals" tag.</li>
        <li>Higher activity levels (>7,000 steps) were associated with fewer symptoms overall.</li>
    </ul>
    <p><strong>Questions for Doctor:</strong></p>
    <ul>
        <li>Could my headaches be related to my sleep patterns?</li>
        <li>Are there specific types of physical activity you'd recommend?</li>
        <li>Should I be concerned about the correlation between meals and headaches?</li>
    </ul>
""";
// Parse the doctor summary into sections
Map<String, String> _parseDoctorSummary(String rawSummary) {
  final summary = _stripHtmlTags(rawSummary);
  final sections = <String, String>{};

  final symptomsMatch = RegExp(
    r'Key Symptoms Reported:\n(.*?)\nOverall Patterns:',
    dotAll: true,
  ).firstMatch(summary);
  if (symptomsMatch != null) {
    sections['Symptoms'] = symptomsMatch.group(1)!.trim();
  }

  final patternsMatch = RegExp(
    r'Overall Patterns:\n(.*?)\nQuestions for Doctor:',
    dotAll: true,
  ).firstMatch(summary);
  if (patternsMatch != null) {
    sections['Patterns'] = patternsMatch.group(1)!.trim();
  }

  final questionsMatch = RegExp(
    r'Questions for Doctor:\n(.*)',
    dotAll: true,
  ).firstMatch(summary);
  if (questionsMatch != null) {
    sections['Questions'] = questionsMatch.group(1)!.trim();
  }

  return sections;
}

final Map<String, String> doctorSummarySections = _parseDoctorSummary(
  dummyDoctorSummaryRaw,
);

// --- App Code ---

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    // Load .env file
    await dotenv.load();

    // Initialize AuthService
    final authService = AuthService();
    await authService.init();
  } catch (e) {
    debugPrint('Error initializing app: $e');
    // Continue execution even if initialization fails
    // The AuthWrapper will handle the error UI
  }

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'HealthSync Flutter',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: const Color(
          0xFFF4F4F4,
        ), // Match body background
        colorScheme: ColorScheme.fromSwatch().copyWith(
          primary: const Color(0xFF0056B3), // Match h1, h2 color
          secondary: Colors.blueAccent, // Placeholder
        ),
        fontFamily: 'sans-serif', // Match body font-family
        textTheme: const TextTheme(
          bodyMedium: TextStyle(
            color: Color(0xFF333333),
            height: 1.6,
          ), // Match body color and line-height
          headlineSmall: TextStyle(
            color: Color(0xFF0056B3),
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ), // Match h2 color + bold
          titleLarge: TextStyle(
            color: Color(0xFF0056B3),
            fontWeight: FontWeight.bold,
          ), // Match h1 color + bold
          titleMedium: TextStyle(
            fontWeight: FontWeight.bold,
          ), // For card titles
          bodySmall: TextStyle(color: Colors.grey), // For chart titles/axis
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF0056B3), // Use primary color for AppBar
          foregroundColor: Colors.white, // White text on AppBar
        ),
        cardTheme: CardTheme(
          // Style cards similar to sections
          color: Colors.white,
          elevation: 2.0, // Similar to box-shadow
          margin: const EdgeInsets.symmetric(
            vertical: 8.0,
            horizontal: 12.0,
          ), // Adjusted margin
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8.0),
          ),
        ),
      ),
      initialRoute: '/',
      routes: AppRoutes.getRoutes(),
      // Wrap the main app in the AuthWrapper for safe initialization
      home: AuthWrapper(
        child: Scaffold(
          appBar: AppBar(
            title: const Text('HealthSync'),
            actions: [
              // Profile button
              IconButton(
                icon: const Icon(Icons.account_circle),
                onPressed: () {
                  Navigator.pushNamed(context, '/profile');
                },
              ),
            ],
          ),
          body: const Center(
            child: Text(
              'App Initialized Successfully',
              style: TextStyle(fontSize: 18),
            ),
          ),
        ),
      ),
    );
  }
}

// Home Page (Main App UI)
class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _selectedPageIndex = 0; // Index for the selected page

  // List of pages accessible from the drawer
  final List<Widget> _pages = [
    const DailyLogView(),
    const WeeklyNarrativeView(),
    const SummaryPage(), // Summary Page
    const PatternsPage(), // Patterns Page
    const DoctorPrepView(),
    const AddRecordView(),
  ];

  // Titles corresponding to the pages
  final List<String> _pageTitles = [
    'Daily Log',
    'Weekly View',
    'Summary',
    'Patterns',
    'Doctor Prep',
    'Add Record',
  ];

  void _selectPage(int index) {
    setState(() {
      _selectedPageIndex = index;
    });
    Navigator.of(context).pop(); // Close the drawer
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_pageTitles[_selectedPageIndex]), // Dynamic title
        actions: [
          IconButton(
            icon: const Icon(Icons.account_circle),
            onPressed: () {
              Navigator.pushNamed(context, '/profile');
            },
          ),
        ],
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: <Widget>[
            DrawerHeader(
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary,
              ),
              child: const Text(
                'HealthSync Menu',
                style: TextStyle(color: Colors.white, fontSize: 24),
              ),
            ),
            for (int i = 0; i < _pages.length; i++)
              ListTile(
                leading: Icon(_getIconForPage(i)), // Add icons later
                title: Text(_pageTitles[i]),
                selected: i == _selectedPageIndex,
                onTap: () => _selectPage(i),
              ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text('Logout'),
              onTap: () {
                // Navigate back to login page
                Navigator.pushReplacementNamed(context, '/');
              },
            ),
          ],
        ),
      ),
      body: _pages[_selectedPageIndex], // Show the selected page
    );
  }

  // Helper to get icons (replace with actual icons later)
  IconData _getIconForPage(int index) {
    switch (index) {
      case 0:
        return Icons.calendar_today;
      case 1:
        return Icons.bar_chart;
      case 2:
        return Icons.insights; // Summary
      case 3:
        return Icons.pattern_detected; // Patterns
      case 4:
        return Icons.medical_services_outlined; // Doctor Prep
      case 5:
        return Icons.add_circle_outline; // Add Record
      default:
        return Icons.circle;
    }
  }
}

// These are declarations for the imported classes from other files
// This is needed because main.dart references them
class DailyLogView extends StatefulWidget {
  const DailyLogView({super.key});
  @override
  State<DailyLogView> createState() => throw UnimplementedError();
}

class WeeklyNarrativeView extends StatefulWidget {
  const WeeklyNarrativeView({super.key});
  @override
  State<WeeklyNarrativeView> createState() => throw UnimplementedError();
}

class SummaryPage extends StatelessWidget {
  const SummaryPage({super.key});
  @override
  Widget build(BuildContext context) => throw UnimplementedError();
}

class PatternsPage extends StatelessWidget {
  const PatternsPage({super.key});
  @override
  Widget build(BuildContext context) => throw UnimplementedError();
}

class DoctorPrepView extends StatelessWidget {
  const DoctorPrepView({super.key});
  @override
  Widget build(BuildContext context) => throw UnimplementedError();
}

class AddRecordView extends StatefulWidget {
  const AddRecordView({super.key});
  @override
  State<AddRecordView> createState() => throw UnimplementedError();
}
