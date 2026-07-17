import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart'; 
import 'dart:math'; 
import 'package:intl/intl.dart'; 
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:auth0_flutter/auth0_flutter.dart';
import 'package:auth0_flutter/auth0_flutter_web.dart';
import 'auth_service.dart';
import 'user.dart';
import 'constants.dart';



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
      "steps": "4200", 
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
      "steps": "9100", 
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
      "steps": "3800", 
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


String _stripHtmlTags(String htmlString) {
  return htmlString
      .replaceAll(RegExp(r'<[^>]*>'), '\n') 
      .replaceAll(RegExp(r'\n\s*\n'), '\n') 
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

final String weekInReviewText = _stripHtmlTags(
    dummyNarrativeRaw.substring(
        dummyNarrativeRaw.indexOf("<p><strong>Your Week in Review"),
        dummyNarrativeRaw.indexOf("<p><strong>Pattern Spotlight:")
    )
);

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




void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  
  await dotenv.load();
  
  
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
        scaffoldBackgroundColor: const Color(0xFFF4F4F4), 
        colorScheme: ColorScheme.fromSwatch().copyWith(
          primary: const Color(0xFF0056B3), 
          secondary: Colors.blueAccent, 
        ),
        fontFamily: 'sans-serif', 
        textTheme: const TextTheme(
          bodyMedium: TextStyle(color: Color(0xFF333333), height: 1.6), 
          headlineSmall: TextStyle(color: Color(0xFF0056B3), fontWeight: FontWeight.bold, fontSize: 18), 
          titleLarge: TextStyle(color: Color(0xFF0056B3), fontWeight: FontWeight.bold), 
          titleMedium: TextStyle(fontWeight: FontWeight.bold), 
          bodySmall: TextStyle(color: Colors.grey), 
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF0056B3), 
          foregroundColor: Colors.white, 
        ),
        cardTheme: CardTheme( 
          color: Colors.white,
          elevation: 2.0, 
          margin: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 12.0), 
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8.0),
          ),
        ),
        tabBarTheme: const TabBarTheme(
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          indicatorColor: Colors.white,
        ),
        inputDecorationTheme: InputDecorationTheme( 
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
        sliderTheme: SliderThemeData( 
          activeTrackColor: Theme.of(context).colorScheme.primary.withOpacity(0.7),
          inactiveTrackColor: Theme.of(context).colorScheme.primary.withOpacity(0.2),
          thumbColor: Theme.of(context).colorScheme.primary,
          overlayColor: Theme.of(context).colorScheme.primary.withOpacity(0.1),
          valueIndicatorColor: Theme.of(context).colorScheme.primary,
          valueIndicatorTextStyle: const TextStyle(color: Colors.white),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData( 
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
      home: const AuthScreen(), 
    );
  }
}



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



class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _selectedPageIndex = 0; 
  final AuthService _authService = AuthService();

  
  late final List<Widget> _pages;

  @override
  void initState() {
    super.initState();
    
    
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

  
  Future<void> _logout() async {
    await _authService.logout();
    
    if (mounted) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const AuthScreen()),
      );
    }
  }
  
  
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
    Navigator.of(context).pop(); 
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_pageTitles[_selectedPageIndex]), 
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
                leading: Icon(_getIconForPage(i)), 
                title: Text(_pageTitles[i]),
                selected: i == _selectedPageIndex,
                onTap: () => _selectPage(i),
              ),
          ],
        ),
      ),
      body: _pages[_selectedPageIndex], 
    );
  }

   
  IconData _getIconForPage(int index) {
    switch (index) {
      case 0: return Icons.calendar_today;
      case 1: return Icons.bar_chart;
      case 2: return Icons.insights; 
      case 3: return Icons.pattern; 
      case 4: return Icons.medical_services_outlined; 
      case 5: return Icons.add_circle_outline; 
      case 6: return Icons.person; 
      default: return Icons.circle;
    }
  }
}




class DailyLogView extends StatefulWidget {
  const DailyLogView({super.key});

  @override
  State<DailyLogView> createState() => _DailyLogViewState();
}

class _DailyLogViewState extends State<DailyLogView> {
  bool _sortAscending = false; 
  List<Map<String, dynamic>> _sortedLogs = [];

  @override
  void initState() {
    super.initState();
    _sortLogs();
  }

  void _sortLogs() {
    
    final DateFormat format = DateFormat("EEEE, MMMM d, yyyy"); 
    List<Map<String, dynamic>> logsToSort = List.from(dummyLogs); 

    logsToSort.sort((a, b) {
      try {
        DateTime dateA = format.parse(a['date']);
        DateTime dateB = format.parse(b['date']);
        return _sortAscending ? dateA.compareTo(dateB) : dateB.compareTo(dateA);
      } catch (e) {
        
        print("Error parsing date: $e");
        return 0; 
      }
    });

    
    if (mounted) {
      setState(() {
        _sortedLogs = logsToSort;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return Column( 
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
                  _sortLogs(); 
                },
                style: TextButton.styleFrom(
                  foregroundColor: Theme.of(context).colorScheme.primary, 
                ),
              ),
            ],
          ),
        ),
        Expanded( 
          child: ListView.builder(
            itemCount: _sortedLogs.length, 
            itemBuilder: (context, index) {
              
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


enum HealthMetric { sleep, steps, calories, hr }


class WeeklyNarrativeView extends StatefulWidget {
  const WeeklyNarrativeView({super.key});

  @override
  State<WeeklyNarrativeView> createState() => _WeeklyNarrativeViewState();
}

class _WeeklyNarrativeViewState extends State<WeeklyNarrativeView> {
  HealthMetric _selectedMetric = HealthMetric.sleep; 

  
  double _parseHealthData(String value) {
    final numericString = value.replaceAll(RegExp(r'[^0-9.]'), '');
    return double.tryParse(numericString) ?? 0.0;
  }

  
  String _getDayInitial(String dateString) {
    return dateString.substring(0, 1); 
  }

  
  String _metricToString(HealthMetric metric) {
    switch (metric) {
      case HealthMetric.sleep: return "Sleep (hrs)";
      case HealthMetric.steps: return "Steps";
      case HealthMetric.calories: return "Active Cal";
      case HealthMetric.hr: return "Resting HR";
    }
  }

  
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
          
          DropdownButtonFormField<HealthMetric>(
            value: _selectedMetric,
            decoration: const InputDecoration(
              
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

          
          _WeeklyDataChart(
            title: _metricToString(_selectedMetric),
            data: _getDataForMetric(_selectedMetric),
            dayInitials: dayInitials,
            color: _getColorForMetric(_selectedMetric),
          ),

          const SizedBox(height: 24),
          
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: Column(
                 crossAxisAlignment: CrossAxisAlignment.start,
                 children: [
                   Text("Your Week in Review", style: textTheme.titleMedium),
                   const SizedBox(height: 8),
                   Text(
                     weekInReviewText.replaceFirst("Your Week in Review (March 24-28)", "").trim(), 
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
    final maxY = data.isEmpty ? 10.0 : data.reduce(max) * 1.2; 

    return Column(
      children: [
         SizedBox(
          height: 150, 
          child: BarChart(
            BarChartData(
              maxY: maxY,
              barTouchData: BarTouchData(enabled: false), 
              titlesData: FlTitlesData(
                show: true,
                rightTitles: const AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
                topTitles: const AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    getTitlesWidget: (double value, TitleMeta meta) {
                      final index = value.toInt();
                      if (index >= 0 && index < dayInitials.length) {
                        return SideTitleWidget(
                          meta: meta,
                          space: 4,
                          child: Text(
                            dayInitials[index],
                            style: textTheme.bodySmall,
                          ),
                        );
                      }
                      return Container();
                    },
                    reservedSize: 18,
                  ),
                ),
                leftTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 35,
                    interval: maxY / 4 > 1 ? (maxY / 4).roundToDouble() : 1,
                    getTitlesWidget: (double value, TitleMeta meta) {
                      if (value == 0 ||
                          value == meta.max ||
                          value == meta.max / 2) {
                        if (meta.max > 0 &&
                            (value - 0).abs() < meta.max * 0.1 &&
                            value != 0)
                          return Container();
                        if (meta.max > 0 &&
                            (value - meta.max / 2).abs() < meta.max * 0.1 &&
                            value != meta.max / 2)
                          return Container();

                        return SideTitleWidget(
                          meta: meta,
                          space: 4,
                          child: Text(
                            value.toStringAsFixed(0),
                            style: textTheme.bodySmall,
                          ),
                        );
                      }
                      return Container();
                    },
                  ),
                ),
              ),
              borderData: FlBorderData(show: false),
              gridData: FlGridData(
                show: true,
                drawVerticalLine: false,
                horizontalInterval:
                    maxY / 4 > 1 ? (maxY / 4).roundToDouble() : 1,
                getDrawingHorizontalLine: (value) {
                  return FlLine(
                    color: Colors.grey.withOpacity(0.3),
                    strokeWidth: 1,
                  );
                },
              ),
              barGroups: List.generate(data.length, (index) {
                return BarChartGroupData(
                  x: index,
                  barRods: [
                    BarChartRodData(
                      toY: data[index],
                      color: color,
                      width: 16,
                      borderRadius: const BorderRadius.only(
                        topLeft: Radius.circular(4),
                        topRight: Radius.circular(4),
                      ),
                    ),
                  ],
                );
              }),
            ),
          ),
        ),
      ],
    );
  }
}


class PatternsPage extends StatelessWidget {
  const PatternsPage({super.key});

  
  List<String> _extractPatterns(String rawNarrative) {
    final patternsSectionStart = rawNarrative.indexOf(
      "<p><strong>Pattern Spotlight:",
    );
    if (patternsSectionStart == -1) return [];

    
    final ulStart = rawNarrative.indexOf("<ul>", patternsSectionStart);
    if (ulStart == -1) return [];

    
    final patternsSectionEnd = rawNarrative.indexOf("</ul>", ulStart);
    if (patternsSectionEnd == -1) return [];

    
    final patternsHtml = rawNarrative.substring(
      ulStart + 4,
      patternsSectionEnd,
    ); 
    final listItemsHtml = RegExp(
      r'<li>(.*?)</li>',
      dotAll: true,
    ).allMatches(patternsHtml);

    return listItemsHtml
        .map((match) {
          
          return _stripHtmlTags(match.group(1) ?? '').trim();
        })
        .where((pattern) => pattern.isNotEmpty)
        .toList(); 
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final patterns = _extractPatterns(dummyNarrativeRaw);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Potential Health Patterns", style: textTheme.headlineSmall),
          const SizedBox(height: 16),
          if (patterns.isEmpty)
            Card(
              
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Center(
                  child: Text(
                    "No patterns identified yet.",
                    style: textTheme.bodyMedium,
                  ),
                ),
              ),
            )
          else
            ListView.builder(
              shrinkWrap: true, 
              physics:
                  const NeverScrollableScrollPhysics(), 
              itemCount: patterns.length,
              itemBuilder: (context, index) {
                final pattern = patterns[index];
                
                final parts = pattern.split(':');
                
                final title =
                    parts.length > 1
                        ? parts[0]
                            .trim()
                            .replaceAll('<strong>', '')
                            .replaceAll('</strong>', '')
                        : 'Pattern ${index + 1}';
                final description =
                    parts.length > 1
                        ? parts.sublist(1).join(':').trim()
                        : pattern;

                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(title, style: textTheme.titleMedium),
                        const SizedBox(height: 8),
                        Text(description, style: textTheme.bodyMedium),
                      ],
                    ),
                  ),
                );
              },
            ),
        ],
      ),
    );
  }
}


class SummaryPage extends StatelessWidget {
  const SummaryPage({super.key});

  
  double _parseHealthData(String value) {
    
    if (value.contains('/')) {
      final parts = value.split('/');
      return double.tryParse(parts[0]) ?? 0.0;
    }
    
    final numericString = value.replaceAll(RegExp(r'[^0-9.]'), '');
    return double.tryParse(numericString) ?? 0.0;
  }

  
  List<FlSpot> _getSpotsForMetric(String metricKey) {
    List<FlSpot> spots = [];
    final DateFormat format = DateFormat("EEEE, MMMM d, yyyy");
    
    List<Map<String, dynamic>> sortedLogs = List.from(dummyLogs);
    sortedLogs.sort((a, b) {
      try {
        return format.parse(a['date']).compareTo(format.parse(b['date']));
      } catch (e) {
        return 0;
      }
    });

    for (int i = 0; i < sortedLogs.length; i++) {
      final log = sortedLogs[i];
      double yValue;
      if (metricKey == 'mood' || metricKey == 'energy') {
        yValue = _parseHealthData(log[metricKey]);
      } else if (log['healthData'] != null &&
          log['healthData'][metricKey] != null) {
        
        yValue = _parseHealthData(log['healthData'][metricKey]);
      } else {
        yValue = 0.0; 
      }
      spots.add(FlSpot(i.toDouble(), yValue)); 
    }
    return spots;
  }

  
  Widget _bottomTitleWidgets(double value, TitleMeta meta, int totalLogs) {
    const style = TextStyle(
      color: Colors.grey,
      fontWeight: FontWeight.bold,
      fontSize: 10,
    );
    String text = '';
    
    int interval = (totalLogs / 3).ceil().clamp(
      1,
      totalLogs,
    ); 
    if (value.toInt() % interval == 0 && value.toInt() < totalLogs) {
      try {
        
        List<Map<String, dynamic>> sortedLogs = List.from(dummyLogs);
        final DateFormat format = DateFormat("EEEE, MMMM d, yyyy");
        sortedLogs.sort(
          (a, b) => format.parse(a['date']).compareTo(format.parse(b['date'])),
        );
        
        if (value.toInt() >= 0 && value.toInt() < sortedLogs.length) {
          DateTime date = format.parse(sortedLogs[value.toInt()]['date']);
          text = DateFormat.Md().format(date); 
        }
      } catch (e) {
        text = '';
        print("Error formatting date label: $e");
      }
    }

    
    return SideTitleWidget(
      meta: meta,
      space: 4,
      child: Text(text, style: style),
    );
  }

  
  Widget _leftTitleWidgets(double value, TitleMeta meta) {
    const style = TextStyle(
      color: Colors.grey,
      fontWeight: FontWeight.bold,
      fontSize: 10,
    );
    
    double interval = ((meta.max - meta.min) / 4).clamp(1.0, double.infinity);
    
    if (value == meta.min ||
        value == meta.max ||
        (value > meta.min &&
            value < meta.max &&
            ((value - meta.min) % interval < 1 ||
                (meta.max - value) % interval < 1))) {
      
      if (meta.max <= 5 && value != meta.min && value != meta.max) {
        
        if ((value - (meta.min + meta.max) / 2).abs() > 0.1) return Container();
      }
      
      return SideTitleWidget(
        meta: meta,
        space: 4,
        child: Text(
          value.toInt().toString(),
          style: style,
        ), 
      );
    }
    return Container();
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final moodSpots = _getSpotsForMetric('mood');
    final energySpots = _getSpotsForMetric('energy');
    final sleepSpots = _getSpotsForMetric('sleep');
    final stepsSpots = _getSpotsForMetric('steps');
    final totalLogs = dummyLogs.length; 

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Health Summary Trends", style: textTheme.headlineSmall),
          const SizedBox(height: 24),

          _buildChartCard(
            context: context,
            title: "Mood (1-5)",
            spots: moodSpots,
            color: Colors.blue,
            minY: 1,
            maxY: 5, 
            totalLogs: totalLogs,
          ),
          const SizedBox(height: 16),
          _buildChartCard(
            context: context,
            title: "Energy (1-5)",
            spots: energySpots,
            color: Colors.orange,
            minY: 1,
            maxY: 5, 
            totalLogs: totalLogs,
          ),
          const SizedBox(height: 16),
          _buildChartCard(
            context: context,
            title: "Sleep (Hours)",
            spots: sleepSpots,
            color: Colors.indigo,
            minY: 0, 
            totalLogs: totalLogs,
          ),
          const SizedBox(height: 16),
          _buildChartCard(
            context: context,
            title: "Steps",
            spots: stepsSpots,
            color: Colors.green,
            minY: 0, 
            totalLogs: totalLogs,
          ),
        ],
      ),
    );
  }

  
  Widget _buildChartCard({
    required BuildContext context,
    required String title,
    required List<FlSpot> spots,
    required Color color,
    required int totalLogs,
    double? minY, 
    double? maxY,
  }) {
    final textTheme = Theme.of(context).textTheme;
    
    final calculatedMinY =
        minY ?? (spots.isEmpty ? 0 : spots.map((s) => s.y).reduce(min) * 0.8);
    final calculatedMaxY =
        maxY ?? (spots.isEmpty ? 10 : spots.map((s) => s.y).reduce(max) * 1.2);
    final finalMinY =
        calculatedMinY > calculatedMaxY
            ? calculatedMaxY - 1
            : calculatedMinY; 
    final finalMaxY =
        calculatedMaxY < finalMinY
            ? finalMinY + 1
            : calculatedMaxY; 
    final interval = ((finalMaxY - finalMinY) / 4).clamp(
      1.0,
      double.infinity,
    ); 

    return Card(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(
          16.0,
          16.0,
          16.0,
          8.0,
        ), 
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(title, style: textTheme.titleMedium),
            const SizedBox(height: 20), 
            SizedBox(
              height: 150,
              child:
                  spots.isEmpty
                      ? Center(
                        child: Text(
                          "No data available",
                          style: textTheme.bodySmall,
                        ),
                      )
                      : LineChart(
                        LineChartData(
                          minY: finalMinY,
                          maxY: finalMaxY,
                          gridData: FlGridData(
                            show: true,
                            drawVerticalLine: false,
                            horizontalInterval: interval,
                            getDrawingHorizontalLine:
                                (value) => FlLine(
                                  color: Colors.grey.withOpacity(0.3),
                                  strokeWidth: 1,
                                ),
                          ),
                          titlesData: FlTitlesData(
                            show: true,
                            rightTitles: const AxisTitles(
                              sideTitles: SideTitles(showTitles: false),
                            ),
                            topTitles: const AxisTitles(
                              sideTitles: SideTitles(showTitles: false),
                            ),
                            bottomTitles: AxisTitles(
                              sideTitles: SideTitles(
                                showTitles: true,
                                reservedSize: 22,
                                interval: 1,
                                getTitlesWidget:
                                    (value, meta) => _bottomTitleWidgets(
                                      value,
                                      meta,
                                      totalLogs,
                                    ),
                              ),
                            ),
                            leftTitles: AxisTitles(
                              sideTitles: SideTitles(
                                showTitles: true,
                                reservedSize: 28,
                                interval: interval,
                                getTitlesWidget: _leftTitleWidgets,
                              ),
                            ),
                          ),
                          borderData: FlBorderData(show: false),
                          lineBarsData: [
                            LineChartBarData(
                              spots: spots,
                              isCurved: true,
                              color: color,
                              barWidth: 3,
                              isStrokeCapRound: true,
                              dotData: const FlDotData(show: false),
                              belowBarData: BarAreaData(
                                show: true,
                                color: color.withOpacity(0.2),
                              ),
                            ),
                          ],
                        ),
                      ),
            ),
          ],
        ),
      ),
    );
  }
}

class DoctorPrepView extends StatelessWidget {
  const DoctorPrepView({super.key});

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Doctor Visit Preparation", style: textTheme.headlineSmall),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text("Key Symptoms Reported", style: textTheme.titleMedium),
                  const SizedBox(height: 8),
                  Text(
                    doctorSummarySections['Symptoms'] ??
                        'No symptom data available.',
                    style: textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text("Overall Patterns", style: textTheme.titleMedium),
                  const SizedBox(height: 8),
                  Text(
                    doctorSummarySections['Patterns'] ??
                        'No pattern data available.',
                    style: textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text("Questions for Doctor", style: textTheme.titleMedium),
                  const SizedBox(height: 8),
                  Text(
                    doctorSummarySections['Questions'] ??
                        'No questions generated.',
                    style: textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}



class AddRecordView extends StatefulWidget {
  const AddRecordView({super.key});

  @override
  State<AddRecordView> createState() => _AddRecordViewState();
}

class _AddRecordViewState extends State<AddRecordView> {
  double _moodValue = 3.0;
  double _energyValue = 3.0;
  final _symptomsController = TextEditingController();
  final _notesController = TextEditingController();
  final _tagsController = TextEditingController();
  final _formKey = GlobalKey<FormState>(); 

  @override
  void dispose() {
    _symptomsController.dispose();
    _notesController.dispose();
    _tagsController.dispose();
    super.dispose();
  }

  void _submitForm() {
    
    
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Record Saved (Simulated)')));

    
    setState(() {
      _moodValue = 3.0;
      _energyValue = 3.0;
      _symptomsController.clear();
      _notesController.clear();
      _tagsController.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final inputDecorationTheme = Theme.of(context).inputDecorationTheme;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Form(
        
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("New Entry", style: textTheme.headlineSmall),
            Text(
              "How are you feeling today?",
              style: textTheme.bodyMedium?.copyWith(color: Colors.grey[700]),
            ),
            const SizedBox(height: 24),

            
            Text(
              "Mood (1-5): ${_moodValue.toInt()}",
              style: textTheme.titleMedium,
            ),
            Slider(
              value: _moodValue,
              min: 1,
              max: 5,
              divisions: 4,
              label: _moodValue.toInt().toString(),
              onChanged: (value) {
                setState(() {
                  _moodValue = value;
                });
              },
            ),
            const Row(
              
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [Text("1 (Poor)"), Text("5 (Excellent)")],
            ),
            const SizedBox(height: 24),

            
            Text(
              "Energy Level (1-5): ${_energyValue.toInt()}",
              style: textTheme.titleMedium,
            ),
            Slider(
              value: _energyValue,
              min: 1,
              max: 5,
              divisions: 4,
              label: _energyValue.toInt().toString(),
              onChanged: (value) {
                setState(() {
                  _energyValue = value;
                });
              },
            ),
            const Row(
              
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [Text("1 (Low)"), Text("5 (High)")],
            ),
            const SizedBox(height: 24),

            
            Text("Symptoms", style: textTheme.titleMedium),
            const SizedBox(height: 8),
            TextFormField(
              controller: _symptomsController,
              decoration: const InputDecoration(
                
                hintText: "Headache:7, Fatigue:5",
                helperText: "Format: Symptom:Severity, e.g., \"Headache:7\"",
                
              ),
              keyboardType: TextInputType.text,
            ),
            const SizedBox(height: 24),

            
            Text("Notes", style: textTheme.titleMedium),
            const SizedBox(height: 8),
            TextFormField(
              controller: _notesController,
              decoration: const InputDecoration(
                
                hintText: "How was your day? Any notable events or feelings?",
                
              ),
              keyboardType: TextInputType.multiline,
              maxLines: 3,
            ),
            const SizedBox(height: 24),

            
            Text("Tags", style: textTheme.titleMedium),
            const SizedBox(height: 8),
            TextFormField(
              controller: _tagsController,
              decoration: const InputDecoration(
                
                hintText: "stress poor_sleep skipped_meals",
                helperText:
                    "Space or comma separated, e.g., \"stress poor_sleep\"",
                
              ),
              keyboardType: TextInputType.text,
            ),
            const SizedBox(height: 32),

            
            Center(
              
              child: ElevatedButton(
                onPressed: _submitForm,
                child: const Text("Save Entry"),
              ),
            ),
            const SizedBox(height: 16), 
          ],
        ),
      ),
    );
  }
}
