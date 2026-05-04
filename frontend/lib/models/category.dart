class Category {
  final String id;
  final String name;
  final String code;
  final String? icon;
  final int sortOrder;

  Category({
    required this.id,
    required this.name,
    required this.code,
    this.icon,
    this.sortOrder = 0,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      code: json['code'] ?? '',
      icon: json['icon'],
      sortOrder: json['sort_order'] ?? 0,
    );
  }
}
