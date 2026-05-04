import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../models/models.dart';

class ApiService {
  static String baseUrl = const String.fromEnvironment('API_BASE_URL',
      defaultValue: 'http://170.106.198.106',

  static void setBaseUrl(String url) {
    baseUrl = url;
  }

  late final Dio _dio;
  String? _accessToken;

  String? get currentToken => _accessToken;

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      headers: {
        'Content-Type': 'application/json',
      },
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (_accessToken != null) {
          options.headers['Authorization'] = 'Bearer $_accessToken';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        debugPrint('API Error: ${error.message}');
        return handler.next(error);
      },
    ));
  }

  void setToken(String? token) {
    _accessToken = token;
  }

  Future<List<News>> getNewsList({
    String? category,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final response = await _dio.get('/api/v1/news', queryParameters: {
        if (category != null) 'category': category,
        'page': page,
        'page_size': pageSize,
      });

      return (response.data as List)
          .map((json) => News.fromJson(json))
          .toList();
    } catch (e) {
      debugPrint('Error fetching news list: $e');
      return [];
    }
  }

  Future<List<News>> searchNews(String query, {int page = 1, int pageSize = 20}) async {
    try {
      final response = await _dio.get('/api/v1/news/search', queryParameters: {
        'q': query,
        'page': page,
        'page_size': pageSize,
      });

      return (response.data as List)
          .map((json) => News.fromJson(json))
          .toList();
    } catch (e) {
      debugPrint('Error searching news: $e');
      return [];
    }
  }

  Future<News?> getNewsDetail(String newsId) async {
    try {
      final response = await _dio.get('/api/v1/news/$newsId');
      return News.fromJson(response.data);
    } catch (e) {
      debugPrint('Error fetching news detail: $e');
      return null;
    }
  }

  Future<List<Category>> getCategories() async {
    try {
      final response = await _dio.get('/api/v1/categories');
      return (response.data as List)
          .map((json) => Category.fromJson(json))
          .toList();
    } catch (e) {
      debugPrint('Error fetching categories: $e');
      return [];
    }
  }

  Future<bool> register({
    String? email,
    String? phone,
    required String password,
    String? nickname,
  }) async {
    try {
      final response = await _dio.post('/api/v1/users/register', data: {
        if (email != null) 'email': email,
        if (phone != null) 'phone': phone,
        'password': password,
        if (nickname != null) 'nickname': nickname,
      });

      if (response.data['access_token'] != null) {
        _accessToken = response.data['access_token'];
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('Error registering: $e');
      return false;
    }
  }

  Future<bool> login({
    String? email,
    String? phone,
    required String password,
  }) async {
    try {
      final formData = FormData.fromMap({
        'username': email ?? phone ?? '',
        'password': password,
      });

      final response = await _dio.post(
        '/api/v1/users/login',
        data: formData,
        options: Options(contentType: Headers.formUrlEncodedContentType),
      );

      if (response.data['access_token'] != null) {
        _accessToken = response.data['access_token'];
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('Error logging in: $e');
      return false;
    }
  }

  Future<User?> getCurrentUser() async {
    try {
      final response = await _dio.get('/api/v1/users/me');
      return User.fromJson(response.data);
    } catch (e) {
      debugPrint('Error fetching current user: $e');
      return null;
    }
  }

  Future<bool> updateUserProfile({String? nickname, String? avatar}) async {
    try {
      final response = await _dio.put('/api/v1/users/me', data: {
        if (nickname != null) 'nickname': nickname,
        if (avatar != null) 'avatar': avatar,
      });
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Error updating user profile: $e');
      return false;
    }
  }

  Future<List<News>> getFavorites() async {
    try {
      final response = await _dio.get('/api/v1/users/favorites');
      return (response.data as List)
          .map((json) => News.fromJson(json))
          .toList();
    } catch (e) {
      debugPrint('Error fetching favorites: $e');
      return [];
    }
  }

  Future<bool> addFavorite(String newsId) async {
    try {
      await _dio.post('/api/v1/users/favorites/$newsId');
      return true;
    } catch (e) {
      debugPrint('Error adding favorite: $e');
      return false;
    }
  }

  Future<bool> removeFavorite(String newsId) async {
    try {
      await _dio.delete('/api/v1/users/favorites/$newsId');
      return true;
    } catch (e) {
      debugPrint('Error removing favorite: $e');
      return false;
    }
  }

  Future<bool> addHistory(String newsId) async {
    try {
      await _dio.post('/api/v1/users/history/$newsId');
      return true;
    } catch (e) {
      debugPrint('Error adding history: $e');
      return false;
    }
  }

  Future<List<Map<String, dynamic>>> getHistory({int page = 1, int pageSize = 20}) async {
    try {
      final response = await _dio.get('/api/v1/users/history', queryParameters: {
        'page': page,
        'page_size': pageSize,
      });
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      debugPrint('Error fetching history: $e');
      return [];
    }
  }
}
