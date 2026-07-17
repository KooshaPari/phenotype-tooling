import 'package:flutter/material.dart';
import 'auth_screen.dart';
import 'profile_page.dart';

class AppRoutes {
  static const String auth = '/';
  static const String home = '/home';
  static const String profile = '/profile';

  static Map<String, WidgetBuilder> getRoutes() {
    return {
      // auth: (context) => const AuthScreen(), // Remove '/' route - handled by MaterialApp.home
      profile: (context) => const ProfilePage(),
      // The home route should be defined in main.dart with the MyHomePage widget
    };
  }
}
