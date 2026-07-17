import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart'; // Import fl_chart
import 'dart:math'; // Import for max function
import 'package:intl/intl.dart'; // Import intl package
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:auth0_flutter/auth0_flutter.dart';
import 'package:auth0_flutter/auth0_flutter_web.dart';
import 'auth_service.dart';
import 'user.dart';
import 'constants.dart';

// --- Dummy Data (Converted from JS) ---

const List<Map<String, dynamic>> dummyLogs = [
  {
    "date": "Monday, March 24, 2025",
    "mood": "3/5 (Average)",
    "energy": "2/5 (Low)",
    "symptoms": "Headache (6/10 severity)",
    "notes": "Slept poorly last night. Busy day at work with back-to-back meetings.",
    "tags": ["#stress", "#poor_sleep"],
    "healthData": {
      "sleep": "5.5 hours",
      "steps": "4200", // Removed comma for easier parsing
      "activeCalories": "180",
      "restingHR": "72 bpm"
    }
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
      "restingHR": "68 bpm"
    }
  },
  {
    "date": "Friday, March 28, 2025",
    "mood": "2/5 (Poor)",
    "energy": "2/5 (Low)",
    "symptoms": "Headache (7/10 severity), Fatigue (6/10)",
    "notes": "Skipped breakfast, worked through lunch. Headache started around 2pm.",
    "tags": ["#skipped_meals", "#headache"],
    "healthData": {
      "sleep": "6.1 hours",
      "steps": "3800", // Removed comma
      "activeCalories": "150",
      "restingHR": "74 bpm"
    }
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
      "restingHR": "65 bpm"
    }
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
      "restingHR": "70 bpm"
    }
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
      "restingHR": "69 bpm"
    }
  }
];

// Basic HTML stripping for narrative/summary for simplicity
String _stripHtmlTags(String htmlString) {
  return htmlString
      .replaceAll(RegExp(r'<[^>]*>'), '\n') // Replace tags with newlines
      .replaceAll(RegExp(r'\n\s*\n'), '\n') // Remove multiple consecutive newlines
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
        dummyNarrativeRaw.indexOf("<p><strong>Pattern Spotlight:")
    )
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

  final symptomsMatch = RegExp(r'Key Symptoms Reported:\n(.*?)\nOverall Patterns:', dotAll: true).firstMatch(summary);
  if (symptomsMatch != null) {
    sections['Symptoms'] = symptomsMatch.group(1)!.trim();
  }

  final patternsMatch = RegExp(r'Overall Patterns:\n(.*?)\nQuestions for Doctor:', dotAll: true).firstMatch(summary);
  if (patternsMatch != null) {
    sections['Patterns'] = patternsMatch.group(1)!.trim();
  }

   final questionsMatch = RegExp(r'Questions for Doctor:\n(.*)', dotAll: true).firstMatch(summary);
  if (questionsMatch != null) {
    sections['Questions'] = questionsMatch.group(1)!.trim();
  }

  return sections;
}
final Map<String, String> doctorSummarySections = _parseDoctorSummary(dummyDoctorSummaryRaw);


// --- App Code ---

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Load .env file
  await dotenv.load();
  
  // Initialize AuthService
  final authService = AuthService();
  await authService.init();

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
        scaffoldBackgroundColor: const Color(0xFFF4F4F4), // Match body background
        colorScheme: ColorScheme.fromSwatch().copyWith(
          primary: const Color(0xFF0056B3), // Match h1, h2 color
          secondary: Colors.blueAccent, // Placeholder
        ),
        fontFamily: 'sans-serif', // Match body font-family
        textTheme: const TextTheme(
          bodyMedium: TextStyle(color: Color(0xFF333333), height: 1.6), // Match body color and line-height
          headlineSmall: TextStyle(color: Color(0xFF0056B3), fontWeight: FontWeight.bold, fontSize: 18), // Match h2 color + bold
          titleLarge: TextStyle(color: Color(0xFF0056B3), fontWeight: FontWeight.bold), // Match h1 color + bold
          titleMedium: TextStyle(fontWeight: FontWeight.bold), // For card titles
          bodySmall: TextStyle(color: Colors.grey), // For chart titles/axis
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF0056B3), // Use primary color for AppBar
          foregroundColor: Colors.white, // White text on AppBar
        ),
        cardTheme: CardTheme( // Style cards similar to sections
          color: Colors.white,
          elevation: 2.0, // Similar to box-shadow
          margin: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 12.0), // Adjusted margin
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8.0),
          ),
        ),
        tabBarTheme: const TabBarTheme(
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          indicatorColor: Colors.white,
        ),
        inputDecorationTheme: InputDecorationTheme( // Consistent input decoration
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8.0),
            borderSide: BorderSide(color: Colors.grey.shade400),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8.0),
            borderSide: BorderSide(color: Theme.of(context).colorScheme.primary, width: 2.0),
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
          filled: true,
          fillColor: Colors.white,
          hintStyle: TextStyle(color: Colors.grey.shade500),
          labelStyle: TextStyle(color: Theme.of(context).colorScheme.primary),
        ),
        sliderTheme: SliderThemeData( // Style sliders
          activeTrackColor: Theme.of(context).colorScheme.primary.withOpacity(0.7),
          inactiveTrackColor: Theme.of(context).colorScheme.primary.withOpacity(0.2),
          thumbColor: Theme.of(context).colorScheme.primary,
          overlayColor: Theme.of(context).colorScheme.primary.withOpacity(0.1),
          valueIndicatorColor: Theme.of(context).colorScheme.primary,
          valueIndicatorTextStyle: const TextStyle(color: Colors.white),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData( // Style buttons
          style: ElevatedButton.styleFrom(
            backgroundColor: Theme.of(context).colorScheme.primary,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 12.0),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8.0),
            ),
            textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
        ),
      ),
      home: const AuthScreen(), // Start with Auth Screen
    );
  }
}

// --- Authentication Pages ---

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final AuthService _authService = AuthService();
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    // Check if user is already authenticated
    if (_authService.isAuthenticated()) {
      _navigateToHome();
    }
  }

  void _navigateToHome() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const MyHomePage()),
    );
  }

  Future<void> _login() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final user = await _authService.login();
      if (user != null) {
        _navigateToHome();
      } else {
        setState(() {
          _errorMessage = 'Authentication failed. Please try again.';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('HealthSync'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              'Welcome to HealthSync',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Color(0xFF0056B3),
              ),
            ),
            const SizedBox(height: 30),
            const Text(
              'Track and analyze your health patterns',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 50),
            if (_errorMessage != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 20),
                child: Text(
                  _errorMessage!,
                  style: const TextStyle(color: Colors.red),
                ),
              ),
            _isLoading
                ? const CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: _login,
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(200, 50),
                    ),
                    child: const Text('Login with Auth0'),
                  ),
          ],
        ),
      ),
    );
  }
}

// --- Profile Page ---
class ProfilePage extends StatelessWidget {
  final UserProfile? user;
  final Function() onLogout;

  const ProfilePage({
    super.key,
    required this.user,
    required this.onLogout,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Your Profile", style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 20),
          UserWidget(user: user),
          const SizedBox(height: 30),
          Center(
            child: ElevatedButton(
              onPressed: onLogout,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
              ),
              child: const Text('Logout'),
            ),
          ),
        ],
      ),
    );
  }
}

// --- Main App Screen with Drawer ---

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _selectedPageIndex = 0; // Index for the selected page
  final AuthService _authService = AuthService();

  // List of pages accessible from the drawer
  late final List<Widget> _pages;

  @override
  void initState() {
    super.initState();
    
    // Initialize pages with the ProfilePage that requires user and logout function
    _pages = [
      const DailyLogView(),
      const WeeklyNarrativeView(),
      const SummaryPage(),
      const PatternsPage(),
      const DoctorPrepView(),
      const AddRecordView(),
      ProfilePage(
        user: _authService.user,
        onLogout: _logout,
      ),
    ];
  }

  // Logout function
  Future<void> _logout() async {
    await _authService.logout();
    // Navigate back to auth screen
    if (mounted) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const AuthScreen()),
      );
    }
  }
  
  // Titles corresponding to the pages
  final List<String> _pageTitles = [
    'Daily Log',
    'Weekly View',
    'Summary',
    'Patterns',
    'Doctor Prep',
    'Add Record',
    'Profile',
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
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: <Widget>[
            DrawerHeader(
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'HealthSync Menu',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                    ),
                  ),
                  const SizedBox(height: 10),
                  if (_authService.user != null)
                    Text(
                      'Welcome, ${_authService.user!.name ?? _authService.user!.email ?? 'User'}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                      ),
                    ),
                ],
              ),
            ),
            for (int i = 0; i < _pages.length; i++)
              ListTile(
                leading: Icon(_getIconForPage(i)), // Add icons
                title: Text(_pageTitles[i]),
                selected: i == _selectedPageIndex,
                onTap: () => _selectPage(i),
              ),
          ],
        ),
      ),
      body: _pages[_selectedPageIndex], // Show the selected page
    );
  }

   // Helper to get icons
  IconData _getIconForPage(int index) {
    switch (index) {
      case 0: return Icons.calendar_today;
      case 1: return Icons.bar_chart;
      case 2: return Icons.insights; // Summary
      case 3: return Icons.pattern; // Patterns
      case 4: return Icons.medical_services_outlined; // Doctor Prep
      case 5: return Icons.add_circle_outline; // Add Record
      case 6: return Icons.person; // Profile
      default: return Icons.circle;
    }
  }
}


// --- Existing View Widgets (Now Pages) ---

class DailyLogView extends StatefulWidget {
  const DailyLogView({super.key});

  @override
  State<DailyLogView> createState() => _DailyLogViewState();
}

class _DailyLogViewState extends State<DailyLogView> {
  bool _sortAscending = false; // Default: Most recent first
  List<Map<String, dynamic>> _sortedLogs = [];

  @override
  void initState() {
    super.initState();
    _sortLogs();
  }

  void _sortLogs() {
    // Ensure intl is initialized if needed (usually not required for DateFormat)
    final DateFormat format = DateFormat("EEEE, MMMM d, yyyy"); // Format to parse dates
    List<Map<String, dynamic>> logsToSort = List.from(dummyLogs); // Create a mutable copy

    logsToSort.sort((a, b) {
      try {
        DateTime dateA = format.parse(a['date']);
        DateTime dateB = format.parse(b['date']);
        return _sortAscending ? dateA.compareTo(dateB) : dateB.compareTo(dateA);
      } catch (e) {
        // Handle potential parsing errors, maybe log them
        print("Error parsing date: $e");
        return 0; // Keep original order if parsing fails
      }
    });

    // Check if the widget is still mounted before calling setState
    if (mounted) {
      setState(() {
        _sortedLogs = logsToSort;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return Column( // Wrap ListView in a Column to add the button row easily
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              TextButton.icon(
                icon: Icon(_sortAscending ? Icons.arrow_upward : Icons.arrow_downward),
                label: Text(_sortAscending ? 'Oldest First' : 'Most Recent First'),
                onPressed: () {
                  setState(() {
                    _sortAscending = !_sortAscending;
                  });
                  _sortLogs(); // Re-sort the logs
                },
                style: TextButton.styleFrom(
                  foregroundColor: Theme.of(context).colorScheme.primary, // Use theme color
                ),
              ),
            ],
          ),
        ),
        Expanded( // Make ListView take remaining space
          child: ListView.builder(
            itemCount: _sortedLogs.length, // Count only the logs now
            itemBuilder: (context, index) {
              // No need to adjust index anymore
              final log = _sortedLogs[index];
              final healthData = log['healthData'] as Map<String, dynamic>;
              final tags = log['tags'] as List<dynamic>;

              return Card(
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(log['date'], style: textTheme.titleMedium),
                      const SizedBox(height: 8),
                      Text('Mood: ${log['mood']}'),
                      Text('Energy: ${log['energy']}'),
                      Text('Symptoms: ${log['symptoms']}'),
                      const SizedBox(height: 4),
                      Text('Notes: ${log['notes']}'),
                      const SizedBox(height: 4),
                      Text('Tags: ${tags.join(', ')}', style: const TextStyle(fontStyle: FontStyle.italic)),
                      const SizedBox(height: 8),
                      Text('Apple Health Data:', style: textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold)),
                      Padding(
                        padding: const EdgeInsets.only(left: 8.0, top: 4.0),
                        child: Text(
                          'Sleep: ${healthData['sleep']} | Steps: ${healthData['steps']} | Active Calories: ${healthData['activeCalories']} | Resting HR: ${healthData['restingHR']}',
                          style: textTheme.bodySmall,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}

// Enum for chart types
enum HealthMetric { sleep, steps, calories, hr }

// Updated WeeklyNarrativeView (Stateful)
class WeeklyNarrativeView extends StatefulWidget {
  const WeeklyNarrativeView({super.key});

  @override
  State<WeeklyNarrativeView> createState() => _WeeklyNarrativeViewState();
}

class _WeeklyNarrativeViewState extends State<WeeklyNarrativeView> {
  HealthMetric _selectedMetric = HealthMetric.sleep; // Default selection

  // Helper function to parse numeric data
  double _parseHealthData(String value) {
    final numericString = value.replaceAll(RegExp(r'[^0-9.]'), '');
    return double.tryParse(numericString) ?? 0.0;
  }

  // Helper function to get day initials
  String _getDayInitial(String dateString) {
    return dateString.substring(0, 1); // M, W, F
  }

  // Map metric enum to display string
  String _metricToString(HealthMetric metric) {
    switch (metric) {
      case HealthMetric.sleep: return "Sleep (hrs)";
      case HealthMetric.steps: return "Steps";
      case HealthMetric.calories: return "Active Cal";
      case HealthMetric.hr: return "Resting HR";
    }
  }

  // Map metric enum to data list
  List<double> _getDataForMetric(HealthMetric metric) {
     switch (metric) {
      case HealthMetric.sleep:
        return dummyLogs.map((log) => _parseHealthData(log['healthData']['sleep'])).toList();
      case HealthMetric.steps:
        return dummyLogs.map((log) => _parseHealthData(log['healthData']['steps'])).toList();
      case HealthMetric.calories:
        return dummyLogs.map((log) => _parseHealthData(log['healthData']['activeCalories'])).toList();
      case HealthMetric.hr:
        return dummyLogs.map((log) => _parseHealthData(log['healthData']['restingHR'])).toList();
    }
  }

   // Map metric enum to color
  Color _getColorForMetric(HealthMetric metric) {
     switch (metric) {
      case HealthMetric.sleep: return Colors.indigo;
      case HealthMetric.steps: return Colors.green;
      case HealthMetric.calories: return Colors.orange;
      case HealthMetric.hr: return Colors.red;
    }
  }


  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final dayInitials = dummyLogs.map((log) => _getDayInitial(log['date'])).toList();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Weekly Health Data Trends", style: textTheme.headlineSmall),
          const SizedBox(height: 16),
          // Dropdown Selector
          DropdownButtonFormField<HealthMetric>(
            value: _selectedMetric,
            decoration: const InputDecoration(
              // labelText: 'Select Metric', // Optional label
              border: OutlineInputBorder(),
              contentPadding: EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
            ),
            items: HealthMetric.values.map((HealthMetric metric) {
              return DropdownMenuItem<HealthMetric>(
                value: metric,
                child: Text(_metricToString(metric)),
              );
            }).toList(),
            onChanged: (HealthMetric? newValue) {
              if (newValue != null) {
                setState(() {
                  _selectedMetric = newValue;
                });
              }
            },
          ),
          const SizedBox(height: 20),

          // Conditionally Displayed Chart
          _WeeklyDataChart(
            title: _metricToString(_selectedMetric),
            data: _getDataForMetric(_selectedMetric),
            dayInitials: dayInitials,
            color: _getColorForMetric(_selectedMetric),
          ),

          const SizedBox(height: 24),
          // Week in Review Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: Column(
                 crossAxisAlignment: CrossAxisAlignment.start,
                 children: [
                   Text("Your Week in Review", style: textTheme.titleMedium),
                   const SizedBox(height: 8),
                   Text(
                     weekInReviewText.replaceFirst("Your Week in Review (March 24-28)", "").trim(), // Remove redundant title
                     style: textTheme.bodyMedium,
                   ),
                 ]
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// Reusable Bar Chart Widget 
class _WeeklyDataChart extends StatelessWidget {
  final String title;
  final List<double> data;
  final List<String> dayInitials;
  final Color color;

  const _WeeklyDataChart({
    required this.title,
    required this.data,
    required this.dayInitials,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final maxY = data.isEmpty ? 10.0 : data.reduce(max) * 1.2; // Add padding to max Y

    return Column(
      children: [
         SizedBox(
          height: 150, // Increased height slightly for better visibility
          child: BarChart(
            BarChartData(
              maxY: maxY,
              barTouchData: BarTouchData(enabled: false), // Disable touch interactions for simplicity
              titlesData: FlTitlesData(
                show: true,
                rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                topTitles: const AxisTitles(sideTitles: SideTitles(showT