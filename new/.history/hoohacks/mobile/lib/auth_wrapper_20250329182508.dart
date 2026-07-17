import 'package:flutter/material.dart';
import 'auth_service.dart';
import 'auth_screen.dart';

/// Auth wrapper to integrate auth0 with existing application
class AuthWrapper extends StatefulWidget {
  final Widget child;
  
  const AuthWrapper({Key? key, required this.child}) : super(key: key);

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  final AuthService _authService = AuthService();
  bool _checking = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    // Simulate a small delay to initialize Auth state
    await Future.delayed(const Duration(milliseconds: 200));
    
    // Check if Auth0 initialization failed
    if (!_authService.isInitialized) {
      _error = _authService.initError ?? 'Failed to initialize authentication service';
    } else {
      await _authService.init();
    }
    
    if (mounted) {
      setState(() {
        _checking = false;
      });
    }
  }
  
  Widget _buildErrorScreen() {
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
                  // Skip Auth0 and go to the main app
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
    
    // Show error screen if Auth0 initialization failed
    if (_error != null) {
      return _buildErrorScreen();
    }
    
    // Check if user is authenticated
    return _authService.isAuthenticated() ? widget.child : const AuthScreen();
  }
}
