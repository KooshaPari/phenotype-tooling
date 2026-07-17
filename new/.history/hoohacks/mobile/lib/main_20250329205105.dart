import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:mobile/auth_service.dart';
import 'package:mobile/auth_wrapper.dart';
import 'package:mobile/app_routes.dart'; // Import for named routes
// Modified import
// Modified import
import 'package:mobile/src/components/navbar.dart'; // Modified import
import 'package:mobile/src/pages/homepage.dart'; // Modified import
import 'package:mobile/src/pages/weekly_summary.dart'; // Modified import
// Modified import
import 'package:mobile/src/pages/entry_page.dart'; // Modified import

void main() async { // Make main async
  WidgetsFlutterBinding.ensureInitialized(); // Ensure bindings are initialized

  try {
    // Load .env file
    await dotenv.load();
    
    // Initialize AuthService (using singleton pattern)
    final authService = AuthService();
    await authService.init(); // Initialize if needed (e.g., for web)
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
      debugShowCheckedModeBanner: false,
      title: 'Flutter Demo', // Will likely update this later
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      // AuthWrapper handles showing AuthScreen or the main app (NavBarController)
      home: const AuthWrapper(
        child: NavBarController(),
      ),
      initialRoute: '/', // Let AuthWrapper handle the initial screen
      routes: AppRoutes.getRoutes(), // Use named routes
    );
  }
}

class NavBarController extends StatefulWidget {
  const NavBarController({super.key});

  @override
  _NavBarControllerState createState() => _NavBarControllerState();
}

class _NavBarControllerState extends State<NavBarController> {
  int _selectedIndex = 0;

  final List<Widget> _pages = [
    const HomePage(title: 'HealthSync'),
    const WeeklySummary(),
    const EntryPage(),
  ];

  final List<String> _titles = [
    'HealthSync',
    'Weekly Summary',
    'Entries',
  ];

  void _onItemTapped(int index) {
    setState(() => _selectedIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.green,
        title: Center(
          child: Text(
            _titles[_selectedIndex],
            style: const TextStyle(
              fontSize: 24,
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          )
        ),
        leading: IconButton(
          icon: const Icon(
            Icons.menu,
            color: Colors.white,
          ),
          onPressed: () {
            // open the menu
          },
        ),
        actions: [
          IconButton(
            icon: const Icon(
              Icons.settings,
              color: Colors.white,
            ),
            onPressed: () {
              Navigator.pushNamed(context, '/profile'); // Navigate to profile page
            }
          ),
        ],
      ),
      body: _pages[_selectedIndex], // Middle page changes dynamically
      bottomNavigationBar: NavBar(
        selectedIndex: _selectedIndex,
        onItemTapped: _onItemTapped,
      ),
    );
  }
}
