class User {
  final String id;
  final String? email;
  final String? phone;
  final String? nickname;
  final String? avatar;
  final List<String> favorites;
  final DateTime createdAt;

  User({
    required this.id,
    this.email,
    this.phone,
    this.nickname,
    this.avatar,
    this.favorites = const [],
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? '',
      email: json['email'],
      phone: json['phone'],
      nickname: json['nickname'],
      avatar: json['avatar'],
      favorites: List<String>.from(json['favorites'] ?? []),
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
    );
  }
}

class AuthToken {
  final String accessToken;
  final String tokenType;

  AuthToken({
    required this.accessToken,
    this.tokenType = 'bearer',
  });

  factory AuthToken.fromJson(Map<String, dynamic> json) {
    return AuthToken(
      accessToken: json['access_token'] ?? '',
      tokenType: json['token_type'] ?? 'bearer',
    );
  }
}
