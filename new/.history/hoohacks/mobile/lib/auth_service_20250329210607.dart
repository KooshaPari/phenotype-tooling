import 'package:auth0_flutter/auth0_flutter.dart';
import 'package:auth0_flutter/auth0_flutter_web.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter/material.dart'; // Import needed for ChangeNotifier

class AuthService with ChangeNotifier {
  // Add 'with ChangeNotifier'
  static final AuthService _instance = AuthService._internal();

  Auth0? auth0;
  Auth0Web? auth0Web;
  UserProfile? _user;
  bool _isInitialized = false;
  String? _initError;

  // Singleton pattern
  factory AuthService() {
    return _instance;
  }

  AuthService._internal() {
    _initializeAuth0();
  }

  void _initializeAuth0() {
    try {
      final domain = dotenv.env['AUTH0_DOMAIN'];
      final clientId = dotenv.env['AUTH0_CLIENT_ID'];

      if (domain == null ||
          domain.isEmpty ||
          clientId == null ||
          clientId.isEmpty) {
        _initError = 'Auth0 credentials are missing or invalid in .env file';
        _isInitialized = false;
        debugPrint('AuthService Error: $_initError');
        return;
      }

      auth0 = Auth0(domain, clientId);
      auth0Web = Auth0Web(domain, clientId);
      _isInitialized = true;
      _initError = null;
    } catch (e) {
      _initError = 'Failed to initialize Auth0: $e';
      _isInitialized = false;
      debugPrint('AuthService Error: $_initError');
    }
  }

  UserProfile? get user => _user;
  bool get isInitialized => _isInitialized;
  String? get initError => _initError;

  Future<void> init() async {
    if (!_isInitialized) {
      debugPrint(
        'AuthService Warning: Attempting to use init() when not properly initialized',
      );
      return;
    }

    try {
      if (kIsWeb) {
        final credentials = await auth0Web!.onLoad();
        _user = credentials?.user;
      }
    } catch (e) {
      debugPrint('Auth0 initialization error: $e');
    }
  }

  Future<UserProfile?> login() async {
    if (!_isInitialized) {
      debugPrint(
        'AuthService Warning: Attempting to use login() when not properly initialized',
      );
      return null;
    }

    try {
      if (kIsWeb) {
        await auth0Web!.loginWithRedirect(redirectUrl: 'http://localhost:3000');
        return _user;
      }

      final scheme = dotenv.env['AUTH0_CUSTOM_SCHEME'];
      if (scheme == null || scheme.isEmpty) {
        debugPrint(
          'AuthService Error: AUTH0_CUSTOM_SCHEME is missing or invalid in .env file',
        );
        return null;
      }

      // Diagnostic: Add a small delay before calling webAuthentication
      await Future.delayed(const Duration(milliseconds: 500));

      final credentials = await auth0!
          .webAuthentication(scheme: scheme)
          // Use a Universal Link callback URL on iOS 17.4+ / macOS 14.4+
          // useHTTPS is ignored on Android
          .login(useHTTPS: true);

      _user = credentials.user;
      return _user;
    } catch (e) {
      debugPrint('Login error: $e');
      return null;
    }
  }

  Future<void> logout() async {
    if (!_isInitialized) {
      debugPrint(
        'AuthService Warning: Attempting to use logout() when not properly initialized',
      );
      return;
    }

    try {
      if (kIsWeb) {
        await auth0Web!.logout(returnToUrl: 'http://localhost:3000');
      } else {
        final scheme = dotenv.env['AUTH0_CUSTOM_SCHEME'];
        if (scheme == null || scheme.isEmpty) {
          debugPrint(
            'AuthService Error: AUTH0_CUSTOM_SCHEME is missing or invalid in .env file',
          );
          return;
        }

        await auth0!
            .webAuthentication(scheme: scheme)
            // Use a Universal Link logout URL on iOS 17.4+ / macOS 14.4+
            // useHTTPS is ignored on Android
            .logout(useHTTPS: true);
      }
      _user = null;
    } catch (e) {
      debugPrint('Logout error: $e');
    }
  }

  bool isAuthenticated() {
    return _user != null;
  }
}
