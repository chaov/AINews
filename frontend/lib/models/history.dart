class HistoryItem {
  final String id;
  final String title;
  final String? summary;
  final String sourceName;
  final DateTime viewedAt;

  HistoryItem({
    required this.id,
    required this.title,
    this.summary,
    required this.sourceName,
    required this.viewedAt,
  });

  factory HistoryItem.fromJson(Map<String, dynamic> json) {
    return HistoryItem(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      summary: json['summary'],
      sourceName: json['source_name'] ?? '',
      viewedAt: DateTime.tryParse(json['viewed_at'] ?? '') ?? DateTime.now(),
    );
  }
}
