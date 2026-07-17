import 'package:flutter/material.dart';
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
  final AuthService _authService = AuthService(); // Use singleton instance
  bool _checking = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _authService.addListener(_onAuthStateChanged); // Add listener
    // Use WidgetsBinding to call async code after first frame
    WidgetsBinding.instance.addPostFrameCallback((_) {
       _checkAuthStatus();
    });
  }

  @override
  void dispose() {
    _authService.removeListener(_onAuthStateChanged); // Remove listener
    super.dispose();
  }

  // Method to trigger rebuild on auth state change
  void _onAuthStateChanged() {
    if (mounted) {
      setState(() {});
    }
  }

  Future<void> _checkAuthStatus() async {
    // Simulate a small delay to allow Auth0 SDK to potentially initialize
    await Future.delayed(const Duration(milliseconds: 200));
    
    // Check if Auth0 initialization failed (based on the internal state set during creation)
    if (!_authService.isInitialized) {
      _error = _authService.initError ?? 'Failed to initialize authentication service';
    } else {
      // Trigger the web onLoad check if needed
      await _authService.init();
    }
    
    if (mounted) {
      setState(() {
        _checking = false;
      });
    }
  }
  
  Widget _buildErrorScreen(BuildContext context) { // Pass context
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
    
    // Check if user is authenticated using the singleton instance
    return _authService.isAuthenticated() ? widget.child : const AuthScreen();
  }
}
