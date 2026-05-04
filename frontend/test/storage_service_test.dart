import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:ai_news_app/frontend/lib/services/storage_service.dart';

void main() {
  group('StorageService', () {
    late StorageService storageService;

    setUp(() async {
      SharedPreferences.setMockInitialValues({});
      final prefs = await SharedPreferences.getInstance();
      storageService = StorageService(prefs);
    });

    test('save and retrieve token', () async {
      await storageService.saveToken('test_token_123');
      expect(storageService.getToken(), 'test_token_123');
    });

    test('remove token', () async {
      await storageService.saveToken('test_token');
      await storageService.removeToken();
      expect(storageService.getToken(), isNull);
    });

    test('save and retrieve user id', () async {
      await storageService.saveUserId('user_123');
      expect(storageService.getUserId(), 'user_123');
    });

    test('remove user id', () async {
      await storageService.saveUserId('user_123');
      await storageService.removeUserId();
      expect(storageService.getUserId(), isNull);
    });

    test('save and retrieve theme mode', () async {
      await storageService.setThemeMode('dark');
      expect(storageService.getThemeMode(), 'dark');
    });

    test('default theme mode is system', () {
      expect(storageService.getThemeMode(), 'system');
    });

    test('save and retrieve notifications enabled', () async {
      await storageService.setNotificationsEnabled(false);
      expect(storageService.getNotificationsEnabled(), false);
    });

    test('default notifications enabled is true', () {
      expect(storageService.getNotificationsEnabled(), true);
    });

    test('clearAll removes all data', () async {
      await storageService.saveToken('token');
      await storageService.saveUserId('user_id');
      await storageService.setThemeMode('dark');
      await storageService.clearAll();
      expect(storageService.getToken(), isNull);
      expect(storageService.getUserId(), isNull);
      expect(storageService.getThemeMode(), 'system');
    });
  });
}
