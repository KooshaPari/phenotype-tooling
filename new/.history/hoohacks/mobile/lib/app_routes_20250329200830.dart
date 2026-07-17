import 'package:flutter/material.dart';
import 'auth_screen.dart';
import 'profile_page.dart';

class AppRoutes {
  static const String auth = '/';
  static const String home = '/home';
  static const String profile = '/profile';

  static Map<String, WidgetBuilder> getRoutes() {
    return {
      // auth: (context) => const AuthScreen(), // '/' is handled by MaterialApp.home -> AuthWrapper
      home: (context) => const NavBarController(), // Add route for the main authenticated view
      profile: (context) => const ProfilePage(),
    };
  }
}
