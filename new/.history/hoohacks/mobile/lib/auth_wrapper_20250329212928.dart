import 'package:flutter/material.dart';
import 'package:provider/provider.dart'; // Import provider
import 'auth_service.dart';
import 'auth_screen.dart';

/// Auth wrapper to integrate auth0 with existing application
class AuthWrapper extends StatefulWidget {
  final Widget child;
  
  const AuthWrapper({super.key, required this.child});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  // REMOVE: No longer need manual instance or listeners
  // final AuthService _authService = AuthService();
  bool _checking = true;
  String? _error;
  // Keep track of the previous authentication state to detect changes
  bool _wasAuthenticated = false;

  @override
  void initState() {
    super.initState();
    // REMOVE: No longer need manual listener
    // _authService.addListener(_onAuthStateChanged);
    // Use WidgetsBinding to call async code after first frame
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _checkAuthStatus();
    });
  }

  // REMOVE: No longer need dispose for listener
  // @override
  // void dispose() {
  //   _authService.removeListener(_onAuthStateChanged); // Remove listener
  //   super.dispose();
  // }

  // REMOVE: No longer need manual rebuild trigger
  // void _onAuthStateChanged() {
  //   // Trigger a rebuild when auth state changes
  //   if (mounted) {
  //     setState(() {});
  //   }
  // }

  Future<void> _checkAuthStatus() async {
    // Access AuthService via Provider
    // Use listen: false because we only need to call init() once,
    // the build method will handle reacting to state changes.
    final authService = Provider.of<AuthService>(context, listen: false);

    // Simulate a small delay to allow Auth0 SDK to potentially initialize
    await Future.delayed(const Duration(milliseconds: 200));

    // Check if Auth0 initialization failed (based on the internal state set during creation)
    if (!authService.isInitialized) {
      _error = authService.initError ?? 'Failed to initialize authentication service';
    } else {
      // Trigger the web onLoad check if needed
      await authService.init();
    }

    if (mounted) {
      setState(() {
        _checking = false;
      });
    }
  }

  Widget _buildErrorScreen(BuildContext context) { // Pass context
    // Access AuthService via Provider if needed for retry logic
    final authService = Provider.of<AuthService>(context, listen: false);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Authentication Error'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.error_outline,
                color: Colors.red,
                size: 80,
              ),
              const SizedBox(height: 16),
              Text(
                'Authentication Configuration Error',
                style: Theme.of(context).textTheme.headlineSmall,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              Text(
                _error ?? 'Unknown error occurred',
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              const Text(
                'Please check the .env file and ensure that valid Auth0 credentials are provided.',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: () {
                  // Reset state and retry check
                  setState(() {
                    _checking = true;
                    _error = null;
                  });
                  _checkAuthStatus();
                },
                child: const Text('Retry'),
              ),
              const SizedBox(height: 16),
              TextButton(
                onPressed: () {
                  // Skip Auth0 and go to the main app - This might need adjustment
                  // depending on how you want unauthenticated access to work.
                  // For now, it navigates directly to the child widget.
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (context) => widget.child),
                  );
                },
                child: const Text('Continue Without Authentication'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Use context.watch<AuthService>() to listen for changes
    final authService = context.watch<AuthService>();
    final bool isAuthenticated = authService.isAuthenticated();

    // --- Navigation Logic ---
    // Check if the state changed from unauthenticated to authenticated
    // and we are past the initial checking phase.
    if (!_wasAuthenticated && isAuthenticated && !_checking) {
      // Schedule navigation after the current build frame to avoid errors
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) { // Ensure the widget is still in the tree
          // Replace the current route (likely AuthScreen or the callback URL view)
          // with the home route.
          Navigator.pushReplacementNamed(context, '/home');
        }
      });
    }
    // Update the previous state for the next build cycle
    _wasAuthenticated = isAuthenticated;
    // --- End Navigation Logic ---

    if (_checking) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    // Show error screen if Auth0 initialization failed (error set in _checkAuthStatus)
    if (_error != null) {
      return _buildErrorScreen(context); // Pass context
    }

    // Show error screen if Auth0 initialization failed (error set in _checkAuthStatus)
    if (_error != null) {
      return _buildErrorScreen(context); // Pass context
    }

    // Decide which screen to show based on the *current* auth state.
    // The navigation logic above handles redirecting *after* the state changes.
    // If navigation is pending, this might briefly show AuthScreen before navigating.
    // Alternatively, could return a loading indicator here while navigation is pending.
    return isAuthenticated ? widget.child : const AuthScreen();
  }
}
