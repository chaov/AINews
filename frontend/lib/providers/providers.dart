import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/models.dart';
import '../services/services.dart';
import '../services/storage_service.dart';

final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService();
});

final storageServiceProvider = Provider<StorageService>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return StorageService(prefs);
});

final themeModeProvider = StateNotifierProvider<ThemeModeNotifier, ThemeMode>((ref) {
  return ThemeModeNotifier(ref.read(storageServiceProvider));
});

class ThemeModeNotifier extends StateNotifier<ThemeMode> {
  final StorageService _storageService;

  ThemeModeNotifier(this._storageService) : super(ThemeMode.system) {
    _loadTheme();
  }

  void _loadTheme() {
    final mode = _storageService.getThemeMode();
    state = _parseMode(mode);
  }

  ThemeMode _parseMode(String mode) {
    switch (mode) {
      case 'light':
        return ThemeMode.light;
      case 'dark':
        return ThemeMode.dark;
      default:
        return ThemeMode.system;
    }
  }

  Future<void> setThemeMode(String mode) async {
    await _storageService.setThemeMode(mode);
    state = _parseMode(mode);
  }
}

final newsListProvider = StateNotifierProvider<NewsListNotifier, AsyncValue<List<News>>>((ref) {
  return NewsListNotifier(ref.read(apiServiceProvider));
});

class NewsListNotifier extends StateNotifier<AsyncValue<List<News>>> {
  final ApiService _apiService;
  int _currentPage = 1;
  bool _hasMore = true;
  String? _currentCategory;

  NewsListNotifier(this._apiService) : super(const AsyncValue.loading()) {
    loadNews();
  }

  bool get hasMore => _hasMore;

  Future<void> loadNews({String? category, bool refresh = false}) async {
    if (refresh) {
      _currentPage = 1;
      _hasMore = true;
      _currentCategory = category;
    }

    try {
      final news = await _apiService.getNewsList(
        category: category ?? _currentCategory,
        page: _currentPage,
      );
      _hasMore = news.length >= 20;
      if (refresh || _currentPage == 1) {
        state = AsyncValue.data(news);
      } else {
        final current = state.value ?? [];
        state = AsyncValue.data([...current, ...news]);
      }
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> loadMore() async {
    if (!_hasMore) return;
    _currentPage++;
    await loadNews(category: _currentCategory);
  }

  Future<void> refresh({String? category}) async {
    await loadNews(category: category, refresh: true);
  }
}

final categoryProvider = StateNotifierProvider<CategoryNotifier, AsyncValue<List<Category>>>((ref) {
  return CategoryNotifier(ref.read(apiServiceProvider));
});

class CategoryNotifier extends StateNotifier<AsyncValue<List<Category>>> {
  final ApiService _apiService;

  CategoryNotifier(this._apiService) : super(const AsyncValue.loading()) {
    loadCategories();
  }

  Future<void> loadCategories() async {
    try {
      final categories = await _apiService.getCategories();
      state = AsyncValue.data(categories);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}

final selectedCategoryProvider = StateProvider<String?>((ref) => null);

final newsDetailProvider = FutureProvider.family<News?, String>((ref, newsId) async {
  final apiService = ref.read(apiServiceProvider);
  return await apiService.getNewsDetail(newsId);
});

final searchNewsProvider = StateNotifierProvider<SearchNewsNotifier, AsyncValue<List<News>>>((ref) {
  return SearchNewsNotifier(ref.read(apiServiceProvider));
});

class SearchNewsNotifier extends StateNotifier<AsyncValue<List<News>>> {
  final ApiService _apiService;

  SearchNewsNotifier(this._apiService) : super(const AsyncValue.data([]));

  Future<void> search(String query) async {
    if (query.isEmpty) {
      state = const AsyncValue.data([]);
      return;
    }

    state = const AsyncValue.loading();
    try {
      final results = await _apiService.searchNews(query);
      state = AsyncValue.data(results);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  void clear() {
    state = const AsyncValue.data([]);
  }
}

final favoritesProvider = StateNotifierProvider<FavoritesNotifier, AsyncValue<List<News>>>((ref) {
  return FavoritesNotifier(ref.read(apiServiceProvider));
});

class FavoritesNotifier extends StateNotifier<AsyncValue<List<News>>> {
  final ApiService _apiService;

  FavoritesNotifier(this._apiService) : super(const AsyncValue.data([]));

  Future<void> loadFavorites() async {
    state = const AsyncValue.loading();
    try {
      final favorites = await _apiService.getFavorites();
      state = AsyncValue.data(favorites);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> addFavorite(String newsId) async {
    final success = await _apiService.addFavorite(newsId);
    if (success) {
      await loadFavorites();
    }
  }

  Future<void> removeFavorite(String newsId) async {
    final success = await _apiService.removeFavorite(newsId);
    if (success) {
      await loadFavorites();
    }
  }
}

final historyProvider = StateNotifierProvider<HistoryNotifier, AsyncValue<List<HistoryItem>>>>((ref) {
  return HistoryNotifier(ref.read(apiServiceProvider));
});

class HistoryNotifier extends StateNotifier<AsyncValue<List<HistoryItem>>> {
  final ApiService _apiService;
  int _currentPage = 1;
  bool _hasMore = true;

  HistoryNotifier(this._apiService) : super(const AsyncValue.data([]));

  bool get hasMore => _hasMore;

  Future<void> loadHistory({bool refresh = false}) async {
    if (refresh) {
      _currentPage = 1;
      _hasMore = true;
    }

    state = const AsyncValue.loading();
    try {
      final data = await _apiService.getHistory(page: _currentPage);
      final items = data.map((json) => HistoryItem.fromJson(json)).toList();
      _hasMore = items.length >= 20;
      if (_currentPage == 1 || refresh) {
        state = AsyncValue.data(items);
      } else {
        final current = state.value ?? [];
        state = AsyncValue.data([...current, ...items]);
      }
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> loadMore() async {
    if (!_hasMore) return;
    _currentPage++;
    await loadHistory();
  }

  Future<void> addHistory(String newsId) async {
    await _apiService.addHistory(newsId);
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.read(apiServiceProvider), ref.read(storageServiceProvider));
});

class AuthState {
  final bool isLoggedIn;
  final bool isLoading;
  final String? token;
  final String? error;

  AuthState({
    this.isLoggedIn = false,
    this.isLoading = false,
    this.token,
    this.error,
  });

  AuthState copyWith({
    bool? isLoggedIn,
    bool? isLoading,
    String? token,
    String? error,
  }) {
    return AuthState(
      isLoggedIn: isLoggedIn ?? this.isLoggedIn,
      isLoading: isLoading ?? this.isLoading,
      token: token ?? this.token,
      error: error,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final ApiService _apiService;
  final StorageService _storageService;

  AuthNotifier(this._apiService, this._storageService) : super(AuthState()) {
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final token = _storageService.getToken();
    if (token != null) {
      _apiService.setToken(token);
      state = state.copyWith(isLoggedIn: true, token: token);
    }
  }

  Future<bool> login({String? email, String? phone, required String password}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final success = await _apiService.login(
        email: email,
        phone: phone,
        password: password,
      );

      if (success) {
        final token = _apiService.currentToken;
        if (token != null) {
          await _storageService.saveToken(token);
        }
        state = state.copyWith(isLoggedIn: true, isLoading: false, token: token);
        return true;
      } else {
        state = state.copyWith(isLoading: false, error: '登录失败');
        return false;
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }

  Future<bool> register({
    String? email,
    String? phone,
    required String password,
    String? nickname,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final success = await _apiService.register(
        email: email,
        phone: phone,
        password: password,
        nickname: nickname,
      );

      if (success) {
        final token = _apiService.currentToken;
        if (token != null) {
          await _storageService.saveToken(token);
        }
        state = state.copyWith(isLoggedIn: true, isLoading: false, token: token);
        return true;
      } else {
        state = state.copyWith(isLoading: false, error: '注册失败');
        return false;
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }

  Future<void> logout() async {
    await _storageService.removeToken();
    await _storageService.removeUserId();
    _apiService.setToken(null);
    state = AuthState();
  }
}
