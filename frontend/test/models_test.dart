import 'package:flutter_test/flutter_test.dart';
import 'package:ai_news_app/frontend/lib/models/news.dart';
import 'package:ai_news_app/frontend/lib/models/user.dart';
import 'package:ai_news_app/frontend/lib/models/category.dart';

void main() {
  group('News Model', () {
    test('fromJson creates News with all fields', () {
      final json = {
        'id': 'abc123',
        'title': 'Test Title',
        'summary': 'Test Summary',
        'evaluation': 'Test Evaluation',
        'source_name': 'Test Source',
        'source_url': 'https://example.com',
        'category': 'tech',
        'tags': ['AI', 'Flutter'],
        'published_at': '2026-04-30T10:00:00Z',
        'view_count': 42,
        'is_active': true,
      };

      final news = News.fromJson(json);

      expect(news.id, 'abc123');
      expect(news.title, 'Test Title');
      expect(news.summary, 'Test Summary');
      expect(news.evaluation, 'Test Evaluation');
      expect(news.sourceName, 'Test Source');
      expect(news.sourceUrl, 'https://example.com');
      expect(news.category, 'tech');
      expect(news.tags, ['AI', 'Flutter']);
      expect(news.viewCount, 42);
      expect(news.isActive, true);
    });

    test('fromJson handles null optional fields', () {
      final json = {
        'id': 'abc123',
        'title': 'Test Title',
        'source_name': 'Source',
        'source_url': 'https://example.com',
        'category': 'tech',
        'published_at': '2026-04-30T10:00:00Z',
      };

      final news = News.fromJson(json);

      expect(news.summary, isNull);
      expect(news.evaluation, isNull);
      expect(news.tags, []);
      expect(news.viewCount, 0);
      expect(news.isActive, true);
    });

    test('fromJson handles missing fields with defaults', () {
      final json = <String, dynamic>{};

      final news = News.fromJson(json);

      expect(news.id, '');
      expect(news.title, '');
      expect(news.category, 'general');
    });

    test('toJson produces correct map', () {
      final news = News(
        id: 'abc123',
        title: 'Test',
        summary: 'Summary',
        sourceName: 'Source',
        sourceUrl: 'https://example.com',
        category: 'tech',
        tags: ['AI'],
        publishedAt: DateTime(2026, 4, 30),
      );

      final json = news.toJson();

      expect(json['id'], 'abc123');
      expect(json['title'], 'Test');
      expect(json['source_name'], 'Source');
      expect(json['tags'], ['AI']);
    });
  });

  group('User Model', () {
    test('fromJson creates User with all fields', () {
      final json = {
        'id': 'user123',
        'email': 'test@example.com',
        'phone': '13800138000',
        'nickname': 'TestUser',
        'avatar': 'https://example.com/avatar.png',
        'favorites': ['news1', 'news2'],
        'created_at': '2026-04-30T10:00:00Z',
      };

      final user = User.fromJson(json);

      expect(user.id, 'user123');
      expect(user.email, 'test@example.com');
      expect(user.phone, '13800138000');
      expect(user.nickname, 'TestUser');
      expect(user.favorites, ['news1', 'news2']);
    });

    test('fromJson handles null optional fields', () {
      final json = {
        'id': 'user123',
        'favorites': [],
        'created_at': '2026-04-30T10:00:00Z',
      };

      final user = User.fromJson(json);

      expect(user.email, isNull);
      expect(user.phone, isNull);
      expect(user.nickname, isNull);
      expect(user.avatar, isNull);
    });
  });

  group('AuthToken Model', () {
    test('fromJson creates AuthToken', () {
      final json = {
        'access_token': 'token123',
        'token_type': 'bearer',
      };

      final token = AuthToken.fromJson(json);

      expect(token.accessToken, 'token123');
      expect(token.tokenType, 'bearer');
    });

    test('fromJson uses default token_type', () {
      final json = {
        'access_token': 'token123',
      };

      final token = AuthToken.fromJson(json);

      expect(token.tokenType, 'bearer');
    });
  });

  group('Category Model', () {
    test('fromJson creates Category with all fields', () {
      final json = {
        'id': 'cat123',
        'name': '科技',
        'code': 'tech',
        'icon': 'computer',
        'sort_order': 1,
      };

      final category = Category.fromJson(json);

      expect(category.id, 'cat123');
      expect(category.name, '科技');
      expect(category.code, 'tech');
      expect(category.icon, 'computer');
      expect(category.sortOrder, 1);
    });

    test('fromJson handles null optional fields', () {
      final json = {
        'id': 'cat123',
        'name': '科技',
        'code': 'tech',
      };

      final category = Category.fromJson(json);

      expect(category.icon, isNull);
      expect(category.sortOrder, 0);
    });
  });
}
