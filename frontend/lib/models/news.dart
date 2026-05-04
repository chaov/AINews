class News {
  final String id;
  final String title;
  final String? summary;
  final String? evaluation;
  final String sourceName;
  final String sourceUrl;
  final String category;
  final List<String> tags;
  final DateTime publishedAt;
  final int viewCount;
  final bool isActive;

  News({
    required this.id,
    required this.title,
    this.summary,
    this.evaluation,
    required this.sourceName,
    required this.sourceUrl,
    required this.category,
    this.tags = const [],
    required this.publishedAt,
    this.viewCount = 0,
    this.isActive = true,
  });

  factory News.fromJson(Map<String, dynamic> json) {
    return News(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      summary: json['summary'],
      evaluation: json['evaluation'],
      sourceName: json['source_name'] ?? '',
      sourceUrl: json['source_url'] ?? '',
      category: json['category'] ?? 'general',
      tags: List<String>.from(json['tags'] ?? []),
      publishedAt: DateTime.tryParse(json['published_at'] ?? '') ?? DateTime.now(),
      viewCount: json['view_count'] ?? 0,
      isActive: json['is_active'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'summary': summary,
      'evaluation': evaluation,
      'source_name': sourceName,
      'source_url': sourceUrl,
      'category': category,
      'tags': tags,
      'published_at': publishedAt.toIso8601String(),
      'view_count': viewCount,
      'is_active': isActive,
    };
  }
}
