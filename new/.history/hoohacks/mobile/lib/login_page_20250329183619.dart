import 'package:flutter/material.dart';
import 'auth_service.dart';
// Import HomePage if it exists, otherwise create a placeholder later
// import 'home_page.dart'; 

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final AuthService _authService = AuthService();
  bool _isLoading = false;

  Future<void> _login() async {
    setState(() {
      _isLoading = true;
    });

    final user = await _authService.login();

    setState(() {
      _isLoading = false;
    });

    if (user != null && mounted) {
      // Navigate to HomePage - Placeholder for now
      // Navigator.pushReplacement(
      //   context,
      //   MaterialPageRoute(builder: (context) => const HomePage()),
      // );
       ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Login Successful: ${user.name}')),
      );
       debugPrint("Login Successful: ${user.name}"); // Add debug print
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Login failed')),
      );
       debugPrint("Login Failed"); // Add debug print
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Login'),
      ),
      body: Center(
        child: _isLoading
            ? const CircularProgressIndicator()
            : ElevatedButton(
                onPressed: _login,
                child: const Text('Log In / Sign Up'),
              ),
      ),
    );
  }
}
